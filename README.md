# Python ACL Benchmark

Python 向け AtCoder Library を **CPython / PyPy × 入力サイズ** で比較するリポジトリです。
比較フォルダに実装を追加して push すると、GitHub Actions が影響のある比較だけを再計測し、SVG グラフと HTML レポートを更新します。

比較対象:

- [not522/ac-library-python](https://github.com/not522/ac-library-python)
- [shakayami/ACL-for-python](https://github.com/shakayami/ACL-for-python)
- [tatyam-prime/acl-cpp-python](https://github.com/tatyam-prime/acl-cpp-python)
- 各フォルダに追加した自作実装

外部ライブラリの取得先と commit SHA は [sources.lock.json](sources.lock.json) に固定しています。
上流のコードは `.cache/` に取得し、このリポジトリには再配布しません。各ライブラリのライセンスは上流の LICENSE を参照してください。

## GitHub で使う

1. GitHub に空のリポジトリを作成し、このディレクトリを commit / push します。
2. リポジトリの **Settings → Pages → Build and deployment → Source** を **GitHub Actions** に設定します。
3. **Actions → ACL benchmarks** を開きます。push で自動実行され、**Run workflow** からも実行できます。
4. 完了すると `https://<owner>.github.io/<repository>/` にグラフが公開されます。実際の URL は `deploy` ジョブの `github-pages` 環境にも表示されます。

最初の push の例です。URL は作成したリポジトリに置き換えてください。

```bash
git add .
git commit -m "Add Python ACL benchmarks"
git remote add origin https://github.com/<owner>/<repository>.git
git push -u origin main
```

結果は自動作成される **`gh-pages` ブランチ** にも保存されます。GitHub 上でそのブランチの `README.md` を開くだけで SVG グラフを閲覧できます。`data/` には全サンプルを含む JSON が残ります。
Pages の設定をまだ行っていなくても、計測と `gh-pages` への保存が成功していれば、ブランチ上のグラフと Actions の `benchmark-site` artifact を利用できます。

デフォルトブランチだけが結果を公開します。Pull Request / その他のブランチでは計測・グラフ生成まで実行し、`benchmark-results` / `benchmark-site` artifact として 14 日間保存します。
CI が `gh-pages` に書き込めるよう、組織のポリシーでも workflow の `contents: write` を許可してください。
公開時の競合は通常の Git push で検出し、古い実行で新しい結果を上書きしません。

## 比較する内容

| フォルダ | 処理 | not522 | shakayami | tatyam |
| --- | --- | :---: | :---: | :---: |
| `dsu` | Union-Find の merge / same | ✓ | ✓ | ✓ |
| `fenwicktree` | 点加算 / 区間和 | ✓ | ✓ | ✓ |
| `segtree` | 点更新 / 区間和 | ✓ | ✓ | — |
| `lazysegtree` | 区間加算 / 区間和 | ✓ | ✓ | — |
| `convolution` | mod 998244353 の畳み込み | ✓ | ✓ | ✓ |
| `suffix_array` | 接尾辞配列 | ✓ | ✓ | ✓ |
| `lcp_array` | LCP 配列 | ✓ | ✓ | ✓ |
| `z_algorithm` | Z-algorithm | ✓ | ✓ | ✓ |
| `scc` | 強連結成分分解 | ✓ | ✓ | ✓ |
| `two_sat` | 2-SAT | ✓ | ✓ | ✓ |
| `maxflow` | 最大流 | ✓ | ✓ | ✓ |
| `mincostflow` | 最小費用流 | ✓ | ✓ | ✓ |
| `floor_sum` | floor_sum の反復 | ✓ | ✓ | ✓ |
| `crt` | 中国剰余定理の反復 | ✓ | ✓ | ✓ |

固定した tatyam 版には Segment Tree / Lazy Segment Tree の Python API がないため、この 2 ケースは 2 実装で比較します。
グラフの `n` の意味、操作回数、計測に含める処理は各 `case.json` の `description` と `workload.py` に記載しています。
例えば DSU は `n` 頂点と `4n` クエリ、畳み込みはそれぞれ長さ `n` の配列です。グラフはこのワークロードに対する結果です。

線形・準線形の処理を比較する 12 ケース（最大流・最小費用流を除く）は、**`n = 500,000` まで**計測します。
通常は `128, 512, 2048, 8192, 32768, 131072, 500000`、畳み込みは `64, 256, 1024, 4096, 16384, 65536, 131072, 500000` です。
`floor_sum` / `crt` の `n` は固定範囲の引数に対する呼び出し回数です。最大流は従来どおり `n = 2,048`、最小費用流は `n = 128` まで計測します。
大規模な CPython の畳み込み・遅延セグメント木では反復計測に時間がかかるため、実装 × 入力サイズの時間上限は最大 2,400 秒、CI の計測ジョブ全体は 180 分に設定しています。

SCC は最大 32 頂点の強連結成分を持つグラフ、2-SAT は最大 32 変数の独立ブロックからなる充足可能な式を使います。
2-SAT の充足不能な入力は計測前の正解チェックで検証します。最大流・最小費用流は容量 1 の疎な二部グラフで、始点・終点を含めた総頂点数は `2n+2`、重複辺も含みます。
一般の大きな強連結成分、充足不能な式、任意の容量を持つネットワークを比較する場合は、別の比較フォルダにワークロードを追加してください。

## 実装を追加する

同じ問題を解くファイルを `benchmarks/<比較名>/implementations/` に追加します。
`_` から始まるファイルは補助モジュールとして扱い、計測対象にはしません。

```text
benchmarks/
  dsu/
    case.json
    workload.py
    implementations/
      not522.py
      shakayami.py
      tatyam.py
      my_dsu.py          # ここに追加
```

動く自作 DSU の例を [examples/custom_dsu.py](examples/custom_dsu.py) に用意しています。

```bash
cp examples/custom_dsu.py benchmarks/dsu/implementations/my_dsu.py
python3 -m benchkit run --case dsu
pypy3 -m benchkit run --case dsu
python3 -m benchkit report
```

`implementations/*.py` は次のインターフェースを持たせます。入力と出力の形式はその比較の `workload.py` および既存の実装に合わせてください。

```python
LABEL = "My implementation"  # 省略するとファイル名
# SOURCE = "not522"         # sources.lock.json の取得先を使うときだけ指定

def run(data):
    # 毎回ここで新しいデータ構造を作り、処理結果を返す
    # data を変更せず、同じ入力には常に同じ出力を返す
    ...
```

`LABEL` / `SOURCE` は文字列リテラルにします。入力と戻り値は JSON 化可能な値にしてください。
比較フォルダと `implementations/` は import の探索対象になるので、補助コードを同じフォルダに配置できます。
戻り値はケース全体で共通にし、例えば DSU は `same` の真偽値リストを返します。
出力順が一意でない場合はソートなどで正規化します。その正規化の時間も `run()` に含まれます。

外部リポジトリを新しく使う場合は `sources.lock.json` に URL と **40 桁の commit SHA** を追加し、アダプタの `SOURCE` にそのキーを書きます。
通常の Python コードならチェックアウトが import 対象になります。ビルドが必要なら `"install": "pip"` を指定すると、実行中のインタープリタで専用キャッシュへインストールします。必要なビルド依存は `build_dependencies` で固定できます。
追加の実行時依存を自動でインストールする機構はありません。必要なら CI のセットアップ手順にも明示してください。

## 比較する処理を追加する

[examples/new_case/](examples/new_case/) を `benchmarks/<新しい名前>/` にコピーします。ランナーや CI の編集は不要です。

- `case.json`: タイトル、説明、入力サイズ、反復回数など。
- `workload.py`: `make_input(size, seed)` で入力を生成し、`validation_cases()` で `(入力, 期待値)` のリストを返す。
- `implementations/*.py`: 共通の `run(data)` を持つ実装を 1 つ以上置く。

期待値は対象ライブラリに依存しない単純な実装や手計算から作成してください。
小さい検証用入力には多少遅い総当たりも使えます。`validation_cases()` と入力生成は計測時間に含みません。

設定例:

```json
{
  "title": "DSU / Union-Find",
  "description": "n 頂点・4n 回の merge / same。初期化を含む。",
  "sizes": [128, 512, 2048, 8192, 32768, 131072, 500000],
  "seed": 42,
  "repeat": 5,
  "warmup": 3,
  "warmup_seconds": 0.25,
  "sample_seconds": 0.025,
  "timeout": 300
}
```

`sizes` は昇順の正整数です。`warmup` と `warmup_seconds` は両方の条件を満たすまでウォームアップします。
`sample_seconds` を目安に 1 サンプル内の呼び出し回数を校正し、**1 回の `run(data)` あたりの秒数**を保存します。
`timeout` は実装 × 入力サイズごとのプロセス全体に対する秒数です。

## 何が再計測されるか

| 変更 | 再計測 |
| --- | --- |
| 実装の追加・修正・削除 | その比較の全実装・全サイズ |
| `case.json` / `workload.py` / 比較内の補助ファイル | その比較 |
| `sources.lock.json` の revision / ビルド設定 | そのソースを利用する比較 |
| 計測基盤、workflow、Python / PyPy、CPU、runner image | 影響する全比較 |
| `benchkit/report.py` / ルート README | 計測を再利用してレポートを生成 |
| 比較フォルダの削除 | 保存結果とグラフを削除 |

入力・コード・ソースの SHA・設定・環境をハッシュ化して判定します。Git の直前の 1 commit との差分に依存しないため、途中で CI が失敗した場合も取りこぼしません。
1 つの実装を変更した場合も、その比較の全実装を同じマシンで測り直します。未変更の比較の結果・計測日時は保持します。
GitHub runner の CPU や image が変わったときは、コード変更がなくても再計測します。

全件を測り直すには **Run workflow → full** を有効にするか、ローカルで `--force` を指定します。
上流の最新版へ追従するには、`sources.lock.json` の SHA を更新して push してください。上流の変更だけではこのリポジトリの CI は起動しません。

## ローカルで実行する

必要なものは Python 3.10 以上、PyPy、Git です。tatyam 版のビルドには C++ コンパイラ、CMake、Python の開発ヘッダとネットワーク接続が必要です。
CI では Ubuntu 24.04、CPython 3.11、PyPy 3.11 / 7.3.20 を使用します。それぞれ独立した仮想環境を作り、その中で pip を固定します。PyPy 同梱 CFFI の依存を満たすため、PyPy 側には `pycparser` も固定してインストールします。
ランナーとレポート自体は Python 標準ライブラリのみで動作します。
Ubuntu の OS パッケージ版で `ensurepip is not available` と表示される場合は、`python3-venv` / `pypy3-venv` も必要です。GitHub Actions の Python には含まれています。

```bash
# それぞれのランタイム用に独立した環境を作成します。
python3 -m venv .venv-cpython
pypy3 -m venv .venv-pypy
.venv-cpython/bin/python -m pip install --upgrade 'pip==25.3'
.venv-pypy/bin/python -m pip install --upgrade 'pip==25.3' 'pycparser==2.23'
.venv-cpython/bin/python -m pip --version
.venv-pypy/bin/python -m pip --version
.venv-cpython/bin/python -m pip check
.venv-pypy/bin/python -m pip check

.venv-cpython/bin/python -m benchkit list

# 動作確認: 各比較の最小サイズだけを短時間で測る
.venv-cpython/bin/python -m benchkit run --quick
.venv-pypy/bin/python -m benchkit run --quick

# 通常の計測: 並列にせず順番に実行する
.venv-cpython/bin/python -m benchkit run
.venv-pypy/bin/python -m benchkit run
.venv-cpython/bin/python -m benchkit report --results results --output site

# site/index.html を直接開くか、ローカルサーバーで閲覧
.venv-cpython/bin/python -m http.server 8000 --directory site
```

`--case dsu --case convolution` のように複数指定も可能です。
`--quick` の結果はレポートで動作確認用と表示し、通常の計測では再利用しません。
ソースとネイティブビルドは `.cache/`、計測結果は `results/`、グラフは `site/` に作成します。いずれも Git の管理対象外です。
`.cache/` 内のコードは直接編集せず、変更したい実装は比較フォルダに置いてください。

## 計測方法と読み方

- CPython / PyPy は **同じ GitHub runner 上で順番に** 実行します。各実装・各サイズには独立したプロセスを使います。
- 計測対象は `run(data)` です。データ構造の初期化、API 呼び出し、Python と C++ の値変換、戻り値作成を含みます。import、ビルド、入力生成、計測前の正解チェック、プロセス起動は含みません。2-SAT では戻り値を共通化するため、得た解が全節を満たすかの確認も `run()` 内で行い、その時間を含みます。
- 同じ seed の入力を使い、小さい入力の独立した正解チェックと、全計測サイズでの実装間の出力チェックを行います。同じコード・設定の結果が揃ったランタイム間でも出力を照合します。
- PyPy の JIT ウォームアップを行い、各サンプルの前に `gc.collect()` を実行します。計測中は GC を有効にしたままです。ウォームアップが十分かはケースによるため、必要に応じて設定を増やしてください。
- グラフはケースごとに **CPython 用と PyPy 用を別々に** 生成し、それぞれの計測値に合わせて軸の範囲を調整します。中央値を線で、観測した最小値から最大値を帯とひげで表示します。帯は信頼区間ではありません。通常は両軸対数で、小さいほど高速です。
- CPU、OS、Python のビルド、ライブラリ SHA、計測日時、全サンプル、バッチ回数を JSON に記録します。
- GitHub の共有 runner には実行ごとの揺らぎがあります。小さな差を厳密な順位とみなさず、必要なら `--force` で再計測してください。CI 環境の結果であり、AtCoder の実行環境そのものの速度ではありません。

正解不一致、import / ビルド失敗、タイムアウトはエラーにし、その実行の結果を公開しません。
成功した比較の結果は一時ファイルから置き換え、失敗時に不完全な JSON を保存しないようにしています。

## 開発時の確認

```bash
python3 -m unittest discover -s tests -v
```

差分計測、実装追加・削除、正解不一致、タイムアウト、入力変更検出、グラフ生成、公開結果の復元・競合を確認します。
公開処理のテストは一時ディレクトリ内の Git リポジトリを使い、GitHub には書き込みません。

GitHub Pages の設定については [GitHub 公式ドキュメント](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages) も参照してください。
