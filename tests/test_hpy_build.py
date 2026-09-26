import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from benchkit.hpy_build import build, local_source_files
from benchkit.runner import fingerprint, run, runtime_info
from benchkit.sources import source_specs


class HPyBuildTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for name in ("acl_hpy", "acl_cffi", "benchkit"):
            (self.root / name).mkdir()
        for name in ("acl_hpy/native.cpp", "acl_hpy/__init__.py", "acl_hpy/setup.py",
                     "acl_cffi/native.cpp", "acl_cffi/cdef.h", "benchkit/hpy_build.py",
                     "benchkit/cffi_build.py", "requirements-hpy.txt"):
            (self.root / name).write_text("initial\n")
        self.spec = {"url": "https://example.org/acl.git", "rev": "a" * 40,
                     "install": "hpy", "path": "acl_hpy"}
        (self.root / "sources.lock.json").write_text(json.dumps({"hpy": self.spec}))
        self.case_path = self.root / "benchmarks" / "sample"
        (self.case_path / "implementations").mkdir(parents=True)
        (self.case_path / "case.json").write_text(json.dumps({
            "sizes": [2], "repeat": 1, "warmup": 0, "warmup_seconds": 0, "sample_seconds": 0,
        }))
        (self.case_path / "workload.py").write_text(
            "def make_input(size, seed): return list(range(size))\n"
            "def validation_cases(): return [([], 0), ([1, 2], 3)]\n")
        (self.case_path / "implementations" / "hpy.py").write_text(
            "SOURCE = 'hpy'\ndef run(data): return sum(data)\n")

    def test_local_and_shared_kernel_changes_invalidate_consumers(self):
        def key(sources):
            return fingerprint(self.root, {"path": self.case_path}, {}, {}, sources)
        original = key({"hpy": self.spec})
        unrelated = key({})
        for name in ("acl_hpy/native.cpp", "acl_hpy/__init__.py", "acl_hpy/setup.py",
                     "acl_cffi/native.cpp", "acl_cffi/cdef.h", "benchkit/hpy_build.py",
                     "requirements-hpy.txt"):
            (self.root / name).write_text("changed\n")
            current = key({"hpy": self.spec})
            self.assertNotEqual(original, current, name)
            self.assertEqual(unrelated, key({}), name)
            original = current
        (self.root / "acl_hpy" / "README.md").write_text("docs only\n")
        (self.root / "acl_cffi" / "__init__.py").write_text("unrelated wrapper\n")
        self.assertEqual(original, key({"hpy": self.spec}))

    def test_source_validation_and_shared_kernel_dependencies(self):
        self.assertEqual(source_specs(self.root)["hpy"], self.spec)
        files = local_source_files(self.root, self.spec)
        self.assertIn(self.root / "acl_cffi" / "native.cpp", files)
        for path in ("..", ".", "missing"):
            with self.assertRaises(ValueError):
                local_source_files(self.root, dict(self.spec, path=path))

    def test_runtime_changes_invalidate_results_but_not_workload(self):
        first_env = {"abi": "universal", "packages": {"hpy": "0.9.0"}, "mode": "universal"}
        results = self.root / "results"
        destination = results / runtime_info()["id"] / "sample.json"
        with patch("benchkit.hpy_build.build_environment", return_value=first_env) as describe, \
                patch("benchkit.sources.prepare", return_value={"hpy": self.root / "acl_hpy"}), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(run(results, root=self.root), 1)
            first = json.loads(destination.read_text())
            self.assertEqual(first["runtime"]["hpy_build"], first_env)
            self.assertEqual(run(results, root=self.root), 0)
            describe.return_value = dict(first_env, mode="debug")
            self.assertEqual(run(results, root=self.root), 1)
            second = json.loads(destination.read_text())
            self.assertNotEqual(first["fingerprint"], second["fingerprint"])
            self.assertEqual(first["workload_fingerprint"], second["workload_fingerprint"])

    def test_build_cache_and_failed_build_retry(self):
        checkout = self.root / ".cache" / "checkout"
        checkout.mkdir(parents=True)

        def compile_module(args, **kwargs):
            self.assertIn("--hpy-abi=universal", args)
            self.assertEqual(kwargs["env"]["ACL_INCLUDE_DIR"], str(checkout))
            staged = Path(args[args.index("--build-lib") + 1] + "-hpy-universal")
            staged.mkdir()
            (staged / "_acl_hpy_native.hpy0.so").write_bytes(b"test fixture")
            (staged / "_acl_hpy_native.py").write_text("# loader\n")

        # __file__ belongs to the real builder, so mirror it into this fixture.
        with patch("benchkit.hpy_build.__file__", str(self.root / "benchkit" / "hpy_build.py")), \
                patch("benchkit.hpy_build.build_environment", return_value={"abi": "universal"}), \
                patch("benchkit.hpy_build.subprocess.run", side_effect=compile_module) as compiler:
            first = build(self.root, checkout, self.spec, "runtime")
            self.assertTrue((first / ".bench-install-ready").exists())
            self.assertEqual(first, build(self.root, checkout, self.spec, "runtime"))
            self.assertEqual(compiler.call_count, 1)
            (self.root / "acl_cffi" / "native.cpp").write_text("new kernel\n")
            compiler.side_effect = subprocess.CalledProcessError(1, ["compiler"])
            with self.assertRaises(subprocess.CalledProcessError):
                build(self.root, checkout, self.spec, "runtime")
            self.assertEqual(len(list(checkout.parent.glob("*/.bench-install-ready"))), 1)
            compiler.side_effect = compile_module
            second = build(self.root, checkout, self.spec, "runtime")
            self.assertNotEqual(first, second)
            self.assertTrue((second / ".bench-install-ready").exists())


if __name__ == "__main__":
    unittest.main()
