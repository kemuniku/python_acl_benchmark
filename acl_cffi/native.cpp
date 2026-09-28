// C ABI over the official AtCoder Library. No C++ exceptions cross this boundary.
#include <atcoder/convolution>
#include <atcoder/dsu>
#include <atcoder/fenwicktree>
#include <atcoder/math>
#include <atcoder/maxflow>
#include <atcoder/mincostflow>
#include <atcoder/scc>
#include <atcoder/string>
#include <atcoder/twosat>
#include <algorithm>
#include <climits>
#include <cstdio>
#include <exception>
#include <limits>
#include <new>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

extern "C" {
#include "cdef.h"
}

namespace {
using wide = __int128;
using uwide = unsigned __int128;
constexpr uwide wide_max = (~uwide(0)) >> 1;
thread_local char error_message[512] = "";
thread_local int error_code = 0;

void set_error(int code, const char *message) noexcept {
    error_code = code;
    std::snprintf(error_message, sizeof(error_message), "%s", message);
}

void record_exception() noexcept {
    try {
        throw;
    } catch (const std::bad_alloc &) {
        set_error(3, "native allocation failed");
    } catch (const std::overflow_error &error) {
        set_error(2, error.what());
    } catch (const std::invalid_argument &error) {
        set_error(1, error.what());
    } catch (const std::length_error &error) {
        set_error(2, error.what());
    } catch (const std::exception &error) {
        set_error(4, error.what());
    } catch (...) {
        set_error(4, "unknown native exception");
    }
}

template <class F> int checked(F action) noexcept {
    set_error(0, "");
    try {
        return action();
    } catch (...) {
        record_exception();
        return -1;
    }
}

template <class T, class F> T *checked_new(F action) noexcept {
    set_error(0, "");
    try {
        return action();
    } catch (...) {
        record_exception();
        return nullptr;
    }
}

void require(bool condition, const char *message) {
    if (!condition) throw std::invalid_argument(message);
}

void size_ok(int n) {
    require(n >= 0, "size must be nonnegative");
    require(n < INT_MAX, "size must be smaller than INT_MAX");
}

void vertex(int v, int n) { require(0 <= v && v < n, "vertex/index is out of range"); }

template <class T> void handle_ok(T *handle) {
    require(handle != nullptr, "native object is closed");
}

template <class T> void buffer_ok(const T *data, int n) {
    require(n == 0 || data != nullptr, "null array buffer");
}

template <class T> std::vector<T> vector_from(const T *data, int n) {
    size_ok(n);
    buffer_ok(data, n);
    if (!n) return {};
    return std::vector<T>(data, data + n);
}

long long narrow(wide value) {
    if (value < LLONG_MIN || value > LLONG_MAX)
        throw std::overflow_error("result does not fit in signed 64 bits");
    return static_cast<long long>(value);
}

int flatten(const std::vector<std::vector<int>> &groups, int n,
            int *vertices, int *offsets) {
    buffer_ok(vertices, n);
    buffer_ok(offsets, 1);
    int position = 0;
    offsets[0] = 0;
    for (std::size_t i = 0; i < groups.size(); ++i) {
        for (int v : groups[i]) vertices[position++] = v;
        offsets[i + 1] = position;
    }
    return static_cast<int>(groups.size());
}
}  // namespace

struct acl_dsu {
    int n;
    atcoder::dsu graph;
    explicit acl_dsu(int size) : n(size), graph(size) {}
};
struct acl_fenwick {
    int n;
    // Extra precision prevents signed-64 wrapping before a sum is returned.
    atcoder::fenwick_tree<wide> tree;
    uwide magnitude = 0;
    explicit acl_fenwick(int size) : n(size), tree(size) {}
};
struct acl_scc {
    int n;
    int edges = 0;
    atcoder::scc_graph graph;
    explicit acl_scc(int size) : n(size), graph(size) {}
};
struct acl_twosat {
    int n;
    int clauses = 0;
    bool solved = false;
    bool possible = false;
    atcoder::two_sat graph;
    explicit acl_twosat(int size) : n(size), graph(size) {}
};
struct acl_mf {
    int n;
    int edges = 0;
    atcoder::mf_graph<long long> graph;
    explicit acl_mf(int size) : n(size), graph(size) {}
};
struct acl_mcf {
    int n;
    int edges = 0;
    bool used = false;
    uwide cost_bound = 0;
    // The public capacity/cost types remain signed 64 bits. Wider intermediate
    // costs let us report OverflowError instead of invoking signed-overflow UB.
    atcoder::mcf_graph<long long, wide> graph;
    explicit acl_mcf(int size) : n(size), graph(size) {}
};

extern "C" {
const char *acl_last_error(void) { return error_message; }
int acl_error_code(void) { return error_code; }

acl_dsu *acl_dsu_new(int n) {
    return checked_new<acl_dsu>([&] { size_ok(n); return new acl_dsu(n); });
}
void acl_dsu_delete(acl_dsu *handle) { delete handle; }
int acl_dsu_merge(acl_dsu *h, int a, int b) {
    return checked([&] { handle_ok(h); vertex(a, h->n); vertex(b, h->n); return h->graph.merge(a, b); });
}
int acl_dsu_same(acl_dsu *h, int a, int b) {
    return checked([&] { handle_ok(h); vertex(a, h->n); vertex(b, h->n); return int(h->graph.same(a, b)); });
}
int acl_dsu_leader(acl_dsu *h, int a) {
    return checked([&] { handle_ok(h); vertex(a, h->n); return h->graph.leader(a); });
}
int acl_dsu_size(acl_dsu *h, int a) {
    return checked([&] { handle_ok(h); vertex(a, h->n); return h->graph.size(a); });
}
int acl_dsu_groups(acl_dsu *h, int *vertices, int *offsets) {
    return checked([&] { handle_ok(h); return flatten(h->graph.groups(), h->n, vertices, offsets); });
}

acl_fenwick *acl_fenwick_new(int n) {
    return checked_new<acl_fenwick>([&] {
        size_ok(n); require(n < (1 << 30), "Fenwick size must be smaller than 2^30");
        return new acl_fenwick(n);
    });
}
void acl_fenwick_delete(acl_fenwick *handle) { delete handle; }
int acl_fenwick_add(acl_fenwick *h, int p, long long value) {
    return checked([&] {
        handle_ok(h); vertex(p, h->n);
        uwide magnitude = value < 0 ? uwide(-wide(value)) : uwide(value);
        if (h->magnitude > wide_max - magnitude)
            throw std::overflow_error("Fenwick accumulation exceeds signed 128-bit safety bound");
        h->tree.add(p, wide(value));
        h->magnitude += magnitude;
        return 0;
    });
}
int acl_fenwick_sum(acl_fenwick *h, int left, int right, long long *result) {
    return checked([&] {
        handle_ok(h); buffer_ok(result, 1);
        require(0 <= left && left <= right && right <= h->n, "invalid sum interval");
        *result = narrow(h->tree.sum(left, right));
        return 0;
    });
}

acl_scc *acl_scc_new(int n) {
    return checked_new<acl_scc>([&] { size_ok(n); return new acl_scc(n); });
}
void acl_scc_delete(acl_scc *handle) { delete handle; }
int acl_scc_add_edge(acl_scc *h, int from, int to) {
    return checked([&] {
        handle_ok(h); vertex(from, h->n); vertex(to, h->n);
        if (h->edges == INT_MAX) throw std::overflow_error("too many edges");
        h->graph.add_edge(from, to); ++h->edges;
        return 0;
    });
}
int acl_scc_groups(acl_scc *h, int *vertices, int *offsets) {
    return checked([&] { handle_ok(h); return flatten(h->graph.scc(), h->n, vertices, offsets); });
}

acl_twosat *acl_twosat_new(int n) {
    return checked_new<acl_twosat>([&] {
        size_ok(n); require(n < INT_MAX / 2, "too many variables");
        return new acl_twosat(n);
    });
}
void acl_twosat_delete(acl_twosat *handle) { delete handle; }
int acl_twosat_add_clause(acl_twosat *h, int i, int f, int j, int g) {
    return checked([&] {
        handle_ok(h); vertex(i, h->n); vertex(j, h->n);
        require((f == 0 || f == 1) && (g == 0 || g == 1), "clause values must be boolean");
        if (h->clauses >= INT_MAX / 2) throw std::overflow_error("too many clauses");
        h->graph.add_clause(i, bool(f), j, bool(g));
        ++h->clauses; h->solved = false;
        return 0;
    });
}
int acl_twosat_satisfiable(acl_twosat *h) {
    return checked([&] {
        handle_ok(h); h->possible = h->graph.satisfiable(); h->solved = true;
        return int(h->possible);
    });
}
int acl_twosat_answer(acl_twosat *h, int *answer) {
    return checked([&] {
        handle_ok(h); buffer_ok(answer, h->n);
        if (!h->solved || !h->possible)
            throw std::runtime_error("answer requires a successful satisfiable() call after the last clause");
        auto values = h->graph.answer();
        for (int i = 0; i < h->n; ++i) answer[i] = values[i];
        return 0;
    });
}

acl_mf *acl_mf_new(int n) {
    return checked_new<acl_mf>([&] { size_ok(n); return new acl_mf(n); });
}
void acl_mf_delete(acl_mf *handle) { delete handle; }
int acl_mf_add_edge(acl_mf *h, int from, int to, long long cap) {
    return checked([&] {
        handle_ok(h); vertex(from, h->n); vertex(to, h->n);
        require(cap >= 0, "capacity must be nonnegative");
        if (h->edges >= INT_MAX / 2) throw std::overflow_error("too many residual edges");
        int edge = h->graph.add_edge(from, to, cap); ++h->edges;
        return edge;
    });
}
int acl_mf_get_edge(acl_mf *h, int index, acl_mf_edge *result) {
    return checked([&] {
        handle_ok(h); vertex(index, h->edges); buffer_ok(result, 1);
        auto edge = h->graph.get_edge(index);
        *result = {edge.from, edge.to, edge.cap, edge.flow};
        return 0;
    });
}
int acl_mf_change_edge(acl_mf *h, int index, long long cap, long long flow) {
    return checked([&] {
        handle_ok(h); vertex(index, h->edges);
        require(cap >= 0 && 0 <= flow && flow <= cap, "require 0 <= flow <= capacity");
        h->graph.change_edge(index, cap, flow);
        return 0;
    });
}
int acl_mf_flow(acl_mf *h, int source, int sink, long long limit, long long *result) {
    return checked([&] {
        handle_ok(h); vertex(source, h->n); vertex(sink, h->n); buffer_ok(result, 1);
        require(source != sink, "source and sink must differ");
        require(limit >= 0, "flow limit must be nonnegative");
        *result = h->graph.flow(source, sink, limit);
        return 0;
    });
}
int acl_mf_min_cut(acl_mf *h, int source, int *reachable) {
    return checked([&] {
        handle_ok(h); vertex(source, h->n); buffer_ok(reachable, h->n);
        auto values = h->graph.min_cut(source);
        for (int i = 0; i < h->n; ++i) reachable[i] = values[i];
        return 0;
    });
}

acl_mcf *acl_mcf_new(int n) {
    return checked_new<acl_mcf>([&] { size_ok(n); return new acl_mcf(n); });
}
void acl_mcf_delete(acl_mcf *handle) { delete handle; }
int acl_mcf_add_edge(acl_mcf *h, int from, int to, long long cap, long long cost) {
    return checked([&] {
        handle_ok(h); vertex(from, h->n); vertex(to, h->n);
        require(cap >= 0 && cost >= 0, "capacity and cost must be nonnegative");
        if (h->used) throw std::runtime_error("cannot add edges after min-cost flow");
        if (h->edges >= INT_MAX / 2) throw std::overflow_error("too many residual edges");
        uwide bound = uwide(cap) * uwide(cost);
        if (h->cost_bound > wide_max - bound)
            throw std::overflow_error("total capacity times cost exceeds signed 128-bit safety bound");
        int edge = h->graph.add_edge(from, to, cap, wide(cost));
        h->cost_bound += bound; ++h->edges;
        return edge;
    });
}
int acl_mcf_get_edge(acl_mcf *h, int index, acl_mcf_edge *result) {
    return checked([&] {
        handle_ok(h); vertex(index, h->edges); buffer_ok(result, 1);
        auto edge = h->graph.get_edge(index);
        *result = {edge.from, edge.to, edge.cap, edge.flow, narrow(edge.cost)};
        return 0;
    });
}
int acl_mcf_flow(acl_mcf *h, int source, int sink, long long limit,
                 long long *flow, long long *cost) {
    return checked([&] {
        handle_ok(h); vertex(source, h->n); vertex(sink, h->n);
        buffer_ok(flow, 1); buffer_ok(cost, 1);
        require(source != sink, "source and sink must differ");
        require(limit >= 0, "flow limit must be nonnegative");
        if (h->used) throw std::runtime_error("min-cost flow can be called only once per graph");
        h->used = true;
        auto result = h->graph.flow(source, sink, limit);
        long long checked_cost = narrow(result.second);
        *flow = result.first; *cost = checked_cost;
        return 0;
    });
}

int acl_convolution(const long long *a, int na, const long long *b, int nb, int *result) {
    return checked([&] {
        size_ok(na); size_ok(nb); buffer_ok(a, na); buffer_ok(b, nb);
        if (!na || !nb) return 0;
        require(static_cast<long long>(na) + nb - 1 <= (1 << 23),
                "convolution output length must not exceed 2^23 for modulus 998244353");
        buffer_ok(result, na + nb - 1);
        using mint = atcoder::modint998244353;
        std::vector<mint> left(na), right(nb);
        for (int i = 0; i < na; ++i) left[i] = a[i];
        for (int i = 0; i < nb; ++i) right[i] = b[i];
        auto product = atcoder::convolution(std::move(left), std::move(right));
        for (std::size_t i = 0; i < product.size(); ++i) result[i] = product[i].val();
        return 0;
    });
}

int acl_suffix_array(const int *values, int n, int *result) {
    return checked([&] {
        auto input = vector_from(values, n); buffer_ok(result, n);
        if (!n) return 0;
        auto bounds = std::minmax_element(input.begin(), input.end());
        std::vector<int> sa;
        // Preserve linear SA-IS behavior for bounded alphabets such as strings;
        // arbitrary signed integers use ACL's coordinate-compressing overload.
        if (*bounds.first >= 0 && *bounds.second <= std::max(n, 256))
            sa = atcoder::suffix_array(input, *bounds.second);
        else
            sa = atcoder::suffix_array(input);
        std::copy(sa.begin(), sa.end(), result);
        return 0;
    });
}

int acl_lcp_array(const int *values, int n, const int *sa, int *result) {
    return checked([&] {
        auto input = vector_from(values, n);
        auto suffixes = vector_from(sa, n);
        buffer_ok(result, n > 0 ? n - 1 : 0);
        if (!n) return 0;
        std::vector<int> rank(static_cast<std::size_t>(n) + 1, -1);
        for (int i = 0; i < n; ++i) {
            vertex(sa[i], n);
            require(rank[sa[i]] == -1, "suffix array must be a permutation");
            rank[sa[i]] = i;
        }
        // A permutation is lexicographically sorted iff these adjacent
        // first-symbol/tail-rank pairs are strictly increasing (linear check).
        for (int i = 1; i < n; ++i) {
            int a = sa[i - 1], b = sa[i];
            require(values[a] < values[b] ||
                        (values[a] == values[b] && rank[a + 1] < rank[b + 1]),
                    "suffix array is not sorted for the given sequence");
        }
        auto lcp = atcoder::lcp_array(input, suffixes);
        if (!lcp.empty()) std::copy(lcp.begin(), lcp.end(), result);
        return 0;
    });
}

int acl_z_algorithm(const int *values, int n, int *result) {
    return checked([&] {
        auto input = vector_from(values, n); buffer_ok(result, n);
        auto z = atcoder::z_algorithm(input);
        if (!z.empty()) std::copy(z.begin(), z.end(), result);
        return 0;
    });
}

int acl_z_algorithm_bytes(const char *values, int n, int *result) {
    return checked([&] {
        size_ok(n); buffer_ok(values, n); buffer_ok(result, n);
        std::string input(values ? values : "", n);
        auto z = atcoder::z_algorithm(input);
        if (!z.empty()) std::copy(z.begin(), z.end(), result);
        return 0;
    });
}

int acl_crt(const long long *residues, const long long *moduli, int n,
            long long *residue, long long *modulus) {
    return checked([&] {
        size_ok(n); buffer_ok(residues, n); buffer_ok(moduli, n);
        buffer_ok(residue, 1); buffer_ok(modulus, 1);
        // Validate every modulus, even if an earlier pair is inconsistent.
        for (int i = 0; i < n; ++i) require(moduli[i] > 0, "CRT moduli must be positive");
        long long r = 0, m = 1;
        for (int i = 0; i < n; ++i) {
            long long ri = residues[i] % moduli[i];
            if (ri < 0) ri += moduli[i];
            long long gcd = std::gcd(m, moduli[i]);
            if ((wide(ri) - r) % gcd != 0) { *residue = 0; *modulus = 0; return 0; }
            if (wide(m / gcd) * moduli[i] > LLONG_MAX)
                throw std::overflow_error("CRT least common multiple exceeds signed 64 bits");
            auto combined = atcoder::crt({r, ri}, {m, moduli[i]});
            r = combined.first; m = combined.second;
        }
        *residue = r; *modulus = m;
        return 0;
    });
}

int acl_floor_sum(long long n, long long m, long long a, long long b, long long *result) {
    return checked([&] {
        buffer_ok(result, 1);
        require(0 <= n && n < (1LL << 32), "floor_sum requires 0 <= n < 2^32");
        require(1 <= m && m < (1LL << 32), "floor_sum requires 1 <= m < 2^32");
        // Normalize in 128 bits: a == LLONG_MIN and cancellations between
        // negative/positive terms must not overflow before the final check.
        long long ar = a % m; if (ar < 0) ar += m;
        long long br = b % m; if (br < 0) br += m;
        wide total = wide(n) * (n - 1) / 2 * ((wide(a) - ar) / m)
                   + wide(n) * ((wide(b) - br) / m)
                   + atcoder::floor_sum(n, m, ar, br);
        *result = narrow(total);
        return 0;
    });
}
}  // extern "C"
