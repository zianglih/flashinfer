# Adjacent raw-depth comparison: depths2,3,5

Raw5 is the lowest measured Mega latency at all five shapes. It is the appropriate raw-depth control for the next two-transform-group trial; keep scheduling and raw depth fixed while changing producer count. These are single sequential runs with independent split tuning, not confidence intervals or proof that raw5 is optimal beyond the measured matrix.

## Source and measurement

- Run order: raw3, restored raw2, raw5. All runs use the public dynamic-N path and identical flag4-epi settings, H7168/I2048/E256/top-k8, real EP8 on eight B300 and **global** source tokens. BF16 activations/wire, packed NVFP4 weights, post-FC2 FP32 route scores and the existing split `--no-fused-finalize` reduction are preserved.
- Three warmups,100 fixed iterations,CUDA graph,cold L2,CUPTI; median across iterations of the maximum-rank GPU kernel wall span. Compilation,tuning,weight preparation,cache flush and codegen-only timing are excluded. Numerical validation is separate.
- Every run has 16 recorded source hashes, independently verified against c7713ba1 or the frozen raw-depth kernel snapshot. Only kernel source differs; all commands and hashes are preserved in the JSON. Remote Git HEAD is a stale checkout marker; actual overlays determine execution.
- Identical knobs: `{"epi_flag_batch": [2, 4], "flag_batch": 4, "group_hint": 512, "load_balance_mode": "atomic_counter", "token_back_mode": "epi_warps"}`. M256/N128/K256,512threads,register cap128,one transform group. Raw A+SF stage depth is 2/3/5; transformed-A,activation and accumulator stages remain 2.

| Depth | Declared source | Kernel SHA256 |
| --- | --- | --- |
| raw3 | c7713ba1+raw3 | 95f2cc38823c9c7e09a9659f84a294ffa80a31f87f4d934450fd7913b7ec8be9 |
| raw2 | c7713ba1 | 98e4694e90a48c14722fef1d32b1bbf5600537feb6bbe6e9420c9a853b7d4647 |
| raw5 | c7713ba1+raw5 | 3bf69b9526757dceb6db680429d1a9e6590365135f433d840a55eb804d921940 |

## Complete raw pairs

All latency values are ms. Ratios are derived from the printed six-decimal latencies.

| Run | Global tokens | Split W4A16 ms | Mega W4A16 ms | Split/Mega |
| --- | --- | --- | --- | --- |
| raw3 | 1 | 0.080720 | 0.102480 | 0.787666 |
| raw3 | 8 | 0.157745 | 0.177778 | 0.887315 |
| raw3 | 32 | 0.200193 | 0.222241 | 0.900792 |
| raw3 | 128 | 0.233313 | 0.261378 | 0.892627 |
| raw3 | 4096 | 0.555141 | 0.537045 | 1.033696 |
| raw2 | 1 | 0.096082 | 0.108608 | 0.884668 |
| raw2 | 8 | 0.153938 | 0.218801 | 0.703553 |
| raw2 | 32 | 0.198785 | 0.292419 | 0.679795 |
| raw2 | 128 | 0.234994 | 0.346786 | 0.677634 |
| raw2 | 4096 | 0.541143 | 0.655702 | 0.825288 |
| raw5 | 1 | 0.085473 | 0.081969 | 1.042748 |
| raw5 | 8 | 0.161122 | 0.163377 | 0.986198 |
| raw5 | 32 | 0.202977 | 0.214993 | 0.944110 |
| raw5 | 128 | 0.230752 | 0.235745 | 0.978820 |
| raw5 | 4096 | 0.554293 | 0.515732 | 1.074769 |

## Raw5 versus the measured raw3 candidate

Split-control spread is max(split_raw3,split_raw5)/min−1 and includes tuner/process/order variation; it is not an error bar on Mega.

| Global tokens | Raw2 Mega ms | Raw3 Mega ms | Raw5 Mega ms | Raw5 reduction vs raw3 | Raw5 reduction vs raw2 | Raw3/raw5 split spread |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 0.108608 | 0.102480 | 0.081969 | 20.01% | 24.53% | 5.89% |
| 8 | 0.218801 | 0.177778 | 0.163377 | 8.10% | 25.33% | 2.14% |
| 32 | 0.292419 | 0.222241 | 0.214993 | 3.26% | 26.48% | 1.39% |
| 128 | 0.346786 | 0.261378 | 0.235745 | 9.81% | 32.02% | 1.11% |
| 4096 | 0.655702 | 0.537045 | 0.515732 | 3.97% | 21.35% | 0.15% |

Raw5 has a same-run advantage over split at T1 and T4096 and remains slower at T8/32/128. T1 had large variation across prior runs; retain that caveat. The final repeated full sweep must establish any stable split-beating claim. Raw3-versus-restored-raw2 historical details remain in RAW_DEPTH_COMPARISON_001.md.

## Actual split tactics

All 120 setup selections are preserved in rank0…rank7 order. Each cell gives FC1 M×N×K / FC2 M×N×K, with cluster(2,1),raster_along_m=true. The boolean is not the two-CTA flag; local M128 uses one-CTA instructions and M256 uses two-CTA. Tuner outputs are observed, not fixed.

| Run | Global tokens | Rank0…rank7 FC1/FC2 tactics |
| --- | --- | --- |
| raw3 | 1 | 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256 |
| raw3 | 8 | 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256 |
| raw3 | 32 | 128×16×256/128×16×256; 256×16×256/256×16×256; 128×16×256/128×16×256; 128×16×256/256×16×256; 128×8×256/128×8×256; 256×16×256/128×16×256; 128×16×256/128×16×256; 256×16×256/128×16×256 |
| raw3 | 128 | 128×16×256/128×16×256; 256×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 256×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256 |
| raw3 | 4096 | 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256 |
| raw2 | 1 | 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256 |
| raw2 | 8 | 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256 |
| raw2 | 32 | 128×8×256/128×8×256; 256×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/256×16×256; 128×8×256/128×8×256; 256×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256 |
| raw2 | 128 | 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256 |
| raw2 | 4096 | 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256 |
| raw5 | 1 | 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256 |
| raw5 | 8 | 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256 |
| raw5 | 32 | 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 256×16×256/128×16×256; 128×16×256/128×16×256; 256×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256 |
| raw5 | 128 | 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256 |
| raw5 | 4096 | 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256 |

## Codegen boundary

All 24 rank captures at depths 2/3/5 retain REG128/STACK112/LOCAL0,96-byte PTX local depot,40PTX local operations and21SASS local operations in the existing FC2 router footprint. No new transform local instructions appear. Per-role setmax targets are unchanged: control80,epilogue176,dispatch64,transform launch128. Static instruction counts are 6000/6016/6056; all 256 decode instructions and source-attributed transform opcode counts are identical after removing PCs.

The same R20 dependency has 85 instruction-slot distance: raw2 LDS0x6350→F2FP0x68a0,raw3 0x6410→0x6960,raw5 0x6590→0x6ae0, with no intervening textual control transfer. This is staging evidence with unchanged decode arithmetic; no prior PC sample count is transferred to a candidate binary.

- Source-correlated reports: `profiles/codegen-comparison/raw-depths.json` and `.md`; configuration/snapshots are alongside.
- Reproduce: `python3 compare_raw_depth_three.py`.
- Raw 30 timing rows: `logs/raw-depth-paired-002.raw.csv`; all raw/derived values, 120 actual tactics and provenance: `logs/raw-depth-paired-002.comparison.json`.
