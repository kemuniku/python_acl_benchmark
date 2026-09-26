"""Run the independent ACL oracles through HPy, including its debug runtime."""
import gc
import importlib
import os
from pathlib import Path
import sys
import unittest

import test_acl_cffi as oracles


class ACLHPyTests(oracles.ACLCFFITests):
    @classmethod
    def setUpClass(cls):
        try:
            cls.acl = importlib.import_module("acl_hpy")
            cls.acl.dsu(0).close()
        except ImportError as error:
            if os.environ.get("ACL_HPY_REQUIRE_NATIVE") == "1":
                raise
            raise unittest.SkipTest("HPy backend has not been built: %s" % error)

    def setUp(self):
        if os.environ.get("HPY") == "debug":
            from hpy.debug import LeakDetector
            detector = LeakDetector()
            detector.start()
            self.addCleanup(detector.stop)
            self.addCleanup(gc.collect)

    def test_universal_extension_is_loaded(self):
        native = importlib.import_module("_acl_hpy_native")
        self.assertIn(".hpy0.", native.__spec__.origin)
        with self.acl.dsu(0) as graph:
            self.assertIs(type(graph._native), native.dsu)

    def test_all_benchmark_validation_inputs(self):
        from benchkit.runner import discover
        from benchkit.worker import load_module
        for name, case in discover().items():
            adapter = case["path"] / "implementations" / "hpy_universal.py"
            if not adapter.exists():
                continue
            with self.subTest(case=name):
                workload = load_module("hpy_test_workload_" + name, case["path"] / "workload.py")
                implementation = load_module("hpy_test_adapter_" + name, adapter)
                for data, expected in workload.validation_cases():
                    self.assertEqual(implementation.run(data), expected)

    def test_isolated_worker_can_import_hpy_runtime(self):
        # An adapter named hpy.py would shadow HPy's namespace package after
        # the worker adds implementations/ to sys.path. Use hpy_universal.py.
        from benchkit.runner import discover, run_worker, settings_for
        native = importlib.import_module("_acl_hpy_native")
        source = Path(native.__spec__.origin).parent
        case = discover()["dsu"]
        adapter = next(item for item in case["adapters"] if item["source"] == "hpy")
        settings = settings_for(case, quick=True)
        result = run_worker(case, adapter, settings["sizes"][0], settings, {"hpy": source})
        self.assertEqual(len(result["samples"]), 2)
        self.assertTrue(result["checksum"])

    def test_iterables_and_edge_attributes(self):
        self.assertEqual(self.acl.convolution998244353(iter([1, 2]), iter([3, 4])), [3, 10, 8])
        self.assertEqual(self.acl.crt(iter([2, 3]), iter([3, 5])), (8, 15))
        self.assertEqual(self.acl.suffix_array(iter([2, 1, 2])), [1, 2, 0])
        with self.acl.mf_graph(n=2) as graph:
            graph.add_edge(0, 1, 2)
            self.assertEqual(graph.get_edge(0).cap, 2)
        with self.acl.mcf_graph(n=2) as graph:
            graph.add_edge(0, 1, 2, 3)
            self.assertEqual(graph.get_edge(0).cost, 3)

    def test_reentering_closed_object_and_wrong_self_are_rejected(self):
        graph = self.acl.dsu(1)
        graph.close()
        with self.assertRaises(RuntimeError):
            graph.__enter__()
        native = importlib.import_module("_acl_hpy_native")
        with self.assertRaises(TypeError):
            native.dsu.merge(object(), 0, 0)
        with self.acl.fenwick_tree(1) as tree:
            with self.assertRaises(TypeError):
                native.dsu.merge(tree._native, 0, 0)

    def test_argument_conversion_failures_release_handles(self):
        class BadIndex:
            def __index__(self):
                raise LookupError("conversion failed")

        for _ in range(20):
            for function in (self.acl.suffix_array, self.acl.z_algorithm):
                with self.assertRaises(LookupError):
                    function([1, BadIndex()])
                with self.assertRaises(OverflowError):
                    function([1, 1 << 40])
            with self.assertRaises(LookupError):
                self.acl.convolution998244353([1, BadIndex()], [1])
            with self.assertRaises(ValueError):
                self.acl.dsu(-1)
        with self.acl.dsu(1) as graph:
            with self.assertRaises(TypeError):
                graph.merge(0)
            with self.assertRaises(TypeError):
                graph.same(0, 0, 0)
            with self.assertRaises(LookupError):
                graph.leader(BadIndex())

    @unittest.skipIf(
        os.environ.get("HPY") == "debug" and getattr(sys, "pypy_version_info", ())[:3] == (7, 3, 20),
        "PyPy 7.3.20 HPy debug aborts on reentrant HPy calls from __index__; covered in normal mode",
    )
    def test_conversion_may_close_its_owner_without_use_after_free(self):
        graph = self.acl.dsu(1)

        class ClosingIndex:
            def __index__(self):
                graph.close()
                return 0

        with self.assertRaises(RuntimeError):
            graph.leader(ClosingIndex())


if __name__ == "__main__":
    unittest.main()
