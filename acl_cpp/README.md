# C++ ACL（参考用）

公式 AtCoder Library を C++17 の独立したプログラムで実行し、PyPy のグラフに灰色の破線で表示します。全14ケースが対象です。ACL のリビジョンは `sources.lock.json` の `cpp` に固定し、CFFI / HPy と同じリビジョンを使います。

```bash
# PyPy の既存結果を保持して、参考系列を追加・更新します。
.venv-cpython/bin/python -m benchkit cpp-reference --results results
.venv-cpython/bin/python -m benchkit report --results results --output site

# 今回のローカル計測結果に追加する場合
.venv-cpython/bin/python -m benchkit cpp-reference --results .cache/local-benchmark-4s/results
```

`--case dsu` でケースを選択し、`--force` で参考系列を再計測できます。保存された PyPy のサイズ・seed・ウォームアップ・サンプル数を使います。結果の CPU・OS が現在の環境と異なる場合は追加を拒否します。同じ機種であることは確認しますが、測定日時やマシンの負荷の差はなくせません。

計測にはデータ構造の初期化、操作ループ、C++ の戻り値作成・破棄を含めます。SCC の出力の整列や 2-SAT の解の検査も含みます。入力は既存の `workload.py` で生成し、各サイズを独立した子プロセスで実行します。入力の読み取り後に `std::chrono::steady_clock` で測定し、結果の JSON 出力は測定後に行います。

**参考用です。** Python との値変換、プロセス起動、入出力、入力生成、事前の正解チェックは計測値に含みません。操作ループも C++ 内で動くため、Python から呼び出す CFFI / HPy とは条件が異なります。現在のワークロードに合わせ、整数は主に64ビット、文字列は ASCII を使用します。Python バインディングと同等の型・範囲チェックや任意精度整数の処理は行いません。

各子プロセスの上限は保存結果の `timeout`（通常4秒）です。入力の受け渡し、事前実行、ウォームアップ、全サンプル、結果の出力までを含めて打ち切ります。親 Python プロセスでの入力生成・エンコードやビルドはこの上限に含みません。タイムアウトしたサイズは別途記録し、グラフから除外して後続サイズを計測します。

既存の小さい入力の独立した正解データで検証し、計測後には同じサイズの保存済み Python 全実装との出力一致も確認します。既存の測定値は変更せず、PyPy の JSON の `references` にサンプル、入力・出力のハッシュ、コンパイラ、最適化オプション、ACL の SHA、計測日時を記録します。

GCC または Clang と Git が必要です。標準のビルドオプションは `-std=c++17 -O3 -DNDEBUG -march=native` です。`CXX`、`CPPFLAGS`、`CXXFLAGS`、`LDFLAGS` も反映し、環境とコードを含むハッシュでビルドと参考値を再利用します。バイナリは `.cache/cpp-reference/` に保存します。

ネイティブ部分の正解検査・実測・タイムアウトのテスト:

```bash
binary=$(.venv-cpython/bin/python -c 'from benchkit.cpp_reference import build; print(build()[0])')
ACL_CPP_REFERENCE_BINARY="$binary" .venv-cpython/bin/python -m unittest discover -s tests -p test_cpp_reference.py
```
