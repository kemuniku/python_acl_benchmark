"""Independent correctness and boundary checks for the optional native backend."""

import gc
import importlib
import itertools
import math
import os
import random
import unittest
import weakref


class ACLCFFITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.acl = importlib.import_module("acl_cffi")
            cls.acl.dsu(0).close()
        except ImportError as error:
            if os.environ.get("ACL_CFFI_REQUIRE_NATIVE") == "1":
                raise
            raise unittest.SkipTest("CFFI backend has not been built: %s" % error)

    def test_dsu_matches_explicit_component_labels(self):
        rng = random.Random(731)
        for n in (0, 1, 2, 17):
            with self.subTest(n=n), self.acl.dsu(n) as graph:
                labels = list(range(n))
                for _ in range(150 if n else 0):
                    a, b = rng.randrange(n), rng.randrange(n)
                    if rng.randrange(2):
                        old, new = labels[b], labels[a]
                        labels = [new if x == old else x for x in labels]
                        leader = graph.merge(a, b)
                        self.assertEqual(graph.leader(a), leader)
                        self.assertEqual(graph.leader(b), leader)
                    self.assertEqual(graph.same(a, b), labels[a] == labels[b])
                    self.assertEqual(graph.size(a), labels.count(labels[a]))
                expected = {frozenset(i for i in range(n) if labels[i] == x)
                            for x in labels}
                self.assertEqual({frozenset(group) for group in graph.groups()}, expected)

    def test_ordered_set_avl_rank_predecessor_and_reinsertion(self):
        if not hasattr(self.acl, "ordered_set"):
            self.skipTest("CFFI-only AVL ordered set")
        import bisect
        rng = random.Random(707)
        with self.acl.ordered_set() as tree:
            expected = []
            for _ in range(2000):
                x = rng.randrange(250)
                index = bisect.bisect_left(expected, x)
                if rng.randrange(2):
                    added = index == len(expected) or expected[index] != x
                    self.assertEqual(tree.add(x), added)
                    if added:
                        expected.insert(index, x)
                else:
                    removed = index < len(expected) and expected[index] == x
                    self.assertEqual(tree.discard(x), removed)
                    if removed:
                        expected.pop(index)
                self.assertEqual(tree.count_leq(x), bisect.bisect_right(expected, x))
                self.assertEqual(tree.kth(len(expected) + 1), -1)
                self.assertEqual(tree.kth(1), expected[0] if expected else -1)
                self.assertEqual(tree.le(x), expected[bisect.bisect_right(expected, x) - 1]
                                 if bisect.bisect_right(expected, x) else -1)
                self.assertEqual(tree.ge(x), expected[index] if index < len(expected) else -1)
            with self.assertRaises(ValueError):
                tree.add(-1)
        with self.assertRaises(RuntimeError):
            tree.kth(1)

    def test_ordered_set_adapter_matches_python_oracle(self):
        if not hasattr(self.acl, "ordered_set"):
            self.skipTest("CFFI-only ordered set")
        from benchkit.worker import load_module
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        workload = load_module("ordered_set_operation_oracle", root / "benchmarks/ordered_set/workload.py")
        adapter = load_module("ordered_set_operation_adapter", root / "benchmarks/ordered_set/implementations/cffi.py")
        rng = random.Random(9921)
        for _ in range(15):
            initial = [rng.randrange(90) for _ in range(30)]
            queries = [(kind := rng.randrange(6), rng.randrange(1, 110) if kind == 2 else rng.randrange(110))
                       for _ in range(200)]
            self.assertEqual(adapter.run((initial, queries)), workload.oracle((initial, queries)))

    def test_callback_segment_trees_match_naive_ranges(self):
        if not hasattr(self.acl, "segtree"):
            self.skipTest("CFFI-only segment trees")
        from operator import add
        rng = random.Random(134)
        for n in (0, 1, 5, 25):
            values = [rng.randrange(-20, 20) for _ in range(n)]
            with self.acl.segtree(add, 0, values) as tree:
                for _ in range(80):
                    if n and rng.randrange(2):
                        i, v = rng.randrange(n), rng.randrange(-20, 20)
                        values[i] = v
                        tree.set(i, v)
                    left, right = sorted((rng.randrange(n + 1), rng.randrange(n + 1)))
                    self.assertEqual(tree.prod(left, right), sum(values[left:right]))
            with self.acl.lazy_segtree(lambda a, b: (a[0] + b[0], a[1] + b[1]), (0, 0),
                                       lambda f, v: (v[0] + f * v[1], v[1]), add, 0,
                                       [(v, 1) for v in values]) as tree:
                for _ in range(80):
                    left, right = sorted((rng.randrange(n + 1), rng.randrange(n + 1)))
                    if rng.randrange(2):
                        delta = rng.randrange(-10, 10)
                        tree.apply(left, right, delta)
                        values[left:right] = [v + delta for v in values[left:right]]
                    self.assertEqual(tree.prod(left, right), sum(values[left:right]))

    def test_fenwick_matches_python_sums(self):
        rng = random.Random(953)
        for n in (0, 1, 3, 32):
            with self.subTest(n=n), self.acl.fenwick_tree(n) as tree:
                values = [0] * n
                self.assertEqual(tree.sum(0, n), 0)
                for _ in range(100 if n else 0):
                    index, delta = rng.randrange(n), rng.randrange(-100, 101)
                    values[index] += delta
                    tree.add(index, delta)
                    left, right = sorted((rng.randrange(n + 1), rng.randrange(n + 1)))
                    self.assertEqual(tree.sum(left, right), sum(values[left:right]))
                self.assertEqual(tree.sum(0, n), sum(values))

    def test_scc_matches_reachability_and_topological_order(self):
        rng = random.Random(417)
        for n in range(9):
            for _ in range(8):
                edges = [(a, b) for a in range(n) for b in range(n)
                         if rng.randrange(4) == 0]
                reachable = [[a == b for b in range(n)] for a in range(n)]
                with self.acl.scc_graph(n) as graph:
                    for a, b in edges:
                        graph.add_edge(a, b)
                        reachable[a][b] = True
                    for middle in range(n):
                        for a in range(n):
                            for b in range(n):
                                reachable[a][b] |= reachable[a][middle] and reachable[middle][b]
                    groups = graph.scc()
                self.assertEqual(sorted(v for group in groups for v in group), list(range(n)))
                component = {v: index for index, group in enumerate(groups) for v in group}
                for a in range(n):
                    for b in range(n):
                        self.assertEqual(component[a] == component[b],
                                         reachable[a][b] and reachable[b][a])
                for a, b in edges:
                    self.assertLessEqual(component[a], component[b])

    def test_two_sat_matches_exhaustive_assignments(self):
        rng = random.Random(109)
        for n in range(7):
            for _ in range(12):
                clauses = [(rng.randrange(n), bool(rng.randrange(2)),
                            rng.randrange(n), bool(rng.randrange(2)))
                           for _ in range(3 * n)]
                valid = lambda answer: all(answer[a] == f or answer[b] == g
                                           for a, f, b, g in clauses)
                expected = any(valid(answer) for answer in
                               itertools.product((False, True), repeat=n))
                with self.acl.two_sat(n) as solver:
                    for clause in clauses:
                        solver.add_clause(*clause)
                    self.assertEqual(solver.satisfiable(), expected)
                    if expected:
                        answer = solver.answer()
                        self.assertEqual(len(answer), n)
                        self.assertTrue(valid(answer))

    def test_two_sat_answers_require_a_current_satisfying_solution(self):
        with self.acl.two_sat(1) as solver:
            with self.assertRaises(RuntimeError):
                solver.answer()
            solver.add_clause(0, True, 0, True)
            self.assertTrue(solver.satisfiable())
            self.assertEqual(solver.answer(), [True])
            solver.add_clause(0, False, 0, False)
            with self.assertRaises(RuntimeError):
                solver.answer()
            self.assertFalse(solver.satisfiable())
            with self.assertRaises(RuntimeError):
                solver.answer()

    def test_maxflow_matches_exhaustive_cuts(self):
        rng = random.Random(809)
        for n in range(2, 7):
            for _ in range(12):
                edges = [(rng.randrange(n), rng.randrange(n), rng.randrange(4))
                         for _ in range(2 * n)]
                cuts = [{0} | {v for v, chosen in zip(range(1, n - 1), mask) if chosen}
                        for mask in itertools.product((False, True), repeat=n - 2)]
                expected = min(sum(cap for a, b, cap in edges if a in cut and b not in cut)
                               for cut in cuts)
                with self.acl.mf_graph(n) as graph:
                    for edge in edges:
                        graph.add_edge(*edge)
                    self.assertEqual(graph.flow(0, n - 1), expected)
                    self.assertEqual(graph.flow(0, n - 1), 0)
                    cut = graph.min_cut(0)
                    self.assertTrue(cut[0])
                    self.assertFalse(cut[-1])
                    self.assertEqual(sum(cap for a, b, cap in edges if cut[a] and not cut[b]),
                                     expected)

    def test_maxflow_flow_limit_preserves_residual_graph(self):
        with self.acl.mf_graph(3) as graph:
            graph.add_edge(0, 1, 7)
            graph.add_edge(1, 2, 5)
            self.assertEqual(graph.flow(0, 2, 2), 2)
            self.assertEqual(graph.flow(0, 2), 3)

    def test_flow_edge_inspection_and_capacity_change(self):
        with self.acl.mf_graph(3) as graph:
            first = graph.add_edge(0, 1, 4)
            second = graph.add_edge(1, 2, 3)
            self.assertEqual((first, second), (0, 1))
            self.assertEqual(tuple(graph.get_edge(first)), (0, 1, 4, 0))
            graph.change_edge(first, 2, 0)
            self.assertEqual(graph.flow(0, 2), 2)
            self.assertEqual([tuple(edge) for edge in graph.edges()],
                             [(0, 1, 2, 2), (1, 2, 3, 2)])
            with self.assertRaises(ValueError):
                graph.change_edge(first, 1, 2)
            with self.assertRaises(ValueError):
                graph.get_edge(2)
        with self.acl.mcf_graph(3) as graph:
            first = graph.add_edge(0, 1, 2, 3)
            second = graph.add_edge(1, 2, 1, 4)
            self.assertEqual((first, second), (0, 1))
            self.assertEqual(tuple(graph.get_edge(first)), (0, 1, 2, 0, 3))
            self.assertEqual(tuple(graph.flow(0, 2)), (1, 7))
            self.assertEqual([tuple(edge) for edge in graph.edges()],
                             [(0, 1, 2, 1, 3), (1, 2, 1, 1, 4)])

    def test_mincostflow_matches_exhaustive_integral_flows(self):
        rng = random.Random(457)
        # Small DAGs avoid negative residual cycles in the independent flow oracle.
        for _ in range(24):
            n = 4
            edges = [(a, b, rng.randrange(3), rng.randrange(5))
                     for a in range(n) for b in range(a + 1, n)]
            feasible = []
            for amounts in itertools.product(*(range(cap + 1) for a, b, cap, cost in edges)):
                balance, price = [0] * n, 0
                for (a, b, cap, cost), amount in zip(edges, amounts):
                    balance[a] -= amount
                    balance[b] += amount
                    price += amount * cost
                if not any(balance[1:-1]):
                    feasible.append((balance[-1], price))
            expected = min(feasible, key=lambda value: (-value[0], value[1]))
            with self.acl.mcf_graph(n) as graph:
                for edge in edges:
                    graph.add_edge(*edge)
                self.assertEqual(tuple(graph.flow(0, n - 1)), expected)

    def test_mincostflow_limit_and_repeat_call_guard(self):
        with self.acl.mcf_graph(3) as graph:
            graph.add_edge(0, 1, 3, 2)
            graph.add_edge(1, 2, 3, 4)
            self.assertEqual(tuple(graph.flow(0, 2, 2)), (2, 12))
            with self.assertRaises(RuntimeError):
                graph.flow(0, 2)
            with self.assertRaises(RuntimeError):
                graph.add_edge(0, 2, 1, 0)

    def test_computed_integer_overflows_are_rejected(self):
        largest = (1 << 63) - 1
        with self.acl.fenwick_tree(2) as tree:
            tree.add(0, largest)
            tree.add(1, largest)
            self.assertEqual(tree.sum(0, 1), largest)
            with self.assertRaises(OverflowError):
                tree.sum(0, 2)
            tree.add(1, -largest)
            self.assertEqual(tree.sum(0, 2), largest)
        with self.acl.mcf_graph(2) as graph:
            graph.add_edge(0, 1, 2, largest)
            with self.assertRaises(OverflowError):
                graph.flow(0, 1)
        with self.assertRaises(OverflowError):
            self.acl.crt([0, 0], [largest, 2])
        with self.assertRaises(OverflowError):
            self.acl.floor_sum(3, 1, largest, 0)

    def test_convolution_matches_quadratic_oracle_including_ntt(self):
        rng = random.Random(229)
        modulus = 998244353
        # Both lengths > 60 exercise ACL's NTT path, including non-power-of-two lengths.
        for n, m in ((0, 0), (0, 4), (1, 1), (4, 7), (61, 67), (97, 101)):
            left = [rng.randrange(-2 * modulus, 2 * modulus) for _ in range(n)]
            right = [rng.randrange(-2 * modulus, 2 * modulus) for _ in range(m)]
            before = left[:], right[:]
            expected = [0] * (n + m - 1) if n and m else []
            for i, a in enumerate(left):
                for j, b in enumerate(right):
                    expected[i + j] = (expected[i + j] + a * b) % modulus
            self.assertEqual(self.acl.convolution998244353(left, right), expected)
            self.assertEqual((left, right), before)

    def test_crt_matches_exhaustive_residues(self):
        rng = random.Random(541)
        cases = [([], []), ([1, 0], [2, 2]), ([-1, 2], [4, 6]), ([99], [1])]
        cases += [([rng.randrange(-10, 11) for _ in range(3)],
                   [rng.randrange(1, 9) for _ in range(3)]) for _ in range(60)]
        for residues, moduli in cases:
            common = math.lcm(*moduli)
            solutions = [x for x in range(common)
                         if all(x % m == r % m for r, m in zip(residues, moduli))]
            expected = (solutions[0], common) if solutions else (0, 0)
            self.assertEqual(tuple(self.acl.crt(residues, moduli)), expected)

    def test_crt_large_moduli_and_overflow(self):
        rng = random.Random(941)
        for _ in range(100):
            moduli = [rng.randrange(1, 100000) for _ in range(4)]
            residues = [rng.randrange(-100000, 100000) for _ in moduli]
            expected_r, expected_m = 0, 1
            for ri, mi in zip(residues, moduli):
                gcd = math.gcd(expected_m, mi)
                if (ri - expected_r) % gcd:
                    expected_r, expected_m = 0, 0
                    break
                factor = mi // gcd
                x = ((ri - expected_r) // gcd * pow(expected_m // gcd, -1, factor)) % factor if factor > 1 else 0
                expected_r = (expected_r + expected_m * x) % (expected_m * factor)
                expected_m *= factor
            if expected_m <= (1 << 63) - 1:
                self.assertEqual(self.acl.crt(residues, moduli), (expected_r, expected_m))
        maximum = (1 << 63) - 1
        self.assertEqual(self.acl.crt([maximum - 1, 0], [maximum, 1]), (maximum - 1, maximum))
        with self.assertRaises(OverflowError):
            self.acl.crt([maximum - 1, 0], [maximum, 2])

    def test_floor_sum_matches_python_integer_division(self):
        rng = random.Random(641)
        for _ in range(300):
            n, m = rng.randrange(30), rng.randrange(1, 40)
            a, b = rng.randrange(-70, 71), rng.randrange(-70, 71)
            self.assertEqual(self.acl.floor_sum(n, m, a, b),
                             sum((a * i + b) // m for i in range(n)))

    def test_string_algorithms_match_naive_codepoint_and_byte_oracles(self):
        rng = random.Random(103)
        values = ["", "a", "banana", "aaaaa", "あ😀あ\x00é😀", b"\x00\xff\x00a\xff", [],
                  [8, 2, 8, 0, 2], [-3, 4, -3, 0]]
        values += [[rng.randrange(6) for _ in range(n)] for n in (9, 41, 103)]
        for value in values:
            with self.subTest(value=value):
                expected_sa = sorted(range(len(value)), key=lambda i: value[i:])
                sa = self.acl.suffix_array(value)
                self.assertEqual(sa, expected_sa)
                expected_lcp = []
                for a, b in zip(sa, sa[1:]):
                    common = 0
                    while a + common < len(value) and b + common < len(value):
                        if value[a + common] != value[b + common]:
                            break
                        common += 1
                    expected_lcp.append(common)
                self.assertEqual(self.acl.lcp_array(value, sa), expected_lcp)
                expected_z = []
                for start in range(len(value)):
                    common = 0
                    while start + common < len(value) and value[common] == value[start + common]:
                        common += 1
                    expected_z.append(common)
                self.assertEqual(self.acl.z_algorithm(value), expected_z)

    def test_z_algorithm_large_ascii_and_bytes_inputs(self):
        for value in ("a" * 10000, b"\x00" * 10000, "ab\x00" * 3000):
            with self.subTest(kind=type(value), length=len(value)):
                if len(set(value)) == 1:
                    expected = [len(value) - i for i in range(len(value))]
                else:
                    expected = [len(value)] + [0] * (len(value) - 1)
                    for i in range(3, len(value), 3):
                        expected[i] = len(value) - i
                self.assertEqual(self.acl.z_algorithm(value), expected)

    def test_native_handle_close_is_idempotent_and_context_manager_closes(self):
        for constructor, method, args in (
                (self.acl.dsu, "groups", ()),
                (self.acl.fenwick_tree, "sum", (0, 1)),
                (self.acl.scc_graph, "scc", ()),
                (self.acl.two_sat, "satisfiable", ()),
                (self.acl.mf_graph, "add_edge", (0, 1, 1)),
                (self.acl.mcf_graph, "add_edge", (0, 1, 1, 1))):
            with self.subTest(constructor=constructor.__name__):
                with constructor(2) as instance:
                    self.assertIsNotNone(instance)
                instance.close()
                with self.assertRaises(RuntimeError):
                    getattr(instance, method)(*args)

    def test_native_handles_do_not_keep_python_owners_alive(self):
        # The ffi.gc finalizer must not capture its Python owner and create a cycle.
        for constructor in (self.acl.dsu, self.acl.fenwick_tree, self.acl.scc_graph,
                            self.acl.two_sat, self.acl.mf_graph, self.acl.mcf_graph):
            instance = constructor(4)
            reference = weakref.ref(instance)
            del instance
            gc.collect()
            gc.collect()  # PyPy may schedule native finalizers after the first collection.
            self.assertIsNone(reference())

    def test_invalid_domains_are_rejected_before_native_calls(self):
        for constructor in (self.acl.dsu, self.acl.fenwick_tree, self.acl.scc_graph,
                            self.acl.two_sat, self.acl.mf_graph, self.acl.mcf_graph):
            with self.subTest(constructor=constructor.__name__):
                with self.assertRaises((ValueError, OverflowError)):
                    constructor(-1)
                with self.assertRaises(OverflowError):
                    constructor(1 << 63)
        with self.assertRaises(ValueError):
            self.acl.fenwick_tree(1 << 30)
        with self.acl.dsu(2) as graph:
            for index in (-1, 2):
                with self.assertRaises((IndexError, ValueError)):
                    graph.leader(index)
        with self.acl.fenwick_tree(2) as tree:
            with self.assertRaises((IndexError, ValueError)):
                tree.add(2, 1)
            with self.assertRaises((IndexError, ValueError)):
                tree.sum(2, 1)
            with self.assertRaises(OverflowError):
                tree.add(0, 1 << 63)
        with self.acl.mf_graph(2) as graph:
            with self.assertRaises(ValueError):
                graph.add_edge(0, 1, -1)
            with self.assertRaises(ValueError):
                graph.flow(0, 0)
            with self.assertRaises(OverflowError):
                graph.add_edge(0, 1, 1 << 63)
        with self.acl.mcf_graph(2) as graph:
            with self.assertRaises(ValueError):
                graph.add_edge(0, 1, 1, -1)
            with self.assertRaises(OverflowError):
                graph.add_edge(0, 1, 1, 1 << 63)
        for call in (lambda: self.acl.crt([1], []),
                     lambda: self.acl.crt([1], [0]),
                     lambda: self.acl.floor_sum(-1, 3, 1, 0),
                     lambda: self.acl.floor_sum(2, 0, 1, 0),
                     lambda: self.acl.lcp_array("abc", [0, 0, 2]),
                     lambda: self.acl.lcp_array("abc", [0, 1])):
            with self.assertRaises(ValueError):
                call()


class ACLCFFIBatchTests(unittest.TestCase):
    """Batch APIs are specific to CFFI and are not inherited by HPy tests."""

    @classmethod
    def setUpClass(cls):
        try:
            cls.acl = importlib.import_module("acl_cffi")
            cls.acl.dsu(0).close()
        except ImportError as error:
            if os.environ.get("ACL_CFFI_REQUIRE_NATIVE") == "1":
                raise
            raise unittest.SkipTest("CFFI backend has not been built: %s" % error)

    def test_batch_operations_match_individual_calls_and_keep_state(self):
        operations = [(0, 0, 1), (1, 0, 1), (1, 1, 2), (0, 2, 3), (1, 2, 3)]
        with self.acl.dsu(4) as batched, self.acl.dsu(4) as individual:
            expected = []
            for kind, a, b in operations:
                if kind == 0:
                    individual.merge(a, b)
                else:
                    expected.append(individual.same(a, b))
            self.assertEqual(batched.process(operations[:2]) + batched.process(operations[2:]), expected)
            self.assertEqual(batched.groups(), individual.groups())
            with self.assertRaises(ValueError):
                batched.process([(2, 0, 1)])

        operations = [(0, 0, 5), (0, 3, -2), (1, 0, 4), (1, 1, 3)]
        with self.acl.fenwick_tree(4) as batched, self.acl.fenwick_tree(4) as individual:
            expected = []
            for kind, a, b in operations:
                if kind == 0:
                    individual.add(a, b)
                else:
                    expected.append(individual.sum(a, b))
            self.assertEqual(batched.process(operations), expected)
            self.assertEqual(batched.sum(0, 4), individual.sum(0, 4))
            with self.assertRaises(ValueError):
                batched.process([(0, 1 << 32, 1)])

        edges = [(0, 1), (1, 0), (1, 2)]
        with self.acl.scc_graph(3) as batched, self.acl.scc_graph(3) as individual:
            batched.add_edges(edges)
            for a, b in edges:
                individual.add_edge(a, b)
            self.assertEqual(batched.scc(), individual.scc())
            with self.assertRaises(ValueError):
                batched.add_edges([(0, 3)])

    def test_crt_batch_matches_individual_calls_and_rejects_errors(self):
        cases = [([0, 1, 2, 3], [2, 3, 5, 7]),
                 ([-1, -2, -3, -4], [3, 5, 7, 11]),
                 ([0, 1, 0, 1], [2, 2, 3, 3])]
        self.assertEqual(self.acl.crt_many(cases),
                         [list(self.acl.crt(r, m)) for r, m in cases])
        self.assertEqual(self.acl.crt_many([]), [])
        with self.assertRaises(ValueError):
            self.acl.crt_many([([0] * 4, [2, 3, 0, 5])])
        with self.assertRaises(OverflowError):
            self.acl.crt_many([([0, 0, 0, 0], [(1 << 63) - 1, 2, 1, 1])])


if __name__ == "__main__":
    unittest.main()
