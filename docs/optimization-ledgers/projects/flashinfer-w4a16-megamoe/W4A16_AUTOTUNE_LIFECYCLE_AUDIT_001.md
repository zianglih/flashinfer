# W4A16 collective autotune lifecycle

The proposed W4A16 adapter reuses the established NVFP4/MXFP8 knob dictionaries, collective ordering, cache format and benchmark. It fixes two dequantization warp groups and selects three validated geometries, two flag batches and two supported token-return modes. It does not expose an arbitrary-knob framework.

This CPU source audit uses the snapshots in `MEGAMOE_TUNING_ENTRYPOINT_AUDIT_001.json` and `candidates/w4a16_autotune/performance/manifest.json`. GPU execution of the new adapter is pending. The earlier entry-point audit describes pre-patch code; the unapplied implementation is `candidates/w4a16_autotune/performance/autotune-and-benchmark.patch`.

## Lifetime and score

`shim/autotune.py::autotune_knobs` rejects graph capture and requires every EP rank to enter with identical candidate ordering. Per candidate, it applies knobs, barriers, performs three warmup forwards by default (first compilation included), barriers again, and times ten synchronized forwards with `time.perf_counter`. It takes a median per rank and barriers after that candidate. After the complete sweep, an all-reduce MAX combines rank medians and all ranks apply the same minimum-scoring candidate. Rank 0 prints the full ranking. The callback runs on every rank and chooses which rank writes the winner.

The W4A16 launch closure must invoke full `w4a16_mega_moe(..., sync=True)`, including post-FC2 routing weights and TopkReduce. The raw thunk omits that reducer. Candidate outputs overwrite the caller's `y`. The backend then executes the chosen configuration before returning its normal forward result, following NVFP4/MXFP8. All tuning finishes during eager collective warmup before graph capture.

W4A16 `apply_knobs` releases compiled workspace and invalidates the compile. Ranks must traverse the same sweep together. Existing backends disable workspace pooling for auto sessions to avoid mutating shared frontend state; the W4A16 backend proposal mirrors this. The backend stores a copy of the returned winner before clearing its pending flag, allowing setup-time benchmark reporting.

## Measurement boundary

The online score is **MAX of per-rank median synchronized host-forward time**. The final benchmark is **median of per-iteration MAX rank GPU CUPTI span**, with graph replay and cold L2. Different aggregation order, host synchronization and graph/cache conditions can alter rankings. The shared tuner remains unchanged; its wall-clock score is setup evidence rather than final CUPTI performance.

After auto warmup, the benchmark records the actual returned winner per shape/rank and measures its forward with the existing CUPTI timer. Preserve online rankings, paired split/Mega rows, fresh actual split tactics, and adjacent explicit-knob remeasurements of close finalists. Do not reconstruct historical winners or call near-tied online rankings a performance conclusion.

## Failure and correctness boundary

The generic tuner catches exceptions and scores infinity. Its source assumes deterministic all-rank constructor/compile failures. A rank-local failure before a barrier can desynchronize ordering, and a device fault or nonreturning kernel cannot be recovered by that handler. It has no numerical oracle. A successful ranking alone therefore proves neither correctness nor general failure recovery.

Use the established public numerical suite and independent Mega oracle to gate supported geometry/return combinations; preserve an external timeout. Fatal/asymmetric failures stop the experiment and retain evidence. Do not relax tolerances or continue a poisoned collective. Strict split-output equality uses a different BF16 rank-local versus global reduction contract and is not a substitute for the independent Mega oracle.

The candidates retain BF16 activation/dispatch/combine/output, FP32 globals after MMA, existing clamp placement, and external FP32 routing weights after BF16 FC2 output. Precision, clamp, activation quantization, in-kernel reduction and pipeline/group counts are not tuning axes. Both supported token-return modes remain candidates, matching the existing NVFP4 pattern.

## Cache and provenance

Reuse `shim/knob_cache.py` without schema changes. W4A16 lookup and recording use `dtype="w4a16"`, post-SwiGLU I, capacity tokens per rank and BF16 combine wire. Only rank 0 writes. Lookup matches other dimensions exactly and chooses the exact capacity, otherwise the smallest greater bucket, otherwise the largest smaller bucket. Explicit dictionaries keep precedence. Integration preserves cached return mode instead of overwriting it with an implicit named-argument default.

The existing key omits live/global tokens, routing skew, source/compiler hash, stage policy and clamp. Use separate effort-owned cache files per frozen source/input scenario. In EP8, global 1/2/4/8 share capacity 1; record global/live counts beside every winner and avoid claiming one capacity entry covers every live-rank distribution. All ranks need consistent cache contents and candidate order.

Future runs need explicit source/test manifests including new kernel, epilogue, frontend, preparation/backend, public test/oracle and benchmark files. Historical tracked-only manifests omitted some newly added files. Contemporaneous timing/codegen manifests provide independent context but cannot retroactively make those numerical runs fully source-attested. Integration owns the prospective runner manifest fix.

## Delivered scope

The performance artifact adds `w4a16_candidates`, `autotune_w4a16_mega_moe`, their local exports, and literal-auto parsing/forwarding plus actual winner reporting. Integration owns config/backend first-forward tuning, pooling behavior, factory lookup, public exports and contract tests. Six CPU tests and independent interface review pass. Generic tuner and other dtype adapters are unchanged; core benchmark timing is unchanged. Standalone `moe_ep.tune --dtype w4a16` is a separate possible extension, not required for this live-input benchmark path.
