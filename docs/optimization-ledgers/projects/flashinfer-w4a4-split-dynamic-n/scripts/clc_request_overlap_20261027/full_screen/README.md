# CLC request-overlap fixed-native screen

The sole source delta moves the existing cancellation request before the one-slot local metadata acquire. Both frozen sources retain the same six-field all-CLC diagnostic enumeration, queue depth, prefetch, PDL and arithmetic. The production policy cleanup remains separate; this screen adds no tactics or public parameters.

- Source: frozen `4e155c30` control patch `97cf417d`, candidate patch `3ed310c6`. Kernel source receipts are copied into `results/` and verified before and after every arm.
- Workloads: V3 EP8, V41-Flash EP4, Kimi K3 EP8; tokens 32, 128, 4096, 16384; standard NVFP4, per-token NVFP4, MXFP4x8, MXFP8. Fused finalize disabled. NV timing includes initial activation quantization; the established activation-only per-token recipe is preserved.
- Timing: source-paired CAAC, 10 warmups and 100 cold-L2 CUPTI CUDA-graph samples per point/arm. Saved native all-CLC `1-B` tactics are used unchanged. Every measurement must hit its cache, select both CLC phases, match native route identities and retain exactly 100 samples.
- Two exclusive shards: NV on GPU5; MX on GPU6. Each full CAAC stays on the same GPU. Ratios are combined across workloads; raw latency samples from different GPUs are never pooled.
- Existing source-matched V3 MXFP4x8 T32 and K3 standard/per-token NVFP4 T16384 are reused from `perf-general-20261026/clc-request-overlap`. Their original scheduler overrides were no-ops (`True, True` to `True, True`). This round measures the remaining 45 affected points, with incidental unchanged W4A16 observations.
- C++ compilation cache remains persistent and shared; DSL namespaces remain source-private. No production benchmark edits, native AUTO search, TRT timing, or correctness/sanitizer expansion.

Helpers are task-local. `run_fixed.py` and the observer reuse the completed startup/norm harness, with only experiment paths, wording, token list, and an optional backend selector changed. `collect.py` transfers small JSON/log/helper files only, excluding compiler caches. `analyze.py` checks raw medians, source identity, cache hits, route identity and duplicate coverage before emitting the final 48-point summary.

## Result: reject

Overall geometric mean **0.999956×**; decode **0.997000×**; prefill **1.002920×**. All 24 decode points are slower. Unchanged W4A16 decode remains within 0.99947–1.00071×. Some large prefill measurements drift, so their apparent gains are not used to offset the systematic decode cost. No reverse repeats or broader AUTO work are warranted.

| Model | Tokens | W4A4 | Per-token | MXFP4x8 | MXFP8 |
|---|---:|---:|---:|---:|---:|
| v3 | 32 | 0.99611× | 0.99873× | 0.99732× | 0.98839× |
| v3 | 128 | 0.99943× | 0.99877× | 0.99707× | 0.99695× |
| v3 | 4096 | 1.00171× | 1.00098× | 1.00237× | 1.00068× |
| v3 | 16384 | 1.00117× | 1.00352× | 1.00386× | 1.00665× |
| v41-flash | 32 | 0.99596× | 0.99646× | 0.99774× | 0.99753× |
| v41-flash | 128 | 0.99758× | 0.99666× | 0.99876× | 0.99648× |
| v41-flash | 4096 | 0.99957× | 0.99916× | 1.00092× | 1.00046× |
| v41-flash | 16384 | 0.99905× | 1.00408× | 1.02845× | 1.00448× |
| kimi-k3 | 32 | 0.99582× | 0.99668× | 0.99827× | 0.99529× |
| kimi-k3 | 128 | 0.99636× | 0.99836× | 0.99997× | 0.99738× |
| kimi-k3 | 4096 | 1.00540× | 1.00657× | 1.00707× | 1.00339× |
| kimi-k3 | 16384 | 1.00491× | 1.00708× | 0.97490× | 1.00446× |

Full four-arm raw medians, per-arm samples, actual tactics, route hashes and provenance remain in `summary.stdout`, `summary.json`, and `results/`. `decision.json` records the boundary and checksums. GPUs5/6 are released, verified at 0% utilization / 0 MiB with no compute processes.
