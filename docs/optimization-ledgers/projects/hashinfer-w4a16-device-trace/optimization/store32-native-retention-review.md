# Store32 native audit and retention recommendation

Recommendation: **reject Store32 and keep R1/store16 as the retained parent**. All requested sweeps completed and their audits passed. EP4 decode improves slightly, EP8 decode regresses, and the uniform target has no measured benefit. This does not justify replacing the previous retained step.

| Workload | Store32 speedup vs R1/store16 |
|---|---:|
| Native EP4 decode, global T4–512 geometric mean | 1.010772x |
| Native EP8 decode, global T4–512 geometric mean | 0.985816x |
| Uniform GLM5 target EP4, global T1024 | 0.997292x (329.827 → 330.723 us) |

Native dimensions are **H7168/I2048/E256/K8**. The separate uniform target is H6144/I2048/E256/K8, 256 tokens/rank. Each native result uses 100 untrimmed cold-L2 CUDA-graph CUPTI samples per row, after three warmups; a sample is the per-iteration maximum across ranks, and each table latency is its median. Ratios greater than 1 favor Store32. EPs are reported separately.

## All native rows

| Global tokens | EP4 store16 us | EP4 store32 us | EP4 speedup | EP8 store16 us | EP8 store32 us | EP8 speedup |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 67.841 | 66.385 | 1.021933x | 64.944 | 74.113 | 0.876284x |
| 2 | 93.936 | 88.577 | 1.060513x | 90.945 | 95.201 | 0.955294x |
| 4 | 119.185 | 116.337 | 1.024485x | 98.849 | 107.728 | 0.917575x |
| 8 | 159.138 | 147.345 | 1.080033x | 122.961 | 127.329 | 0.965695x |
| 16 | 196.258 | 201.362 | 0.974655x | 137.234 | 138.176 | 0.993175x |
| 32 | 269.443 | 259.874 | 1.036822x | 164.977 | 167.730 | 0.983590x |
| 64 | 294.435 | 302.755 | 0.972521x | 193.745 | 192.257 | 1.007737x |
| 128 | 320.212 | 320.323 | 0.999652x | 193.522 | 190.209 | 1.017420x |
| 256 | 330.323 | 331.507 | 0.996428x | 191.746 | 191.442 | 1.001588x |
| 512 | 346.707 | 344.692 | 1.005849x | 203.169 | 202.464 | 1.003482x |
| 4096 | 795.143 | 781.735 | 1.017152x | 460.692 | 453.220 | 1.016486x |
| 8192 | 1484.748 | 1432.588 | 1.036410x | 786.690 | 778.165 | 1.010955x |
| 16384 | 2857.385 | 2848.677 | 1.003057x | 1480.067 | 1495.976 | 0.989365x |

EP4 prefill T4096/T8192/T16384 ratios are **1.017152x / 1.036410x / 1.003057x**. EP8 prefill ratios are **1.016486x / 1.010955x / 0.989365x**. EP8 T4 is a same-tactic regression from 98.849 to 107.728 us (0.917575x); it cannot be explained by an AUTO winner change. EP4 also has slower T16/T64 rows despite its positive aggregate.

## Selected tactic changes

EP4 selects identical complete tactic dictionaries on every row. EP8 changes only `group_hint`:

| EP8 global tokens | store16 group | store32 group |
|---:|---:|---:|
| 1 | 512 | 1024 |
| 2 | 1024 | 512 |
| 8 | 512 | 1024 |
| 16 | 512 | 1024 |
| 64 | 512 | 1024 |
| 256 | 1024 | 512 |

N geometry, return mode, and remaining knobs are unchanged for each paired row. The comparison measures the complete AUTO policy, not a fixed-tactic isolated instruction latency. The copied caches match the final capacity-keyed winners (11 entries per EP4 arm, 10 per EP8 arm); multiple smallest global sizes share one capacity key. Cache event-timing scores are not substituted for the cold-CUPTI medians.

## Numerical, fixture and source audit

- Identical weight and input/routing hashes within each EP comparison; all **52 EP4 and 104 EP8 rank/shape output hashes match**. Every row reports finite outputs and repeated bit equality.
- Independent reference coverage in these native logs is **T128 only**: four rank checks per EP4 arm and eight per EP8 arm, all with zero mismatch/nonfinite. Output-hash parity at other token sizes is not independent-reference coverage.
- Both logs per EP contain `BENCHMARK_COMPLETE` and matching `EXPERIMENT_COMPLETE_JSON` source closure. Digests match the frozen source manifest; no traceback is present. Recorded host/boot/image/device inventory and software/timing contracts match.
- Environment: node `hu-pdx-38`, B300 SXM6 AC, `nvcr.io/nvidia/pytorch:26.05-py3`, Torch `2.12.0a0+5aff3928d8.nv26.05`, CUDA 13.2, CUPTI 13.4.0.
- These are one ordered before/after sweep per EP, with earlier retained-control logs and no reverse-order repetition. Temporal drift remains a limitation. The recommendation is based on the absence of a consistent incremental benefit, not a universal claim about x32 store performance.

```text
store16 7a48709ed07bc8496908625b921927b04dbcca495d7a3b1ced9a7bd28d072234
store32 a1a23c62aa625139bd41588d69c8d98e55c96b66dc0c94e6a361e321a0674244
```

## Instruction evidence and interpretation

The matched uninstrumented N64/G512 uniform-target SASS audit proves FC1 per-K **225 → 223** instructions and FC2 **231 → 226**. Both phases replace four x16 stores with two x32 stores, with the documented register/control deltas. These are real repeated-body reductions, not an inferred saving from the Python opcode name.

Whole-kernel static count increases **5112 → 5152 (+40)**, with most extra instructions in other regions. Those additions are not all once-per-kernel costs, and static totals alone do not establish dynamic cost. Decoder wait helpers remain unchanged five-instruction retry paths; both variants use REG96/STACK0 with no LDL/STL. There is no observed spill explanation for the timing. The matched audit is a specialization-specific code-generation result, not an audit of every native AUTO specialization.

The per-K savings and unchanged resources support testing Store32, which is now complete. They do not override the EP8 regression and flat uniform-target result. Proceed with subsequent experiments from store16, keeping Store32 artifacts as a rejected isolated step.

## Preserved evidence

- `store32-native-ep4-review-r1.{json,md}` and `store32-native-ep8-review-r1.{json,md}`: standard summarizer output, all samples, quarter medians, full tactic dictionaries and log hashes.
- `results/store32-native-ep{4,8}-after-r1.log` and their `-cache/hashinfer-knobs.json`; copy receipts verify the selectively fetched files.
- `store32-native-retention-review.json`: independent closure/cache/source/tactic audit.
- `native-codegen-followups.md`, `native-codegen-followup-analysis/comparison.json`, and `extra-regions.json`: exact instruction counts and matched artifact fingerprints.
- `store32-cumulative-summary.json`: separate uniform-target result.

Only the completed native log and knob-cache file for each EP were copied from C2. Existing causal reports were not overwritten. This auditor ran no GPU work and made no production-source edits.
