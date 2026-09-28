# Ordered Set の計測

[Library Checker Ordered Set](https://judge.yosupo.jp/problem/ordered_set) の[公式生成器](https://github.com/yosupo06/library-checker-problems/tree/master/data_structure/ordered_set)で37入力（`example_00`～`01`、`small_00`～`02`、`max_random_00`～`31`）と公式正解を取得します。生成器のリビジョンは `sources.lock.json` に固定し、`hash.json` に記載された各入力・正解の SHA-256 と照合します。初回生成でハッシュが合わない場合は、該当ケースのみ上流の生成器・正解プログラムで再生成して一致を確認します。

最大ケースは `N, Q` がそれぞれ最大500,000です。37入力はそれぞれ異なる負荷なので折れ線は表示しません。全ケース中で最も遅い中央値とその公式ケース名を実装ごとに棒グラフへ表示します。60秒で打ち切られた入力がある実装の棒は表示しません。

比較する実装は次の5系列です。

| 系列 | 実装 |
| --- | --- |
| harurun (`library_codex`) | `ordered_set.TreapSet.TreapSet` |
| harurun (`library`) | `SegTree.BinaryTrie.BinaryTrie`（非負整数を30ビットで管理） |
| tatyam | `tatyam-prime/SortedSet` の `SortedSet.py` |
| sortedcontainers | `sortedcontainers.SortedSet` |
| CFFI | 自作の部分木サイズ付き AVL 木。Python 側から1操作ずつ呼び出す |

初期構築と全クエリ（挿入、削除、1始まりの k 番目、`x` 以下の個数、前後要素の検索）を計測します。入力生成、CFFI のビルド、各ケースの公式正解との照合は計測時間から除外します。全実装は同じ入力と5回のサンプルを使います。取得元と SHA は `sources.lock.json` に記録し、上流のコードを再配布しません。

```bash
python -m pip install -r requirements-cffi.txt -r requirements-ordered-set.txt
python -m benchkit run --case ordered_set --quick
python -m benchkit run --case ordered_set
```

初回実行はテストケースを生成・検証します。既存の C++ ACL には Ordered Set がないため、このケースに C++ 参考系列はありません。

すべての実装で従来どおり Python 側からクエリを1件ずつ呼び出します。CFFI 版の `kth`・`le`・`ge` はネイティブ関数から値を直接受け取り、クエリごとの戻り値領域の確保を省きます。ループで使うメソッド参照は開始時に取得します。公開 API と CFFI 呼び出し回数は従来と同じです。ローカル CPython での単発計測は `max_random_00` が約0.21秒から約0.18秒、`max_random_31` が約0.66秒から約0.60秒でした。公開ベンチマークの PyPy での値は CI の再計測結果を参照してください。
