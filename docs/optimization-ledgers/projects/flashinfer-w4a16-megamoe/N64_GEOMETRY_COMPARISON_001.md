# N64 geometry comparison: M128 versus M256

The four-shape baseline does not establish a general M preference. M128 is 3.08% faster at T8, with 0.21% split-control spread, but its T64 latency is 4.16% higher while the split arm also shifts by 4.42%. Differences at T1/T4096 are only about 0.5%. Both N64 geometries regress T4096 versus the adjacent M256/N128 control by roughly 9–10%.

## Source and measurement

All 16 recorded source hashes are identical between M128/N64 and M256/N64. Both use the frozen `candidates/w4a16_m256n64_timing/source` (kernel SHA256 `5ea9b59f882cef50e6da6c915295acaa626b92331f4fb592c0744b47628de866`), and the unchanged fe4 benchmark SHA256 `681cb0f8f4b2819068a69b3b69aabb0db697d8b2e6b0e18612a154adf2741f21`. Only the M tile and corresponding use_2cta_instrs knobs differ: [128,64,256]/false versus [256,64,256]/true. Both retain cluster(2,1,1), two decoded-TMEM stages, the preferred-five raw-stage fitter and two groups decoding disjoint halves of each K tile. These measurements precede the separate third-stage source change.

The adjacent fe4 and published full13 controls have identical source hashes; only kernel/frontend/epilogue differ from the geometry candidate. All per-rank/token split input shapes match. Actual split tuning reruns each process, and all 200 original tactic records are retained. The capture-time source labels and remote Git HEAD remain verbatim in JSON, alongside independently verified hashes.

Real EP8 on eight B300 GPUs, H7168/I2048/E256/top-k8, global source tokens, BF16 activations/wire and NVFP4 weights. Image `nvcr.io/nvidia/pytorch:26.05-py3`, toolkit CUDA13.2.78, DSL4.7.1 with bundled compiler CUDA13.3.27. Three warmups, 100 CUPTI iterations, CUDA graph and cold L2. Latency is the median of per-iteration maximum-rank full-forward GPU activity spans; tuning/setup/compilation/flush are excluded. Split keeps `--no-fused-finalize`. Numerical and codegen/resource checks remain separate evidence.

| Run | Start UTC | Before M128 start |
| --- | --- | --- |
| full13_n128 | Tue Sep  8 04:57:16 UTC 2026 | 62 m 55 s |
| adjacent_n128 | Tue Sep  8 05:34:53 UTC 2026 | 25 m 18 s |
| m256_n64 | Tue Sep  8 05:49:42 UTC 2026 | 10 m 29 s |
| m128_n64 | Tue Sep  8 06:00:11 UTC 2026 | candidate |

These are ordered process medians, not a confidence interval. Split spread is max/min−1 and reflects tuner, process and ordering variation; it is not a statistical error bar for Mega.

Numerical logs report 10 EP1 passes and 10 passes per EP2 rank for both geometries (M256 public-002, M128 public-001), with recorded compiled geometry. Their tracked-only provenance helper omitted untracked kernel/frontend/epilogue/test hashes. Timing source hashes are exact, but they must not be presented as retroactive source attestation for those numerical runs. The missing hashes remain a disclosed limitation; future runs must capture explicit required paths. Original M256 public-001 artifacts remain preserved separately.

## Same-source M comparison at N64

M128 change is 100 × (M128/M256 − 1); positive means slower.

| Global tokens | M256 Mega ms | M128 Mega ms | M128 change | M256 split ms | M128 split ms | Split spread | Changed tactic ranks |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 0.091089 | 0.090625 | -0.51% | 0.069136 | 0.082033 | 18.65% | 3, 4, 5 |
| 8 | 0.159825 | 0.154897 | -3.08% | 0.152801 | 0.153121 | 0.21% | 3, 4, 5 |
| 64 | 0.216242 | 0.225234 | +4.16% | 0.212369 | 0.221747 | 4.42% | 0, 4, 6 |
| 4096 | 0.567268 | 0.564245 | -0.53% | 0.544930 | 0.548612 | 0.68% | none |

T8 is the strongest M128-favoring observation in this pair. T64 does not establish a repeatable M256 advantage because the split arm shifts by a similar amount; it deserves a repeat with reversed order. T1 is dominated by large split variation, and the 0.53% T4096 difference is below its 0.68% split spread. None supports a universal selector rule. Every N64 measurement remains slower than its own same-run split arm.

## Adjacent fe4 N128 reference

| Global tokens | M256/N128 ms | M256/N64 ms | M256/N64 change | M128/N64 ms | M128/N64 change |
| --- | --- | --- | --- | --- | --- |
| 1 | 0.092033 | 0.091089 | -1.03% | 0.090625 | -1.53% |
| 8 | 0.160818 | 0.159825 | -0.62% | 0.154897 | -3.68% |
| 64 | 0.227314 | 0.216242 | -4.87% | 0.225234 | -0.92% |
| 4096 | 0.516021 | 0.567268 | +9.93% | 0.564245 | +9.35% |

The older full13 T64 value was 0.252721 ms, slower than the later adjacent 0.227314 ms and repeated controls. It is preserved below as context; choosing it alone would overstate N64 gains. Both N64 geometries lose the N128 large-token advantage in this baseline, so third-stage and full-grid evidence should precede any promotion.

## Complete raw timings and actual tactics

All 50 raw rows and 200 actual split selections are retained: eight rows/32 tactics for each N64 geometry and the adjacent control, plus 26 rows/104 tactics from the published full13 context. JSON includes complete original records, exact commands and artifact hashes.

| Run | Variant | Global tokens | EP | Latency ms |
| --- | --- | --- | --- | --- |
| full13_n128 | w4a16 | 1 | 8 | 0.082065 |
| full13_n128 | w4a16_megamoe | 1 | 8 | 0.098720 |
| full13_n128 | w4a16 | 2 | 8 | 0.116321 |
| full13_n128 | w4a16_megamoe | 2 | 8 | 0.113489 |
| full13_n128 | w4a16 | 4 | 8 | 0.143713 |
| full13_n128 | w4a16_megamoe | 4 | 8 | 0.134864 |
| full13_n128 | w4a16 | 8 | 8 | 0.154993 |
| full13_n128 | w4a16_megamoe | 8 | 8 | 0.159777 |
| full13_n128 | w4a16 | 16 | 8 | 0.179522 |
| full13_n128 | w4a16_megamoe | 16 | 8 | 0.181090 |
| full13_n128 | w4a16 | 32 | 8 | 0.204194 |
| full13_n128 | w4a16_megamoe | 32 | 8 | 0.210721 |
| full13_n128 | w4a16 | 64 | 8 | 0.221715 |
| full13_n128 | w4a16_megamoe | 64 | 8 | 0.252721 |
| full13_n128 | w4a16 | 128 | 8 | 0.236673 |
| full13_n128 | w4a16_megamoe | 128 | 8 | 0.242498 |
| full13_n128 | w4a16 | 256 | 8 | 0.242978 |
| full13_n128 | w4a16_megamoe | 256 | 8 | 0.246594 |
| full13_n128 | w4a16 | 512 | 8 | 0.240290 |
| full13_n128 | w4a16_megamoe | 512 | 8 | 0.255026 |
| full13_n128 | w4a16 | 1024 | 8 | 0.262257 |
| full13_n128 | w4a16_megamoe | 1024 | 8 | 0.265906 |
| full13_n128 | w4a16 | 2048 | 8 | 0.350451 |
| full13_n128 | w4a16_megamoe | 2048 | 8 | 0.346882 |
| full13_n128 | w4a16 | 4096 | 8 | 0.544547 |
| full13_n128 | w4a16_megamoe | 4096 | 8 | 0.506356 |
| adjacent_n128 | w4a16 | 1 | 8 | 0.068736 |
| adjacent_n128 | w4a16_megamoe | 1 | 8 | 0.092033 |
| adjacent_n128 | w4a16 | 8 | 8 | 0.151345 |
| adjacent_n128 | w4a16_megamoe | 8 | 8 | 0.160818 |
| adjacent_n128 | w4a16 | 64 | 8 | 0.210402 |
| adjacent_n128 | w4a16_megamoe | 64 | 8 | 0.227314 |
| adjacent_n128 | w4a16 | 4096 | 8 | 0.550629 |
| adjacent_n128 | w4a16_megamoe | 4096 | 8 | 0.516021 |
| m256_n64 | w4a16 | 1 | 8 | 0.069136 |
| m256_n64 | w4a16_megamoe | 1 | 8 | 0.091089 |
| m256_n64 | w4a16 | 8 | 8 | 0.152801 |
| m256_n64 | w4a16_megamoe | 8 | 8 | 0.159825 |
| m256_n64 | w4a16 | 64 | 8 | 0.212369 |
| m256_n64 | w4a16_megamoe | 64 | 8 | 0.216242 |
| m256_n64 | w4a16 | 4096 | 8 | 0.544930 |
| m256_n64 | w4a16_megamoe | 4096 | 8 | 0.567268 |
| m128_n64 | w4a16 | 1 | 8 | 0.082033 |
| m128_n64 | w4a16_megamoe | 1 | 8 | 0.090625 |
| m128_n64 | w4a16 | 8 | 8 | 0.153121 |
| m128_n64 | w4a16_megamoe | 8 | 8 | 0.154897 |
| m128_n64 | w4a16 | 64 | 8 | 0.221747 |
| m128_n64 | w4a16_megamoe | 64 | 8 | 0.225234 |
| m128_n64 | w4a16 | 4096 | 8 | 0.548612 |
| m128_n64 | w4a16_megamoe | 4096 | 8 | 0.564245 |

| Run | Global tokens | Rank0…rank7 FC1/FC2 tactics |
| --- | --- | --- |
| full13_n128 | 1 | 128×16×256/256×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256 |
| full13_n128 | 2 | 128×16×256/256×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256 |
| full13_n128 | 4 | 128×16×256/256×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256 |
| full13_n128 | 8 | 128×16×256/256×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256 |
| full13_n128 | 16 | 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256 |
| full13_n128 | 32 | 128×16×256/256×16×256; 128×16×256/256×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/256×16×256; 128×8×256/128×8×256; 256×16×256/128×16×256 |
| full13_n128 | 64 | 128×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 256×16×256/256×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256 |
| full13_n128 | 128 | 128×16×256/128×16×256; 128×16×256/256×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256 |
| full13_n128 | 256 | 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×32×256/256×32×256; 128×16×256/128×16×256; 128×16×256/128×16×256 |
| full13_n128 | 512 | 128×32×256/256×32×256; 128×32×256/256×32×256; 128×32×256/128×32×256; 128×32×256/128×32×256; 128×32×256/128×32×256; 128×32×256/256×32×256; 128×32×256/256×32×256; 128×32×256/256×32×256 |
| full13_n128 | 1024 | 256×64×256/256×64×256; 256×64×256/256×64×256; 256×64×256/256×64×256; 256×64×256/128×64×256; 256×64×256/128×64×256; 256×64×256/256×64×256; 256×64×256/128×64×256; 256×64×256/128×64×256 |
| full13_n128 | 2048 | 256×64×256/128×64×256; 256×64×256/128×64×256; 256×64×256/256×64×256; 256×64×256/256×64×256; 256×64×256/256×64×256; 256×64×256/256×64×256; 256×64×256/128×64×256; 256×128×256/256×128×256 |
| full13_n128 | 4096 | 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256 |
| adjacent_n128 | 1 | 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256 |
| adjacent_n128 | 8 | 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256 |
| adjacent_n128 | 64 | 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 256×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256 |
| adjacent_n128 | 4096 | 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256 |
| m256_n64 | 1 | 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256 |
| m256_n64 | 8 | 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256 |
| m256_n64 | 64 | 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 256×16×256/128×16×256; 128×8×256/128×8×256; 256×16×256/128×16×256; 128×16×256/128×16×256 |
| m256_n64 | 4096 | 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256 |
| m128_n64 | 1 | 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256 |
| m128_n64 | 8 | 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256 |
| m128_n64 | 64 | 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/256×16×256; 128×16×256/128×16×256 |
| m128_n64 | 4096 | 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256 |

Reproduce with `python3 compare_n64_geometries.py`. The follow-up plan is `N64_FULL_GRID_PLAN.md`; it uses the existing benchmark and tactic recorder without a new harness. No active source or GPU work was performed for this report.
