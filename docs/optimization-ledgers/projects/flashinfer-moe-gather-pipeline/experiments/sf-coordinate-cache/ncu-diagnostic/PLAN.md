# Held N3U FC1 paired diagnostic

Four source reports: N3U W4A4 T16384, EP8 and TP8, each current c1ac control versus rejected15d6 candidate. No source, compiler, tactic, graph, math or timing-policy change. The complete56-cell primary remains immutable and rejected.

| Scope | Frozen FC1 | Frozen FC2, retained in public graph | Primary CAAC observation |
|---|---|---|---|
| EP8 | M512/N128/C2, K256,4 stages, static persistent | M256/N128/C2 | +4.748737%; FC1 exposed−25.232µs |
| TP8 | M128/N256/C1, K256,4 stages, static persistent | M256/N256/C2 | −4.687648%; FC1 exposed+55.721µs |

Both reuse the exact recorded route IDs/weights and public winner entries from `evidence/sf-coordinate-cache-screen/1793411008505163000/data`. `plan.json` carries each exact tactic/route/source binding. No FC2 retune result is substituted.

## Minimal adaptation

- Reuse `profiling/n3u-tp-w4a4-16k/retained-2b8/run_ncu.py` and its `profile_pc_entry.py`, changing only topology/role/source/leaf/current head and canonical cache environment. Keep the passive tactic/route guards, normal compile options, original returned-library capture and exact FC1 selection.
- Reuse the already working combined `--section SourceCounters --metrics ...` pattern from `experiments/paired-4over6-error/isolated-intermediate-ncu/run.py`: one report per topology/arm, four reports total. Keep the established ~20 aggregate metrics (issue/tensor, long/short scoreboard, MIO, barrier/wait/math throttle, executed instructions, global sectors, DRAM/L2 traffic and throughput, register/shared launch data). Do not collect the full section set or add a second profiler campaign.
- Use current `performance/harness/register_guard.py` unchanged, with c1ac/15d6 source records and original resource checks. Copy helper files only into this diagnostic leaf; never edit a historical profiler or production source.
- Run serially on fresh-idle GPU3, control then candidate for each topology. No other GPU timing during profiling. Each NCU application replay uses one captured steady-state public graph iteration after the existing three profiler-path warmups and existing L2 flush. The benchmark `--warmup 10 --iters 100` arguments remain conventional but are not the profiling-path warmup count; this is not a new CAAC run.
- Reuse warmed private workspace/CuTe roots from the screen, with `FLASHINFER_CUBIN_DIR` fixed to the canonical shared cubin path and private `generated` links resolving to the canonical directory. Bind `cache-ready-current.json` ad6b3a6d/readiness e466ac7c, including adopted moe_utils046552b8. Existing actual-arm normal loads, generated Ninja equality/no-op and ELF hashes must pass before profiling and remain unchanged afterward. Full source inventories are checked before/after the bounded diagnostic; normal per-process source guards remain.

## Evidence and interpretation

Capture the actual returned FC1 PTX/cubin/SASS and driver resources for every NCU application replay, with unchanged options. Verify same-arm replay image identity and bind every exported source PC/instruction to that image using the existing bounded display normalization. No forced compilation or changed optimization flags to obtain artifacts. If the normal path cannot provide the actual FC1 image, stop at that concrete boundary rather than introduce a new capture framework.

Map coordinate `LDS.128` → dependent `R2UR` → `UTMALDG.GATHER4`, publication `STS`/warp synchronization, SF `cp.async` issue/completion, producer-empty waits, consumer-ready waits and epilogue dependencies separately. Read SourceCounters' actual shared wavefront/excess information at each coordinate load; distinguish per-warp conflict from possible inter-warp service pressure. EP packet count4 versus TP16 is an address-pattern difference, not a bank-conflict diagnosis. Preserve all PCs and raw counters; sampled stalls are neither latency measurements nor additive time fractions.

The existing command is application replay with **node-level FC1 selection**, not range or whole-graph profiling. Nsight Compute serializes kernel launches for this collection, so it **does not preserve the production FC1/FC2 PDL overlap**, despite replaying the original graph with PDL enabled. This can compare the target FC1's native work/dependencies under the same profiler conditions, but cannot establish a full-chain overlap/interference mechanism. Profiler durations are diagnostic and cannot replace the56-cell CUPTI results. [NVIDIA serialization documentation](https://docs.nvidia.com/nsight-compute/ProfilingGuide/index.html#serialization).

No GPU command has been launched for this plan. Rejection closure is additive at `../performance-rejection.json`; parent review precedes deployment.
