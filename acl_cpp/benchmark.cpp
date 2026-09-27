// Standalone reference: inputs come from the Python workloads, timing stays in C++.
#include <atcoder/all>
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using ll = long long;
using Clock = std::chrono::steady_clock;
static_assert(sizeof(ll) == 8, "The local input protocol uses signed 64-bit words");

ll read_word() {
    ll value;
    if (!std::cin.read(reinterpret_cast<char *>(&value), sizeof(value)))
        throw std::runtime_error("truncated input");
    return value;
}
size_t read_size() {
    ll size = read_word();
    if (size < 0 || size > 10000000) throw std::runtime_error("invalid input length");
    return static_cast<size_t>(size);
}
std::vector<ll> read_vector() {
    std::vector<ll> values(read_size());
    if (!std::cin.read(reinterpret_cast<char *>(values.data()), values.size() * sizeof(ll)))
        throw std::runtime_error("truncated vector");
    return values;
}
template <size_t N> auto read_rows() {
    static_assert(sizeof(std::array<ll, N>) == N * sizeof(ll));
    std::vector<std::array<ll, N>> rows(read_size());
    if (!std::cin.read(reinterpret_cast<char *>(rows.data()), rows.size() * sizeof(rows[0])))
        throw std::runtime_error("truncated rows");
    return rows;
}
std::string read_string() {
    auto values = read_vector();
    std::string result;
    result.reserve(values.size());
    for (ll value : values) {
        // Existing string workloads use ASCII; keep byte and character indices equal.
        if (value < 0 || value > 127) throw std::runtime_error("reference workload requires ASCII");
        result.push_back(static_cast<char>(value));
    }
    return result;
}

template <class T> void json(const T &value);
template <class T> void json(const std::vector<T> &values);
template <class T, class U> void json(const std::pair<T, U> &value);
template <class T, size_t N> void json(const std::array<T, N> &values);
void json(bool value) { std::cout << (value ? "true" : "false"); }
template <class T> void json(const T &value) { std::cout << value; }
template <class T> void json(const std::vector<T> &values) {
    std::cout << '[';
    for (size_t i = 0; i < values.size(); ++i) {
        if (i) std::cout << ',';
        json(static_cast<T>(values[i]));
    }
    std::cout << ']';
}
template <class T, class U> void json(const std::pair<T, U> &value) {
    std::cout << '['; json(value.first); std::cout << ','; json(value.second); std::cout << ']';
}
template <class T, size_t N> void json(const std::array<T, N> &values) {
    std::cout << '[';
    for (size_t i = 0; i < N; ++i) { if (i) std::cout << ','; json(values[i]); }
    std::cout << ']';
}

double seconds(Clock::time_point start) {
    return std::chrono::duration<double>(Clock::now() - start).count();
}
struct Settings { int repeat, warmup; double warmup_seconds, sample_seconds; };

template <class F> void measure(F run, const Settings &settings, bool validate) {
    auto baseline = run();
    if (validate) { json(baseline); return; }
    int warmed = 0;
    auto start = Clock::now();
    while (warmed < settings.warmup || seconds(start) < settings.warmup_seconds) {
        if (run() != baseline) throw std::runtime_error("non-deterministic warmup result");
        ++warmed;
    }
    start = Clock::now();
    auto value = run();
    double elapsed = seconds(start);
    if (value != baseline) throw std::runtime_error("non-deterministic calibration result");
    int loops = static_cast<int>(std::clamp(settings.sample_seconds / std::max(elapsed, 1e-9), 1.0, 10000.0));
    std::vector<double> samples;
    for (int sample = 0; sample < settings.repeat; ++sample) {
        start = Clock::now();
        for (int iteration = 0; iteration < loops; ++iteration) {
            value = run();
            // Make each result observable to the optimizer without timing a hash
            // or JSON serialization. GCC/Clang compile this barrier to no code.
            asm volatile("" : : "g"(&value) : "memory");
        }
        samples.push_back(seconds(start) / loops);
        if (value != baseline) throw std::runtime_error("non-deterministic measured result");
    }
    std::cout << "{\"samples\":"; json(samples);
    std::cout << ",\"loops\":" << loops << ",\"warmup_runs\":" << warmed << ",\"output\":";
    json(baseline);
    std::cout << '}';
}

ll add(ll a, ll b) { return a + b; }
ll zero() { return 0; }
struct Sum { ll value, length; };
Sum combine(Sum a, Sum b) { return {a.value + b.value, a.length + b.length}; }
Sum empty_sum() { return {0, 0}; }
Sum mapping(ll f, Sum x) { return {x.value + f * x.length, x.length}; }

void dispatch(const std::string &name, const Settings &settings, bool validate) {
    if (name == "dsu") {
        int n = static_cast<int>(read_size()); auto ops = read_rows<3>();
        measure([&] {
            atcoder::dsu graph(n); std::vector<bool> result;
            for (auto [kind, a, b] : ops) {
                if (!kind) graph.merge(a, b); else result.push_back(graph.same(a, b));
            }
            return result;
        }, settings, validate);
    } else if (name == "fenwicktree") {
        int n = static_cast<int>(read_size()); auto ops = read_rows<3>();
        measure([&] {
            atcoder::fenwick_tree<ll> tree(n); std::vector<ll> result;
            for (auto [kind, a, b] : ops) {
                if (!kind) tree.add(a, b); else result.push_back(tree.sum(a, b));
            }
            return result;
        }, settings, validate);
    } else if (name == "segtree") {
        auto initial = read_vector(); auto ops = read_rows<3>();
        measure([&] {
            atcoder::segtree<ll, add, zero> tree(initial); std::vector<ll> result;
            for (auto [kind, a, b] : ops) {
                if (!kind) tree.set(a, b); else result.push_back(tree.prod(a, b));
            }
            return result;
        }, settings, validate);
    } else if (name == "lazysegtree") {
        auto rows = read_rows<2>(); std::vector<Sum> initial;
        for (auto row : rows) initial.push_back({row[0], row[1]});
        auto ops = read_rows<4>();
        measure([&] {
            atcoder::lazy_segtree<Sum, combine, empty_sum, ll, mapping, add, zero> tree(initial);
            std::vector<ll> result;
            for (auto [kind, l, r, amount] : ops) {
                if (!kind) tree.apply(l, r, amount); else result.push_back(tree.prod(l, r).value);
            }
            return result;
        }, settings, validate);
    } else if (name == "convolution") {
        auto a = read_vector(), b = read_vector();
        measure([&] { return atcoder::convolution<998244353>(a, b); }, settings, validate);
    } else if (name == "crt") {
        std::vector<std::pair<std::vector<ll>, std::vector<ll>>> queries(read_size());
        for (auto &query : queries) { query.first = read_vector(); query.second = read_vector(); }
        measure([&] {
            std::vector<std::pair<ll, ll>> result;
            for (const auto &query : queries) result.push_back(atcoder::crt(query.first, query.second));
            return result;
        }, settings, validate);
    } else if (name == "floor_sum") {
        auto queries = read_rows<4>();
        measure([&] {
            std::vector<ll> result;
            for (auto [n, m, a, b] : queries) result.push_back(atcoder::floor_sum(n, m, a, b));
            return result;
        }, settings, validate);
    } else if (name == "scc") {
        int n = static_cast<int>(read_size()); auto edges = read_rows<2>();
        measure([&] {
            atcoder::scc_graph graph(n);
            for (auto [a, b] : edges) graph.add_edge(a, b);
            auto result = graph.scc();
            for (auto &group : result) std::sort(group.begin(), group.end());
            std::sort(result.begin(), result.end());
            return result;
        }, settings, validate);
    } else if (name == "two_sat") {
        int n = static_cast<int>(read_size()); auto clauses = read_rows<4>();
        measure([&] {
            atcoder::two_sat solver(n);
            for (auto [i, f, j, g] : clauses) solver.add_clause(i, f, j, g);
            bool possible = solver.satisfiable(), valid = true;
            if (possible) {
                auto answer = solver.answer();
                for (auto [i, f, j, g] : clauses)
                    if (answer[i] != bool(f) && answer[j] != bool(g)) { valid = false; break; }
            }
            return std::array<bool, 2>{possible, valid};
        }, settings, validate);
    } else if (name == "maxflow") {
        int n = static_cast<int>(read_size()), s = static_cast<int>(read_word()), t = static_cast<int>(read_word());
        auto edges = read_rows<3>();
        measure([&] {
            atcoder::mf_graph<ll> graph(n);
            for (auto [a, b, cap] : edges) graph.add_edge(a, b, cap);
            return graph.flow(s, t);
        }, settings, validate);
    } else if (name == "mincostflow") {
        int n = static_cast<int>(read_size()), s = static_cast<int>(read_word()), t = static_cast<int>(read_word());
        auto edges = read_rows<4>();
        measure([&] {
            atcoder::mcf_graph<ll, ll> graph(n);
            for (auto [a, b, cap, cost] : edges) graph.add_edge(a, b, cap, cost);
            return graph.flow(s, t);
        }, settings, validate);
    } else if (name == "suffix_array") {
        auto s = read_string();
        measure([&] { return atcoder::suffix_array(s); }, settings, validate);
    } else if (name == "lcp_array") {
        auto s = read_string(); auto values = read_vector();
        std::vector<int> sa(values.begin(), values.end());
        measure([&] { return s.empty() ? std::vector<int>{} : atcoder::lcp_array(s, sa); }, settings, validate);
    } else if (name == "z_algorithm") {
        auto s = read_string();
        measure([&] { return atcoder::z_algorithm(s); }, settings, validate);
    } else {
        throw std::runtime_error("unsupported reference case: " + name);
    }
}

int main(int argc, char **argv) {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    std::cout << std::setprecision(17);
    try {
        if (argc != 7) throw std::runtime_error("expected case, mode, repeat, warmup, warmup_seconds, sample_seconds");
        Settings settings{std::stoi(argv[3]), std::stoi(argv[4]), std::stod(argv[5]), std::stod(argv[6])};
        if (settings.repeat < 1 || settings.warmup < 0 || settings.warmup_seconds < 0 || settings.sample_seconds < 0)
            throw std::runtime_error("invalid measurement settings");
        bool validate = std::string(argv[2]) == "validate";
        dispatch(argv[1], settings, validate);
        std::cout << '\n';
        return 0;
    } catch (const std::exception &error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
