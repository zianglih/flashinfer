# N3U TP8 MXFP4x8 at 32 tokens: retained native diagnosis

The case streams substantial weights even at 32 tokens. Both FCs read approximately 269 MB, close to the 268.08 MB of unique packed weights and weight scales implied by the saved route. FC1 combines that traffic with Gather4 and a larger quantized epilogue; FC2 has a visible scalar-alpha load dependency. The capture does **not** establish a new general simplification or justify a stage-policy change. Existing alpha-prefetch and cache-policy experiments must not be repeated as new mechanisms.

## Scope and native timing

Source: retained `49c91adf47d30fc2049c76cbaf34d0ccf3291434`, through the immutable, actually measured `bf072d26 + 482b636a` snapshot. All 13,245 inventory files match the retained commit. GPU4: `GPU-bab88130-5692-5702-ff8d-8f2f966ed945`, B300, `fi-gather-pipeline-1030`, C2/ziangli. The frozen public choice, routes, compiler flags and persistent release C++/CuTe caches were preserved. No source edits, new tactics, clock changes, iKET instrumentation, or external-baseline reruns.

The existing exact-source integer-store campaign supplies 200 strict cold-L2 CUDA-graph CUPTI samples; no new native timing run was necessary. The two candidate medians are 125.697 and 125.4405 us, aggregate **125.5687 us**, repeat spread **0.2045%**, observed SM clock 2032 MHz/reason0. Historical TRT is 115.8727 us, the requested **−7.722%** ranking signal; it remains a reused historical comparison, not a new causal backend experiment.

| Native component | Pass1 duration / exposed extension (us) | Pass2 duration / exposed extension (us) |
| --- | ---: | ---: |
| Routing | 8.8635 / 8.8635 | 8.8155 / 8.8155 |
| FC1 | 63.8725 / 63.7445 | 64.2560 / 64.0965 |
| FC2 | 69.6480 / 46.1115 | 69.4240 / 45.4400 |
| Combine | 9.1520 / 7.0080 | 9.1200 / 6.9925 |

Extensions are recomputed per sample against the preceding activity end; there are no uncovered gaps. Component medians should not be summed into an exact median DAG. FC2 overlaps FC1, and combine overlaps FC2. `analyze_cupti.py` and `native-cupti.json` preserve all samples and source/route joins.

## Actual geometry and storage

| Property | FC1 | FC2 |
| --- | ---: | ---: |
| Logical channel M | 128 | 128 |
| Physical MMA M / channel tiles | 128 / 1 | 128 / 1 |
| Recorded route N / allocated TMEM N | 16 / 32 | 16 / 32 |
| Operand B copy rows | 32 | 16 |
| K per stage / K stages per work tile | 256 / 8 | 128 / 5 |
| Operand stages / accumulator stages | 5 / 2 | 10 / 2 |
| Accumulator columns / total TMEM columns | 32 / 128 | 32 / 128 |
| Threads per CTA / grid CTAs | 384 / 148 | 256 / 148 |
| Initial registers / driver local bytes | 168 / 0 | 72 / 0 |
| Dynamic shared bytes | 215,936 | 215,936 |
| SMEM-limited CTAs per SM | 1 | 1 |
| Register-limited CTAs per SM | 1 | 3 |
| CLC / accumulator overlap | false / false | false / false |

Do not infer M256 from FC1's shared bytes. Mixed-input unpacking gives A **Int8 shared storage for packed FP4 weights**; it is not doubled channel M or activation storage. FC1 per-stage storage is 32,768 B A + 8,192 B B + 2,048 B SF = 43,008 B; FC2 is 16,384 + 4,096 + 1,024 = 21,504 B. Both use 215,040 operand bytes plus 896 metadata/scratch bytes. The native resource values are captured from the returned compiled callable, not inferred from the logical tactic. Pipeline indices carry across work tiles; FC2's ten physical stages are not ten stages of one five-stage work tile.

The saved route has 704 assignments and 385 active experts; per-expert counts are 175×1, 130×2, 58×3, 17×4, 4×5, 1×7, plus127 empty experts. Runtime MMA N rounds each live expert to8, while recorded N16 remains unchanged. There are 1,925 FC1 work tiles (385×5 channel tiles) and 6,160 FC2 work tiles (385×16). This sparse output geometry does not make the workload automatically scheduler-bound.

## Native NCU counters

Application replay profiles one selected kernel at a time. These durations and sample counts are diagnostic and do not replace the native CUPTI values above.

| Counter | FC1 | FC2 |
| --- | ---: | ---: |
| Diagnostic duration (us) | 67.360 | 51.936 |
| DRAM read / write (decimal MB) | 268.557 / 10.471 | 269.480 / 5.382 |
| DRAM sustained-peak throughput | 54.01% | 69.03% |
| L2 hit / sustained-peak throughput | 27.21% / 34.67% | 31.72% / 45.42% |
| Warp instructions executed | 8,500,620 | 7,593,916 |
| Issue-active | 15.03% | 15.35% |
| Long / short scoreboard | 73.33% / 2.35% | 60.25% / 6.31% |
| MIO throttle / math throttle | 0.92% / 0.22% | 0.97% / 0.19% |
| Active warps per scheduler | 3.00 | 2.00 |
| Tensor-pipe sustained-peak activity | 2.58% | 3.40% |

Each FC's logical unique weight traffic is `385×640×2048/2 = 252,313,600 B`; weight SF adds `385×640×2048/32 = 15,769,600 B`. Their 268,083,200 B sum closely matches measured reads. This is a source-byte estimate, not per-operand attribution by the DRAM counter. Activation and metadata payloads are much smaller. FC1's lower bandwidth is consistent with more exposed dependent work, but the available counters do not isolate the causal cost of its five-stage queue versus Gather4/epilogue work. No stage sweep is warranted from this observation alone.

## Exact PC and dependency attribution

All 2,072 FC1 and 1,224 FC2 PC rows match the actual loaded native ELF, after explicit display-only NCU/cuobjdump address/operand normalization. Across all 18 application-replay processes, the same FC1 and FC2 ELF hashes recur (36 loaded images), with unchanged driver resources and LOCAL0. `analyze_pc.py` saves the exact probe, consumer branch, slow-loop instructions and barrier offsets for each group.

| Selected dependency/issue sites | FC1 samples (of3,343) | FC2 samples (of2,922) |
| --- | ---: | ---: |
| Epilogue accumulator-ready wait | 938 | 463 |
| Gather/activation operand-empty wait | 577 | 348 |
| Weight operand-empty wait | 239 | 184 |
| Gather completion relay | 287 | — |
| MMA weight/operand-ready wait | 114 | 117 |
| MMA gather-ready wait | 71 | — |
| MMA accumulator-empty wait | 0 | 18 |
| Terminal CTA join | 332 | 435 |
| Scalar expert-alpha load consumer | 41 | 366 |
| Gather route-ID load consumers | 53 | — |
| Valid-row metadata consumer (gather / MMA) | 45 / 0 | — / 112 |
| Weight cache metadata consumer | not singled out | 132 |
| Gather4 issue instructions | 3 | — |
| Scale S2T issue instructions | 6 | 4 |
| MMA issue instructions | 26 | 12 |
| PDL acquire instructions | 0 | 0 |

These are sampled warp observations, **not duration fractions**; FC1 has four gather and four epilogue warps but one MMA warp, so raw totals cannot rank critical-path costs across roles. Terminal samples are on the consumer after `BAR.SYNC.DEFER_BLOCKING`; they show role-arrival imbalance, not permission to remove the join. The small MMA accumulator-empty counts do not identify epilogue backpressure as the main exposed limiter. Low samples on issue instructions and low MIO throttle do not prove a TMA queue is never limiting; readiness/reuse dependencies are the larger observed sites. No CLC scheduler executes in this static tactic.

The hot FC2 `FMUL2` at0x37a0 is a **global scalar-alpha dependency**, not evidence of TMEM bandwidth saturation. Its `R68` comes from `LDG.E` at0x3540, which assigns dependency barrier2; the FMUL waits mask0x4, with no intervening barrier2 reassignment/wait. The TMEM `R20→R58` move at0x35a0 independently waits mask0x8 earlier. FC1's corresponding alpha load0x3c60 and FMUL0x44e0 have the same barrier2 chain. Raw encodings and the replayable check are preserved in `summarize.py`/`analysis.json`. [NVIDIA's profiling guide](https://docs.nvidia.com/nsight-compute/ProfilingGuide/) explains why a dependent arithmetic instruction carries the sampled stall rather than the producing global load.

The other conspicuous scalar sites are already tile-invariant:

- FC2 neighbor-expert cache metadata consumer0x950 executes6,160 times, once per work tile. Its load/selection implements the retained route-aware cache policy; constant FIRST and NORMAL were both rejected in this project.
- FC2 `mn_limit` consumer0x2500 also executes6,160 times. It supplies the runtime valid-N MMA descriptor and is outside the five-stage K loop. Reusing it across roles would require a new publication/lifetime mechanism.
- FC1 gather `mn_limit` consumer0x5560 and route-ID division consumers0x5700/0x5710 execute7,700 times, four warps×1,925 work tiles, not once per K stage. The current cache already amortizes route extraction over K; batched route-ID changes are closed history.
- Scale S2T and MMA have low direct issue samples here. Their larger readiness waits and the weight traffic are real dependencies; scalar instruction counts alone do not establish a removable bottleneck.

## History boundary and conclusion

The most concrete scalar overlap idea is **not new**. Old-project `codegen-epilogue-prefetch-20261026/README.md` proves that moving expert alpha ahead of the accumulator wait worked in PTX/SASS for both FCs and narrow/wide NVFP4/MXFP8 cases, with unchanged occupancy and no spills. `perf-general-20261026/README.md` records completed bounded gains of roughly0.1–0.45% depending on mode and leaves that candidate unretained. The current profile supplies a measured dependency signal, but not a new mechanism or authority to rerun it. Separately, `optimization-20261027/epilogue/README.md` records rejection of the larger scatter-metadata preload rewrite; it explicitly removed the unrelated FC1 alpha change before its retained candidate screen.

Existing fixed weight cache policies, descriptor prefetch, live-group/route batching, terminal PDL removal, ownership rewrites and stage balancing remain closed. This diagnosis finds **no distinct, source-simple general optimization to propose now**. It does establish why tiny-token routing can still stream hundreds of MB, the actual M128×1 geometry, the exposed native FC1/FC2 extensions, and the scalar-alpha versus TMEM attribution boundary.

All four NCU calls completed; full source pre/post manifests, persistent release-library/Ninja fingerprints/no-op checks and GPU4 idle check pass. The initial missing dump-directory failure stopped before the first owned FC1 launch and remains in `closure/`; the successful retry only created that directory, with unchanged source/compiler/cache settings. GPU4 is released. `analysis.json`, `pc-analysis.json`, native raw CSV/NCU reports, every ELF/PTX/SASS, and `closure/r1/controller-receipt.json` are the audit entry points.
