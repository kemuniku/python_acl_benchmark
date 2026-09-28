"""Official fixtures and independent small-case checks for every ordered set."""
import copy
import os
from pathlib import Path
import random
import unittest

from benchkit.runner import discover
from benchkit.worker import checksum, load_module


class OrderedSetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        checkout = os.environ.get("ACL_ORDERED_SET_SOURCE")
        if not checkout:
            if os.environ.get("ACL_ORDERED_SET_REQUIRE"):
                raise RuntimeError("ACL_ORDERED_SET_SOURCE must point to official generated fixtures")
            raise unittest.SkipTest("Set ACL_ORDERED_SET_SOURCE to generated Library Checker tests")
        os.environ["ACL_BENCH_FIXTURES"] = checkout
        cls.addClassCleanup(os.environ.pop, "ACL_BENCH_FIXTURES", None)
        cls.case = discover()["ordered_set"]
        cls.workload = load_module("_ordered_set_workload_test", cls.case["path"] / "workload.py")

    def test_official_and_random_cases(self):
        workload = self.workload
        cases = list(workload.validation_cases())
        for index in (1, 2):
            data = workload.make_input(index, 42)
            cases.append((data, workload.expected_output(index)))
        large, queries = workload.make_input(6, 42)
        cases.append(((large, queries[:256]), workload.oracle((large, queries[:256]))))
        rng = random.Random(223)
        for _ in range(30):
            initial = sorted(set(rng.randrange(64) for _ in range(rng.randrange(20))))
            queries = [(kind := rng.randrange(6), rng.randrange(1, 30) if kind == 2 else rng.randrange(64))
                       for _ in range(60)]
            data = initial, queries
            cases.append((data, workload.oracle(data)))
        for adapter_info in self.case["adapters"]:
            adapter = load_module("_ordered_adapter_" + adapter_info["id"], adapter_info["path"])
            for index, (data, expected) in enumerate(cases):
                with self.subTest(adapter=adapter_info["id"], case=index):
                    original = copy.deepcopy(data)
                    self.assertEqual(checksum(adapter.run(data)), checksum(expected))
                    self.assertEqual(data, original)


if __name__ == "__main__":
    unittest.main()
