"""Official ACL through HPy Universal; build with `benchkit build --source hpy`."""
from collections import namedtuple

try:
    import _acl_hpy_native as _native
except ImportError as exc:
    raise ImportError(
        "The ACL HPy extension is not built. Run `python -m benchkit build "
        "--source hpy` and add its printed source path to PYTHONPATH."
    ) from exc

__all__ = [
    "dsu", "fenwick_tree", "scc_graph", "two_sat", "mf_graph", "mcf_graph",
    "convolution998244353", "crt", "floor_sum", "suffix_array", "lcp_array", "z_algorithm",
]
_INT64_MAX = (1 << 63) - 1
_MFEdge = namedtuple("MFEdge", "from_ to cap flow")
_MCFEdge = namedtuple("MCFEdge", "from_ to cap flow cost")


class _Handle:
    # Composition avoids relying on Python subclass support in HPy runtimes.
    # The native HPy object's destroy slot owns and frees the C++ allocation.
    def __init__(self, n=0):
        self._native = self._factory(n)

    def close(self):
        self._native.close()

    def __enter__(self):
        self._native._check_open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False


class dsu(_Handle):
    _factory = _native.dsu

    def merge(self, a, b):
        return self._native.merge(a, b)

    def same(self, a, b):
        return self._native.same(a, b)

    def leader(self, a):
        return self._native.leader(a)

    def size(self, a):
        return self._native.size(a)

    def groups(self):
        return self._native.groups()


class fenwick_tree(_Handle):
    _factory = _native.fenwick_tree

    def add(self, p, value):
        self._native.add(p, value)

    def sum(self, left, right):
        return self._native.sum(left, right)


class scc_graph(_Handle):
    _factory = _native.scc_graph

    def add_edge(self, source, target):
        self._native.add_edge(source, target)

    def scc(self):
        return self._native.scc()


class two_sat(_Handle):
    _factory = _native.two_sat

    def add_clause(self, i, f, j, g):
        self._native.add_clause(i, f, j, g)

    def satisfiable(self):
        return self._native.satisfiable()

    def answer(self):
        return self._native.answer()


class mf_graph(_Handle):
    _factory = _native.mf_graph

    def add_edge(self, source, target, capacity):
        return self._native.add_edge(source, target, capacity)

    def get_edge(self, index):
        return _MFEdge(*self._native._get_edge(index))

    def edges(self):
        return [_MFEdge(*edge) for edge in self._native._edges()]

    def change_edge(self, index, capacity, flow):
        self._native.change_edge(index, capacity, flow)

    def flow(self, source, sink, flow_limit=_INT64_MAX):
        return self._native.flow(source, sink, flow_limit)

    def min_cut(self, source):
        return self._native.min_cut(source)


class mcf_graph(_Handle):
    _factory = _native.mcf_graph

    def add_edge(self, source, target, capacity, cost):
        return self._native.add_edge(source, target, capacity, cost)

    def get_edge(self, index):
        return _MCFEdge(*self._native._get_edge(index))

    def edges(self):
        return [_MCFEdge(*edge) for edge in self._native._edges()]

    def flow(self, source, sink, flow_limit=_INT64_MAX):
        return self._native.flow(source, sink, flow_limit)


def _sequence(values):
    return values if isinstance(values, (str, bytes, list, tuple)) else list(values)


def convolution998244353(a, b):
    return _native.convolution998244353(_sequence(a), _sequence(b))


def crt(residues, moduli):
    return _native.crt(_sequence(residues), _sequence(moduli))


def floor_sum(n, m, a, b):
    return _native.floor_sum(n, m, a, b)


def suffix_array(values):
    return _native.suffix_array(_sequence(values))


def lcp_array(values, sa):
    return _native.lcp_array(_sequence(values), _sequence(sa))


def z_algorithm(values):
    return _native.z_algorithm(_sequence(values))
