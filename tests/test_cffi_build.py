import contextlib
import copy
import io
import json
import os
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from benchkit.cffi_build import build, build_environment, local_source_files
from benchkit.runner import fingerprint, run, runtime_info
from benchkit.sources import source_specs


class CffiSourceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "acl_cffi"
        self.source.mkdir()
        (self.source / "native.cpp").write_text("int example() { return 1; }\n")
        (self.source / "__init__.py").write_text("VALUE = 1\n")
        (self.source / "README.md").write_text("Documentation\n")
        (self.source / "cdef.h").write_text("int example(void);\n")
        (self.root / "requirements-cffi.txt").write_text("cffi==1.17.1\n")
        self.spec = {"url": "https://example.org/acl.git", "rev": "a" * 40,
                     "install": "cffi", "path": "acl_cffi"}

    def test_native_and_python_changes_invalidate_only_consumers(self):
        case_path = self.root / "benchmarks" / "sample"
        case_path.mkdir(parents=True)
        (case_path / "workload.py").write_text("def make_input(): return []\n")
        case = {"path": case_path}
        def key(sources):
            return fingerprint(self.root, case, {}, {}, sources)
        original = key({"cffi": self.spec})
        unrelated = key({})
        (self.source / "native.cpp").write_text("int example() { return 2; }\n")
        native_changed = key({"cffi": self.spec})
        self.assertNotEqual(original, native_changed)
        self.assertEqual(unrelated, key({}))
        (self.source / "__init__.py").write_text("VALUE = 2\n")
        python_changed = key({"cffi": self.spec})
        self.assertNotEqual(native_changed, python_changed)
        (self.source / "README.md").write_text("Edited documentation\n")
        self.assertEqual(python_changed, key({"cffi": self.spec}))

    def test_local_source_must_stay_in_repository(self):
        with self.assertRaises(ValueError):
            local_source_files(self.root, {"path": ".."})
        with self.assertRaises(ValueError):
            local_source_files(self.root, {"path": "."})
        with self.assertRaises(ValueError):
            local_source_files(self.root, {"path": "missing"})

    def test_lock_requires_a_real_local_source_directory(self):
        lock = self.root / "sources.lock.json"
        lock.write_text(json.dumps({"cffi": self.spec}))
        self.assertEqual(source_specs(self.root)["cffi"], self.spec)
        invalid = dict(self.spec)
        del invalid["path"]
        lock.write_text(json.dumps({"cffi": invalid}))
        with self.assertRaises(ValueError):
            source_specs(self.root)


    def test_build_cache_tracks_environment_and_requirements_but_not_docs(self):
        checkout = self.root / "cache" / self.spec["rev"]
        checkout.mkdir(parents=True)
        builder = Mock()
        fake_cffi = SimpleNamespace(FFI=Mock(return_value=builder))
        environment = {"packages": {"cffi": "1.17.1"}, "environment": {"CXXFLAGS": "-O2"}}
        with patch.dict(sys.modules, {"cffi": fake_cffi}), \
                patch("benchkit.cffi_build.build_environment", return_value=environment) as describe:
            first = build(self.root, checkout, self.spec, "interpreter-a")
            self.assertEqual(builder.compile.call_count, 1)
            self.assertEqual(first, build(self.root, checkout, self.spec, "interpreter-a"))
            (self.source / "README.md").write_text("Documentation changed\n")
            self.assertEqual(first, build(self.root, checkout, self.spec, "interpreter-a"))
            self.assertEqual(builder.compile.call_count, 1)
            changed = copy.deepcopy(environment)
            changed["environment"]["CXXFLAGS"] = "-O3"
            describe.return_value = changed
            second = build(self.root, checkout, self.spec, "interpreter-a")
            self.assertNotEqual(first, second)
            self.assertEqual(builder.compile.call_count, 2)
            (self.root / "requirements-cffi.txt").write_text("cffi==1.17.1\npycparser==2.23\n")
            third = build(self.root, checkout, self.spec, "interpreter-a")
            self.assertNotEqual(second, third)
            self.assertEqual(builder.compile.call_count, 3)
            marker = json.loads((third / ".bench-install-ready").read_text())
            self.assertEqual(marker["build"]["environment"], changed)

    def test_toolchain_changes_remeasure_and_preserve_build_provenance(self):
        case_path = self.root / "benchmarks" / "sample"
        (case_path / "implementations").mkdir(parents=True)
        (case_path / "case.json").write_text(json.dumps({
            "sizes": [1], "repeat": 1, "warmup": 0,
            "warmup_seconds": 0, "sample_seconds": 0,
        }))
        (case_path / "workload.py").write_text(
            "def make_input(size, seed): return list(range(size))\n"
            "def validation_cases(): return [([], 0), ([1, 2], 3)]\n")
        (case_path / "implementations" / "local.py").write_text(
            "SOURCE = 'cffi'\ndef run(data): return sum(data)\n")
        (self.root / "sources.lock.json").write_text(json.dumps({"cffi": self.spec}))
        results = self.root / "results"
        result = results / runtime_info()["id"] / "sample.json"
        first_environment = {"packages": {"setuptools": "80.9.0"}, "compilers": {"CC": "compiler v1"}}
        second_environment = {"packages": {"setuptools": "81.0.0"}, "compilers": {"CC": "compiler v2"}}
        with patch("benchkit.cffi_build.build_environment", return_value=first_environment) as describe, \
                patch("benchkit.sources.prepare", return_value={"cffi": self.source}), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(run(results, root=self.root), 1)
            first = json.loads(result.read_text())
            self.assertEqual(first["runtime"]["cffi_build"], first_environment)
            self.assertEqual(run(results, root=self.root), 0)
            describe.return_value = second_environment
            self.assertEqual(run(results, root=self.root), 1)
            second = json.loads(result.read_text())
            self.assertEqual(second["runtime"]["cffi_build"], second_environment)
            self.assertNotEqual(first["fingerprint"], second["fingerprint"])
            self.assertEqual(first["workload_fingerprint"], second["workload_fingerprint"])

    def test_build_environment_records_dependencies_commands_and_flags(self):
        packages = {name: SimpleNamespace(__version__=version) for name, version in
                    (("cffi", "1.17.1"), ("setuptools", "80.9.0"), ("pycparser", "2.23"))}
        compiler_environment = {"CC": "compiler-wrapper cc", "CXX": "compiler-wrapper c++",
                                "CXXFLAGS": "-fno-omit-frame-pointer", "LDFLAGS": "-static-libstdc++"}
        with patch.dict(sys.modules, packages), patch.dict(os.environ, compiler_environment), \
                patch("benchkit.cffi_build.shutil.which", return_value="/usr/bin/compiler-wrapper"), \
                patch("benchkit.cffi_build.subprocess.check_output", return_value="Compiler version 1\n") as version:
            actual = build_environment()
        self.assertEqual(actual["packages"], {name: module.__version__ for name, module in packages.items()})
        for name, value in compiler_environment.items():
            self.assertEqual(actual["environment"][name], value)
        self.assertEqual(actual["compilers"]["CXX"]["command"], ["compiler-wrapper", "c++"])
        self.assertEqual(version.call_count, 2)
        self.assertEqual(actual["compilers"]["CC"]["version"], "Compiler version 1\n")

    def test_build_output_keeps_subprocess_stdout_out_of_print_path(self):
        script = """
import os
import subprocess
import sys
from benchkit.cffi_build import _build_output
try:
    with _build_output():
        print('Python build output')
        os.write(1, b'Native build output\\n')
        subprocess.run([sys.executable, '-c', "print('Compiler build output')"], check=True)
        raise RuntimeError('build failed')
except RuntimeError:
    pass
print('/only/the/native/path')
"""
        result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, check=True)
        self.assertEqual(result.stdout, "/only/the/native/path\n")
        for output in ("Python build output", "Native build output", "Compiler build output"):
            self.assertIn(output, result.stderr)


if __name__ == "__main__":
    unittest.main()
