import contextlib
import copy
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from benchkit.cpp_reference import CASES, attach, invoke, measure_point, validate
from benchkit.runner import discover, runtime_info, settings_for
from benchkit.worker import checksum, load_module


class CPPReferenceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.case = self.root / "benchmarks" / "dsu"
        (self.case / "implementations").mkdir(parents=True)
        self.settings = dict(sizes=[2, 8], seed=42, repeat=2, warmup=0,
                             warmup_seconds=0, sample_seconds=0, timeout=4, quick=False)
        (self.case / "case.json").write_text(json.dumps(self.settings))
        (self.case / "workload.py").write_text(
            "def make_input(size, seed): return list(range(size))\n"
            "def validation_cases(): return [([1, 2], 3)]\n")
        (self.case / "implementations" / "first.py").write_text("def run(data): return sum(data)\n")
        (self.root / "sources.lock.json").write_text(json.dumps({"cpp": {"rev": "a" * 40, "url": "local"}}))
        self.results = self.root / "results"
        self.destination = self.results / "pypy" / "dsu.json"
        self.destination.parent.mkdir(parents=True)
        self.record = dict(case="dsu", runtime=dict(runtime_info(), id="pypy", implementation="PyPy"),
                           settings=self.settings, fingerprint="python-timings", measured_at="unchanged",
                           series=[dict(id="first", label="first", points=[self.point(n) for n in (2, 8)])])
        self.destination.write_text(json.dumps(self.record))
        self.info = {"flags": ["-O3"], "environment": {"compilers": {"CXX": {"version": "test compiler\n"}}}}

    def point(self, size):
        return dict(size=size, median=.001, min=.001, max=.001, samples=[.001, .001],
                    checksum=checksum(sum(range(size))))

    def test_attach_preserves_python_results_and_reuses_reference(self):
        with patch("benchkit.cpp_reference.build", return_value=(Path("/binary"), self.info)), \
                patch("benchkit.cpp_reference.validate"), \
                patch("benchkit.cpp_reference.measure_point", side_effect=lambda b, n, w, size, s: self.point(size)) as measure, \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(attach(self.results, root=self.root), 1)
            actual = json.loads(self.destination.read_text())
            self.assertEqual({k: v for k, v in actual.items() if k != "references"}, self.record)
            self.assertTrue(actual["references"][0]["reference"])
            self.assertEqual(actual["references"][0]["runtime"]["id"], "cpp")
            self.assertEqual(attach(self.results, root=self.root), 0)
            self.assertEqual(measure.call_count, 2)
            with (self.case / "workload.py").open("a") as stream:
                stream.write("\n# changed input preparation\n")
            self.assertEqual(attach(self.results, root=self.root), 1)
            self.assertEqual(measure.call_count, 4)

    def test_timeout_is_not_stored_as_a_timing_and_later_points_continue(self):
        def measure(binary, name, workload, size, settings):
            if size == 2:
                raise subprocess.TimeoutExpired(["/binary"], 4)
            return self.point(size)
        with patch("benchkit.cpp_reference.build", return_value=(Path("/binary"), self.info)), \
                patch("benchkit.cpp_reference.validate"), \
                patch("benchkit.cpp_reference.measure_point", side_effect=measure), \
                contextlib.redirect_stdout(io.StringIO()):
            attach(self.results, root=self.root)
        reference = json.loads(self.destination.read_text())["references"][0]
        self.assertEqual([p["size"] for p in reference["points"]], [8])
        self.assertEqual(reference["timeouts"], [{"size": 2, "timeout_seconds": 4}])

    def test_mismatch_does_not_overwrite_python_results(self):
        original = self.destination.read_bytes()
        with patch("benchkit.cpp_reference.build", return_value=(Path("/binary"), self.info)), \
                patch("benchkit.cpp_reference.validate"), \
                patch("benchkit.cpp_reference.measure_point", side_effect=lambda b, n, w, size, s: dict(self.point(size), checksum="wrong")), \
                contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(RuntimeError, r"C\+\+/Python result mismatch"):
                attach(self.results, root=self.root)
        self.assertEqual(self.destination.read_bytes(), original)

    def test_mismatched_host_is_rejected(self):
        record = copy.deepcopy(self.record)
        record["runtime"]["cpu"] = "Another CPU"
        self.destination.write_text(json.dumps(record))
        with patch("benchkit.cpp_reference.build", return_value=(Path("/binary"), self.info)):
            with self.assertRaisesRegex(ValueError, "host differs"):
                attach(self.results, root=self.root)


class CPPNativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        filename = os.environ.get("ACL_CPP_REFERENCE_BINARY")
        if not filename:
            raise unittest.SkipTest("Set ACL_CPP_REFERENCE_BINARY to a built standalone reference")
        cls.binary = Path(filename)
        if not cls.binary.is_file():
            raise RuntimeError("Missing C++ reference executable: " + filename)

    def test_all_workload_oracles(self):
        cases = discover()
        for name in sorted(CASES):
            with self.subTest(case=name):
                case = cases[name]
                workload = load_module("_test_cpp_" + name, case["path"] / "workload.py")
                validate(self.binary, name, workload, settings_for(case, quick=True))

    def test_real_measurements_and_timeout(self):
        case = discover()["dsu"]
        workload = load_module("_cpp_test_dsu", case["path"] / "workload.py")
        settings = settings_for(case, quick=True)
        point = measure_point(self.binary, "dsu", workload, 19, settings)
        self.assertEqual(point["checksum"], checksum(workload.oracle(workload.make_input(19, settings["seed"]))))
        self.assertEqual(len(point["samples"]), 2)
        self.assertGreater(point["min"], 0)
        with self.assertRaises(subprocess.TimeoutExpired):
            invoke(self.binary, "dsu", workload.make_input(2, 0),
                   dict(settings, timeout=.02, warmup_seconds=10))


if __name__ == "__main__":
    unittest.main()
