# FC2 K-tail fixed-tactic experiment

Source: `flashinfer-stage-capacity-ktail-review`, HEAD `63d5fa0ea1c60e49242970e7721f0581e41c267a`, unstaged full-index patch `0e356993ff79061743451ce3e9473f582264e23a8eb80be7025be3c334c3cc6a`. Control is the formatted stage-capacity plus zero-count routing-helper candidate (patch `aafc4ffd2d74e502bc6eb1f000837a04d9f0e044b4efbba483cd68bac70813d6`). Complete source maps are in `source.json` and `gate.json`.

- FC2 selects K8 for narrow M128 only when reduction divides its `2 * public_k` tile; otherwise K4. Dtype defines public K (256 for FP4×FP4;128 otherwise).
- The common core preserves streamed-weight EVICT_FIRST for narrow one-CTA geometry independently of K depth. All existing FC1 narrow configurations use K8 for all dtypes; this does not change their policy.
- The host selector is evaluated outside CUDA kernels and remains compile-time specialization. No model dimensions or phase flag are added.
- The candidate inherits capacity-derived operand stages and exact helper guard unchanged; full scoped pre-commit passes.

Actual CuTe layouts / nested SharedStorage were audited for 180 policies per source. The FC2 selector is extracted from the actual host AST. All 180 preserve cache hints and bulk epilogue policy; all V3, FC1, and MX policies are identical. Only nine V4.1 FC2 FP4×FP4 policies differ: N16/32/64 for SF16-E4, SF16-E8, SF32-E8. Standard NV K512/stage4 becomes K256/stage9 for N16/32 and stage8 for N64. Capacity is 232448 bytes, maximum actual shared storage 230400 bytes, stages range3–10. `layout-comparison.json` contains every change.

The actual V4.1 intermediate dimension2304 takes five K512 tiles (2560 reduction values) versus nine K256 tiles (2304), eliminating 11.1% padded MMA work relative to useful K. More TMA issues and stage barriers may offset this gain; performance decides.

Fixed diagnostic runs use unchanged `benchmarks/bench_moe_deepseek.py` SHA `d925f7f06015b4876a0a54f40305588290d245becbb44d503b722009586a09bb`, native CUDA-graph/CUPTI cold-L2 methodology, warmup10/iters100, EP4, no fused finalize, and no autotuning. Original route tensors are regenerated with the existing per-point seed42 and checked against prior baseline hashes/full histograms. Serialized caches force identical CuTe W4A4 tactics in both source arms; existing W4A16 cache entries remain for the script's shared `cutedsl` selector. Each geometry uses C1/A1/A2/C2 on one dedicated GPU:

- GPU5 N16/M128/M128 at T8/16/512 (affected K-tail policy).
- GPU7 N128/M256/M256 at T64 (unchanged-policy noise control).

All83 source pins are checked before/after every process; loaded cache hashes, actual route identities, and selected tactics are verified. Full output is retained; no cross-GPU latency comparison is made.

Retention caveat: the simple divisibility selector also switches some smaller K where K4 and K8 produce equal padded work (e.g.FP4K384). If retained, consider a strict padded-work comparison instead. This would produce identical V3/V4.1 selection and narrow its effect on unmeasured dimensions. Current measured source is frozen.

## Outcome: reject

Both C/A pairs agree: fixed NV N16 T8=0.9891×, T16=0.9909×, T512=0.9826×. Unchanged N128 T64=1.0009×; W4A16 controls range0.9980–1.0006×. All source, cache, tactic, and route checks passed. The reduced padding does not compensate for shorter-tile pipeline cost in this trial. Keep K512 policy; do not promote this candidate. GPUs5/7 are released. Raw native output, observer receipts, and exact timing medians are in `raw/`; derived paired results are in `summary.json`.
