# Bounded early-scheduler PDL decode screen

GPU5 on the existing c3 B300 devbox. Frozen source-paired CAAC uses the already-selected all-CLC native 1-B cache for both arms, with no tactic overrides or retuning. V3 and K3 use EP8; V41-Flash uses EP4. Tokens 32/128, four affected formats: standard NVFP4, per-token NVFP4, MXFP4x8, and MXFP8. W4A16 is an incidental unchanged control from the existing NV selector. No TRTLLM backend is rerun.

Timing uses the public `benchmarks/bench_moe_deepseek.py`, 10 warmups/100 cold-L2 CUPTI graph samples, fused finalize disabled. NV family includes initial activation quantization; the public per-token recipe remains unchanged. `run_fixed.py` reuses the dedicated-norm diagnostic runner, and `observe_table.py` reuses the startup-scheduler observer, with only task-local paths and provenance wording changed. No production file is edited.

Each arm verifies source/head/full-index diff hashes, unchanged native cache, the original native routing IDs/weights, effective CLC depth 1 and weight-prefetch contracts, exact selected tactics in both phases, and raw 100-sample medians. Source-private DSL workspaces reuse the persistent native C++ cache. `collect.py` collects only logs, JSON and helper sources; `analyze.py` independently verifies the raw receipts and medians.

- control: HEAD `b85eff41a6c30687a93e95455a3f68ff77d14ac5`, patch SHA256 `97cf417da9591d530dd5febf3163c1525fabd9c399ce1a6c4a089cba4992f528`.
- candidate: HEAD `b85eff41a6c30687a93e95455a3f68ff77d14ac5`, patch SHA256 `ac6444ef4c37f78fa5587ff6bec52d40460db21b78417b83de90e9710cf48165`.

Results are diagnostic at fixed native control geometries, not a new native-AUTO retention sweep. Both frozen remote sources and original cache files remain unchanged.

## Completed result

All six decode cells completed with frozen source/cache hashes, matching native routing IDs/weights, effective CLC and prefetch contracts, identical selected tactics and independently verified 100-sample medians. Across 24 affected points, the geomean is 1.00094x; range 0.99897–1.00241x. Largest absolute change is 0.52 us. W4A16 remained an unchanged control. These are neutral-to-small effects, not a gap-closing speedup claim.

| Model | Tokens | W4A4 | PER-TOKEN | MXFP4x8 | MXFP8 |
|---|---:|---:|---:|---:|---:|
| v3 | 32 | 1.00156x | 1.00149x | 0.99897x | 1.00048x |
| v3 | 128 | 1.00047x | 0.99977x | 1.00183x | 1.00198x |
| v41-flash | 32 | 1.00120x | 1.00079x | 1.00241x | 1.00150x |
| v41-flash | 128 | 1.00198x | 0.99994x | 1.00107x | 1.00099x |
| kimi-k3 | 32 | 1.00085x | 1.00088x | 1.00121x | 1.00088x |
| kimi-k3 | 128 | 1.00008x | 1.00078x | 1.00129x | 1.00023x |

The V41 mixed T16384 reverse ACCA repeat preserves the original prefill cache and route hashes. Medians `[candidate, control, control, candidate]` were `[0.9162945,0.925510,0.901255,0.9053665]` ms, yielding 1.00280x. The previous 0.98792x slowdown did not reproduce; control drift of −2.62% still exceeds the measured effect. No precise prefill speedup is inferred.

Recommendation: retainable as a small PDL scheduling refinement that prepares already-published metadata before waiting on payload, with unchanged correctness/resource gates and no material sustained regression in this bounded screen. This does not establish a headline speedup; final native retuning remains necessary. GPU5 is released and verified idle. See `retention-recommendation.json`, both summary files, and the complete raw `results/` collection.
