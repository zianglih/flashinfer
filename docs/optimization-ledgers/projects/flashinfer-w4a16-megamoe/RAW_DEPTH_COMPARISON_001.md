# Adjacent raw-depth comparison: raw3 versus restored raw2

Raw3 reduces MegaMoE latency by 18.10–24.63% at global T8–4096 in this adjacent comparison. The observed T1 gain is 5.64%, while its split-control spread is 19.03%, so T1 does not support a robust gain claim. Both runs remain single 100-iteration measurements of each shape, with independent split tuning; no confidence interval is implied.

## Provenance and method

- Order: raw3 first, restored raw2 second; each has five global token counts, real EP8 on eight B300, H7168/I2048/E256/top-k8. BF16 activations/wire, NVFP4 packed weights, canonical matched weights/scales/routes, post-FC2 FP32 route weights. Existing split `--no-fused-finalize` reduction contract is preserved.
- Declared sources: raw3 `c7713ba1+raw3`, raw2 `c7713ba1`. All 16 recorded source hashes were independently checked against `git show c7713ba1` or the frozen raw3 kernel snapshot. The only recorded repository source difference is the kernel raw-stage-depth override. Remote Git HEAD remained `91bda04c66f7cb851e1ab3b78b9fecea644b9844`; source overlays determine execution.
- Raw2 kernel SHA256 `98e4694e90a48c14722fef1d32b1bbf5600537feb6bbe6e9420c9a853b7d4647`; raw3 `95f2cc38823c9c7e09a9659f84a294ffa80a31f87f4d934450fd7913b7ec8be9`.
- Identical knobs: `{"epi_flag_batch": [2, 4], "flag_batch": 4, "group_hint": 512, "load_balance_mode": "atomic_counter", "token_back_mode": "epi_warps"}`; M256/N128/K256 dynamic N, launch cap 128, one transform group, transformed-A/activation/accumulator rings remain two. Raw A+SF ring depth is the experiment.
- Three warmups, 100 fixed CUPTI iterations, CUDA graph, cold L2. Each measurement is the median of per-iteration maximum-rank kernel wall spans; tuning, compilation, setup and cache flush are excluded. Codegen capture timings are excluded. Numerical validation is separate; no tolerance relaxation or split reduction change was introduced.

## Complete raw paired timings

All values are ms. `Split/Mega` uses the same run and favors Mega above 1; ratios here are derived from the printed latencies.

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

## Controlled comparison

Control spread is max(split_raw2,split_raw3)/min−1. It includes separate autotuning/process/order variation; it is not an error bar on Mega.

| Global tokens | Raw2 Mega ms | Raw3 Mega ms | Raw3 latency reduction | Raw2/Raw3 | Split control spread |
| --- | --- | --- | --- | --- | --- |
| 1 | 0.108608 | 0.102480 | 5.64% | 1.0598 | 19.03% |
| 8 | 0.218801 | 0.177778 | 18.75% | 1.2308 | 2.47% |
| 32 | 0.292419 | 0.222241 | 24.00% | 1.3158 | 0.71% |
| 128 | 0.346786 | 0.261378 | 24.63% | 1.3268 | 0.72% |
| 4096 | 0.655702 | 0.537045 | 18.10% | 1.2209 | 2.59% |

Raw3 remains slower than split at T1/8/32/128. At T4096 its 0.537045 ms is below the same-run split 0.555141 ms, or 1.0337× split/Mega; this narrow single-run advantage needs repeated evidence before treating it as a stable split-beating result. The raw-depth gain is materially larger than the observed split spread at T8–4096.

## Actual split tactics

All 80 setup selections are preserved below by rank. Each tuple also has cluster(2,1) and raster_along_m=true. Each cell is FC1 M×N×K / FC2 M×N×K, rank0…rank7; M128 means one-CTA instructions, M256 means two-CTA. These are actual rerun tuner choices, not frozen tactics.

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

## Source-correlated codegen

The adjacent `profiles/tmem-raw2-control-codegen-001` and `profiles/tmem-raw3-codegen-001` use the same dynamic-N/scheduling/compiler settings. Each has eight rank artifacts. Both report REG128/STACK112/LOCAL0, 512 threads, a 96-byte PTX local depot, 40 PTX local operations and 21 SASS local operations. The explicit FC2 router footprint and role register targets are unchanged, with no new transform local instructions. Total static SASS grows from 6000 to 6016.

The sampled raw2 F2FP at 0x68a0 becomes 0x6960 in raw3. Both read R20 produced by LDS.128, at 0x6350/raw2 or 0x6410/raw3. Both have a distance of 85 instruction slots and no textual control transfer; preceding STTM.x8 stores still use R4. Source-correlated transform opcode counts remain identical. This supports unchanged decode arithmetic with a staging change; it does not turn a long-scoreboard sample into proof of pure decode-throughput limitation.

- Detailed per-PC/role codegen: `profiles/codegen-comparison/raw2-vs-raw3.json` and `.md`.
- Reproduce analysis: `python3 compare_raw_depth.py`; codegen: `python3 compare_public_codegen.py profiles/codegen-comparison/raw2-vs-raw3.config.json --output profiles/codegen-comparison/raw2-vs-raw3.json`.
- Raw 20 latency rows: `logs/raw-depth-paired-001.raw.csv`; raw/derived values, all 80 tactics, source hashes and exact commands: `logs/raw-depth-paired-001.comparison.json`.
