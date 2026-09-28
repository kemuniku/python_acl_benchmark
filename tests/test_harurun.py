"""Validate the pinned upstream adapters against independent workload oracles."""
import copy
import os
from pathlib import Path
import sys
import unittest

from benchkit.runner import discover
from benchkit.worker import checksum, load_module


class HarurunTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = os.environ.get("ACL_HARURUN_SOURCE")
        if not source:
            raise unittest.SkipTest("Set ACL_HARURUN_SOURCE to the pinned upstream checkout")
        if not all((Path(source) / name).is_dir() for name in ("library", "library_codex")):
            raise RuntimeError("Missing harurun library or library_codex: " + source)
        sys.path.insert(0, source)
        cls.addClassCleanup(sys.path.remove, source)

    def test_all_adapters_against_oracles_without_input_mutation(self):
        cases = discover()
        expected = {"dsu", "fenwicktree", "segtree", "lazysegtree", "convolution",
                    "crt", "floor_sum", "scc", "two_sat", "maxflow", "mincostflow",
                    "suffix_array", "lcp_array", "z_algorithm"}
        self.assertTrue(expected <= cases.keys())
        old_library = expected - {"crt", "maxflow", "mincostflow"}
        for name in sorted(expected):
            case = cases[name]
            for variant in (("harurun", "harurun_library") if name in old_library else ("harurun",)):
                with self.subTest(case=name, variant=variant):
                    self.check_adapter(name, case, variant)

    def check_adapter(self, name, case, variant):
        adapter = load_module("_" + variant + "_adapter_" + name,
                              case["path"] / "implementations" / (variant + ".py"))
        workload = load_module("_harurun_workload_" + name, case["path"] / "workload.py")
        validation = list(workload.validation_cases())
        # CRT/flow benchmark inputs exceed their brute-force oracles;
        # those already provide randomized tiny validation cases.
        sizes = () if name in ("crt", "floor_sum", "maxflow", "mincostflow") else (1, 2, 5)
        for size in sizes:
            for seed in (0, 17, 42):
                data = workload.make_input(size, seed)
                validation.append((data, workload.oracle(data)))
        for data, expected in validation:
            original = copy.deepcopy(data)
            self.assertEqual(checksum(adapter.run(data)), checksum(expected))
            self.assertEqual(checksum(adapter.run(data)), checksum(expected))
            self.assertEqual(data, original)


if __name__ == "__main__":
    unittest.main()
