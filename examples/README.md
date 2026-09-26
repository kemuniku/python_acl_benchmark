# 比較対象を追加する例

リポジトリのルートで実行します。

## 既存の DSU 比較に実装を追加

```sh
cp examples/custom_dsu.py benchmarks/dsu/implementations/local.py
python3 -m benchkit run --case dsu
python3 -m benchkit report
```

`local.py` の `LABEL` と実装を編集してください。外部ソースを必要としない実装では `SOURCE` を省略します。同じフォルダへ別名の `.py` ファイルを追加すると比較対象も増えます。PyPy でも計測するには、同じ `run` コマンドを `pypy3` で実行します。

## 新しい比較ケースを追加

```sh
cp -r examples/new_case benchmarks/prefix_sum
python3 -m benchkit run --case prefix_sum
python3 -m benchkit report
```

この例は累積和を比較します。`case.json` に入力サイズや計測回数、`workload.py` に入力生成と正解検証、`implementations/*.py` に各実装を定義します。入力生成と正解検証は計測の対象外です。

`make_input(n, seed)` は同じ引数から同じ入力を生成します。`validation_cases()` は `(入力, 期待する出力)` の組を返し、期待値は比較対象の実装に依存せず用意してください。各実装の `run(data)` は入力を変更せず、呼び出すたびに同じ結果を返します。入力と出力には JSON に変換できる値を使います。

先に短い動作確認を行う場合は、通常の結果とは別の保存先を指定できます。

```sh
python3 -m benchkit run --case prefix_sum --quick --results /tmp/acl-example-results
python3 -m benchkit report --results /tmp/acl-example-results --output /tmp/acl-example-site
```

動作確認用の結果はレポート上で `quick` と表示されます。
