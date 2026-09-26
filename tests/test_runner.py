import contextlib
import copy
import subprocess
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from benchkit.runner import discover, fingerprint, read_json, reusable, run, runtime_info, settings_for


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.results = self.root / "results"
        self.make_case("one")
        self.make_case("two")

    def make_case(self, name):
        directory = self.root / "benchmarks" / name
        (directory / "implementations").mkdir(parents=True)
        (directory / "case.json").write_text(json.dumps({
            "title": name, "sizes": [2, 8], "repeat": 2, "warmup": 0,
            "warmup_seconds": 0, "sample_seconds": 0,
        }))
        (directory / "workload.py").write_text(
            "def make_input(size, seed):\n    return list(range(size))\n"
            "def validation_cases():\n    return [([], 0), ([1, 2], 3)]\n"
        )
        (directory / "implementations" / "first.py").write_text("def run(data):\n    return sum(data)\n")
        return directory

    def execute(self, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()):
            return run(self.results, root=self.root, **kwargs)

    def result(self, name):
        return self.results / runtime_info()["id"] / (name + ".json")

    def test_initial_unchanged_and_case_local_invalidation(self):
        self.assertEqual(self.execute(), 2)
        unchanged = self.result("two").read_bytes()
        self.assertEqual(self.execute(), 0)
        adapter = self.root / "benchmarks/one/implementations/first.py"
        adapter.write_text(adapter.read_text() + "\n# implementation changed\n")
        self.assertEqual(self.execute(), 1)
        self.assertEqual(self.result("two").read_bytes(), unchanged)
        self.assertEqual(self.execute(force=True), 2)

    def test_add_remove_implementation_and_deleted_case(self):
        self.execute()
        second = self.root / "benchmarks/one/implementations/second.py"
        second.write_text("LABEL = 'New implementation'\ndef run(data):\n    return sum(data)\n")
        self.assertEqual(self.execute(), 1)
        self.assertEqual(len(read_json(self.result("one"))["series"]), 2)
        second.unlink()
        self.assertEqual(self.execute(), 1)
        self.assertEqual(len(read_json(self.result("one"))["series"]), 1)
        (self.root / "benchmarks/two/case.json").unlink()
        self.assertEqual(self.execute(), 0)
        self.assertFalse(self.result("two").exists())

    def test_bad_answers_fail_without_overwriting_previous_success(self):
        self.execute(selected=["one"])
        previous = self.result("one").read_bytes()
        (self.root / "benchmarks/one/implementations/first.py").write_text("def run(data):\n    return -1\n")
        with self.assertRaisesRegex(RuntimeError, "Correctness check failed"):
            self.execute(selected=["one"])
        self.assertEqual(self.result("one").read_bytes(), previous)

    def test_full_size_output_mismatch_fails(self):
        (self.root / "benchmarks/one/implementations/second.py").write_text(
            "def run(data):\n    return sum(data) + (1 if len(data) > 2 else 0)\n"
        )
        with self.assertRaisesRegex(RuntimeError, "Result mismatch"):
            self.execute(selected=["one"])
        self.assertFalse(self.result("one").exists())

    def test_worker_timeout(self):
        config = self.root / "benchmarks/one/case.json"
        settings = json.loads(config.read_text())
        settings["timeout"] = 0.01
        config.write_text(json.dumps(settings))
        (self.root / "benchmarks/one/implementations/first.py").write_text(
            "import time\ndef run(data):\n    time.sleep(1)\n    return sum(data)\n"
        )
        with self.assertRaisesRegex(RuntimeError, "timed out"):
            self.execute(selected=["one"])

    def test_input_mutation_is_rejected(self):
        (self.root / "benchmarks/one/implementations/first.py").write_text(
            "def run(data):\n    result = sum(data)\n    data.append(0)\n    return result\n"
        )
        with self.assertRaisesRegex(RuntimeError, "must not mutate"):
            self.execute(selected=["one"])

    def test_corrupt_cache_is_remeasured(self):
        self.execute(selected=["one"])
        self.result("one").write_text("broken json")
        self.assertEqual(self.execute(selected=["one"]), 1)

    def test_invalid_cached_samples_and_summaries_are_not_reused(self):
        self.execute(selected=["one"])
        path = self.result("one")
        previous = read_json(path)
        case = discover(self.root)["one"]
        settings = settings_for(case)
        bad_points = [
            {"samples": [float("nan"), 1.0]},
            {"samples": [float("inf"), 1.0]},
            {"samples": [float("-inf"), 1.0]},
            {"samples": [-1.0, 1.0]},
            {"samples": [0.0, 1.0]},
            {"samples": [True, 1.0]},
            {"samples": ["1", 1.0]},
            {"samples": [10 ** 400, 1.0]},
            {"samples": [1.0]},
            {"median": float("nan")},
            {"min": float("inf")},
            {"max": -1.0},
            {"median": previous["series"][0]["points"][0]["median"] + 1.0},
            {"samples": [1.0, 1.0], "min": 1.0, "max": 1.0, "median": True},
            {"samples": [1e308, 1e308], "min": 1e308, "max": 1e308, "median": float("inf")},
        ]
        for changes in bad_points:
            with self.subTest(changes=changes):
                corrupted = copy.deepcopy(previous)
                corrupted["series"][0]["points"][0].update(changes)
                path.write_text(json.dumps(corrupted))
                self.assertFalse(reusable(path, previous["fingerprint"], case, settings))
        # Cache rejection must lead to successful recovery through the run path.
        self.assertEqual(self.execute(selected=["one"]), 1)
        self.assertTrue(reusable(path, previous["fingerprint"], case, settings))

    def test_matching_runtime_results_share_workload_identity(self):
        native_runtime = runtime_info()
        peer_runtime = dict(native_runtime, id="peer", implementation="PeerPython", version="0.0")
        self.execute(selected=["one"])
        native = read_json(self.result("one"))
        with patch("benchkit.runner.runtime_info", return_value=peer_runtime):
            self.assertEqual(self.execute(selected=["one"]), 1)
        peer = read_json(self.results / "peer" / "one.json")
        self.assertNotEqual(native["fingerprint"], peer["fingerprint"])
        self.assertEqual(native["workload_fingerprint"], peer["workload_fingerprint"])
        self.assertEqual(
            [p["checksum"] for p in native["series"][0]["points"]],
            [p["checksum"] for p in peer["series"][0]["points"]],
        )

    def test_cross_runtime_mismatch_preserves_previous_success(self):
        native_runtime = runtime_info()
        peer_runtime = dict(native_runtime, id="peer", implementation="PeerPython")
        self.execute(selected=["one"])
        with patch("benchkit.runner.runtime_info", return_value=peer_runtime):
            self.execute(selected=["one"])
            path = self.results / "peer" / "one.json"
            previous = path.read_bytes()
            original_points = read_json(path)["series"][0]["points"]

            def different_output(case, adapter, size, settings, source_paths):
                point = copy.deepcopy(next(p for p in original_points if p["size"] == size))
                point["checksum"] = "different-output-on-peer-runtime"
                return point

            with patch("benchkit.runner.run_worker", side_effect=different_output):
                with self.assertRaisesRegex(RuntimeError, "Cross-runtime result mismatch"):
                    self.execute(selected=["one"], force=True)
            self.assertEqual(path.read_bytes(), previous)

    def test_previous_workload_runtime_results_are_not_used_as_oracle(self):
        self.execute(selected=["one"])
        native = read_json(self.result("one"))
        workload = self.root / "benchmarks/one/workload.py"
        workload.write_text(workload.read_text().replace("list(range(size))", "list(range(size * 2))"))
        peer_runtime = dict(runtime_info(), id="peer", implementation="PeerPython")
        with patch("benchkit.runner.runtime_info", return_value=peer_runtime):
            self.assertEqual(self.execute(selected=["one"]), 1)
        peer = read_json(self.results / "peer" / "one.json")
        self.assertNotEqual(native["workload_fingerprint"], peer["workload_fingerprint"])
        self.assertNotEqual(native["series"][0]["points"][0]["checksum"], peer["series"][0]["points"][0]["checksum"])

    def test_non_object_peer_json_does_not_block_regeneration(self):
        peer_path = self.results / "peer" / "one.json"
        peer_path.parent.mkdir(parents=True)
        for value in ([], None):
            with self.subTest(peer=value):
                peer_path.write_text(json.dumps(value))
                self.assertEqual(self.execute(selected=["one"], force=True), 1)
                self.assertTrue(self.result("one").is_file())

    def test_repository_without_a_commit_records_uncommitted(self):
        subprocess.run(["git", "init", "--quiet", str(self.root)], check=True, capture_output=True)
        self.execute(selected=["one"])
        self.assertEqual(read_json(self.result("one"))["commit"], "uncommitted")

    def test_quick_and_full_results_are_distinct(self):
        self.assertEqual(self.execute(selected=["one"], quick=True), 1)
        self.assertEqual(len(read_json(self.result("one"))["series"][0]["points"]), 1)
        self.assertEqual(self.execute(selected=["one"]), 1)

    def test_unused_source_does_not_invalidate_others(self):
        lock = self.root / "sources.lock.json"
        lock.write_text(json.dumps({"library": {"url": "local", "rev": "a" * 40}}))
        adapter = self.root / "benchmarks/one/implementations/first.py"
        adapter.write_text("SOURCE = 'library'\n" + adapter.read_text())
        with patch("benchkit.sources.prepare", return_value={"library": self.root}):
            self.assertEqual(self.execute(), 2)
            lock.write_text(json.dumps({"library": {"url": "local", "rev": "b" * 40}}))
            self.assertEqual(self.execute(), 1)

    def test_shared_code_and_environment_invalidate_but_report_does_not(self):
        case = discover(self.root)["one"]
        runtime = runtime_info()
        settings = settings_for(case)
        initial = fingerprint(self.root, case, runtime, settings, {})
        (self.root / "benchkit").mkdir()
        (self.root / "benchkit/report.py").write_text("# appearance only")
        self.assertEqual(initial, fingerprint(self.root, case, runtime, settings, {}))
        (self.root / "benchkit/worker.py").write_text("# timings changed")
        self.assertNotEqual(initial, fingerprint(self.root, case, runtime, settings, {}))
        self.assertNotEqual(initial, fingerprint(self.root, case, dict(runtime, version="0.0"), settings, {}))

    def test_unknown_case_and_invalid_config_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unknown cases"):
            self.execute(selected=["missing"])
        config = self.root / "benchmarks/one/case.json"
        config.write_text('{"sizes": [10, 1]}')
        with self.assertRaisesRegex(ValueError, "increasing positive"):
            discover(self.root)


if __name__ == "__main__":
    unittest.main()
