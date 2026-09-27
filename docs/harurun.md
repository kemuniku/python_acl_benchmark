# harurun-s-library の計測

[lif4635/harurun-s-library](https://github.com/lif4635/harurun-s-library) のうち、上流の `AGENTS.md` で現行版とされている `library_codex` を使用します。旧 `library` と Codon 向けの `library _codon` は対象に含めません。追加時のコミットは `7c94b7bb0c9d4f6ed0ffa44853febee1e7971ff9` で、取得先と SHA は `sources.lock.json` の `harurun` に固定しています。

既存の14ケースすべてを CPython / PyPy で計測します。凡例は `lif4635/harurun-s-library (library_codex)` です。

| ケース | `library_codex` 内のモジュール・API |
| --- | --- |
| DSU | `union_find.UnionFind.UnionFind` |
| Fenwick Tree | `fenwick_tree.BIT.BIT` |
| Segment Tree | `segment_tree.SegTree.SegTree` |
| Lazy Segment Tree | `segment_tree.LazySegTree.LazySegTree` |
| Convolution | `convolution.NTT998.multiply` |
| CRT | `number_theory.ChineseRemainder.chinese_remainder` |
| Floor sum | `number_theory.FloorSum.floor_sum` |
| SCC | `graph_connectivity.StronglyConnectedComponents.SCC` |
| 2-SAT | `graph.TwoSAT.TwoSAT` |
| Max flow | `graph_flow.MaxFlow.MaxFlowGraph` |
| Min-cost flow | `graph_flow.MinCostFlow.MinCostFlowGraph` |
| Suffix array | `string.SuffixArray.suffix_array` |
| LCP array | `string.SuffixArray.lcp_array` |
| Z-algorithm | `string.ZAlgorithm.z_algorithm` |

各ケースの `implementations/harurun.py` が入力・戻り値を既存ケースに合わせます。上流のアルゴリズムは変更せず、公開APIを呼び出します。

- Lazy Segment Tree は他実装と同じ `(和, 長さ)` を使います。mapping が受け取る追加の区間長引数には依存しません。
- SCC の隣接リスト作成・グループの整列を計測に含めます。上流APIが行う縮約 DAG の構築も含みます。
- 2-SAT は `solve()` の `None` を充足不能と判定します。空の解 `[]` は充足可能です。解が全節を満たすかの検査も既存実装と同じく計測に含めます。
- 畳み込みは法 998244353 専用の `NTT998.multiply` を使用します。

入力サイズ、seed、ウォームアップ、5サンプル、各子プロセス4秒の上限は既存実装と共通です。CIでは独立した正解データに対する照合と入力を変更しないことを両ランタイムで確認します。

```bash
source_path=$(.venv-cpython/bin/python -m benchkit build --source harurun --print-path)
ACL_HARURUN_SOURCE="$source_path" .venv-cpython/bin/python -m unittest discover -s tests -p test_harurun.py
ACL_HARURUN_SOURCE="$source_path" .venv-pypy/bin/python -m unittest discover -s tests -p test_harurun.py
```
