# ACL HPy

公式 [AtCoder Library](https://github.com/atcoder/ac-library) を [HPy Universal ABI](https://docs.hpyproject.org/en/latest/overview.html#target-abis) で呼び出す実装です。CPython / PyPy の両方で同じ ABI を使います。`Python.h`、CPython C API、CFFI は使用しません。

公式 ACL のリビジョンは `sources.lock.json` の `hpy` に固定しています。CFFI 版と同じ `acl_cffi/native.cpp` と `cdef.h` をコンパイルに使用し、入力検査・数値型・アルゴリズムを揃えています。Python との値変換、メソッド呼び出し、ネイティブオブジェクトの管理は `acl_hpy/native.cpp` が HPy API で行います。

## ビルドと計測

C++17 コンパイラと Python の開発ヘッダが必要です。CPython は `hpy==0.9.0`、PyPy は同梱 HPy のヘッダとランタイムを使用します。PyPy は [HPy 0.9 に対応した 7.3.14](https://doc.pypy.org/release-v7.3.14.html) 以降が必要で、CI では 7.3.20 を使用します。PyPy 同梱 HPy は pip で置き換えません。

リポジトリルートの仮想環境で実行してください。

```bash
python -m pip install -r requirements-hpy.txt
python -m benchkit build --source hpy
export PYTHONPATH="$(python -m benchkit build --source hpy --print-path)${PYTHONPATH:+:$PYTHONPATH}"
```

ベンチマークではビルドと読み込みパスの設定を自動で行うため、`PYTHONPATH` の手動設定は不要です。通常の比較にはルート README に従って他の実装の依存もインストールします。

```bash
python -m benchkit run --quick
python -m benchkit run
python -m benchkit report
```

PyPy では上記の `python` をその仮想環境の Python に置き換えます。計測はランタイムごとに順番に実行してください。`HPY=debug` / `HPY=trace` は計測時には設定しないでください。

ビルドは計測時間に含みません。キャッシュは `.cache/sources/hpy/` に保存し、ソース、共通 C++ 処理、依存バージョン、コンパイラ、フラグ、CPU、ランタイムの変更で更新します。HPy のバージョン・ABI・モードは結果 JSON の `runtime.hpy_build` に記録します。

## API

```python
from acl_hpy import dsu, fenwick_tree, convolution998244353

with dsu(5) as graph:
    graph.merge(0, 1)
    assert graph.same(0, 1)

with fenwick_tree(5) as tree:
    tree.add(2, 10)
    assert tree.sum(1, 4) == 10

assert convolution998244353([1, 2], [3, 4]) == [3, 10, 8]
```

対応 API は CFFI 版と同じ12種類です。

| API | 内容 |
| --- | --- |
| `dsu(n=0)` | `merge`, `same`, `leader`, `size`, `groups` |
| `fenwick_tree(n=0)` | `add`, `sum` |
| `scc_graph(n=0)` | `add_edge`, `scc` |
| `two_sat(n=0)` | `add_clause`, `satisfiable`, `answer` |
| `mf_graph(n=0)` | `add_edge`, `get_edge`, `edges`, `change_edge`, `flow`, `min_cut` |
| `mcf_graph(n=0)` | `add_edge`, `get_edge`, `edges`, `flow` |
| `convolution998244353(a, b)` | 法 998244353 の畳み込み |
| `crt(residues, moduli)` | 中国剰余定理 |
| `floor_sum(n, m, a, b)` | 床関数の和 |
| `suffix_array(values)` | 接尾辞配列 |
| `lcp_array(values, sa)` | LCP 配列 |
| `z_algorithm(values)` | Z 配列 |

木・グラフは `with` または `close()` で解放できます。明示的に解放しなかった場合は HPy の `tp_destroy` で解放します。`close()` は繰り返し呼び出せ、解放後の操作は `RuntimeError` です。PyPy では GC まで解放が遅れるため、計測アダプタは `with` を使います。

数値入力は符号付き64ビット、文字列アルゴリズムの整数列は符号付き32ビットです。`str` の添字と LCP 長は Unicode コードポイント、`bytes` はバイト単位です。入力・結果の範囲、最小費用流を1回だけ呼べる制約などは [CFFI 版の入力と範囲](../acl_cffi/README.md#入力と範囲) と同じです。`segtree` / `lazysegtree`、`mcf_graph.slope()` は未実装です。

各ケースの `implementations/hpy_universal.py` がこの API を使用します。`hpy.py` という名前は HPy ランタイムの import と衝突するため使用しません。DSU・グラフなどは Python のループから1操作ずつ呼び出します。計測には Python ラッパー、HPy 呼び出し、入力検査、配列と戻り値の変換を含みます。

## 検証

上記のビルド先を `PYTHONPATH` に設定して実行します。

```bash
ACL_HPY_REQUIRE_NATIVE=1 python -m unittest discover -s tests -p test_acl_hpy.py -v
ACL_HPY_REQUIRE_NATIVE=1 HPY=debug python -m unittest discover -s tests -p test_acl_hpy.py -v
```

CFFI 版と共通の独立した全探索・単純実装との比較に加え、全12ケースの正解チェック、引数変換失敗、オブジェクト解放、デバッグモードでのハンドル漏れを検証します。`ACL_HPY_REQUIRE_NATIVE=1` は未ビルド時も失敗として扱います。

PyPy 7.3.20 の HPy デバッグランタイムは、`__index__` 内から HPy メソッドへ再入すると `Wrong HPy Context` でプロセスを終了するため、そのテスト1件だけを同バージョンのデバッグモードでスキップします。同じテストを PyPy の通常モードと CPython の通常・デバッグモードでは実行します。
