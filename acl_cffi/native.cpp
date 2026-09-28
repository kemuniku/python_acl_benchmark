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

// Ordered set lookups reserve -1 for a missing key, so errors use -2.
template <class F> int checked_ordered_value(F action) noexcept {
    set_error(0, "");
    try {
        return action();
    } catch (...) {
        record_exception();
        return -2;
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
// A size-augmented AVL tree. Index 0 is the empty child; index reuse keeps
// alternating inserts/deletes from growing memory without bound.
struct acl_ordered_set {
    struct Node { int key, left, right, height, size; };
    std::vector<Node> nodes = {{0, 0, 0, 0, 0}};
    std::vector<int> free_nodes;
    int root = 0;

    int height(int p) const { return nodes[p].height; }
    int size(int p) const { return nodes[p].size; }
    void update(int p) {
        nodes[p].height = 1 + std::max(height(nodes[p].left), height(nodes[p].right));
        nodes[p].size = 1 + size(nodes[p].left) + size(nodes[p].right);
    }
    int rotate_left(int p) {
        int q = nodes[p].right;
        nodes[p].right = nodes[q].left;
        nodes[q].left = p;
        update(p); update(q);
        return q;
    }
    int rotate_right(int p) {
        int q = nodes[p].left;
        nodes[p].left = nodes[q].right;
        nodes[q].right = p;
        update(p); update(q);
        return q;
    }
    int balance(int p) {
        update(p);
        int diff = height(nodes[p].left) - height(nodes[p].right);
        if (diff > 1) {
            int q = nodes[p].left;
            if (height(nodes[q].left) < height(nodes[q].right)) nodes[p].left = rotate_left(q);
            return rotate_right(p);
        }
        if (diff < -1) {
            int q = nodes[p].right;
            if (height(nodes[q].right) < height(nodes[q].left)) nodes[p].right = rotate_right(q);
            return rotate_left(p);
        }
        return p;
    }
    int create(int key) {
        if (!free_nodes.empty()) {
            int p = free_nodes.back(); free_nodes.pop_back();
            nodes[p] = {key, 0, 0, 1, 1};
            return p;
        }
        nodes.push_back({key, 0, 0, 1, 1});
        return int(nodes.size()) - 1;
    }
    int insert(int p, int key, bool &added) {
        if (!p) { added = true; return create(key); }
        if (key < nodes[p].key) nodes[p].left = insert(nodes[p].left, key, added);
        else if (key > nodes[p].key) nodes[p].right = insert(nodes[p].right, key, added);
        return added ? balance(p) : p;
    }
    int erase(int p, int key, bool &removed) {
        if (!p) return 0;
        if (key < nodes[p].key) nodes[p].left = erase(nodes[p].left, key, removed);
        else if (key > nodes[p].key) nodes[p].right = erase(nodes[p].right, key, removed);
        else {
            removed = true;
            if (nodes[p].left && nodes[p].right) {
                int q = nodes[p].right;
                while (nodes[q].left) q = nodes[q].left;
                nodes[p].key = nodes[q].key;
                bool ignored = false;
                nodes[p].right = erase(nodes[p].right, nodes[q].key, ignored);
            } else {
                int child = nodes[p].left ? nodes[p].left : nodes[p].right;
                free_nodes.push_back(p);
                return child;
            }
        }
        return removed ? balance(p) : p;
    }
    int count_leq(int key) const {
        int p = root, count = 0;
        while (p) {
            if (nodes[p].key <= key) {
                count += 1 + size(nodes[p].left);
                p = nodes[p].right;
            } else p = nodes[p].left;
        }
        return count;
    }
    int kth(int k) const {
        int p = root;
        if (k < 1 || k > size(p)) return -1;
        while (p) {
            int left = size(nodes[p].left);
            if (k == left + 1) return nodes[p].key;
            if (k <= left) p = nodes[p].left;
            else { k -= left + 1; p = nodes[p].right; }
        }
        return -1;
    }
    int le(int key) const {
        int p = root, result = -1;
        while (p) {
            if (nodes[p].key <= key) { result = nodes[p].key; p = nodes[p].right; }
            else p = nodes[p].left;
        }
        return result;
    }
    int ge(int key) const {
        int p = root, result = -1;
        while (p) {
            if (nodes[p].key >= key) { result = nodes[p].key; p = nodes[p].left; }
            else p = nodes[p].right;
        }
        return result;
    }
};
struct acl_fenwick {
    int n;
    // Extra precision prevents signed-64 wrapping before a sum is returned.
    atcoder::fenwick_tree<wide> tree;
    uwide magnitude = 0;
    explicit acl_fenwick(int size) : n(size), tree(size) {}
};
// Monoid operations are callbacks supplied by Python; the native side owns
// the tree layout and traversal. No Python objects are kept in native memory.
struct acl_segtree {
    int n, base;
    long long identity;
    acl_seg_op op;
    std::vector<long long> tree;
    acl_segtree(const long long *values, int size, long long e, acl_seg_op callback)
        : n(size), base(1), identity(e), op(callback) {
        while (base < n) base *= 2;
        tree.assign(2 * base, e);
        for (int i = 0; i < n; ++i) tree[base + i] = values[i];
        for (int i = base - 1; i; --i) tree[i] = op(tree[i * 2], tree[i * 2 + 1]);
    }
    void set(int index, long long value) {
        int p = base + index;
        tree[p] = value;
        while (p > 1) { p /= 2; tree[p] = op(tree[p * 2], tree[p * 2 + 1]); }
    }
    long long prod(int left, int right) const {
        long long a = identity, b = identity;
        for (left += base, right += base; left < right; left /= 2, right /= 2) {
            if (left & 1) a = op(a, tree[left++]);
            if (right & 1) b = op(tree[--right], b);
        }
        return op(a, b);
    }
};
struct acl_lazysegtree {
    struct Node { long long value, length, lazy; bool pending; };
    int n;
    long long identity, id;
    acl_lazy_op op;
    acl_lazy_mapping mapping;
    acl_lazy_composition composition;
    std::vector<Node> tree;
    acl_lazysegtree(const long long *values, const long long *lengths, int size,
                    long long e, long long identity_action, acl_lazy_op operation,
                    acl_lazy_mapping map, acl_lazy_composition compose)
        : n(size), identity(e), id(identity_action), op(operation), mapping(map),
          composition(compose), tree(4 * std::max(size, 1), {e, 0, identity_action, false}) {
        if (n) build(1, 0, n, values, lengths);
    }
    void build(int p, int l, int r, const long long *values, const long long *lengths) {
        if (l + 1 == r) { tree[p].value = values[l]; tree[p].length = lengths[l]; return; }
        int m = l + (r - l) / 2;
        build(p * 2, l, m, values, lengths); build(p * 2 + 1, m, r, values, lengths);
        pull(p);
    }
    void pull(int p) {
        const Node &a = tree[p * 2], &b = tree[p * 2 + 1];
        tree[p].value = op(a.value, a.length, b.value, b.length);
        tree[p].length = a.length + b.length;
    }
    void apply_node(int p, long long f) {
        Node &node = tree[p];
        node.value = mapping(f, node.value, node.length);
        node.lazy = node.pending ? composition(f, node.lazy) : f;
        node.pending = true;
    }
    void push(int p) {
        if (tree[p].pending) {
            apply_node(p * 2, tree[p].lazy); apply_node(p * 2 + 1, tree[p].lazy);
            tree[p].pending = false; tree[p].lazy = id;
        }
    }
    void apply(int p, int l, int r, int ql, int qr, long long f) {
        if (qr <= l || r <= ql) return;
        if (ql <= l && r <= qr) { apply_node(p, f); return; }
        push(p);
        int m = l + (r - l) / 2;
        apply(p * 2, l, m, ql, qr, f); apply(p * 2 + 1, m, r, ql, qr, f);
        pull(p);
    }
    Node prod(int p, int l, int r, int ql, int qr) {
        if (qr <= l || r <= ql) return {identity, 0, id, false};
        if (ql <= l && r <= qr) return tree[p];
        push(p);
        int m = l + (r - l) / 2;
        Node a = prod(p * 2, l, m, ql, qr), b = prod(p * 2 + 1, m, r, ql, qr);
        return {op(a.value, a.length, b.value, b.length), a.length + b.length, id, false};
    }
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

acl_ordered_set *acl_ordered_new(int unused) {
    return checked_new<acl_ordered_set>([&] {
        require(unused == 0, "ordered set constructor expects zero");
        return new acl_ordered_set();
    });
}
void acl_ordered_delete(acl_ordered_set *h) { delete h; }
int acl_ordered_add(acl_ordered_set *h, int key) {
    return checked([&] {
        handle_ok(h); require(key >= 0, "ordered set keys must be nonnegative");
        bool added = false; h->root = h->insert(h->root, key, added);
        return int(added);
    });
}
int acl_ordered_discard(acl_ordered_set *h, int key) {
    return checked([&] {
        handle_ok(h); require(key >= 0, "ordered set keys must be nonnegative");
        bool removed = false; h->root = h->erase(h->root, key, removed);
        return int(removed);
    });
}
int acl_ordered_count_leq(acl_ordered_set *h, int key) {
    return checked([&] { handle_ok(h); return h->count_leq(key); });
}
int acl_ordered_kth(acl_ordered_set *h, int k, int *answer) {
    return checked([&] {
        handle_ok(h); buffer_ok(answer, 1); *answer = h->kth(k); return 0;
    });
}
int acl_ordered_le(acl_ordered_set *h, int key, int *answer) {
    return checked([&] {
        handle_ok(h); buffer_ok(answer, 1); *answer = h->le(key); return 0;
    });
}
int acl_ordered_ge(acl_ordered_set *h, int key, int *answer) {
    return checked([&] {
        handle_ok(h); buffer_ok(answer, 1); *answer = h->ge(key); return 0;
    });
}
// -1 is the missing-value sentinel; -2 signals an error to Python.
int acl_ordered_kth_value(acl_ordered_set *h, int k) {
    return checked_ordered_value([&] { handle_ok(h); return h->kth(k); });
}
int acl_ordered_le_value(acl_ordered_set *h, int key) {
    return checked_ordered_value([&] { handle_ok(h); return h->le(key); });
}
int acl_ordered_ge_value(acl_ordered_set *h, int key) {
    return checked_ordered_value([&] { handle_ok(h); return h->ge(key); });
}

acl_segtree *acl_seg_new(const long long *values, int n, long long identity, acl_seg_op op) {
    return checked_new<acl_segtree>([&] {
        size_ok(n); require(n <= INT_MAX / 8, "segment tree is too large");
        buffer_ok(values, n); require(op != nullptr, "segment operation must be callable");
        return new acl_segtree(values, n, identity, op);
    });
}
void acl_seg_delete(acl_segtree *h) { delete h; }
int acl_seg_set(acl_segtree *h, int index, long long value) {
    return checked([&] { handle_ok(h); vertex(index, h->n); h->set(index, value); return 0; });
}
int acl_seg_prod(acl_segtree *h, int left, int right, long long *answer) {
    return checked([&] {
        handle_ok(h); require(0 <= left && left <= right && right <= h->n, "invalid segment interval");
        buffer_ok(answer, 1); *answer = h->prod(left, right); return 0;
    });
}
acl_lazysegtree *acl_lazy_new(const long long *values, const long long *lengths, int n,
                              long long identity, long long id,
                              acl_lazy_op op, acl_lazy_mapping mapping, acl_lazy_composition composition) {
    return checked_new<acl_lazysegtree>([&] {
        size_ok(n); require(n <= INT_MAX / 8, "lazy segment tree is too large");
        buffer_ok(values, n); buffer_ok(lengths, n);
        require(op && mapping && composition, "lazy segment callbacks must be callable");
        return new acl_lazysegtree(values, lengths, n, identity, id, op, mapping, composition);
    });
}
void acl_lazy_delete(acl_lazysegtree *h) { delete h; }
int acl_lazy_apply(acl_lazysegtree *h, int left, int right, long long action) {
    return checked([&] {
        handle_ok(h); require(0 <= left && left <= right && right <= h->n, "invalid lazy segment interval");
        if (left < right) h->apply(1, 0, h->n, left, right, action);
        return 0;
    });
}
int acl_lazy_prod(acl_lazysegtree *h, int left, int right, long long *answer) {
    return checked([&] {
        handle_ok(h); require(0 <= left && left <= right && right <= h->n, "invalid lazy segment interval");
        buffer_ok(answer, 1);
        *answer = left < right ? h->prod(1, 0, h->n, left, right).value : h->identity;
        return 0;
    });
}

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
int acl_dsu_process(acl_dsu *h, const int operations[][3], int n, int *answers) {
    return checked([&] {
        handle_ok(h); size_ok(n); buffer_ok(operations, n); buffer_ok(answers, n);
        int count = 0;
        for (int i = 0; i < n; ++i) {
            int kind = operations[i][0], a = operations[i][1], b = operations[i][2];
            require(kind == 0 || kind == 1, "invalid DSU operation");
            vertex(a, h->n); vertex(b, h->n);
            if (kind == 0) h->graph.merge(a, b);
            else answers[count++] = h->graph.same(a, b);
        }
        return count;
    });
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
int acl_fenwick_process(acl_fenwick *h, const long long operations[][3], int n, long long *answers) {
    return checked([&] {
        handle_ok(h); size_ok(n); buffer_ok(operations, n); buffer_ok(answers, n);
        int count = 0;
        for (int i = 0; i < n; ++i) {
            long long kind = operations[i][0], a = operations[i][1], b = operations[i][2];
            require(kind == 0 || kind == 1, "invalid Fenwick operation");
            if (kind == 0) {
                if (a < 0 || a > INT_MAX) throw std::invalid_argument("vertex/index is out of range");
                if (acl_fenwick_add(h, static_cast<int>(a), b) < 0) return -1;
            } else {
                if (a < 0 || a > INT_MAX || b < 0 || b > INT_MAX)
                    throw std::invalid_argument("invalid sum interval");
                if (acl_fenwick_sum(h, static_cast<int>(a), static_cast<int>(b), &answers[count]) < 0)
                    return -1;
                ++count;
            }
        }
        return count;
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
int acl_scc_add_edges(acl_scc *h, const int edges[][2], int n) {
    return checked([&] {
        handle_ok(h); size_ok(n); buffer_ok(edges, n);
        for (int i = 0; i < n; ++i)
            if (acl_scc_add_edge(h, edges[i][0], edges[i][1]) < 0) return -1;
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
            long long mi = moduli[i];
            if (m < mi) {
                std::swap(r, ri);
                std::swap(m, mi);
            }
            if (m % mi == 0) {
                if (r % mi != ri) { *residue = 0; *modulus = 0; return 0; }
                continue;
            }
            auto [gcd, inverse] = atcoder::internal::inv_gcd(m, mi);
            wide difference = wide(ri) - r;
            if (difference % gcd != 0) { *residue = 0; *modulus = 0; return 0; }
            long long quotient = mi / gcd;
            wide next_modulus = wide(m) * quotient;
            if (next_modulus > LLONG_MAX)
                throw std::overflow_error("CRT least common multiple exceeds signed 64 bits");
            wide x = (difference / gcd % quotient) * inverse % quotient;
            wide next_residue = (r + x * m) % next_modulus;
            if (next_residue < 0) next_residue += next_modulus;
            r = static_cast<long long>(next_residue);
            m = static_cast<long long>(next_modulus);
        }
        *residue = r; *modulus = m;
        return 0;
    });
}

int acl_crt4(long long r0, long long r1, long long r2, long long r3,
             long long m0, long long m1, long long m2, long long m3, long long *result) {
    const long long residues[] = {r0, r1, r2, r3};
    const long long moduli[] = {m0, m1, m2, m3};
    return acl_crt(residues, moduli, 4, result, result ? result + 1 : nullptr);
}
int acl_crt4_batch(const long long residues[][4], const long long moduli[][4],
                   int n, long long results[][2]) {
    return checked([&] {
        size_ok(n); buffer_ok(residues, n); buffer_ok(moduli, n); buffer_ok(results, n);
        for (int i = 0; i < n; ++i)
            if (acl_crt(residues[i], moduli[i], 4, &results[i][0], &results[i][1]) < 0)
                return -1;
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
