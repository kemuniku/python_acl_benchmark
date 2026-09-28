# Python ACL ベンチマーク

各実装を PyPy で比較します。グラフはランタイムごとに分け、軸の範囲を個別に調整します。グラフは小さいほど高速です。線は中央値、帯・ひげは観測された最小値から最大値です。正の値には対数軸を使い、0 を含む軸には線形軸を使います。最大入力サイズの棒グラフにはタイムアウトした系列を表示しません。

[HTML レポート](index.html) · [生データ](data/)

## Convolution \(mod 998244353\)

長さ n の 2 配列の畳み込み。FFT インスタンスの初期化・Python/C++ 間の変換も含む。

### PyPy 3.11.13

![Convolution \(mod 998244353\) / PyPy 3.11.13](charts/convolution/pypy.svg)

#### 最大入力サイズ n=500000（タイムアウトは除外）

![Convolution \(mod 998244353\) / PyPy 3.11.13 最大ケース](charts/convolution/pypy-max.svg)

[折れ線 SVG を保存](charts/convolution/pypy.svg) · [最大ケース SVG を保存](charts/convolution/pypy-max.svg)

タイムアウト（グラフから除外）: hpy\_universal n=500000, not522 n=65536, not522 n=131072, not522 n=500000, tatyam n=500000

**参考用：C++単体の実行時間（Pythonとの値変換・プロセス起動・入出力を除外）。**

- C++ ACL（参考用）: 2026-09-28T03:41:17.086172+00:00; g++ \(Ubuntu 13.3.0-6ubuntu2~24.04.1\) 13.3.0 \| -std=c++17 -O3 -DNDEBUG -march=native; timeout n=\[\]

### 計測情報

| ランタイム | 計測日時 | CPU | repeat / warmup / seed | JSON |
| --- | --- | --- | --- | --- |
| PyPy 3.11.13 | 2026-09-28T03:31:17.268470+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/pypy/convolution.json) |

- PyPy 3.11.13: commit `16f32e4c653a3a37e76b0ba0c00dbad7363734ec`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[64, 256, 1024, 4096, 16384, 65536, 131072, 500000\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.13 \(413c9b7f57f5, Jul 03 2025, 18:03:56\) \[PyPy 7.3.20 with GCC 10.2.1 20210130 \(Red Hat 10.2.1-11\)\]
  - cffi: https://github.com/atcoder/ac-library.git @ `864245a00b00dd008d1abfdc239618fdb7d139da`
  - harurun: https://github.com/lif4635/harurun-s-library.git @ `7c94b7bb0c9d4f6ed0ffa44853febee1e7971ff9`
  - hpy: https://github.com/atcoder/ac-library.git @ `864245a00b00dd008d1abfdc239618fdb7d139da`
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`
  - tatyam: https://github.com/tatyam-prime/acl-cpp-python.git @ `b677fa437bdc1b0b7a4512d360de065cdca5778c`

## Chinese remainder theorem

n 組の合同式を処理。各組は 4 個の法、最小公倍数を 64 bit 以内に固定。

### PyPy 3.11.13

![Chinese remainder theorem / PyPy 3.11.13](charts/crt/pypy.svg)

#### 最大入力サイズ n=500000（タイムアウトは除外）

![Chinese remainder theorem / PyPy 3.11.13 最大ケース](charts/crt/pypy-max.svg)

[折れ線 SVG を保存](charts/crt/pypy.svg) · [最大ケース SVG を保存](charts/crt/pypy-max.svg)

タイムアウト（グラフから除外）: cffi n=500000, cffi\_batch n=500000, harurun n=500000, hpy\_universal n=131072, hpy\_universal n=500000, not522 n=500000, shakayami n=500000, tatyam n=131072, tatyam n=500000

**参考用：C++単体の実行時間（Pythonとの値変換・プロセス起動・入出力を除外）。**

- C++ ACL（参考用）: 2026-09-28T03:41:23.877648+00:00; g++ \(Ubuntu 13.3.0-6ubuntu2~24.04.1\) 13.3.0 \| -std=c++17 -O3 -DNDEBUG -march=native; timeout n=\[\]

### 計測情報

| ランタイム | 計測日時 | CPU | repeat / warmup / seed | JSON |
| --- | --- | --- | --- | --- |
| PyPy 3.11.13 | 2026-09-28T03:32:34.436593+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/pypy/crt.json) |

- PyPy 3.11.13: commit `16f32e4c653a3a37e76b0ba0c00dbad7363734ec`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[128, 512, 2048, 8192, 32768, 131072, 500000\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.13 \(413c9b7f57f5, Jul 03 2025, 18:03:56\) \[PyPy 7.3.20 with GCC 10.2.1 20210130 \(Red Hat 10.2.1-11\)\]
  - cffi: https://github.com/atcoder/ac-library.git @ `864245a00b00dd008d1abfdc239618fdb7d139da`
  - harurun: https://github.com/lif4635/harurun-s-library.git @ `7c94b7bb0c9d4f6ed0ffa44853febee1e7971ff9`
  - hpy: https://github.com/atcoder/ac-library.git @ `864245a00b00dd008d1abfdc239618fdb7d139da`
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`
  - tatyam: https://github.com/tatyam-prime/acl-cpp-python.git @ `b677fa437bdc1b0b7a4512d360de065cdca5778c`

## DSU / Union-Find

n 頂点・4n 回の merge / same。初期化と全クエリを計測。

### PyPy 3.11.13

![DSU / Union-Find / PyPy 3.11.13](charts/dsu/pypy.svg)

#### 最大入力サイズ n=500000（タイムアウトは除外）

![DSU / Union-Find / PyPy 3.11.13 最大ケース](charts/dsu/pypy-max.svg)

[折れ線 SVG を保存](charts/dsu/pypy.svg) · [最大ケース SVG を保存](charts/dsu/pypy-max.svg)

タイムアウト（グラフから除外）: cffi n=500000, cffi\_batch n=500000, harurun n=500000, hpy\_universal n=500000, not522 n=500000, shakayami n=500000, tatyam n=131072, tatyam n=500000

**参考用：C++単体の実行時間（Pythonとの値変換・プロセス起動・入出力を除外）。**

- C++ ACL（参考用）: 2026-09-28T03:41:29.896065+00:00; g++ \(Ubuntu 13.3.0-6ubuntu2~24.04.1\) 13.3.0 \| -std=c++17 -O3 -DNDEBUG -march=native; timeout n=\[\]

### 計測情報

| ランタイム | 計測日時 | CPU | repeat / warmup / seed | JSON |
| --- | --- | --- | --- | --- |
| PyPy 3.11.13 | 2026-09-28T03:33:49.422647+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/pypy/dsu.json) |

- PyPy 3.11.13: commit `16f32e4c653a3a37e76b0ba0c00dbad7363734ec`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[128, 512, 2048, 8192, 32768, 131072, 500000\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.13 \(413c9b7f57f5, Jul 03 2025, 18:03:56\) \[PyPy 7.3.20 with GCC 10.2.1 20210130 \(Red Hat 10.2.1-11\)\]
  - cffi: https://github.com/atcoder/ac-library.git @ `864245a00b00dd008d1abfdc239618fdb7d139da`
  - harurun: https://github.com/lif4635/harurun-s-library.git @ `7c94b7bb0c9d4f6ed0ffa44853febee1e7971ff9`
  - hpy: https://github.com/atcoder/ac-library.git @ `864245a00b00dd008d1abfdc239618fdb7d139da`
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`
  - tatyam: https://github.com/tatyam-prime/acl-cpp-python.git @ `b677fa437bdc1b0b7a4512d360de065cdca5778c`

## Fenwick tree

n 要素・4n 回の一点加算 / 区間和。ゼロ初期化と全クエリを計測。

### PyPy 3.11.13

![Fenwick tree / PyPy 3.11.13](charts/fenwicktree/pypy.svg)

#### 最大入力サイズ n=500000（タイムアウトは除外）

![Fenwick tree / PyPy 3.11.13 最大ケース](charts/fenwicktree/pypy-max.svg)

[折れ線 SVG を保存](charts/fenwicktree/pypy.svg) · [最大ケース SVG を保存](charts/fenwicktree/pypy-max.svg)

タイムアウト（グラフから除外）: cffi n=500000, cffi\_batch n=500000, harurun n=500000, hpy\_universal n=500000, not522 n=500000, shakayami n=500000, tatyam n=131072, tatyam n=500000

**参考用：C++単体の実行時間（Pythonとの値変換・プロセス起動・入出力を除外）。**

- C++ ACL（参考用）: 2026-09-28T03:41:36.566195+00:00; g++ \(Ubuntu 13.3.0-6ubuntu2~24.04.1\) 13.3.0 \| -std=c++17 -O3 -DNDEBUG -march=native; timeout n=\[\]

### 計測情報

| ランタイム | 計測日時 | CPU | repeat / warmup / seed | JSON |
| --- | --- | --- | --- | --- |
| PyPy 3.11.13 | 2026-09-28T03:35:05.090278+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/pypy/fenwicktree.json) |

- PyPy 3.11.13: commit `16f32e4c653a3a37e76b0ba0c00dbad7363734ec`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[128, 512, 2048, 8192, 32768, 131072, 500000\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.13 \(413c9b7f57f5, Jul 03 2025, 18:03:56\) \[PyPy 7.3.20 with GCC 10.2.1 20210130 \(Red Hat 10.2.1-11\)\]
  - cffi: https://github.com/atcoder/ac-library.git @ `864245a00b00dd008d1abfdc239618fdb7d139da`
  - harurun: https://github.com/lif4635/harurun-s-library.git @ `7c94b7bb0c9d4f6ed0ffa44853febee1e7971ff9`
  - hpy: https://github.com/atcoder/ac-library.git @ `864245a00b00dd008d1abfdc239618fdb7d139da`
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`
  - tatyam: https://github.com/tatyam-prime/acl-cpp-python.git @ `b677fa437bdc1b0b7a4512d360de065cdca5778c`

## Floor sum

n 回の floor\_sum 呼び出し。引数 n,m は 1..999999、a,b は 0..999999。結果は符号付き 64 bit 以内。

### PyPy 3.11.13

![Floor sum / PyPy 3.11.13](charts/floor_sum/pypy.svg)

#### 最大入力サイズ n=500000（タイムアウトは除外）

![Floor sum / PyPy 3.11.13 最大ケース](charts/floor_sum/pypy-max.svg)

[折れ線 SVG を保存](charts/floor_sum/pypy.svg) · [最大ケース SVG を保存](charts/floor_sum/pypy-max.svg)

タイムアウト（グラフから除外）: hpy\_universal n=500000, not522 n=500000, tatyam n=500000

**参考用：C++単体の実行時間（Pythonとの値変換・プロセス起動・入出力を除外）。**

- C++ ACL（参考用）: 2026-09-28T03:41:40.822501+00:00; g++ \(Ubuntu 13.3.0-6ubuntu2~24.04.1\) 13.3.0 \| -std=c++17 -O3 -DNDEBUG -march=native; timeout n=\[\]

### 計測情報

| ランタイム | 計測日時 | CPU | repeat / warmup / seed | JSON |
| --- | --- | --- | --- | --- |
| PyPy 3.11.13 | 2026-09-28T03:35:57.281208+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/pypy/floor_sum.json) |

- PyPy 3.11.13: commit `16f32e4c653a3a37e76b0ba0c00dbad7363734ec`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[128, 512, 2048, 8192, 32768, 131072, 500000\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.13 \(413c9b7f57f5, Jul 03 2025, 18:03:56\) \[PyPy 7.3.20 with GCC 10.2.1 20210130 \(Red Hat 10.2.1-11\)\]
  - cffi: https://github.com/atcoder/ac-library.git @ `864245a00b00dd008d1abfdc239618fdb7d139da`
  - harurun: https://github.com/lif4635/harurun-s-library.git @ `7c94b7bb0c9d4f6ed0ffa44853febee1e7971ff9`
  - hpy: https://github.com/atcoder/ac-library.git @ `864245a00b00dd008d1abfdc239618fdb7d139da`
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`
  - tatyam: https://github.com/tatyam-prime/acl-cpp-python.git @ `b677fa437bdc1b0b7a4512d360de065cdca5778c`

## Lazy segment tree

n 要素・2n 回の区間加算 / 区間和。\(合計, 要素数\) を保持し構築も計測。C++ 版には公開 API がないため Python 2 実装を比較。

### PyPy 3.11.13

![Lazy segment tree / PyPy 3.11.13](charts/lazysegtree/pypy.svg)

#### 最大入力サイズ n=500000（タイムアウトは除外）

![Lazy segment tree / PyPy 3.11.13 最大ケース](charts/lazysegtree/pypy-max.svg)

[折れ線 SVG を保存](charts/lazysegtree/pypy.svg) · [最大ケース SVG を保存](charts/lazysegtree/pypy-max.svg)

タイムアウト（グラフから除外）: harurun n=131072, harurun n=500000, not522 n=131072, not522 n=500000, shakayami n=131072, shakayami n=500000

**参考用：C++単体の実行時間（Pythonとの値変換・プロセス起動・入出力を除外）。**

- C++ ACL（参考用）: 2026-09-28T02:11:44.372386+00:00; g++ \(Ubuntu 13.3.0-6ubuntu2~24.04.1\) 13.3.0 \| -std=c++17 -O3 -DNDEBUG -march=native; timeout n=\[\]

### 計測情報

| ランタイム | 計測日時 | CPU | repeat / warmup / seed | JSON |
| --- | --- | --- | --- | --- |
| PyPy 3.11.13 | 2026-09-28T02:05:23.799284+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/pypy/lazysegtree.json) |

- PyPy 3.11.13: commit `792088987107c0a8e973f972c98edf33dc35c2d9`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[128, 512, 2048, 8192, 32768, 131072, 500000\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.13 \(413c9b7f57f5, Jul 03 2025, 18:03:56\) \[PyPy 7.3.20 with GCC 10.2.1 20210130 \(Red Hat 10.2.1-11\)\]
  - harurun: https://github.com/lif4635/harurun-s-library.git @ `7c94b7bb0c9d4f6ed0ffa44853febee1e7971ff9`
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`

## LCP array

長さ n の ASCII 文字列と計測外で生成した suffix array から LCP を計算。

### PyPy 3.11.13

![LCP array / PyPy 3.11.13](charts/lcp_array/pypy.svg)

#### 最大入力サイズ n=500000（タイムアウトは除外）

![LCP array / PyPy 3.11.13 最大ケース](charts/lcp_array/pypy-max.svg)

[折れ線 SVG を保存](charts/lcp_array/pypy.svg) · [最大ケース SVG を保存](charts/lcp_array/pypy-max.svg)

タイムアウト（グラフから除外）: hpy\_universal n=500000, tatyam n=500000

**参考用：C++単体の実行時間（Pythonとの値変換・プロセス起動・入出力を除外）。**

- C++ ACL（参考用）: 2026-09-28T03:41:46.958516+00:00; g++ \(Ubuntu 13.3.0-6ubuntu2~24.04.1\) 13.3.0 \| -std=c++17 -O3 -DNDEBUG -march=native; timeout n=\[\]

### 計測情報

| ランタイム | 計測日時 | CPU | repeat / warmup / seed | JSON |
| --- | --- | --- | --- | --- |
| PyPy 3.11.13 | 2026-09-28T03:36:45.485871+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/pypy/lcp_array.json) |

- PyPy 3.11.13: commit `16f32e4c653a3a37e76b0ba0c00dbad7363734ec`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[128, 512, 2048, 8192, 32768, 131072, 500000\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.13 \(413c9b7f57f5, Jul 03 2025, 18:03:56\) \[PyPy 7.3.20 with GCC 10.2.1 20210130 \(Red Hat 10.2.1-11\)\]
  - cffi: https://github.com/atcoder/ac-library.git @ `864245a00b00dd008d1abfdc239618fdb7d139da`
  - harurun: https://github.com/lif4635/harurun-s-library.git @ `7c94b7bb0c9d4f6ed0ffa44853febee1e7971ff9`
  - hpy: https://github.com/atcoder/ac-library.git @ `864245a00b00dd008d1abfdc239618fdb7d139da`
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`
  - tatyam: https://github.com/tatyam-prime/acl-cpp-python.git @ `b677fa437bdc1b0b7a4512d360de065cdca5778c`

## Maximum flow

左右 n 頂点ずつの疎な二部グラフ。各左頂点から 4 辺。ネットワーク構築と最大流を計測。

### PyPy 3.11.13

![Maximum flow / PyPy 3.11.13](charts/maxflow/pypy.svg)

#### 最大入力サイズ n=2048（タイムアウトは除外）

![Maximum flow / PyPy 3.11.13 最大ケース](charts/maxflow/pypy-max.svg)

[折れ線 SVG を保存](charts/maxflow/pypy.svg) · [最大ケース SVG を保存](charts/maxflow/pypy-max.svg)

タイムアウト（グラフから除外）: shakayami n=2048

**参考用：C++単体の実行時間（Pythonとの値変換・プロセス起動・入出力を除外）。**

- C++ ACL（参考用）: 2026-09-28T03:41:48.834806+00:00; g++ \(Ubuntu 13.3.0-6ubuntu2~24.04.1\) 13.3.0 \| -std=c++17 -O3 -DNDEBUG -march=native; timeout n=\[\]

### 計測情報

| ランタイム | 計測日時 | CPU | repeat / warmup / seed | JSON |
| --- | --- | --- | --- | --- |
| PyPy 3.11.13 | 2026-09-28T03:37:08.364361+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/pypy/maxflow.json) |

- PyPy 3.11.13: commit `16f32e4c653a3a37e76b0ba0c00dbad7363734ec`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[8, 32, 128, 512, 2048\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.13 \(413c9b7f57f5, Jul 03 2025, 18:03:56\) \[PyPy 7.3.20 with GCC 10.2.1 20210130 \(Red Hat 10.2.1-11\)\]
  - cffi: https://github.com/atcoder/ac-library.git @ `864245a00b00dd008d1abfdc239618fdb7d139da`
  - harurun: https://github.com/lif4635/harurun-s-library.git @ `7c94b7bb0c9d4f6ed0ffa44853febee1e7971ff9`
  - hpy: https://github.com/atcoder/ac-library.git @ `864245a00b00dd008d1abfdc239618fdb7d139da`
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`
  - tatyam: https://github.com/tatyam-prime/acl-cpp-python.git @ `b677fa437bdc1b0b7a4512d360de065cdca5778c`

## Minimum-cost flow

左右 n 頂点ずつの二部グラフ。各左頂点から 3 辺、非負コスト。構築と最小費用最大流を計測。

### PyPy 3.11.13

![Minimum-cost flow / PyPy 3.11.13](charts/mincostflow/pypy.svg)

#### 最大入力サイズ n=128（タイムアウトは除外）

![Minimum-cost flow / PyPy 3.11.13 最大ケース](charts/mincostflow/pypy-max.svg)

[折れ線 SVG を保存](charts/mincostflow/pypy.svg) · [最大ケース SVG を保存](charts/mincostflow/pypy-max.svg)

**参考用：C++単体の実行時間（Pythonとの値変換・プロセス起動・入出力を除外）。**

- C++ ACL（参考用）: 2026-09-28T03:41:50.726610+00:00; g++ \(Ubuntu 13.3.0-6ubuntu2~24.04.1\) 13.3.0 \| -std=c++17 -O3 -DNDEBUG -march=native; timeout n=\[\]

### 計測情報

| ランタイム | 計測日時 | CPU | repeat / warmup / seed | JSON |
| --- | --- | --- | --- | --- |
| PyPy 3.11.13 | 2026-09-28T03:37:27.175689+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/pypy/mincostflow.json) |

- PyPy 3.11.13: commit `16f32e4c653a3a37e76b0ba0c00dbad7363734ec`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[8, 16, 32, 64, 128\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.13 \(413c9b7f57f5, Jul 03 2025, 18:03:56\) \[PyPy 7.3.20 with GCC 10.2.1 20210130 \(Red Hat 10.2.1-11\)\]
  - cffi: https://github.com/atcoder/ac-library.git @ `864245a00b00dd008d1abfdc239618fdb7d139da`
  - harurun: https://github.com/lif4635/harurun-s-library.git @ `7c94b7bb0c9d4f6ed0ffa44853febee1e7971ff9`
  - hpy: https://github.com/atcoder/ac-library.git @ `864245a00b00dd008d1abfdc239618fdb7d139da`
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`
  - tatyam: https://github.com/tatyam-prime/acl-cpp-python.git @ `b677fa437bdc1b0b7a4512d360de065cdca5778c`

## Strongly connected components

n 頂点・4n 辺。小さいブロック内の辺と前方への辺を混在。グラフ構築と結果の正規化も計測。

### PyPy 3.11.13

![Strongly connected components / PyPy 3.11.13](charts/scc/pypy.svg)

#### 最大入力サイズ n=500000（タイムアウトは除外）

![Strongly connected components / PyPy 3.11.13 最大ケース](charts/scc/pypy-max.svg)

[折れ線 SVG を保存](charts/scc/pypy.svg) · [最大ケース SVG を保存](charts/scc/pypy-max.svg)

タイムアウト（グラフから除外）: cffi n=500000, cffi\_batch n=500000, harurun n=131072, harurun n=500000, hpy\_universal n=500000, not522 n=500000, shakayami n=500000, tatyam n=131072, tatyam n=500000

**参考用：C++単体の実行時間（Pythonとの値変換・プロセス起動・入出力を除外）。**

- C++ ACL（参考用）: 2026-09-28T03:41:58.429373+00:00; g++ \(Ubuntu 13.3.0-6ubuntu2~24.04.1\) 13.3.0 \| -std=c++17 -O3 -DNDEBUG -march=native; timeout n=\[\]

### 計測情報

| ランタイム | 計測日時 | CPU | repeat / warmup / seed | JSON |
| --- | --- | --- | --- | --- |
| PyPy 3.11.13 | 2026-09-28T03:38:44.964379+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/pypy/scc.json) |

- PyPy 3.11.13: commit `16f32e4c653a3a37e76b0ba0c00dbad7363734ec`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[128, 512, 2048, 8192, 32768, 131072, 500000\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.13 \(413c9b7f57f5, Jul 03 2025, 18:03:56\) \[PyPy 7.3.20 with GCC 10.2.1 20210130 \(Red Hat 10.2.1-11\)\]
  - cffi: https://github.com/atcoder/ac-library.git @ `864245a00b00dd008d1abfdc239618fdb7d139da`
  - harurun: https://github.com/lif4635/harurun-s-library.git @ `7c94b7bb0c9d4f6ed0ffa44853febee1e7971ff9`
  - hpy: https://github.com/atcoder/ac-library.git @ `864245a00b00dd008d1abfdc239618fdb7d139da`
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`
  - tatyam: https://github.com/tatyam-prime/acl-cpp-python.git @ `b677fa437bdc1b0b7a4512d360de065cdca5778c`

## Segment tree

n 要素・4n 回の一点更新 / 区間和。構築も計測。C++ 版には公開 API がないため Python 2 実装を比較。

### PyPy 3.11.13

![Segment tree / PyPy 3.11.13](charts/segtree/pypy.svg)

#### 最大入力サイズ n=500000（タイムアウトは除外）

![Segment tree / PyPy 3.11.13 最大ケース](charts/segtree/pypy-max.svg)

[折れ線 SVG を保存](charts/segtree/pypy.svg) · [最大ケース SVG を保存](charts/segtree/pypy-max.svg)

タイムアウト（グラフから除外）: harurun n=500000, not522 n=500000, shakayami n=500000

**参考用：C++単体の実行時間（Pythonとの値変換・プロセス起動・入出力を除外）。**

- C++ ACL（参考用）: 2026-09-28T02:12:10.256768+00:00; g++ \(Ubuntu 13.3.0-6ubuntu2~24.04.1\) 13.3.0 \| -std=c++17 -O3 -DNDEBUG -march=native; timeout n=\[\]

### 計測情報

| ランタイム | 計測日時 | CPU | repeat / warmup / seed | JSON |
| --- | --- | --- | --- | --- |
| PyPy 3.11.13 | 2026-09-28T02:08:35.325863+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/pypy/segtree.json) |

- PyPy 3.11.13: commit `792088987107c0a8e973f972c98edf33dc35c2d9`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[128, 512, 2048, 8192, 32768, 131072, 500000\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.13 \(413c9b7f57f5, Jul 03 2025, 18:03:56\) \[PyPy 7.3.20 with GCC 10.2.1 20210130 \(Red Hat 10.2.1-11\)\]
  - harurun: https://github.com/lif4635/harurun-s-library.git @ `7c94b7bb0c9d4f6ed0ffa44853febee1e7971ff9`
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`

## Suffix array

長さ n の ASCII 文字列の suffix array。Python/C++ 間の変換も含む。

### PyPy 3.11.13

![Suffix array / PyPy 3.11.13](charts/suffix_array/pypy.svg)

#### 最大入力サイズ n=500000（タイムアウトは除外）

![Suffix array / PyPy 3.11.13 最大ケース](charts/suffix_array/pypy-max.svg)

[折れ線 SVG を保存](charts/suffix_array/pypy.svg) · [最大ケース SVG を保存](charts/suffix_array/pypy-max.svg)

**参考用：C++単体の実行時間（Pythonとの値変換・プロセス起動・入出力を除外）。**

- C++ ACL（参考用）: 2026-09-28T03:42:01.499420+00:00; g++ \(Ubuntu 13.3.0-6ubuntu2~24.04.1\) 13.3.0 \| -std=c++17 -O3 -DNDEBUG -march=native; timeout n=\[\]

### 計測情報

| ランタイム | 計測日時 | CPU | repeat / warmup / seed | JSON |
| --- | --- | --- | --- | --- |
| PyPy 3.11.13 | 2026-09-28T03:39:22.864334+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/pypy/suffix_array.json) |

- PyPy 3.11.13: commit `16f32e4c653a3a37e76b0ba0c00dbad7363734ec`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[128, 512, 2048, 8192, 32768, 131072, 500000\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.13 \(413c9b7f57f5, Jul 03 2025, 18:03:56\) \[PyPy 7.3.20 with GCC 10.2.1 20210130 \(Red Hat 10.2.1-11\)\]
  - cffi: https://github.com/atcoder/ac-library.git @ `864245a00b00dd008d1abfdc239618fdb7d139da`
  - harurun: https://github.com/lif4635/harurun-s-library.git @ `7c94b7bb0c9d4f6ed0ffa44853febee1e7971ff9`
  - hpy: https://github.com/atcoder/ac-library.git @ `864245a00b00dd008d1abfdc239618fdb7d139da`
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`
  - tatyam: https://github.com/tatyam-prime/acl-cpp-python.git @ `b677fa437bdc1b0b7a4512d360de065cdca5778c`

## 2-SAT

n 変数・4n 節。充足可能なランダム式の構築と求解。返り値は充足可能性と解の整合性。

### PyPy 3.11.13

![2-SAT / PyPy 3.11.13](charts/two_sat/pypy.svg)

#### 最大入力サイズ n=500000（タイムアウトは除外）

![2-SAT / PyPy 3.11.13 最大ケース](charts/two_sat/pypy-max.svg)

[折れ線 SVG を保存](charts/two_sat/pypy.svg) · [最大ケース SVG を保存](charts/two_sat/pypy-max.svg)

タイムアウト（グラフから除外）: cffi n=500000, harurun n=131072, harurun n=500000, hpy\_universal n=131072, hpy\_universal n=500000, not522 n=131072, not522 n=500000, shakayami n=131072, shakayami n=500000, tatyam n=131072, tatyam n=500000

**参考用：C++単体の実行時間（Pythonとの値変換・プロセス起動・入出力を除外）。**

- C++ ACL（参考用）: 2026-09-28T03:42:11.248848+00:00; g++ \(Ubuntu 13.3.0-6ubuntu2~24.04.1\) 13.3.0 \| -std=c++17 -O3 -DNDEBUG -march=native; timeout n=\[\]

### 計測情報

| ランタイム | 計測日時 | CPU | repeat / warmup / seed | JSON |
| --- | --- | --- | --- | --- |
| PyPy 3.11.13 | 2026-09-28T03:40:40.040484+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/pypy/two_sat.json) |

- PyPy 3.11.13: commit `16f32e4c653a3a37e76b0ba0c00dbad7363734ec`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[128, 512, 2048, 8192, 32768, 131072, 500000\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.13 \(413c9b7f57f5, Jul 03 2025, 18:03:56\) \[PyPy 7.3.20 with GCC 10.2.1 20210130 \(Red Hat 10.2.1-11\)\]
  - cffi: https://github.com/atcoder/ac-library.git @ `864245a00b00dd008d1abfdc239618fdb7d139da`
  - harurun: https://github.com/lif4635/harurun-s-library.git @ `7c94b7bb0c9d4f6ed0ffa44853febee1e7971ff9`
  - hpy: https://github.com/atcoder/ac-library.git @ `864245a00b00dd008d1abfdc239618fdb7d139da`
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`
  - tatyam: https://github.com/tatyam-prime/acl-cpp-python.git @ `b677fa437bdc1b0b7a4512d360de065cdca5778c`

## Z algorithm

長さ n の ASCII 文字列の Z 配列。Python/C++ 間の変換も含む。

### PyPy 3.11.13

![Z algorithm / PyPy 3.11.13](charts/z_algorithm/pypy.svg)

#### 最大入力サイズ n=500000（タイムアウトは除外）

![Z algorithm / PyPy 3.11.13 最大ケース](charts/z_algorithm/pypy-max.svg)

[折れ線 SVG を保存](charts/z_algorithm/pypy.svg) · [最大ケース SVG を保存](charts/z_algorithm/pypy-max.svg)

**参考用：C++単体の実行時間（Pythonとの値変換・プロセス起動・入出力を除外）。**

- C++ ACL（参考用）: 2026-09-28T03:42:14.059197+00:00; g++ \(Ubuntu 13.3.0-6ubuntu2~24.04.1\) 13.3.0 \| -std=c++17 -O3 -DNDEBUG -march=native; timeout n=\[\]

### 計測情報

| ランタイム | 計測日時 | CPU | repeat / warmup / seed | JSON |
| --- | --- | --- | --- | --- |
| PyPy 3.11.13 | 2026-09-28T03:41:12.769262+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/pypy/z_algorithm.json) |

- PyPy 3.11.13: commit `16f32e4c653a3a37e76b0ba0c00dbad7363734ec`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[128, 512, 2048, 8192, 32768, 131072, 500000\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.13 \(413c9b7f57f5, Jul 03 2025, 18:03:56\) \[PyPy 7.3.20 with GCC 10.2.1 20210130 \(Red Hat 10.2.1-11\)\]
  - cffi: https://github.com/atcoder/ac-library.git @ `864245a00b00dd008d1abfdc239618fdb7d139da`
  - harurun: https://github.com/lif4635/harurun-s-library.git @ `7c94b7bb0c9d4f6ed0ffa44853febee1e7971ff9`
  - hpy: https://github.com/atcoder/ac-library.git @ `864245a00b00dd008d1abfdc239618fdb7d139da`
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`
  - tatyam: https://github.com/tatyam-prime/acl-cpp-python.git @ `b677fa437bdc1b0b7a4512d360de065cdca5778c`

CI の CPU・負荷・ランタイムのバージョンによって実行時間は変動します。増分計測ではケースやランタイムごとに計測日時が異なります。各グラフの計測情報と JSON を併せて確認してください。
