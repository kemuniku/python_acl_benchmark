// HPy Universal API only: no Python.h, PyObject*, or CFFI calls.
#include <hpy.h>
#include <type_traits>
#include "../acl_cffi/native.cpp"

namespace {
// A pending Python exception propagates through C++ helpers without losing
// owned handles. No C++ exception may escape an HPy entry point.
struct PythonError {};

class Owned {
    HPyContext *ctx;
    HPy value;
public:
    Owned(HPyContext *ctx, HPy value) : ctx(ctx), value(value) {
        if (HPy_IsNull(value)) throw PythonError{};
    }
    ~Owned() { HPy_Close(ctx, value); }
    Owned(const Owned &) = delete;
    Owned &operator=(const Owned &) = delete;
    operator HPy() const { return value; }
    HPy release() { HPy result = value; value = HPy_NULL; return result; }
};

template <class F> HPy boundary(HPyContext *ctx, F action) noexcept {
    try {
        return action();
    } catch (const PythonError &) {
        return HPy_NULL;
    } catch (const std::bad_alloc &) {
        return HPyErr_NoMemory(ctx);
    } catch (const std::length_error &error) {
        return HPyErr_SetString(ctx, ctx->h_OverflowError, error.what());
    } catch (const std::exception &error) {
        return HPyErr_SetString(ctx, ctx->h_RuntimeError, error.what());
    } catch (...) {
        return HPyErr_SetString(ctx, ctx->h_RuntimeError, "unknown native exception");
    }
}

void native_error(HPyContext *ctx) {
    HPy kind = ctx->h_RuntimeError;
    switch (acl_error_code()) {
        case 1: kind = ctx->h_ValueError; break;
        case 2: kind = ctx->h_OverflowError; break;
        case 3: kind = ctx->h_MemoryError; break;
    }
    HPyErr_SetString(ctx, kind, acl_last_error());
    throw PythonError{};
}

int check(HPyContext *ctx, int status) {
    if (status < 0) native_error(ctx);
    return status;
}

HPy none(HPyContext *ctx) { return HPy_Dup(ctx, ctx->h_None); }

// HPy owns this POD payload. The C++ object is allocated separately, so HPy
// never needs to run a C++ constructor in interpreter-owned memory.
struct Handle {
    void *ptr;
    void (*destroy)(void *);
    int n;
};
HPyType_HELPERS(Handle)

template <class T> void destroy_native(void *ptr) { delete static_cast<T *>(ptr); }

template <class T> T *get(HPyContext *ctx, HPy self) {
    Handle *handle = Handle_AsStruct(ctx, self);
    if (!handle->ptr) {
        HPyErr_SetString(ctx, ctx->h_RuntimeError, "This ACL object has been closed");
        throw PythonError{};
    }
    if (handle->destroy != destroy_native<T>) {
        HPyErr_SetString(ctx, ctx->h_TypeError, "incorrect ACL object type");
        throw PythonError{};
    }
    return static_cast<T *>(handle->ptr);
}

HPyDef_SLOT(handle_destroy, HPy_tp_destroy)
static void handle_destroy_impl(void *data) {
    Handle *handle = static_cast<Handle *>(data);
    if (handle->ptr) handle->destroy(handle->ptr);
}

HPyDef_METH(handle_close, "close", HPyFunc_NOARGS)
static HPy handle_close_impl(HPyContext *ctx, HPy self) {
    Handle *handle = Handle_AsStruct(ctx, self);
    if (handle->ptr) {
        handle->destroy(handle->ptr);
        handle->ptr = nullptr;
    }
    return none(ctx);
}

HPyDef_METH(handle_check_open, "_check_open", HPyFunc_NOARGS)
static HPy handle_check_open_impl(HPyContext *ctx, HPy self) {
    if (!Handle_AsStruct(ctx, self)->ptr)
        return HPyErr_SetString(ctx, ctx->h_RuntimeError, "This ACL object has been closed");
    return none(ctx);
}

template <class T> HPy construct(HPyContext *ctx, HPy cls, const HPy *args,
                               HPy_ssize_t nargs, HPy kw, T *(*create)(int)) {
    return boundary(ctx, [&]() -> HPy {
        int n = 0;
        static const char *keywords[] = {"n", nullptr};
        if (!HPyArg_ParseKeywordsDict(ctx, nullptr, args, nargs, kw, "|i", keywords, &n))
            throw PythonError{};
        // Allocate the HPy payload first. A failed native constructor leaves a
        // null pointer, which the destructor can safely ignore.
        Handle *handle;
        Owned result(ctx, HPy_New(ctx, cls, &handle));
        handle->ptr = nullptr;
        handle->destroy = destroy_native<T>;
        handle->n = n;
        handle->ptr = create(n);
        if (!handle->ptr) native_error(ctx);
        return result.release();
    });
}

#define CONSTRUCTOR(NAME, TYPE) \
    HPyDef_SLOT(NAME##_new, HPy_tp_new) \
    static HPy NAME##_new_impl(HPyContext *ctx, HPy cls, const HPy *args, \
                              HPy_ssize_t nargs, HPy kw) { \
        return construct<TYPE>(ctx, cls, args, nargs, kw, TYPE##_new); \
    }
CONSTRUCTOR(dsu, acl_dsu)
CONSTRUCTOR(fenwick, acl_fenwick)
CONSTRUCTOR(scc, acl_scc)
CONSTRUCTOR(twosat, acl_twosat)
CONSTRUCTOR(mf, acl_mf)
CONSTRUCTOR(mcf, acl_mcf)

// HPyArg_Parse with numeric formats borrows arguments and needs no tracker.
#define PARSE(FORMAT, ...) \
    if (!HPyArg_Parse(ctx, nullptr, args, nargs, FORMAT, __VA_ARGS__)) throw PythonError{}
#define METHOD(NAME, PYNAME) \
    HPyDef_METH(NAME, PYNAME, HPyFunc_VARARGS) \
    static HPy NAME##_impl(HPyContext *ctx, HPy self, const HPy *args, size_t nargs)

template <class T> HPy integer(HPyContext *ctx, T value) {
    return HPyLong_FromInt64_t(ctx, value);
}

template <class T> HPy list(HPyContext *ctx, const T *data, size_t count, bool boolean = false) {
    // Builders do not steal handles; every temporary is closed after Set.
    HPyListBuilder builder = HPyListBuilder_New(ctx, count);
    try {
        for (size_t i = 0; i < count; ++i) {
            Owned item(ctx, boolean ? HPyBool_FromBool(ctx, data[i] != 0) : integer(ctx, data[i]));
            HPyListBuilder_Set(ctx, builder, i, item);
        }
    } catch (...) {
        HPyListBuilder_Cancel(ctx, builder);
        throw;
    }
    return HPyListBuilder_Build(ctx, builder);
}

template <class T> HPy groups(HPyContext *ctx, HPy self, int (*function)(T *, int *, int *)) {
    T *handle = get<T>(ctx, self);
    std::vector<int> vertices(handle->n), offsets(size_t(handle->n) + 1);
    int count = check(ctx, function(handle, vertices.data(), offsets.data()));
    HPyListBuilder builder = HPyListBuilder_New(ctx, count);
    try {
        for (int i = 0; i < count; ++i) {
            Owned item(ctx, list(ctx, vertices.data() + offsets[i], offsets[i + 1] - offsets[i]));
            HPyListBuilder_Set(ctx, builder, i, item);
        }
    } catch (...) {
        HPyListBuilder_Cancel(ctx, builder);
        throw;
    }
    return HPyListBuilder_Build(ctx, builder);
}

METHOD(dsu_merge, "merge") {
    return boundary(ctx, [&] { int a, b; PARSE("ii", &a, &b);
        return integer(ctx, check(ctx, acl_dsu_merge(get<acl_dsu>(ctx, self), a, b))); });
}
METHOD(dsu_same, "same") {
    return boundary(ctx, [&] { int a, b; PARSE("ii", &a, &b);
        return HPyBool_FromBool(ctx, check(ctx, acl_dsu_same(get<acl_dsu>(ctx, self), a, b))); });
}
METHOD(dsu_leader, "leader") {
    return boundary(ctx, [&] { int a; PARSE("i", &a);
        return integer(ctx, check(ctx, acl_dsu_leader(get<acl_dsu>(ctx, self), a))); });
}
METHOD(dsu_size, "size") {
    return boundary(ctx, [&] { int a; PARSE("i", &a);
        return integer(ctx, check(ctx, acl_dsu_size(get<acl_dsu>(ctx, self), a))); });
}
HPyDef_METH(dsu_groups, "groups", HPyFunc_NOARGS)
static HPy dsu_groups_impl(HPyContext *ctx, HPy self) {
    return boundary(ctx, [&] { return groups(ctx, self, acl_dsu_groups); });
}

METHOD(fenwick_add, "add") {
    return boundary(ctx, [&] { int p; long long value; PARSE("iL", &p, &value);
        check(ctx, acl_fenwick_add(get<acl_fenwick>(ctx, self), p, value)); return none(ctx); });
}
METHOD(fenwick_sum, "sum") {
    return boundary(ctx, [&] { int l, r; long long value; PARSE("ii", &l, &r);
        check(ctx, acl_fenwick_sum(get<acl_fenwick>(ctx, self), l, r, &value)); return integer(ctx, value); });
}
METHOD(scc_add, "add_edge") {
    return boundary(ctx, [&] { int a, b; PARSE("ii", &a, &b);
        check(ctx, acl_scc_add_edge(get<acl_scc>(ctx, self), a, b)); return none(ctx); });
}
HPyDef_METH(scc_groups, "scc", HPyFunc_NOARGS)
static HPy scc_groups_impl(HPyContext *ctx, HPy self) {
    return boundary(ctx, [&] { return groups(ctx, self, acl_scc_groups); });
}
METHOD(twosat_add, "add_clause") {
    return boundary(ctx, [&] { int i, f, j, g; PARSE("iiii", &i, &f, &j, &g);
        check(ctx, acl_twosat_add_clause(get<acl_twosat>(ctx, self), i, f, j, g)); return none(ctx); });
}
HPyDef_METH(twosat_satisfiable, "satisfiable", HPyFunc_NOARGS)
static HPy twosat_satisfiable_impl(HPyContext *ctx, HPy self) {
    return boundary(ctx, [&] {
        return HPyBool_FromBool(ctx, check(ctx, acl_twosat_satisfiable(get<acl_twosat>(ctx, self)))); });
}
HPyDef_METH(twosat_answer, "answer", HPyFunc_NOARGS)
static HPy twosat_answer_impl(HPyContext *ctx, HPy self) {
    return boundary(ctx, [&] {
        auto h = get<acl_twosat>(ctx, self); std::vector<int> answer(h->n);
        check(ctx, acl_twosat_answer(h, answer.data()));
        return list(ctx, answer.data(), answer.size(), true); });
}

METHOD(mf_add, "add_edge") {
    return boundary(ctx, [&] { int a, b; long long cap; PARSE("iiL", &a, &b, &cap);
        return integer(ctx, check(ctx, acl_mf_add_edge(get<acl_mf>(ctx, self), a, b, cap))); });
}
METHOD(mf_change, "change_edge") {
    return boundary(ctx, [&] { int i; long long cap, flow; PARSE("iLL", &i, &cap, &flow);
        check(ctx, acl_mf_change_edge(get<acl_mf>(ctx, self), i, cap, flow)); return none(ctx); });
}
METHOD(mf_flow, "flow") {
    return boundary(ctx, [&] { int s, t; long long limit = LLONG_MAX, flow;
        PARSE("ii|L", &s, &t, &limit);
        check(ctx, acl_mf_flow(get<acl_mf>(ctx, self), s, t, limit, &flow)); return integer(ctx, flow); });
}
METHOD(mf_cut, "min_cut") {
    return boundary(ctx, [&] { int s; PARSE("i", &s);
        auto h = get<acl_mf>(ctx, self); std::vector<int> cut(h->n);
        check(ctx, acl_mf_min_cut(h, s, cut.data())); return list(ctx, cut.data(), cut.size(), true); });
}
METHOD(mcf_add, "add_edge") {
    return boundary(ctx, [&] { int a, b; long long cap, cost; PARSE("iiLL", &a, &b, &cap, &cost);
        return integer(ctx, check(ctx, acl_mcf_add_edge(get<acl_mcf>(ctx, self), a, b, cap, cost))); });
}

HPy tuple(HPyContext *ctx, std::initializer_list<long long> values) {
    HPyTupleBuilder builder = HPyTupleBuilder_New(ctx, values.size());
    try {
        int i = 0;
        for (auto value : values) {
            Owned item(ctx, integer(ctx, value));
            HPyTupleBuilder_Set(ctx, builder, i++, item);
        }
    } catch (...) {
        HPyTupleBuilder_Cancel(ctx, builder);
        throw;
    }
    return HPyTupleBuilder_Build(ctx, builder);
}

METHOD(mcf_flow, "flow") {
    return boundary(ctx, [&] { int s, t; long long limit = LLONG_MAX, flow, cost;
        PARSE("ii|L", &s, &t, &limit);
        check(ctx, acl_mcf_flow(get<acl_mcf>(ctx, self), s, t, limit, &flow, &cost));
        return tuple(ctx, {flow, cost}); });
}
HPy edge(HPyContext *ctx, acl_mf *h, int index) {
    acl_mf_edge e; check(ctx, acl_mf_get_edge(h, index, &e));
    return tuple(ctx, {e.from, e.to, e.cap, e.flow});
}
HPy edge(HPyContext *ctx, acl_mcf *h, int index) {
    acl_mcf_edge e; check(ctx, acl_mcf_get_edge(h, index, &e));
    return tuple(ctx, {e.from, e.to, e.cap, e.flow, e.cost});
}
template <class T> HPy edges(HPyContext *ctx, HPy self) {
    int count = get<T>(ctx, self)->edges;
    HPyListBuilder builder = HPyListBuilder_New(ctx, count);
    try {
        for (int i = 0; i < count; ++i) {
            // Allocating a Python tuple may run finalizers that close self.
            Owned item(ctx, edge(ctx, get<T>(ctx, self), i)); HPyListBuilder_Set(ctx, builder, i, item);
        }
    } catch (...) { HPyListBuilder_Cancel(ctx, builder); throw; }
    return HPyListBuilder_Build(ctx, builder);
}
METHOD(mf_edge, "_get_edge") {
    return boundary(ctx, [&] { int i; PARSE("i", &i); return edge(ctx, get<acl_mf>(ctx, self), i); });
}
METHOD(mcf_edge, "_get_edge") {
    return boundary(ctx, [&] { int i; PARSE("i", &i); return edge(ctx, get<acl_mcf>(ctx, self), i); });
}
HPyDef_METH(mf_edges, "_edges", HPyFunc_NOARGS)
static HPy mf_edges_impl(HPyContext *ctx, HPy self) {
    return boundary(ctx, [&] { return edges<acl_mf>(ctx, self); });
}
HPyDef_METH(mcf_edges, "_edges", HPyFunc_NOARGS)
static HPy mcf_edges_impl(HPyContext *ctx, HPy self) {
    return boundary(ctx, [&] { return edges<acl_mcf>(ctx, self); });
}

template <class T> std::vector<T> sequence(HPyContext *ctx, HPy value, bool text = false) {
    HPy_ssize_t n = HPy_Length(ctx, value);
    if (n < 0) throw PythonError{};
    if (n >= INT_MAX) {
        HPyErr_SetString(ctx, ctx->h_OverflowError, "sequence is too large"); throw PythonError{};
    }
    std::vector<T> output(n);
    bool unicode = text && HPyUnicode_Check(ctx, value);
    for (HPy_ssize_t i = 0; i < n; ++i) {
        if (unicode) {
            output[i] = HPyUnicode_ReadChar(ctx, value, i);
        } else {
            Owned item(ctx, HPy_GetItem_i(ctx, value, i));
            auto number = HPyLong_AsInt64_t(ctx, item);
            if (HPyErr_Occurred(ctx)) throw PythonError{};
            // Some PyPy HPy runtimes truncate AsInt32_t on 64-bit hosts.
            // Check explicitly so both runtimes enforce the same API domain.
            if constexpr (std::is_same_v<T, int>) {
                if (number < INT_MIN || number > INT_MAX) {
                    HPyErr_SetString(ctx, ctx->h_OverflowError, "value does not fit in signed 32 bits");
                    throw PythonError{};
                }
            }
            output[i] = static_cast<T>(number);
        }
        if (HPyErr_Occurred(ctx)) throw PythonError{};
    }
    return output;
}

// The O format requires HPyTracker with keyword parsing. For positional-only
// module functions, use borrowed args directly after checking arity.
void arity(HPyContext *ctx, size_t nargs, size_t expected) {
    if (nargs != expected) {
        HPyErr_SetString(ctx, ctx->h_TypeError, "incorrect number of arguments"); throw PythonError{};
    }
}
METHOD(convolution, "convolution998244353") {
    return boundary(ctx, [&] {
        arity(ctx, nargs, 2);
        auto a = sequence<long long>(ctx, args[0]), b = sequence<long long>(ctx, args[1]);
        size_t count = a.empty() || b.empty() ? 0 : a.size() + b.size() - 1;
        if (count > (1 << 23)) {
            HPyErr_SetString(ctx, ctx->h_ValueError, "convolution output length must not exceed 2^23");
            throw PythonError{};
        }
        std::vector<int> result(count);
        check(ctx, acl_convolution(a.data(), a.size(), b.data(), b.size(), result.data()));
        return list(ctx, result.data(), result.size()); });
}
METHOD(crt, "crt") {
    return boundary(ctx, [&] {
        arity(ctx, nargs, 2);
        auto r = sequence<long long>(ctx, args[0]), m = sequence<long long>(ctx, args[1]);
        if (r.size() != m.size()) {
            HPyErr_SetString(ctx, ctx->h_ValueError, "residues and moduli must have the same length");
            throw PythonError{};
        }
        long long result, modulus;
        check(ctx, acl_crt(r.data(), m.data(), r.size(), &result, &modulus));
        return tuple(ctx, {result, modulus}); });
}
METHOD(floor_sum, "floor_sum") {
    return boundary(ctx, [&] { long long n, m, a, b, result; PARSE("LLLL", &n, &m, &a, &b);
        check(ctx, acl_floor_sum(n, m, a, b, &result)); return integer(ctx, result); });
}
HPyDef_METH(suffix_array, "suffix_array", HPyFunc_O)
static HPy suffix_array_impl(HPyContext *ctx, HPy, HPy value) {
    return boundary(ctx, [&] {
        auto input = sequence<int>(ctx, value, true); std::vector<int> result(input.size());
        check(ctx, acl_suffix_array(input.data(), input.size(), result.data()));
        return list(ctx, result.data(), result.size()); });
}
HPyDef_METH(z_algorithm, "z_algorithm", HPyFunc_O)
static HPy z_algorithm_impl(HPyContext *ctx, HPy, HPy value) {
    return boundary(ctx, [&] {
        auto input = sequence<int>(ctx, value, true); std::vector<int> result(input.size());
        check(ctx, acl_z_algorithm(input.data(), input.size(), result.data()));
        return list(ctx, result.data(), result.size()); });
}
METHOD(lcp_array, "lcp_array") {
    return boundary(ctx, [&] {
        arity(ctx, nargs, 2);
        auto input = sequence<int>(ctx, args[0], true), sa = sequence<int>(ctx, args[1]);
        if (input.size() != sa.size()) {
            HPyErr_SetString(ctx, ctx->h_ValueError, "suffix array length must match input length");
            throw PythonError{};
        }
        std::vector<int> result(input.empty() ? 0 : input.size() - 1);
        check(ctx, acl_lcp_array(input.data(), input.size(), sa.data(), result.data()));
        return list(ctx, result.data(), result.size()); });
}

#define TYPE(NAME, PYNAME, ...) \
    HPyDef *NAME##_defs[] = {&NAME##_new, &handle_destroy, &handle_close, &handle_check_open, __VA_ARGS__, nullptr}; \
    HPyType_Spec NAME##_spec = { \
        "_acl_hpy_native." PYNAME, sizeof(Handle), 0, \
        HPy_TPFLAGS_DEFAULT, SHAPE(Handle), nullptr, NAME##_defs, nullptr \
    };
TYPE(dsu, "dsu", &dsu_merge, &dsu_same, &dsu_leader, &dsu_size, &dsu_groups)
TYPE(fenwick, "fenwick_tree", &fenwick_add, &fenwick_sum)
TYPE(scc, "scc_graph", &scc_add, &scc_groups)
TYPE(twosat, "two_sat", &twosat_add, &twosat_satisfiable, &twosat_answer)
TYPE(mf, "mf_graph", &mf_add, &mf_change, &mf_flow, &mf_cut, &mf_edge, &mf_edges)
TYPE(mcf, "mcf_graph", &mcf_add, &mcf_flow, &mcf_edge, &mcf_edges)

HPyDef_SLOT(module_exec, HPy_mod_exec)
static int module_exec_impl(HPyContext *ctx, HPy module) {
    HPyType_Spec *specs[] = {&dsu_spec, &fenwick_spec, &scc_spec, &twosat_spec, &mf_spec, &mcf_spec};
    const char *names[] = {"dsu", "fenwick_tree", "scc_graph", "two_sat", "mf_graph", "mcf_graph"};
    for (int i = 0; i < 6; ++i)
        if (!HPyHelpers_AddType(ctx, module, names[i], specs[i], nullptr)) return -1;
    return 0;
}
HPyDef *module_defs[] = {&module_exec, &convolution, &crt, &floor_sum,
                        &suffix_array, &lcp_array, &z_algorithm, nullptr};
HPyModuleDef module_def = {"Official ACL via HPy Universal ABI", 0, nullptr, module_defs, nullptr};
}  // namespace
HPy_MODINIT(_acl_hpy_native, module_def)
