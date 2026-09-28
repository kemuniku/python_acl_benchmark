# ACL CFFI

公式の [AtCoder Library](https://github.com/atcoder/ac-library) を、[CFFI の out-of-line API mode](https://cffi.readthedocs.io/en/latest/overview.html#main-mode-of-usage) で CPython / PyPy から呼び出す実装です。C++ の型を C ABI の関数とハンドルで包み、Python API から呼び出します。公式 ACL のリビジョンはルートの `sources.lock.json` で固定しています。

## ビルド

Python 環境ごとに CFFI と C / C++ コンパイラが必要です。Debian / Ubuntu では `build-essential`、`libffi-dev`、使用する Python の開発用ヘッダーを用意してください。CI では CPython と PyPy のそれぞれの仮想環境で拡張をビルドします。

リポジトリのルートから実行します。

```bash
python -m pip install -r requirements-cffi.txt
python -m benchkit build --source cffi
export PYTHONPATH="$(python -m benchkit build --source cffi --print-path)${PYTHONPATH:+:$PYTHONPATH}"
```

最後のコマンドは、拡張モジュールのディレクトリを `PYTHONPATH` に追加します。PyPy では上の `python` を `pypy3` または PyPy の仮想環境の Python に置き換えてください。`requirements-cffi.txt` は PyPy 同梱の CFFI とそのバックエンドの組み合わせを維持します。ベンチマークからの利用ではハーネスが自動的にビルドし、読み込みパスを設定します。ビルド済みの拡張は Python の処理系・バージョン・プラットフォームに依存します。CPython 用のファイルを PyPy で使い回すことはできません。

## API

```python
from acl_cffi import dsu, fenwick_tree, convolution998244353

with dsu(5) as graph:
    graph.merge(0, 1)
    assert graph.same(0, 1)
    assert graph.size(0) == 2

with fenwick_tree(5) as tree:
    tree.add(2, 10)
    assert tree.sum(1, 4) == 10

assert convolution998244353([1, 2], [3, 4]) == [3, 10, 8]
```

| API | 内容 |
| --- | --- |
| `dsu(n)` | Union-Find |
| `ordered_set()` | 部分木サイズ付き AVL 木で非負整数の集合を管理。`add` / `discard` / `kth`（1始まり）/ `count_leq` / `le` / `ge` |
| `fenwick_tree(n)` | 点加算・半開区間 `[l, r)` の和 |
| `scc_graph(n)` | 強連結成分分解 |
| `two_sat(n)` | 2-SAT |
| `mf_graph(n)` | 最大流 |
| `mcf_graph(n)` | 最小費用流 |
| `convolution998244353(a, b)` | 法 998244353 の畳み込み |
| `crt(remainders, moduli)` | 中国剰余定理 |
| `crt_many(cases)` | 4合同式ずつの CRT をまとめて処理 |
| `floor_sum(n, m, a, b)` | `sum((a * i + b) // m for i in range(n))` |
| `suffix_array(s)` | 接尾辞配列 |
| `lcp_array(s, sa)` | 接尾辞配列に対応する隣接 LCP |
| `z_algorithm(s)` | Z 配列 |

`segtree` と `lazysegtree` は実装していません。任意の Python 演算を C++ 側に渡す抽象化は今回の対象外です。
`ordered_set` は ACL のバインディングではなく、このリポジトリに追加した C++ AVL 木です。存在しない k 番目や前後要素は `-1` を返します。Library Checker の [比較方法](../docs/ordered_set.md) も参照してください。

グラフ・木のインスタンスは `with` または `close()` でネイティブ領域を解放できます。`close()` は繰り返し呼び出せます。解放後の操作は `RuntimeError` になります。明示的に解放しなかった場合も CFFI のファイナライザで解放されますが、特に PyPy では GC の実行まで遅れるため、繰り返し作成する処理では `with` を使ってください。

## 入力と範囲

- 頂点数・添字・配列長は C++ ACL の `int` の範囲に制限されます。添字・区間・容量などの不正な引数はネイティブ処理を実行する前に検査します。
- 容量、費用、Fenwick Tree の値、数論・畳み込みの整数入力は符号付き 64 bit 整数です。Python の任意精度整数をそのまま扱えるわけではありません。入力が範囲を超える場合は `OverflowError` になります。
- Fenwick Tree のサイズは `n < 2**30` に制限しています。内部合計は広い整数型で保持し、問い合わせ結果が符号付き 64 bit を超える場合は `OverflowError` になります。CRT の最小公倍数、`floor_sum` の結果、最小費用流の合計費用が範囲を超える場合も `OverflowError` になります。
- 最大流の容量、最小費用流の容量・辺費用は非負です。最小費用流への負の辺費用は受け付けません。`mcf_graph.flow()` は同じインスタンスで 1 回だけ呼べます。`slope()` は未実装です。内部演算の安全性のため、全辺の `capacity * cost` の合計は `2**127 - 1` 以下に制限しています。
- 畳み込みは法 998244353 専用です。負の入力も法で正規化されます。
- `str` は Unicode コードポイント、`bytes` はバイト列として扱います。返る添字や LCP 長もその単位です。符号付き 32 bit 整数列も使用できます。
- `floor_sum` の範囲は `0 <= n < 2**32`、`1 <= m < 2**32` です。`a` と `b` は負数も使用できます。
- `crt` で合同式が両立しない場合は `(0, 0)`、空の合同式は `(0, 1)` を返します。法は正数にしてください。

## ベンチマークで測る範囲

各比較フォルダの `implementations/cffi.py` がこの API を使用します。DSU の `merge`、Fenwick Tree の `add`、グラフの `add_edge` などは、他の Python 実装と同様に Python のループから 1 操作ずつ呼び出します。計測には Python / CFFI 間の呼び出しとデータ変換が含まれます。入力生成・ネイティブ拡張のコンパイルは計測時間に含まれません。
CRT は1組ずつ呼び出す方式を保ったまま、4つの合同式の場合は一度の CFFI 呼び出しで整数を渡し、C++ 側の一時ベクトルを作らずに併合します。
CRT・DSU・Fenwick Tree・SCC の `cffi_batch.py` は、入力を CFFI 配列へ変換してから一度に渡します。DSU と Fenwick Tree は `process(operations)`、SCC は `add_edges(edges)`、CRT は `crt_many(cases)` を使います。操作順と結果の順序は操作単位の API と同じです。バッチ系列はデータ変換と C++ 側の処理を計測に含みますが、CFFI 呼び出し回数が異なるため操作単位の系列と区別して表示します。

比較には CFFI の呼び出し方式に加え、ACL のバージョン、入力チェック、数値型の違いも含まれます。Python から各実装の API を使う際の実行時間として比較してください。

```bash
python -m benchkit run
python -m benchkit report --results results --output site
```

## 検証

独立した小規模の全探索・単純実装と比較するテストを用意しています。ビルド先のディレクトリを `PYTHONPATH` に追加した状態で実行します。

```bash
ACL_CFFI_REQUIRE_NATIVE=1 python -m unittest discover -s tests -p test_acl_cffi.py -v
```

`ACL_CFFI_REQUIRE_NATIVE=1` は未ビルドをテスト失敗として扱います。通常の全体テストでは未ビルド時にこのテストクラスだけをスキップできます。CI は両処理系でビルドした後、この指定を付けて検証します。
