# Standalone per-token quantizer scalar hoist — rejected

Base: retained `2b8eb9d8f72ceda3952fbb05054fee97173fc9c7`. Candidate quantizer SHA256: `f5d17d62e0f63af892e0848a2ab19d1823774ffbc6c2f298d1dbc68ba7b2ffdc`. The one-file patch is +12/−10 lines and remains preserved in [candidate.patch](candidate.patch).

The candidate loads the immutable global scale once after the existing PDL wait/startup publication, and computes its precise reciprocal once before the persistent row loop. Both existing row paths reuse that Float32 factor. All per-row quantization math, optional output-scale handling, layouts, public contracts, and synchronization remain unchanged. Scoped pre-commit, syntax, diff and source review passed; see [source.json](source.json).

| Current-runtime native pair | Registers | CUDA local bytes / spill stack | Occupancy | Static non-NOP | Exact result |
|---|---:|---:|---:|---:|---|
| BF16 K640/M4097, precise MSE256/error-fast,64threads, routed64/128, PDL on |61→64|0→0|16→16|743→739|Passed initial output and four changing-scalar/live-row graph replays|
| FP16 K512/M4097, fast ordinary,32threads, linear SF, PDL off |32→32|0→0|32→32|125→125|Passed the same five snapshots|
| FP16 K80/M130, precise MAE448/error-precise,32threads,8×4 SF, folded output scale, PDL on |64→64|16→40|32→32|1430→1455|Candidate stopped by resource guard before launch|
| BF16 K1040/M129, fast MAE256/error-fast,96threads,128×4 SF, PDL off |64→64|0→0|10→10|485→483|Passed the same five snapshots in the parallel lane|

The successful precise pilot proves the intended movement in actual native code: scalar LDG `0xa70` and reciprocal `0xb20` move from the persistent row loop to `0x150`/`0x180`, after the unchanged PDL acquire/fence/startup sequence. The fast pilot also moves its scalar LDG before the loop. This is distinct from the earlier GEMM epilogue alpha-prefetch/reuse experiments.

The supported K80 precise folded-scale case defeats the general change: compiler spill traffic grows from **4 LDL +4 STL** to **22 LDL +10 STL**. CUDA's local-bytes attribute includes the spill stack (16→40); cuobjdump's separate `LOCAL` field remains zero, while `STACK` records this growth. No new explicit PTX local array is present. The longer invariant lifetime has an actual native cost, not just a register-count warning.

The original pilot's strict61→64 register rejection is preserved. Parent review permitted that allocation change because occupancy/block/shared allocation and local memory were unchanged; the subsequent new-spill guard remained strict and stopped the K80 candidate before execution. Seven selected calls passed (three complete pairs plus the failed pair's control); four later planned pairs never ran. No performance, sanitizer, broad suite, or recipe/shape-specific workaround ran. The held24-cell timing plan was [cancelled without deployment](../../audits/quantizer-scalar-hoist/cancellation.json).

Decision: reject the general hoist. Keep the retained implementation and all frozen caches unchanged. No selective fast-math/recipe/shape policy is warranted.

Evidence: [native-summary.json](native-summary.json), [CPU artifact replay](analyze_native.py), [initial movement proof](pilot-native.json), [original pilot evidence](pilot-evidence/fetch.json), [continuation evidence](qualification-r1/fetched/fetch.json), [source/cache/GPU closure](qualification-r1/closure.json). Both full13,245-file inventories and native module/Ninja hashes passed closure; GPUs0/1 were idle and released. All existing helpers, failed receipts, raw outputs, PTX, cubins and SASS are preserved.
