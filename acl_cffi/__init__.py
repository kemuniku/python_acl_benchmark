"""AtCoder Library bindings using CFFI's out-of-line API mode.

Build for the active interpreter with ``python -m benchkit build --source cffi``.
Native graph and tree objects support ``with`` and an idempotent ``close()``.
String algorithms use Unicode code-point indices for ``str`` and byte indices
for ``bytes``. Numeric string inputs consist of signed 32-bit integers; other
numeric inputs use signed 64-bit integers.
"""

from collections import namedtuple

try:
    from _acl_cffi_native import ffi, lib
except ImportError as exc:
    raise ImportError(
        "The ACL CFFI extension is not built for this interpreter. "
        "Run `python -m benchkit build --source cffi` and add its printed "
        "source path to PYTHONPATH."
    ) from exc


__all__ = [
    "dsu", "fenwick_tree", "scc_graph", "two_sat", "mf_graph", "mcf_graph", "ordered_set",
    "convolution998244353", "crt", "crt_many", "floor_sum", "suffix_array", "lcp_array",
    "z_algorithm",
]

_INT64_MAX = (1 << 63) - 1
_MFEdge = namedtuple("MFEdge", "from_ to cap flow")
_MCFEdge = namedtuple("MCFEdge", "from_ to cap flow cost")
_ERRORS = {1: ValueError, 2: OverflowError, 3: MemoryError, 4: RuntimeError}


def _error():
    error_type = _ERRORS.get(lib.acl_error_code(), RuntimeError)
    message = ffi.string(lib.acl_last_error()).decode("utf-8", errors="replace")
    raise error_type(message)


def _check(value):
    if value < 0:
        _error()
    return value


class _Handle:
    """Own a native object without waiting for PyPy's next GC cycle."""

    def _init(self, n, create, destroy):
        self._ptr = None
        ptr = create(n)
        if ptr == ffi.NULL:
            _error()
        self._ptr = ffi.gc(ptr, destroy)
        self._n = n

    def _handle(self):
        if self._ptr is None:
            raise RuntimeError("This ACL object has been closed")
        return self._ptr

    def close(self):
        """Release the native allocation; subsequent calls do nothing."""
        ptr = self._ptr
        if ptr is not None:
            self._ptr = None
            ffi.release(ptr)

    def __enter__(self):
        self._handle()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False

    def _groups(self, function):
        handle = self._handle()
        vertices = ffi.new("int[]", self._n)
        offsets = ffi.new("int[]", self._n + 1)
        count = _check(function(handle, vertices, offsets))
        return [ffi.unpack(vertices + offsets[i], offsets[i + 1] - offsets[i])
                for i in range(count)]


class dsu(_Handle):
    """Disjoint set union with path compression and union by size."""

    def __init__(self, n=0):
        self._init(n, lib.acl_dsu_new, lib.acl_dsu_delete)

    def merge(self, a, b):
        return _check(lib.acl_dsu_merge(self._handle(), a, b))

    def same(self, a, b):
        return bool(_check(lib.acl_dsu_same(self._handle(), a, b)))

    def leader(self, a):
        return _check(lib.acl_dsu_leader(self._handle(), a))

    def size(self, a):
        return _check(lib.acl_dsu_size(self._handle(), a))

    def groups(self):
        return self._groups(lib.acl_dsu_groups)

    def process(self, operations):
        """Process (merge=0 / same=1, a, b) operations in order."""
        handle = self._handle()
        operations = _sequence(operations)
        packed = ffi.new("int[][3]", operations)
        answers = ffi.new("int[]", len(operations))
        count = _check(lib.acl_dsu_process(handle, packed, len(operations), answers))
        return [bool(value) for value in ffi.unpack(answers, count)]


class ordered_set(_Handle):
    """Nonnegative integer ordered set using a size-augmented native AVL tree."""

    def __init__(self):
        self._init(0, lib.acl_ordered_new, lib.acl_ordered_delete)

    def add(self, key):
        return bool(_check(lib.acl_ordered_add(self._handle(), key)))

    def discard(self, key):
        return bool(_check(lib.acl_ordered_discard(self._handle(), key)))

    def count_leq(self, key):
        return _check(lib.acl_ordered_count_leq(self._handle(), key))

    def kth(self, one_based):
        result = ffi.new("int *")
        _check(lib.acl_ordered_kth(self._handle(), one_based, result))
        return result[0]

    def le(self, key):
        result = ffi.new("int *")
        _check(lib.acl_ordered_le(self._handle(), key, result))
        return result[0]

    def ge(self, key):
        result = ffi.new("int *")
        _check(lib.acl_ordered_ge(self._handle(), key, result))
        return result[0]


class fenwick_tree(_Handle):
    """Point additions and half-open range sums, with checked int64 results."""

    def __init__(self, n=0):
        self._init(n, lib.acl_fenwick_new, lib.acl_fenwick_delete)

    def add(self, p, value):
        _check(lib.acl_fenwick_add(self._handle(), p, value))

    def sum(self, left, right):
        handle = self._handle()
        result = ffi.new("long long *")
        _check(lib.acl_fenwick_sum(handle, left, right, result))
        return result[0]

    def process(self, operations):
        """Process (add=0 / sum=1, first, value_or_end) operations in order."""
        handle = self._handle()
        operations = _sequence(operations)
        packed = ffi.new("long long[][3]", operations)
        answers = ffi.new("long long[]", len(operations))
        count = _check(lib.acl_fenwick_process(handle, packed, len(operations), answers))
        return ffi.unpack(answers, count)


class scc_graph(_Handle):
    """Directed graph whose SCCs are returned in topological order."""

    def __init__(self, n=0):
        self._init(n, lib.acl_scc_new, lib.acl_scc_delete)

    def add_edge(self, source, target):
        _check(lib.acl_scc_add_edge(self._handle(), source, target))

    def add_edges(self, edges):
        """Add an iterable of (source, target) edges in order."""
        handle = self._handle()
        edges = _sequence(edges)
        packed = ffi.new("int[][2]", edges)
        _check(lib.acl_scc_add_edges(handle, packed, len(edges)))

    def scc(self):
        return self._groups(lib.acl_scc_groups)


class two_sat(_Handle):
    """Two-SAT clauses and a satisfying assignment when one exists."""

    def __init__(self, n=0):
        self._init(n, lib.acl_twosat_new, lib.acl_twosat_delete)

    def add_clause(self, i, f, j, g):
        _check(lib.acl_twosat_add_clause(self._handle(), i, f, j, g))

    def satisfiable(self):
        return bool(_check(lib.acl_twosat_satisfiable(self._handle())))

    def answer(self):
        handle = self._handle()
        answer = ffi.new("int[]", self._n)
        _check(lib.acl_twosat_answer(handle, answer))
        return [bool(value) for value in ffi.unpack(answer, self._n)]


class mf_graph(_Handle):
    """Maximum flow with nonnegative int64 capacities."""

    def __init__(self, n=0):
        self._init(n, lib.acl_mf_new, lib.acl_mf_delete)
        self._edge_count = 0

    def add_edge(self, source, target, capacity):
        index = _check(lib.acl_mf_add_edge(self._handle(), source, target, capacity))
        self._edge_count += 1
        return index

    def get_edge(self, index):
        handle = self._handle()
        result = ffi.new("acl_mf_edge *")
        _check(lib.acl_mf_get_edge(handle, index, result))
        return _MFEdge(getattr(result, "from"), result.to, result.cap, result.flow)

    def edges(self):
        self._handle()
        return [self.get_edge(i) for i in range(self._edge_count)]

    def change_edge(self, index, capacity, flow):
        _check(lib.acl_mf_change_edge(self._handle(), index, capacity, flow))

    def flow(self, source, sink, flow_limit=_INT64_MAX):
        handle = self._handle()
        result = ffi.new("long long *")
        _check(lib.acl_mf_flow(handle, source, sink, flow_limit, result))
        return result[0]

    def min_cut(self, source):
        handle = self._handle()
        reachable = ffi.new("int[]", self._n)
        _check(lib.acl_mf_min_cut(handle, source, reachable))
        return [bool(value) for value in ffi.unpack(reachable, self._n)]


class mcf_graph(_Handle):
    """Minimum cost flow; call flow once per graph, as required by ACL."""

    def __init__(self, n=0):
        self._init(n, lib.acl_mcf_new, lib.acl_mcf_delete)
        self._edge_count = 0

    def add_edge(self, source, target, capacity, cost):
        index = _check(lib.acl_mcf_add_edge(self._handle(), source, target, capacity, cost))
        self._edge_count += 1
        return index

    def get_edge(self, index):
        handle = self._handle()
        result = ffi.new("acl_mcf_edge *")
        _check(lib.acl_mcf_get_edge(handle, index, result))
        return _MCFEdge(getattr(result, "from"), result.to, result.cap, result.flow, result.cost)

    def edges(self):
        self._handle()
        return [self.get_edge(i) for i in range(self._edge_count)]

    def flow(self, source, sink, flow_limit=_INT64_MAX):
        handle = self._handle()
        flow = ffi.new("long long *")
        cost = ffi.new("long long *")
        _check(lib.acl_mcf_flow(handle, source, sink, flow_limit, flow, cost))
        return flow[0], cost[0]


def _sequence(values):
    if isinstance(values, (list, tuple)):
        return values
    return list(values)


def _string_array(values):
    """Preserve Unicode indices instead of indexing UTF-8 encoded bytes."""
    values = [ord(char) for char in values] if isinstance(values, str) else _sequence(values)
    return ffi.new("int[]", values), len(values)


def convolution998244353(a, b):
    """Return polynomial convolution modulo 998244353."""
    a, b = _sequence(a), _sequence(b)
    na, nb = len(a), len(b)
    aa, bb = ffi.new("long long[]", a), ffi.new("long long[]", b)
    count = na + nb - 1 if na and nb else 0
    result = ffi.new("int[]", count)
    _check(lib.acl_convolution(aa, na, bb, nb, result))
    return ffi.unpack(result, count)


def crt(residues, moduli):
    """Return (smallest nonnegative solution, period), or (0, 0)."""
    residues, moduli = _sequence(residues), _sequence(moduli)
    if len(residues) != len(moduli):
        raise ValueError("residues and moduli must have the same length")
    if len(residues) == 4:
        result = ffi.new("long long[2]")
        _check(lib.acl_crt4(residues[0], residues[1], residues[2], residues[3],
                            moduli[0], moduli[1], moduli[2], moduli[3], result))
        return result[0], result[1]
    rr, mm = ffi.new("long long[]", residues), ffi.new("long long[]", moduli)
    result, period = ffi.new("long long *"), ffi.new("long long *")
    _check(lib.acl_crt(rr, mm, len(residues), result, period))
    return result[0], period[0]


def crt_many(cases):
    """Evaluate batches of four-congruence CRT problems in order."""
    cases = _sequence(cases)
    residues = ffi.new("long long[][4]", [item[0] for item in cases])
    moduli = ffi.new("long long[][4]", [item[1] for item in cases])
    results = ffi.new("long long[][2]", len(cases))
    _check(lib.acl_crt4_batch(residues, moduli, len(cases), results))
    flat = ffi.unpack(ffi.cast("long long *", results), 2 * len(cases))
    return [flat[i:i + 2] for i in range(0, len(flat), 2)]


def floor_sum(n, m, a, b):
    """Return sum((a * i + b) // m for i in range(n)); m must be positive."""
    result = ffi.new("long long *")
    _check(lib.acl_floor_sum(n, m, a, b, result))
    return result[0]


def suffix_array(values):
    """Return sorted suffix indices for Unicode, bytes, or int32 sequences."""
    array, n = _string_array(values)
    result = ffi.new("int[]", n)
    _check(lib.acl_suffix_array(array, n, result))
    return ffi.unpack(result, n)


def lcp_array(values, sa):
    """Return adjacent suffix LCP lengths; sa must permute all indices."""
    array, n = _string_array(values)
    sa = _sequence(sa)
    if len(sa) != n:
        raise ValueError("suffix array length must match input length")
    sa_array = ffi.new("int[]", sa)
    count = max(n - 1, 0)
    result = ffi.new("int[]", count)
    _check(lib.acl_lcp_array(array, n, sa_array, result))
    return ffi.unpack(result, count)


def z_algorithm(values):
    """Return longest common prefix lengths against every suffix."""
    if isinstance(values, str) and values.isascii():
        values = values.encode("ascii")
    if isinstance(values, bytes):
        n = len(values)
        result = ffi.new("int[]", n)
        _check(lib.acl_z_algorithm_bytes(ffi.from_buffer("const char[]", values), n, result))
        return ffi.unpack(result, n)
    array, n = _string_array(values)
    result = ffi.new("int[]", n)
    _check(lib.acl_z_algorithm(array, n, result))
    return ffi.unpack(result, n)
