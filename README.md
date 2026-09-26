# Python ACL ベンチマーク

各実装を CPython / PyPy で比較します。グラフはランタイムごとに分け、軸の範囲を個別に調整します。グラフは小さいほど高速です。線は中央値、帯・ひげは観測された最小値から最大値です。正の値には対数軸を使い、0 を含む軸には線形軸を使います。

[HTML レポート](index.html) · [生データ](data/)

## Convolution \(mod 998244353\)

長さ n の 2 配列の畳み込み。FFT インスタンスの初期化・Python/C++ 間の変換も含む。

### CPython 3.11.16

![Convolution \(mod 998244353\) / CPython 3.11.16](charts/convolution/cpython.svg)

[SVG を保存](charts/convolution/cpython.svg)

### PyPy 3.11.13

![Convolution \(mod 998244353\) / PyPy 3.11.13](charts/convolution/pypy.svg)

[SVG を保存](charts/convolution/pypy.svg)

### 計測情報

| ランタイム | 計測日時 | CPU | repeat / warmup / seed | JSON |
| --- | --- | --- | --- | --- |
| CPython 3.11.16 | 2026-09-26T04:22:50.131644+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/cpython/convolution.json) |
| PyPy 3.11.13 | 2026-09-26T04:26:28.613305+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/pypy/convolution.json) |

- CPython 3.11.16: commit `c23f473cac5c191bf28bbbec358227af77f9bd3c`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[64, 256, 1024, 4096, 16384\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.16 \(main, Aug 13 2026, 02:46:14\) \[GCC 13.3.0\]
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`
  - tatyam: https://github.com/tatyam-prime/acl-cpp-python.git @ `b677fa437bdc1b0b7a4512d360de065cdca5778c`
- PyPy 3.11.13: commit `c23f473cac5c191bf28bbbec358227af77f9bd3c`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[64, 256, 1024, 4096, 16384\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.13 \(413c9b7f57f5, Jul 03 2025, 18:03:56\) \[PyPy 7.3.20 with GCC 10.2.1 20210130 \(Red Hat 10.2.1-11\)\]
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`
  - tatyam: https://github.com/tatyam-prime/acl-cpp-python.git @ `b677fa437bdc1b0b7a4512d360de065cdca5778c`

## Chinese remainder theorem

n 組の合同式を処理。各組は 4 個の法、最小公倍数を 64 bit 以内に固定。

### CPython 3.11.16

![Chinese remainder theorem / CPython 3.11.16](charts/crt/cpython.svg)

[SVG を保存](charts/crt/cpython.svg)

### PyPy 3.11.13

![Chinese remainder theorem / PyPy 3.11.13](charts/crt/pypy.svg)

[SVG を保存](charts/crt/pypy.svg)

### 計測情報

| ランタイム | 計測日時 | CPU | repeat / warmup / seed | JSON |
| --- | --- | --- | --- | --- |
| CPython 3.11.16 | 2026-09-26T04:22:58.119896+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/cpython/crt.json) |
| PyPy 3.11.13 | 2026-09-26T04:26:40.304317+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/pypy/crt.json) |

- CPython 3.11.16: commit `c23f473cac5c191bf28bbbec358227af77f9bd3c`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[128, 512, 2048, 8192, 32768\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.16 \(main, Aug 13 2026, 02:46:14\) \[GCC 13.3.0\]
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`
  - tatyam: https://github.com/tatyam-prime/acl-cpp-python.git @ `b677fa437bdc1b0b7a4512d360de065cdca5778c`
- PyPy 3.11.13: commit `c23f473cac5c191bf28bbbec358227af77f9bd3c`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[128, 512, 2048, 8192, 32768\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.13 \(413c9b7f57f5, Jul 03 2025, 18:03:56\) \[PyPy 7.3.20 with GCC 10.2.1 20210130 \(Red Hat 10.2.1-11\)\]
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`
  - tatyam: https://github.com/tatyam-prime/acl-cpp-python.git @ `b677fa437bdc1b0b7a4512d360de065cdca5778c`

## DSU / Union-Find

n 頂点・4n 回の merge / same。初期化と全クエリを計測。

### CPython 3.11.16

![DSU / Union-Find / CPython 3.11.16](charts/dsu/cpython.svg)

[SVG を保存](charts/dsu/cpython.svg)

### PyPy 3.11.13

![DSU / Union-Find / PyPy 3.11.13](charts/dsu/pypy.svg)

[SVG を保存](charts/dsu/pypy.svg)

### 計測情報

| ランタイム | 計測日時 | CPU | repeat / warmup / seed | JSON |
| --- | --- | --- | --- | --- |
| CPython 3.11.16 | 2026-09-26T04:23:06.019207+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/cpython/dsu.json) |
| PyPy 3.11.13 | 2026-09-26T04:26:52.160556+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/pypy/dsu.json) |

- CPython 3.11.16: commit `c23f473cac5c191bf28bbbec358227af77f9bd3c`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[128, 512, 2048, 8192, 32768\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.16 \(main, Aug 13 2026, 02:46:14\) \[GCC 13.3.0\]
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`
  - tatyam: https://github.com/tatyam-prime/acl-cpp-python.git @ `b677fa437bdc1b0b7a4512d360de065cdca5778c`
- PyPy 3.11.13: commit `c23f473cac5c191bf28bbbec358227af77f9bd3c`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[128, 512, 2048, 8192, 32768\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.13 \(413c9b7f57f5, Jul 03 2025, 18:03:56\) \[PyPy 7.3.20 with GCC 10.2.1 20210130 \(Red Hat 10.2.1-11\)\]
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`
  - tatyam: https://github.com/tatyam-prime/acl-cpp-python.git @ `b677fa437bdc1b0b7a4512d360de065cdca5778c`

## Fenwick tree

n 要素・4n 回の一点加算 / 区間和。ゼロ初期化と全クエリを計測。

### CPython 3.11.16

![Fenwick tree / CPython 3.11.16](charts/fenwicktree/cpython.svg)

[SVG を保存](charts/fenwicktree/cpython.svg)

### PyPy 3.11.13

![Fenwick tree / PyPy 3.11.13](charts/fenwicktree/pypy.svg)

[SVG を保存](charts/fenwicktree/pypy.svg)

### 計測情報

| ランタイム | 計測日時 | CPU | repeat / warmup / seed | JSON |
| --- | --- | --- | --- | --- |
| CPython 3.11.16 | 2026-09-26T04:23:17.690514+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/cpython/fenwicktree.json) |
| PyPy 3.11.13 | 2026-09-26T04:27:03.701144+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/pypy/fenwicktree.json) |

- CPython 3.11.16: commit `c23f473cac5c191bf28bbbec358227af77f9bd3c`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[128, 512, 2048, 8192, 32768\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.16 \(main, Aug 13 2026, 02:46:14\) \[GCC 13.3.0\]
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`
  - tatyam: https://github.com/tatyam-prime/acl-cpp-python.git @ `b677fa437bdc1b0b7a4512d360de065cdca5778c`
- PyPy 3.11.13: commit `c23f473cac5c191bf28bbbec358227af77f9bd3c`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[128, 512, 2048, 8192, 32768\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.13 \(413c9b7f57f5, Jul 03 2025, 18:03:56\) \[PyPy 7.3.20 with GCC 10.2.1 20210130 \(Red Hat 10.2.1-11\)\]
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`
  - tatyam: https://github.com/tatyam-prime/acl-cpp-python.git @ `b677fa437bdc1b0b7a4512d360de065cdca5778c`

## Floor sum

n 回の floor\_sum 呼び出し。引数 n,m は 1..999999、a,b は 0..999999。結果は符号付き 64 bit 以内。

### CPython 3.11.16

![Floor sum / CPython 3.11.16](charts/floor_sum/cpython.svg)

[SVG を保存](charts/floor_sum/cpython.svg)

### PyPy 3.11.13

![Floor sum / PyPy 3.11.13](charts/floor_sum/pypy.svg)

[SVG を保存](charts/floor_sum/pypy.svg)

### 計測情報

| ランタイム | 計測日時 | CPU | repeat / warmup / seed | JSON |
| --- | --- | --- | --- | --- |
| CPython 3.11.16 | 2026-09-26T04:23:27.433009+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/cpython/floor_sum.json) |
| PyPy 3.11.13 | 2026-09-26T04:27:12.903455+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/pypy/floor_sum.json) |

- CPython 3.11.16: commit `c23f473cac5c191bf28bbbec358227af77f9bd3c`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[128, 512, 2048, 8192, 32768\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.16 \(main, Aug 13 2026, 02:46:14\) \[GCC 13.3.0\]
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`
  - tatyam: https://github.com/tatyam-prime/acl-cpp-python.git @ `b677fa437bdc1b0b7a4512d360de065cdca5778c`
- PyPy 3.11.13: commit `c23f473cac5c191bf28bbbec358227af77f9bd3c`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[128, 512, 2048, 8192, 32768\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.13 \(413c9b7f57f5, Jul 03 2025, 18:03:56\) \[PyPy 7.3.20 with GCC 10.2.1 20210130 \(Red Hat 10.2.1-11\)\]
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`
  - tatyam: https://github.com/tatyam-prime/acl-cpp-python.git @ `b677fa437bdc1b0b7a4512d360de065cdca5778c`

## Lazy segment tree

n 要素・2n 回の区間加算 / 区間和。\(合計, 要素数\) を保持し構築も計測。C++ 版には公開 API がないため Python 2 実装を比較。

### CPython 3.11.16

![Lazy segment tree / CPython 3.11.16](charts/lazysegtree/cpython.svg)

[SVG を保存](charts/lazysegtree/cpython.svg)

### PyPy 3.11.13

![Lazy segment tree / PyPy 3.11.13](charts/lazysegtree/pypy.svg)

[SVG を保存](charts/lazysegtree/pypy.svg)

### 計測情報

| ランタイム | 計測日時 | CPU | repeat / warmup / seed | JSON |
| --- | --- | --- | --- | --- |
| CPython 3.11.16 | 2026-09-26T04:24:23.986073+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/cpython/lazysegtree.json) |
| PyPy 3.11.13 | 2026-09-26T04:27:21.382050+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/pypy/lazysegtree.json) |

- CPython 3.11.16: commit `c23f473cac5c191bf28bbbec358227af77f9bd3c`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[128, 512, 2048, 8192, 32768\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.16 \(main, Aug 13 2026, 02:46:14\) \[GCC 13.3.0\]
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`
- PyPy 3.11.13: commit `c23f473cac5c191bf28bbbec358227af77f9bd3c`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[128, 512, 2048, 8192, 32768\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.13 \(413c9b7f57f5, Jul 03 2025, 18:03:56\) \[PyPy 7.3.20 with GCC 10.2.1 20210130 \(Red Hat 10.2.1-11\)\]
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`

## LCP array

長さ n の ASCII 文字列と計測外で生成した suffix array から LCP を計算。

### CPython 3.11.16

![LCP array / CPython 3.11.16](charts/lcp_array/cpython.svg)

[SVG を保存](charts/lcp_array/cpython.svg)

### PyPy 3.11.13

![LCP array / PyPy 3.11.13](charts/lcp_array/pypy.svg)

[SVG を保存](charts/lcp_array/pypy.svg)

### 計測情報

| ランタイム | 計測日時 | CPU | repeat / warmup / seed | JSON |
| --- | --- | --- | --- | --- |
| CPython 3.11.16 | 2026-09-26T04:24:30.823307+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/cpython/lcp_array.json) |
| PyPy 3.11.13 | 2026-09-26T04:27:29.892434+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/pypy/lcp_array.json) |

- CPython 3.11.16: commit `c23f473cac5c191bf28bbbec358227af77f9bd3c`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[128, 512, 2048, 8192, 32768\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.16 \(main, Aug 13 2026, 02:46:14\) \[GCC 13.3.0\]
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`
  - tatyam: https://github.com/tatyam-prime/acl-cpp-python.git @ `b677fa437bdc1b0b7a4512d360de065cdca5778c`
- PyPy 3.11.13: commit `c23f473cac5c191bf28bbbec358227af77f9bd3c`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[128, 512, 2048, 8192, 32768\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.13 \(413c9b7f57f5, Jul 03 2025, 18:03:56\) \[PyPy 7.3.20 with GCC 10.2.1 20210130 \(Red Hat 10.2.1-11\)\]
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`
  - tatyam: https://github.com/tatyam-prime/acl-cpp-python.git @ `b677fa437bdc1b0b7a4512d360de065cdca5778c`

## Maximum flow

左右 n 頂点ずつの疎な二部グラフ。各左頂点から 4 辺。ネットワーク構築と最大流を計測。

### CPython 3.11.16

![Maximum flow / CPython 3.11.16](charts/maxflow/cpython.svg)

[SVG を保存](charts/maxflow/cpython.svg)

### PyPy 3.11.13

![Maximum flow / PyPy 3.11.13](charts/maxflow/pypy.svg)

[SVG を保存](charts/maxflow/pypy.svg)

### 計測情報

| ランタイム | 計測日時 | CPU | repeat / warmup / seed | JSON |
| --- | --- | --- | --- | --- |
| CPython 3.11.16 | 2026-09-26T04:25:01.701650+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/cpython/maxflow.json) |
| PyPy 3.11.13 | 2026-09-26T04:27:43.146991+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/pypy/maxflow.json) |

- CPython 3.11.16: commit `c23f473cac5c191bf28bbbec358227af77f9bd3c`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[8, 32, 128, 512, 2048\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.16 \(main, Aug 13 2026, 02:46:14\) \[GCC 13.3.0\]
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`
  - tatyam: https://github.com/tatyam-prime/acl-cpp-python.git @ `b677fa437bdc1b0b7a4512d360de065cdca5778c`
- PyPy 3.11.13: commit `c23f473cac5c191bf28bbbec358227af77f9bd3c`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[8, 32, 128, 512, 2048\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.13 \(413c9b7f57f5, Jul 03 2025, 18:03:56\) \[PyPy 7.3.20 with GCC 10.2.1 20210130 \(Red Hat 10.2.1-11\)\]
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`
  - tatyam: https://github.com/tatyam-prime/acl-cpp-python.git @ `b677fa437bdc1b0b7a4512d360de065cdca5778c`

## Minimum-cost flow

左右 n 頂点ずつの二部グラフ。各左頂点から 3 辺、非負コスト。構築と最小費用最大流を計測。

### CPython 3.11.16

![Minimum-cost flow / CPython 3.11.16](charts/mincostflow/cpython.svg)

[SVG を保存](charts/mincostflow/cpython.svg)

### PyPy 3.11.13

![Minimum-cost flow / PyPy 3.11.13](charts/mincostflow/pypy.svg)

[SVG を保存](charts/mincostflow/pypy.svg)

### 計測情報

| ランタイム | 計測日時 | CPU | repeat / warmup / seed | JSON |
| --- | --- | --- | --- | --- |
| CPython 3.11.16 | 2026-09-26T04:25:08.408803+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/cpython/mincostflow.json) |
| PyPy 3.11.13 | 2026-09-26T04:27:51.679892+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/pypy/mincostflow.json) |

- CPython 3.11.16: commit `c23f473cac5c191bf28bbbec358227af77f9bd3c`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[8, 16, 32, 64, 128\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.16 \(main, Aug 13 2026, 02:46:14\) \[GCC 13.3.0\]
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`
  - tatyam: https://github.com/tatyam-prime/acl-cpp-python.git @ `b677fa437bdc1b0b7a4512d360de065cdca5778c`
- PyPy 3.11.13: commit `c23f473cac5c191bf28bbbec358227af77f9bd3c`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[8, 16, 32, 64, 128\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.13 \(413c9b7f57f5, Jul 03 2025, 18:03:56\) \[PyPy 7.3.20 with GCC 10.2.1 20210130 \(Red Hat 10.2.1-11\)\]
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`
  - tatyam: https://github.com/tatyam-prime/acl-cpp-python.git @ `b677fa437bdc1b0b7a4512d360de065cdca5778c`

## Strongly connected components

n 頂点・4n 辺。小さいブロック内の辺と前方への辺を混在。グラフ構築と結果の正規化も計測。

### CPython 3.11.16

![Strongly connected components / CPython 3.11.16](charts/scc/cpython.svg)

[SVG を保存](charts/scc/cpython.svg)

### PyPy 3.11.13

![Strongly connected components / PyPy 3.11.13](charts/scc/pypy.svg)

[SVG を保存](charts/scc/pypy.svg)

### 計測情報

| ランタイム | 計測日時 | CPU | repeat / warmup / seed | JSON |
| --- | --- | --- | --- | --- |
| CPython 3.11.16 | 2026-09-26T04:25:17.626030+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/cpython/scc.json) |
| PyPy 3.11.13 | 2026-09-26T04:28:03.965337+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/pypy/scc.json) |

- CPython 3.11.16: commit `c23f473cac5c191bf28bbbec358227af77f9bd3c`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[128, 512, 2048, 8192, 32768\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.16 \(main, Aug 13 2026, 02:46:14\) \[GCC 13.3.0\]
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`
  - tatyam: https://github.com/tatyam-prime/acl-cpp-python.git @ `b677fa437bdc1b0b7a4512d360de065cdca5778c`
- PyPy 3.11.13: commit `c23f473cac5c191bf28bbbec358227af77f9bd3c`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[128, 512, 2048, 8192, 32768\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.13 \(413c9b7f57f5, Jul 03 2025, 18:03:56\) \[PyPy 7.3.20 with GCC 10.2.1 20210130 \(Red Hat 10.2.1-11\)\]
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`
  - tatyam: https://github.com/tatyam-prime/acl-cpp-python.git @ `b677fa437bdc1b0b7a4512d360de065cdca5778c`

## Segment tree

n 要素・4n 回の一点更新 / 区間和。構築も計測。C++ 版には公開 API がないため Python 2 実装を比較。

### CPython 3.11.16

![Segment tree / CPython 3.11.16](charts/segtree/cpython.svg)

[SVG を保存](charts/segtree/cpython.svg)

### PyPy 3.11.13

![Segment tree / PyPy 3.11.13](charts/segtree/pypy.svg)

[SVG を保存](charts/segtree/pypy.svg)

### 計測情報

| ランタイム | 計測日時 | CPU | repeat / warmup / seed | JSON |
| --- | --- | --- | --- | --- |
| CPython 3.11.16 | 2026-09-26T04:25:30.515574+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/cpython/segtree.json) |
| PyPy 3.11.13 | 2026-09-26T04:28:10.831157+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/pypy/segtree.json) |

- CPython 3.11.16: commit `c23f473cac5c191bf28bbbec358227af77f9bd3c`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[128, 512, 2048, 8192, 32768\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.16 \(main, Aug 13 2026, 02:46:14\) \[GCC 13.3.0\]
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`
- PyPy 3.11.13: commit `c23f473cac5c191bf28bbbec358227af77f9bd3c`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[128, 512, 2048, 8192, 32768\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.13 \(413c9b7f57f5, Jul 03 2025, 18:03:56\) \[PyPy 7.3.20 with GCC 10.2.1 20210130 \(Red Hat 10.2.1-11\)\]
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`

## Suffix array

長さ n の ASCII 文字列の suffix array。Python/C++ 間の変換も含む。

### CPython 3.11.16

![Suffix array / CPython 3.11.16](charts/suffix_array/cpython.svg)

[SVG を保存](charts/suffix_array/cpython.svg)

### PyPy 3.11.13

![Suffix array / PyPy 3.11.13](charts/suffix_array/pypy.svg)

[SVG を保存](charts/suffix_array/pypy.svg)

### 計測情報

| ランタイム | 計測日時 | CPU | repeat / warmup / seed | JSON |
| --- | --- | --- | --- | --- |
| CPython 3.11.16 | 2026-09-26T04:25:37.593914+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/cpython/suffix_array.json) |
| PyPy 3.11.13 | 2026-09-26T04:28:19.212483+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/pypy/suffix_array.json) |

- CPython 3.11.16: commit `c23f473cac5c191bf28bbbec358227af77f9bd3c`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[128, 512, 2048, 8192, 32768\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.16 \(main, Aug 13 2026, 02:46:14\) \[GCC 13.3.0\]
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`
  - tatyam: https://github.com/tatyam-prime/acl-cpp-python.git @ `b677fa437bdc1b0b7a4512d360de065cdca5778c`
- PyPy 3.11.13: commit `c23f473cac5c191bf28bbbec358227af77f9bd3c`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[128, 512, 2048, 8192, 32768\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.13 \(413c9b7f57f5, Jul 03 2025, 18:03:56\) \[PyPy 7.3.20 with GCC 10.2.1 20210130 \(Red Hat 10.2.1-11\)\]
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`
  - tatyam: https://github.com/tatyam-prime/acl-cpp-python.git @ `b677fa437bdc1b0b7a4512d360de065cdca5778c`

## 2-SAT

n 変数・4n 節。充足可能なランダム式の構築と求解。返り値は充足可能性と解の整合性。

### CPython 3.11.16

![2-SAT / CPython 3.11.16](charts/two_sat/cpython.svg)

[SVG を保存](charts/two_sat/cpython.svg)

### PyPy 3.11.13

![2-SAT / PyPy 3.11.13](charts/two_sat/pypy.svg)

[SVG を保存](charts/two_sat/pypy.svg)

### 計測情報

| ランタイム | 計測日時 | CPU | repeat / warmup / seed | JSON |
| --- | --- | --- | --- | --- |
| CPython 3.11.16 | 2026-09-26T04:25:50.987412+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/cpython/two_sat.json) |
| PyPy 3.11.13 | 2026-09-26T04:28:33.844934+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/pypy/two_sat.json) |

- CPython 3.11.16: commit `c23f473cac5c191bf28bbbec358227af77f9bd3c`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[128, 512, 2048, 8192, 32768\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.16 \(main, Aug 13 2026, 02:46:14\) \[GCC 13.3.0\]
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`
  - tatyam: https://github.com/tatyam-prime/acl-cpp-python.git @ `b677fa437bdc1b0b7a4512d360de065cdca5778c`
- PyPy 3.11.13: commit `c23f473cac5c191bf28bbbec358227af77f9bd3c`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[128, 512, 2048, 8192, 32768\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.13 \(413c9b7f57f5, Jul 03 2025, 18:03:56\) \[PyPy 7.3.20 with GCC 10.2.1 20210130 \(Red Hat 10.2.1-11\)\]
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`
  - tatyam: https://github.com/tatyam-prime/acl-cpp-python.git @ `b677fa437bdc1b0b7a4512d360de065cdca5778c`

## Z algorithm

長さ n の ASCII 文字列の Z 配列。Python/C++ 間の変換も含む。

### CPython 3.11.16

![Z algorithm / CPython 3.11.16](charts/z_algorithm/cpython.svg)

[SVG を保存](charts/z_algorithm/cpython.svg)

### PyPy 3.11.13

![Z algorithm / PyPy 3.11.13](charts/z_algorithm/pypy.svg)

[SVG を保存](charts/z_algorithm/pypy.svg)

### 計測情報

| ランタイム | 計測日時 | CPU | repeat / warmup / seed | JSON |
| --- | --- | --- | --- | --- |
| CPython 3.11.16 | 2026-09-26T04:25:57.511834+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/cpython/z_algorithm.json) |
| PyPy 3.11.13 | 2026-09-26T04:28:42.181505+00:00 | AMD EPYC 7763 64-Core Processor | 5 / 3 / 42 | [data](data/pypy/z_algorithm.json) |

- CPython 3.11.16: commit `c23f473cac5c191bf28bbbec358227af77f9bd3c`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[128, 512, 2048, 8192, 32768\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.16 \(main, Aug 13 2026, 02:46:14\) \[GCC 13.3.0\]
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`
  - tatyam: https://github.com/tatyam-prime/acl-cpp-python.git @ `b677fa437bdc1b0b7a4512d360de065cdca5778c`
- PyPy 3.11.13: commit `c23f473cac5c191bf28bbbec358227af77f9bd3c`; OS: Linux-6.17.0-1022-azure-x86\_64-with-glibc2.39
  - n=\[128, 512, 2048, 8192, 32768\]; warmup_seconds=0.25; sample_seconds=0.025
  - build: 3.11.13 \(413c9b7f57f5, Jul 03 2025, 18:03:56\) \[PyPy 7.3.20 with GCC 10.2.1 20210130 \(Red Hat 10.2.1-11\)\]
  - not522: https://github.com/not522/ac-library-python.git @ `27fdbb71cd0d566bdeb12746db59c9d908c6b5d5`
  - shakayami: https://github.com/shakayami/ACL-for-python.git @ `880ed3fc236c9628d674363768bcf203fbb84a8d`
  - tatyam: https://github.com/tatyam-prime/acl-cpp-python.git @ `b677fa437bdc1b0b7a4512d360de065cdca5778c`

CI の CPU・負荷・ランタイムのバージョンによって実行時間は変動します。増分計測ではケースやランタイムごとに計測日時が異なります。各グラフの計測情報と JSON を併せて確認してください。
