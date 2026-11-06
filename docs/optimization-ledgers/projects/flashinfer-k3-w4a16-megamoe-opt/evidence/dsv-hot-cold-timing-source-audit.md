# DeepSeek AUTO selection versus final CUPTI timing

Read-only source audit; no timer, catalog, kernel, or GPU changes. The compared source is captured by `next-cross-model-validation-v1/source-maps/expanded24.json`; the native benchmark overlay is `cd70541b397a6c278219e1f8bacc7941d0e3903618f88448e1a7aad29d8e2726`.

The autotuner and final benchmark have distinct timing objectives, already present in the original methodology:

| Property | Native AUTO selection | Final reported benchmark |
|---|---|---|
| Entry point | Direct `bf16_nvfp4_mega_moe` wrapper on staged inputs | `layer.forward(tensors)` |
| Preparation | 3 eager forwards per tactic, then 6 untimed graph replays | Native layer warmup, 3 driver warmups, utility graph preparation and estimate |
| Samples | 10 CUDA-event graph replays | 100 CUPTI graph activity spans |
| L2 | No flush between repeated inputs | A 2×L2 flush before each measured replay, outside measured activity span |
| Rank aggregation | Maximum of each rank's median | Median of per-iteration maximum across ranks |
| Replay pacing | Event pairs and graph replays enqueued in a loop, one final synchronization | Synchronization before and after each replay |

Source anchors:

- `flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/autotune.py`: `_sample_graph_seconds` and `autotune_bf16_nvfp4_mega_moe` implement hot replay timing, rank median/MAX scoring, and winner application.
- `benchmarks/bench_cute_dsl_moe_distributed.py`: `_benchmark_distributed_megamoe` constructs seeded inputs and precomputed routes; `_run_distributed_iterations` requests `enable_cupti=True`, `cold_l2_cache=True`, `aggregate_op=max`, graphs, and 100 samples.
- `flashinfer/testing/utils.py`: `bench_gpu_time_with_cupti` flushes, synchronizes, replays, and computes first-to-last GPU activity span; it aggregates each iteration across ranks afterward.
- `flashinfer/moe_ep/modes/mega_layer.py`: `forward` allocates an owned output and calls `stage_inputs` before `compute`.
- `flashinfer/moe_ep/backends/mega/kernel/sm100/bf16_nvfp4_bf16_cutedsl/backend.py`: `stage_inputs` copies FC1/FC2 scale arrays on each ordinary forward. `compute` invokes the tuner after staging; the tuner replays the lower-level wrapper without repeating this outer staging call. Input staging sources remain retained for each wrapper replay. The scale-copy difference is common to tactics, but the timed scopes are not identical.

A 0.8% hot-score advantage does not imply the same cold-L2 rank-MAX result. Cache reuse, replay pacing, rank variability, sample count, and timing scope can all affect a close ranking. The saved rounded selection scores cannot establish which mechanism caused a particular final-sample regression. The scheduler delta also remains a hypothesis until controlled measurement.

The static FC1 scheduler divisor is `ceil((2E) / cluster_feature_tile)`. Both M128/C2 without 2CTA and M256/C2 with 2CTA have a 128-row CTA feature tile and a 256-row cluster feature tile. DeepSeek E=2304 therefore gives 18; GLM5 gives 16; K3 gives 24. DeepSeek's divisor is not a power of two, but K3 already exercised a non-power-of-two divisor. No compiled instruction count, register-pressure change, or causal cost is inferred from that alone.

For the T32 M128/N32/G1024 winner, the parent/ledger audit establishes at most one token block per expert and 48 local experts, so FC1 work is at most 48×18=864 tiles, below the 1024 group threshold. The prefix shortcut is therefore not repeatedly opening additional groups at this point. Any scheduler-linked effect would need a different explanation, such as compiled code or register effects, confirmed by a controlled comparison.

The prepared diagnostic is `next-dsv-scheduler-ab-v1`: one complete 13-point fixed-winner sweep on the updated scheduler, then one on the original scheduler. Both use the exact same per-token winner map from the completed full24 scan and the same native fixture/timer. Their source maps differ only in `fc1_fc2_fuse_sched.py`. This removes AUTO-versus-fixed preparation history from the scheduler comparison while retaining the old AUTO capture as context. It does not change the production selection or timing methodology, repeat the original BEFORE AUTO sweep, or omit prefill points.
