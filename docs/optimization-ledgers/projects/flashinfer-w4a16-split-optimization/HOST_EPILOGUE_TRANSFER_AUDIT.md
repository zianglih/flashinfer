# Mega-to-split host and epilogue transfer audit

Read-only source review of upstream `488ffbd9fe4455c3b4c3030cf668b5603c6698e4`. No kernel edits, imports, compilation, numerical tests or GPU measurements. Paths below are relative to `flashinfer/` in this project.

## Recommended first candidate: certify full M-cluster alignment

The split kernel still carries dynamic `Int64 m/k` through `fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py:569`; its logical output shape is built from `m` at lines592–601. The nongated deterministic tail store evaluates an M bound for each register element at lines2280–2285. Fused finalize separately computes remaining hidden elements, a positivity guard and a clipped copy width at lines2211–2230. These are actual JIT device expressions, not ordinary Python host overhead.

Small design: in `fused_moe/cute_dsl/blackwell/moe_w4a16.py::_get_compiled_kernel` (lines126–169), derive one Boolean from the existing host `m` and tactic:

```python
cta_m = mma_tiler_m // (2 if mma_tiler_m == 256 else 1)
m_cluster_aligned = m > 0 and m % (cta_m * cluster_shape_mn[0]) == 0
```

Add that Boolean to the existing compile key and private kernel constructor. Keep `m`, `k`, live routed `n`, token count and all tensor layouts dynamic. The class's actual CTA-M formula is lines199–212. Under a compile-time true flag, the nongated tail predicate needs only its existing routed-row distance check; fused finalize can use the constant CTA-M copy width and omit the positive-remainder guard. False retains the exact current predicates/clipping. No pipeline, work ordering, math or public tactic changes.

**Full cluster alignment is essential.** `_compute_grid` rounds CTA extents into clusters (lines2511–2529). Static publication at lines1277–1308 checks the route/group, but does not suppress an individually padded M CTA. For example, M128/C2 at m128 is CTA-aligned but has an out-of-range peer; m384 with a256-feature cluster similarly has a padded peer. A mere `m % cta_m == 0` would be unsafe. With full-cluster alignment, every published valid cluster's CTA and local M coordinate lies below m. CLC similarly derives finite CTA/cluster extents from the same shape. Sentinel/empty work remains excluded by the existing valid-work loop. Gated FC1 sets the nongated subtile count to zero (lines2112–2115), so this candidate does not claim to optimize SwiGLU's separate store body. ReLU2 and FC2 are nongated and use output factor1.

Public functional and wrapper paths reach `CuteDslFusedMoEW4A16Runner.forward` (`tuner.py:1202–1263`) then `launch_w4a16_moe` (`moe_w4a16.py:358`). The sole production constructor/compile call is `moe_w4a16.py:151–191`; two GEMMs share `_run_grouped_gemm`, which derives m from each weight at line217. The compile key currently omits m/k (lines131–148), so adding the Boolean is required to prevent aligned/partial shapes sharing incompatible code. This doubles only the alignment specialization, rather than multiplying kernels by every hidden/intermediate size.

This directly transfers the retained Mega geometry cleanup: the Mega ledger at `../flashinfer-w4a16-megamoe/w4a16_optimization_experiments.md:8776` records removed full-shape bounds, preserved partial guards and unchanged resources. Its sub-percent one-sweep timings did not establish broad latency gain; the relevant precedent is simpler emitted code.

## Second candidate: make fused-finalize top-k a compile-time input

`moe_w4a16_kernel.py:573` receives `top_k` as runtime Int64; the route-score layout at lines619–624 therefore keeps its second dimension dynamic. Fused finalize divides/remainders a nonnegative route index at lines2158–2162, and divides again at line2210. The wrapper's top-k is already fixed (`fused_moe.py:662,765–778`, `tuner.py:1050,1134–1148`), but that fact is lost at the private kernel boundary. The functional API and direct private launch must still derive the value from actual input shapes; a global assumption that every call has top-k8 is invalid.

Small design: include the effective top-k in the existing compile key, change only private `wrapper` top-k to `cutlass.Constexpr`, keep it in `cute.compile` arguments and omit it from the resulting runtime compiled call (as already done for `max_active_clusters`). Non-fused GEMMs retain effective top-k0 and do not instantiate division. Fused top-k1/2/8 can then fold to constant arithmetic. If non-power-of-two native lowering is still poor, the existing CuTe fast-divmod pattern is the next bounded option; preserve nonnegative/sentinel handling and do not narrow Int64 values without range proof.

This is independent of alignment and affects **only atomic fused finalize**. The established split-vs-Mega publication benchmark uses `--no-fused-finalize`; top-k specialization cannot improve that metric. Native inspection should establish whether constant-divisor code is actually smaller before recommending a benchmark. The Mega fast-divmod ledger at line8960 records simpler standard-helper code and native instruction reduction, not a demonstrated broad speedup.

## Lower priority: host launch preparation, not graph GPU time

`moe_w4a16.py:236–303` rebuilds typed pointers on every GEMM launch, and lines306–355 assemble the same compile/launch arguments twice. The retained Mega frontend caches `_runtime_kwargs` by actual buffer/stream identity (`../flashinfer-w4a16-megamoe/flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/nvfp4_w4a16/frontend.py:286–302`); current upstream NVFP4 shim also has that pattern (`moe_ep/kernel_src/cutedsl_megamoe/shim/nvfp4.py:322–358`). A bounded weight-pointer/launch-preparation cache is a possible eager-host improvement, but scratch/output buffers currently belong to each invocation (`moe_w4a16.py:80–82`). Reintroducing persistent global workspace ownership would change a deliberate allocator/graph-lifetime contract. Any cache needs buffer/shape/stream and replacement invalidation, without retaining full-model allocations. No graph-replay GPU speedup is expected. This is not the first candidate.

## Existing validation surface and limits

- `tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoeW4A16::test_route_tile_boundary_accuracy`: six existing explicit pairs, route8/16/32/64/128/192, M128/C1 and C2, M256/C2, one full and one partial route tile per hot expert. Uses H256/I512 and originally deterministic non-fused finalize; the subsequently authorized top-k candidate extends that existing product to both modes.
- `...::TestCuteDslFusedMoeFunctional::test_finalize_handles_cluster_padding_and_partial_tiles` with W4A16: H256/384, explicit M256/C2; H384 exercises the padded M peer. Relevant to both alignment branches.
- `...::TestCuteDslFusedMoeFunctional::test_numerical_accuracy` includes top-k1/2/8; `test_deterministic_finalize_numerical_accuracy` has W4A16 SwiGLU/ReLU2 cases.
- Existing wrapper accuracy and CUDA-graph products cover both finalize modes. If adopting the Boolean specialization, include aligned→partial→aligned calls with the same tactic in one process to verify cache separation. If adopting constexpr top-k, likewise use different top-k values in one process. These are coverage requirements, not claims that existing isolated selectors already prove the new cache contract.
- Native check should compare aligned and partial emitted bounds, full/partial fused copy width, entry arguments, resources and spills; preserve route predicates and all synchronization. No numerical or speedup claim exists for either proposal yet.

## Already present or previously rejected — do not repeat

The prior split ledger `../flashinfer-w4a16/w4a16_optimization_experiments.md` already retains fused FC1 activation (397), lane-local gate/up pairing (574), immediate final accumulator-load release (1950), K256 and23 paired tactics (4130/4171), and fragment-size specialization (5356/5572). Current source retains those patterns. Separate weight/load/transform roles already provide cross-work-tile overlap; this is not missing merely because the API is split.

Do not revive the bounded private permute family (3097 onward), private Triton deterministic reducer (3864's corrected matched A/B), block-wide route metadata cache (3918), staged GEMM2 alpha (4979), early raw-stage release (5442), eager decode/acquire changes or deferred store waits (5607) as new Mega transfers. The prior results are explicit negative or workload-dependent evidence. Broad Cartesian autotuning was already reduced to the measured23 paired tactics; copying Mega's four-entry catalog would discard supported split geometries without new evidence.
