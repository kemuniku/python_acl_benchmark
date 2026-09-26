"""Source changes must win over timestamp-valid bytecode caches on each runtime."""

import json
import os
from pathlib import Path
import py_compile
import tempfile
import unittest

from benchkit.runner import discover, run_worker, settings_for


class BytecodeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="acl-bytecode-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.case_path = self.root / "benchmarks" / "probe"
        self.adapters = self.case_path / "implementations"
        self.adapters.mkdir(parents=True)
        (self.case_path / "case.json").write_text(json.dumps({
            "sizes": [2], "repeat": 1, "warmup": 0,
            "warmup_seconds": 0, "sample_seconds": 0,
        }))
        self.workload = self.case_path / "workload.py"
        self.workload.write_text(
            "def make_input(size, seed):\n    return [1, 2]\n"
            "def validation_cases():\n    return [([1, 2], 3)]\n"
        )
        self.adapter = self.adapters / "local.py"
        self.adapter.write_text("def run(data):\n    return sum(data) + 0\n")

    def assert_changed_source_is_used(self, path, before, after):
        self.assertEqual(len(before.encode()), len(after.encode()))
        path.write_text(before)
        original = path.stat()
        bytecode = Path(py_compile.compile(str(path), doraise=True))
        cached_bytes = bytecode.read_bytes()
        path.write_text(after)
        os.utime(path, ns=(original.st_atime_ns, original.st_mtime_ns))
        self.assertEqual(path.stat().st_size, original.st_size)
        self.assertEqual(path.stat().st_mtime_ns, original.st_mtime_ns)
        case = discover(self.root)["probe"]
        with self.assertRaisesRegex(RuntimeError, "Correctness check failed"):
            run_worker(case, case["adapters"][0], 2, settings_for(case), {})
        self.assertEqual(bytecode.read_bytes(), cached_bytes)

    def test_same_size_adapter_edit_ignores_old_bytecode(self):
        before = self.adapter.read_text()
        self.assert_changed_source_is_used(self.adapter, before, before.replace("+ 0", "+ 1"))

    def test_same_size_workload_edit_ignores_old_bytecode(self):
        before = self.workload.read_text()
        self.assert_changed_source_is_used(self.workload, before, before.replace("[([1, 2], 3)]", "[([1, 2], 4)]"))

    def test_same_size_imported_helper_edit_ignores_old_bytecode(self):
        helper = self.adapters / "_probe_helper.py"
        self.adapter.write_text("from _probe_helper import calculate\ndef run(data):\n    return calculate(data)\n")
        before = "def calculate(data):\n    return sum(data) + 0\n"
        self.assert_changed_source_is_used(helper, before, before.replace("+ 0", "+ 1"))


if __name__ == "__main__":
    unittest.main()
