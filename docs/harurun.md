# harurun-s-library の計測

[lif4635/harurun-s-library](https://github.com/lif4635/harurun-s-library) の現行 `library_codex` と旧 `library` を別系列で計測します。Codon 向けの `library _codon` は対象に含めません。使用コミットは `7c94b7bb0c9d4f6ed0ffa44853febee1e7971ff9` で、取得先と SHA は `sources.lock.json` の `harurun` に固定しています。

PyPy で `library_codex` は14ケース、旧 `library` は対応する11ケースを計測します。凡例はそれぞれ `lif4635/harurun-s-library (library_codex)` と `lif4635/harurun-s-library (library)` です。

| ケース | `library_codex` 内のモジュール・API | 旧 `library` 内のモジュール・API |
| --- | --- | --- |
| DSU | `union_find.UnionFind.UnionFind` | `UnionFind.UnionFind.DSU` |
| Fenwick Tree | `fenwick_tree.BIT.BIT` | `SegTree.BIT.BIT` |
| Segment Tree | `segment_tree.SegTree.SegTree` | `SegTree.SegTree.SegTree` |
| Lazy Segment Tree | `segment_tree.LazySegTree.LazySegTree` | `SegTree.LazySegTree.LazySegTree` |
| Convolution | `convolution.NTT998.multiply` | `convolution.multiply.multiply` |
| CRT | `number_theory.ChineseRemainder.chinese_remainder` | — |
| Floor sum | `number_theory.FloorSum.floor_sum` | `number_theory.floor_sum.floor_sum` |
| SCC | `graph_connectivity.StronglyConnectedComponents.SCC` | `graph.SCC.SCC_construct` |
| 2-SAT | `graph.TwoSAT.TwoSAT` | `graph.twosat.twosat` |
| Max flow | `graph_flow.MaxFlow.MaxFlowGraph` | — |
| Min-cost flow | `graph_flow.MinCostFlow.MinCostFlowGraph` | — |
| Suffix array | `string.SuffixArray.suffix_array` | `string.string.suffix_array` |
| LCP array | `string.SuffixArray.lcp_array` | `string.string.lcp_array` |
| Z-algorithm | `string.ZAlgorithm.z_algorithm` | `string.Z_algorism.Z_algorism` |

各ケースの `implementations/harurun.py` と `implementations/harurun_library.py` が入力・戻り値を既存ケースに合わせます。上流のアルゴリズムは変更せず、公開APIを呼び出します。旧 `library` に CRT・最大流・最小費用流は存在しないため、この3ケースに旧系列はありません。

- Lazy Segment Tree は他実装と同じ `(和, 長さ)` を使います。mapping が受け取る追加の区間長引数には依存しません。
- SCC の隣接リスト作成・グループの整列を計測に含めます。上流APIが行う縮約 DAG の構築も含みます。
- 2-SAT は `solve()` の `None` を充足不能と判定します。空の解 `[]` は充足可能です。解が全節を満たすかの検査も既存実装と同じく計測に含めます。
- 畳み込みは法 998244353 専用の `NTT998.multiply` を使用します。
- 旧 `library` の畳み込みは `convolution.multiply.multiply` を使用します。空配列はAPIに渡す前に空配列を返します。
- 旧 `library` の 2-SAT は節を符号付きリテラルに変換し、返された割当てを照合します。

入力サイズ、seed、ウォームアップ、5サンプル、各子プロセス60秒の上限は既存実装と共通です。CIでは独立した正解データに対する照合と入力を変更しないことを両ランタイムで確認します。

```bash
source_path=$(.venv-cpython/bin/python -m benchkit build --source harurun --print-path)
ACL_HARURUN_SOURCE="$source_path" .venv-cpython/bin/python -m unittest discover -s tests -p test_harurun.py
ACL_HARURUN_SOURCE="$source_path" .venv-pypy/bin/python -m unittest discover -s tests -p test_harurun.py
```
