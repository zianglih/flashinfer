# Fresh R2 tail-variant retention review

Recommendation: retain the original `cd7cc07` implementation and reject all three focused candidates. Every candidate is slower in every pooled shape. No candidate/shape improves in both first and reverse order. The native instruction reductions are real, but the measured public-forward results do not establish a benefit for accepting the wider contract and associated tail changes.

This is an independent analysis recommendation; it does not itself modify the source or PR.

## Measurement and evidence

- Host: `hu-pdx-43`, replacement C2 devbox. All eight phases ran on this host. No measurements from the interrupted `hu-pdx-38` campaign enter these pools.
- Order: A1/B1/C1/D1/D2/C2/B2/A2. Uniform EP4, H6144/I2048/E256/top8, global T128/4096/8192/16384.
- Unchanged benchmark worker: eight-candidate native AUTO per fresh phase, fresh process and caches, three warmups, 100 untrimmed cold-L2 CUDA-graph CUPTI samples per phase/shape, each sample the maximum over ranks. Pooled medians use 200 samples from each source's own two phases.
- Full frozen audit and independent raw-sample arithmetic review pass: 8 phases, 32 cold rows, 3,200 cold rank-MAX samples, 10,240 hot tuner rank samples, 128 selected winner exports, 32 T128 independent-reference rank records and 128 finite/repeat output records. Input, route, weight and output hashes agree across all eight phases.
- Each phase's separate source-bound native codegen audit passes. All 128 selected winners have zero stack/local allocation and no native LDL/STL or PTX local accesses. This is selected-winner coverage, not every compiled AUTO candidate; the user's full catalog zero-spill condition remains unqualified.

## Pooled results

Speedup is original/candidate; above 1 is faster. Times are microseconds.

| Global tokens | Original A | B late/no-prefetch | C late/participant96 | D score-only | A/B | A/C | A/D |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 128 | 282.5140 | 283.9380 | 283.2345 | 284.3075 | 0.994985 | 0.997456 | 0.993692 |
| 4096 | 594.0070 | 596.3880 | 595.2690 | 597.1895 | 0.996008 | 0.997880 | 0.994671 |
| 8192 | 1141.3510 | 1146.7760 | 1148.5705 | 1143.3855 | 0.995269 | 0.993714 | 0.998221 |
| 16384 | 2346.0065 | 2352.4935 | 2364.4450 | 2368.0710 | 0.997243 | 0.992202 | 0.990683 |

The early C T128 observation was not stable: A1/C1 was 1.021020, whereas A2/C2 was 0.986194. C rose from 277.0425 to 286.2420 microseconds (+3.321%) while AUTO switched G1024 to G512. The baseline used G512 both times and fell by 0.204%. Pooling the actual 200 samples gives 0.997456, not a gain. Averaging the two displayed run medians would not reproduce the canonical pooled statistic.

Baseline A1-to-A2 latency changes for T128/4096/8192/16384 were -0.204%/-0.337%/-0.484%/+0.017%. Baseline tactics changed at T4096 and T16384. Candidate tactics also changed across repeats at several shapes. At T8192 every phase used the same recorded N128/G1024/reuse-dispatch tactic, and all three candidates still had pooled ratios below 1. No trimming, outlier deletion, tactic filtering or drift correction was applied.

Small differences must not be attributed entirely to kernel source changes: AUTO winner changes and temporal drift are visible. The defensible conclusion is lack of a demonstrated repeatable gain, not a precise causal slowdown estimate. These uniform results do not replace a native EP4/EP8 broad benchmark and establish no decode geometric mean.

## Preserved artifacts

- `tail-variants-focused-r2-audit-v1.{json,md}`: frozen full auditor output, exact source identities, all raw samples and comparison pools.
- `tail-variants-focused-r2-review-v1.{json,md}`: independently recomputed medians, all eight phase medians/tactics, first/reverse ratios, baseline/candidate repeat drift and tactic match status.
- `tail-variants-focused-r2-progress-v1/`: additive completed-phase snapshots, transfer closures and separate native codegen audits.
- `tail-variants-focused-r2-complete-v1.tgz`: complete immediate evidence archive, SHA256 `df79d8599d3da411e629793eb7810eafcb3529d56b4ba30904b4bbc440f4dde6`.
- `tail-variants-focused-r2-final-transfer-v1.json`: final closure. Campaign SHA256 `723c19deb912ae20a69b1a7096c11467c360d5188d85134e2418b7738f624b18`.

Archive and campaign hashes were independently rechecked after completion. Frozen worker, runner, auditor and source-manifest hashes remain unchanged. The original remote campaign was not mutated during collection. Compiler cache bulk was excluded from the transfer; every measured winner's PTX/CUBIN/SASS/resource/target artifact was retained.

The earlier interrupted host campaign, wide-compound A1/B1 screening, original128 controls and fixed diagnostic studies remain separate and unchanged. No further GPU qualification was launched by this reviewer.
