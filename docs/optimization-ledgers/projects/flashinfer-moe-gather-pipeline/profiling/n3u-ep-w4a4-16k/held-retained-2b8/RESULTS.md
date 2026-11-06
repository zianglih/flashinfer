# N3U EP8 T16384 W4A4 FC1: retained wide-M diagnosis

**No new optimization is justified by this pass alone.** The current wide FC1 has substantial readiness/backpressure and epilogue work, but the native gather task-bound predicate is already eliminated, SF request issue is a small sampled MIO contributor, and the final barrier samples are expected role-join observations rather than an in-loop synchronization target.

## Exact scope

- Retained source `2b8eb9d8f72ceda3952fbb05054fee97173fc9c7`; swap kernel `482b636a1714486e2ffb34c8ae005da3cef26f25f0ce034ba1eb59c6198d6276`. Both source pre/post checks cover all 13,245 tracked files; per-process guards cover the source-relevant 71 files. No source or compiler options changed.
- Recovery C2 B300 GPU3, UUID `GPU-ee4aef4a-e7f5-91fb-213c-d87a88482df1`, `nvcr.io/nvidia/pytorch:26.05-py3`, driver 595.91.07. Existing release C++ ELF/Ninja bytes are unchanged. Both timing owners released their GPUs before PC profiling; GPU3 is now idle/released.
- N3U EP8 / TP1, 16,384 tokens, W4A4, initial activation quantization included. The original recorded route and tactic are replayed with no tuning: route block128, FC1 logical M512/N128/C2/K256 (four operand stages), FC2 M256/N128/C2. The later same-source FC2 M512 selection was not substituted. Static persistent scheduling, PDL and existing gather/epilogue behavior remain unchanged.
- FC1 actual library: cubin `19296983d93f5f56265cc3ee423f2edd340a853ba885eaaab0a5362a07f5b3d7`, 168 initial registers, 384 maximum threads, zero local memory. All five metric replay images and all four PC replay images are identical. PC comparison validates all 4,088 instruction addresses/operands, including predicate and geometry spelling, with only explicitly recorded display normalization.
- NCU is diagnostic application replay with the public profiler start/stop boundary and first matching FC1 launch. These numbers do not replace any benchmark table or CUPTI samples. `fc1-metrics/raw.csv` and `fc1-pc/source-sass.csv` preserve the native raw output.

## Metrics

The isolated profiled FC1 duration is 290.176 us. Tensor activity is 26.52%, DRAM throughput 25.56%, L2 throughput 41.23%, L2 hit rate 72.34%, and issue activity 32.57%. Long scoreboard is 53.98%, MIO throttle 2.00%, barrier 13.59%, short scoreboard 6.47%, wait 5.35%. Dynamic shared memory is 189,440 B (190,464 B allocated including runtime overhead); the grid has 148 CTAs / 74 two-CTA clusters.

For context only, the older TP M128/N256/C1 profile had tensor16.24%, DRAM14.90%, MIO9.81%, barrier8.90%. It differs in topology, geometry and source cohort; this is not a causal before/after comparison. The current wide EP image does not reproduce that high MIO pressure.

## Actual native PC attribution

The table counts sampled stalled-warps at native instruction sites. Counts are not time shares, are not additive to a critical-path estimate, and do not identify which asynchronous producer caused every scoreboard dependency. Different role widths also make direct role-count comparisons misleading.

| Native dependency / instruction group | Long scoreboard | Short scoreboard | MIO | Barrier |
|---|---:|---:|---:|---:|
| Weight operand reuse | 959 | 0 | 0 | 0 |
| Gather operand reuse | 2,381 | 0 | 0 | 0 |
| Gather-completion relay | 1,099 | 0 | 0 | 0 |
| MMA accumulator reuse | 228 | 0 | 0 | 0 |
| MMA weight readiness | 46 | 0 | 0 | 0 |
| MMA gather readiness | 199 | 0 | 0 | 0 |
| Epilogue accumulator readiness | 436 | 0 | 0 | 0 |
| Epilogue TMEM loads | 743 | 362 | 0 | 0 |
| Epilogue TMEM stores | 0 | 197 | 0 | 0 |
| SF cp.async issue | 0 | 0 | 34 | 0 |
| SF cp.async completion | 0 | 0 | 95 | 0 |
| Gather4 issue | 0 | 0 | 34 | 0 |
| Final CTA join and deferred consumers | 0 | 0 | 0 | 2,480 |

- **Operand backpressure is real, but required.** Gather producer empty waits are the two polling sites at `0xe880/0xec70` and their slow loops, backed by operand-empty barriers at offsets32–56. Weight producer reuse waits use the same released operand stages. Completion relay waits track the separate gather-local barriers96–120, then publish gather-full barriers64–88. MMA first waits for the weight stage, publishes weight SF to TMEM, and then waits for gather-full before activation SF/MMA. None of these source dependencies is proven redundant by a stall count.
- **Accumulator reuse is already overlapped.** The MMA waits on accumulator-empty `+0x88` at `0x3500`; epilogue waits on accumulator-full `+0x80` at `0x3fb0`. Logical M512 uses one accumulator stage and the existing protected-column overlap layout; a second complete accumulator bank does not fit beside the scale storage. The epilogue already releases after its protected TMEM reads, before all subsequent quantization/stores finish. This pass is not evidence to undo that lifetime contract or add another staging policy.
- **The final barrier stalls are deferred.** `0xf070` is `BAR.SYNC.DEFER_BLOCKING 0x1, 0x180`; all 2,480 final barrier samples occur at its predicated `EXIT` consumer at `0xf090`. Static scheduling leaves warp3 inactive and branches it directly to this join, and other roles can finish earlier than epilogue. PC data does not identify the particular warps behind these observations, so it cannot quantify a removable tail or justify deleting the CTA/TMEM lifetime join. The only other22 barrier samples are in startup.
- **Some long scoreboard observations are metadata/ownership dependencies.** For example, `0xe410` consumes the per-tile row-count LDG at `0xe3f0` (596 long samples); `0xe5e0` consumes the routed-token map LDG at `0xe520` (212). Other hot uniform-register consumers such as `0xe860` and `0xeca0` are not themselves memory loads, so they must not be labeled as separate DRAM latency. The existing chain includes required metadata lookup and gather coordinate construction.
- **Gather task bounds are compiled away.** All eight static `UTMALDG.2D.GATHER4` instructions at `0xec30`–`0xec60` and `0xefc0`–`0xeff0` are unpredicated. The source `task < tasks` contributes no dynamic bound check in this wide specialization; changing source to special-case it would add maintenance cost without removing native work.
- **No SF coalescing prototype now.** The source-only four-lanes-per-SF-row mapping in `audits/sf-coalesced-lanes/` could reduce repeated sector requests, but adds offset ownership/registers and canonical shared-bank collisions. Here its actual cp.async issue has34 MIO samples and completion95, versus347 total MIO samples and MIO2.00% in the metrics pass. This is insufficient evidence that the extra source/ownership cost would improve the wide EP case.
- **No native-output ownership retry now.** TMEM load/store observations show epilogue work but do not contradict the prior post-gather direct-native ownership experiment's large, stable losses. Avoid repeating that closed approach without a distinct, validated work-removal mechanism.

## Reproducibility and limitations

`controller.py` / `controller_pc.py` preserve the original source, native cache and frozen selection; `run_ncu.py` invokes the installed profiler without changing compiler options. `analyze_metrics.py` binds metric replays; `analyze_wide_pc.py` binds every PC and exact barrier/role dispatch; `write_results.py` generates this report. The metric summary predates PC capture and retains its then-current status; this completed report and PC controller receipt supersede only that status, not its data. Full paths, commands, original stdout, archives, source manifests, cache checks and GPU release are local evidence. No sanitizer, source optimization, retune, benchmark replacement or additional profiling was performed.
