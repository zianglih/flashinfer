# Native four-fix ABBA evidence

Fresh before/after comparison completed on one exclusive 8× B300 SXM6 node. All 56 timing rows and all 448 rank/token pre-timing output records passed the canonical fixture, finite, literal BF16-repeat and known-output checks. This includes both original-source 8,192-token rows; no row is excluded for incorrect output.

- **Sources:** before `7f1a093119f12b1f5b79d50bf6d0c951069224e5`; after `a48e5706c2a7775b0b698aa8eccb4e124b02118c`. The four correctness fixes span three owned kernel files. Both use the identical external current benchmark SHA `f2da99068552d7cde8faae002dbff15198a50c67535ca7510e40c3d507ae6448`, including untimed weight preparation with `enable_pdl=False`.
- **Workload:** EP8 Mega-only; hidden 7,168, intermediate 2,048, 256 experts, top-k 8; all 14 global token counts 1–8,192. Auto-tuned O3, maxregs 96, complete four-tactic catalog. Each row uses 3 warmups and 100 cold-L2 CUDA-graph CUPTI samples; reported latency is the median of per-iteration rank maxima.
- **Order:** A1 before → B1 after → B2 after → A2 before. Each full sweep has a fresh process and private core/compiler caches. Canonical weights, inputs and routes match across all sweeps. No other GPU job or bulk output transfer ran during timing.
- **Environment:** `nvcr.io/nvidia/pytorch:26.05-py3`; host hu-pdx-69; Torch `2.12.0a0+5aff3928d8.nv26.05`, Torch CUDA 13.2, CuTe DSL 4.7.1 with bundled native compiler 13.3. Host driver 590.48.01; loaded compatibility driver `libcuda.so.595.58.03`; nvcc 13.2.78. Exact package/library hashes and both 4,896-file source trees were rechecked before and after.
- **Evidence:** 5,600 raw samples, 2,240 core compile records, 32 full CPU BF16 tensor files. All 98 archived files (948,351,499 bytes) pass size/SHA verification. Raw tensor file bytes match the frozen logs and the successful on-node CPU shape/dtype/logical-hash verifier; local Torch deserialization is not claimed.

Latency in milliseconds. Combined ratio is `sqrt(A1 × A2 / (B1 × B2))`; above 1 means the corrected source is faster. A1/B1 and A2/B2 retain the separate order comparisons.

| Tokens | A1 before | B1 after | B2 after | A2 before | Combined before/after | A1/B1 | A2/B2 | Same tactic |
|---:|---:|---:|---:|---:|---:|---:|---:|:---:|
| 1 | 0.08835300 | 0.08808050 | 0.08763300 | 0.08780800 | 1.002545 | 1.003094 | 1.001997 | no |
| 2 | 0.11350500 | 0.08992050 | 0.10316900 | 0.11870500 | 1.205141 | 1.262282 | 1.150588 | yes |
| 4 | 0.12032100 | 0.12491300 | 0.12585700 | 0.11840100 | 0.951932 | 0.963238 | 0.940758 | yes |
| 8 | 0.13609650 | 0.13604850 | 0.13598550 | 0.14209700 | 1.022405 | 1.000353 | 1.044942 | yes |
| 16 | 0.16864100 | 0.15400150 | 0.15420950 | 0.15452900 | 1.047535 | 1.095061 | 1.002072 | yes |
| 32 | 0.17057750 | 0.17245000 | 0.18408100 | 0.18200150 | 0.988923 | 0.989142 | 0.988703 | yes |
| 64 | 0.20696200 | 0.20368200 | 0.19528150 | 0.19654550 | 1.011277 | 1.016104 | 1.006473 | yes |
| 128 | 0.20713800 | 0.21475300 | 0.21424100 | 0.20718600 | 0.965804 | 0.964541 | 0.967070 | yes |
| 256 | 0.21097800 | 0.22006500 | 0.21145750 | 0.21360100 | 0.984086 | 0.958708 | 1.010137 | yes |
| 512 | 0.20958550 | 0.21851400 | 0.22707400 | 0.21563400 | 0.954368 | 0.959140 | 0.949620 | yes |
| 1024 | 0.22960200 | 0.22816200 | 0.22860950 | 0.23305900 | 1.012866 | 1.006311 | 1.019463 | yes |
| 2048 | 0.32102750 | 0.31288350 | 0.31449800 | 0.31979500 | 1.021425 | 1.026029 | 1.016843 | yes |
| 4096 | 0.47227600 | 0.46861150 | 0.46394000 | 0.46891600 | 1.009272 | 1.007820 | 1.010726 | yes |
| 8192 | 0.76407100 | 0.73922150 | 0.76298300 | 0.73349350 | 0.996828 | 1.033616 | 0.961350 | yes |

Geometric mean over 8–8,192 tokens: **1.001015500×**. Tokens 1/2/4 remain reported and are excluded only from this aggregate.

The corrected source is slower in both orders with the same N64/epi tactic at 4 (+5.05%), 32 (+1.12%), 128 (+3.54%) and 512 (+4.78%) tokens. At 128 tokens the within-arm median drift is below 0.25%; 512 also regresses in both orders. These row-level results motivate the separately authorized minimal wait optimization; this archived comparison is unchanged. Two sweeps per arm describe the observed run, not statistical confidence from 100 correlated graph iterations. The output checks cover two eager forwards before timing, not every timed graph replay.

## Verification and closure

An independent standard-library scanner recomputed all 56 medians directly from the downloaded logs, compared all 5,600 retained samples, checked every canonical fixture/output and winner, and exactly reproduced the table and aggregate without importing the frozen parser.

- Snapshot: `evidence/collected/20260916T025408Z-b88d12cdd5e14b41b0613aae2e110f71`.
- Raw tables and samples: `independently-verified.md`, `independently-verified.json`, `independently-verified.samples.csv` inside the snapshot.
- Independent arithmetic: `owner-independent-arithmetic.json`; reusable audit `evidence/independent-arithmetic.py`.
- Whole compressed archive SHA256: `24d07ae9cf809032d6b428a0f1d022ea5194eb5ab8670e936b7d1ec40d410304` (748,568,613 bytes).
- Fresh post-transfer closure: epoch `1789527640.4404356`, boot `7f67e9f6-5016-4598-8050-a93beafdb59f`; all five recorded process identities/groups and all experiment workers gone, all eight expected UUIDs idle; source/helper/environment pins unchanged.
- The first transfer hit a managed transport reset. Its log and 320 MiB partial file remain preserved. The reviewed resume helper copied the prefix to a fresh destination, transferred smaller chunks and required the original whole-archive SHA before extraction. No benchmark retry occurred.
- Original source trees and all source-specific JIT caches remain intact. GPU ownership was handed to o2_harness_audit for the separately authorized bounded codegen comparison only.

```bash
python3 -B evidence/independent-arithmetic.py \
  evidence/collected/20260916T025408Z-b88d12cdd5e14b41b0613aae2e110f71
```
