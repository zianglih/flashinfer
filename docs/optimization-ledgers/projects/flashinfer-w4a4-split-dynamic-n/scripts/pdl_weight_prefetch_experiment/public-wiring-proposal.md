# Proposed public-chain integration of startup weight prefetch

Read-only design proposal, not a production edit. Baseline is retained `853aaf69d706b291afee477f738956b997033f53`; the two-file single-stage prototype remains frozen in `evidence/pdl-weight-prefetch-r1/source.json`. The multi-stage experiment is separately owned by `tests_scope_audit`.

## Direct behavior knobs and callers

Extend only the two main public split wrappers, preserving their default behavior:

- FC1: `publish_routing_before_signal: bool = False`, forwarded to the private shared launcher.
- FC2: `prefetch_weights_before_wait: bool = False`, forwarded to the private shared launcher.

The private launcher/cache/core already carry these independent compile-time booleans. Do not add a phase flag, infer behavior from activation kind, introduce token/model thresholds, change tactics, or add a new keyword-only separator. Existing deprecated convenience wrappers remain unchanged and inherit false. They do not own a complete chain and cannot infer readiness.

`fused_moe.py:_moe_core_impl` owns routing, preparation, both FC calls, and combine. After its existing architecture/config validation, derive the opt-in once:

```python
prefetch_weights_before_wait = (
    enable_pdl
    and not is_rubin
    and not use_localized_path
    and not use_per_token_activation
    and not use_fused_finalize
    and gemm2_mma_tiler_mn[0] == 128
    and gemm2_cluster_shape_mn == (1, 1)
)
```

Pass this same bool to FC1's `publish_routing_before_signal` and FC2's `prefetch_weights_before_wait`. These are implementation choices inside the known chain; no new high-level MoE option or tuner dimension is needed. The one-CTA restriction is about FC2: FC1 may retain its existing CLC or two-CTA tactic because its publication occurs after the all-thread prerequisite wait. FC2 currently selects static scheduling explicitly. M128 is the current core's one-CTA geometry; logical M256/M512 are two-CTA in retained853, so checking the cluster alone would not be a complete contract.

`benchmarks/bench_moe_deepseek.py:SplitMxfp8Runner.forward` also owns the complete sort→FC1→FC2→combine chain. It always uses PDL, Blackwell, non-per-token and unfused finalize. Derive the pair from `gemm2[0][0] == 128 and gemm2[1] == (1, 1)` and pass the two kwargs explicitly at its existing FC1/FC2 calls. Keep shared preparation, timing, route tensors, native AUTO, and table formatting unchanged. Ordinary NVFP4 benchmark calls go through `_moe_core_impl`; W4A16 uses its distinct backend and is unaffected.

No other repository-owned complete direct FC1/FC2 chain was found by symbol search. Distributed/routine benchmark callers enter the high-level wrapper. Direct tests and the deprecated per-format wrappers keep false unless a task-local gate explicitly establishes the publication contract.

## Explicit unsupported combinations

Public wrappers must reject a requested behavior on Rubin before the Rubin branch can silently discard it. The FC1 publication request is supported only by the Blackwell startup-signal path. FC2 prefetch is supported only by Blackwell, unfused scatter, static scheduling and one-CTA geometry. Keep the core's existing constructor checks as a backstop; wrapper checks should fail before launching any preparation work when possible. A high-level caller chooses false for unsupported paths, preserving those paths.

A public FC2 prefetch request additionally asserts a caller obligation that cannot be detected from geometry: the immediately preceding same-domain producer has completed the routing ancestors and executed a GPU release before its PDL trigger. Document that obligation next to the option. An arbitrary standalone caller must not receive prefetch automatically. PDL-disabled standalone opt-in is ordered by ordinary stream dependencies, but high-level code should choose false when PDL is off because there is no startup overlap to recover.

## Publication and intervening per-token quantization

For the admitted same-stream chain, sort→prepare→FC1 waits make the immutable count/expert metadata visible before FC1's release→trigger. The release synchronizes with FC2's dependent-grid start, so FC2 can read metadata and issue only immutable weights/SFA before its own all-thread wait. B/SFB and all dependent payload reads stay after that wait. No-work grids still execute the wait. See the exact [CUDA13.2 PTX griddepcontrol specification](https://docs.nvidia.com/cuda/archive/13.2.0/parallel-thread-execution/index.html#parallel-synchronization-and-communication-instructions-griddepcontrol); same memory synchronization domain is required for the GPU-scope fence.

Per-token NVFP4 must initially retain false. `_moe_core_impl` inserts `nvfp4_quantize_per_token_cute_dsl` between FC1 and FC2. That quantizer executes a dependency wait and then can trigger FC2 before quantized stores finish, but its trigger paths do not have the release fence needed to republish ancestor routing metadata at dependent-grid start. `convert_sf_to_mma_layout` is only a `view(...).permute(...)`; it does not launch a synchronizing conversion kernel. Therefore it supplies no additional publication edge. Supporting prefetch there would require an explicit republish contract at every quantizer trigger path and another changing-data replay gate. Do not widen this patch into quantizer changes for the small initial gain. Existing per-token functionality remains intact.

## Validation before retaining the integrated source

1. Preserve the prototype's compile-time admission and first-stage expectation accounting. If a capacity-derived multi-stage count wins, use the same caller readiness pair and reprove all primed stages; do not bake a token-specific count into call sites.
2. Replace the task-local private-GEMM override in the replay gate with actual public call wiring. Compare candidate versus retained853 outputs over all three formats and the same changing-input/route/zero-local patterns. Include PDL-off and verify excluded per-token/fused/two-CTA/Rubin call admission statically or with existing focused coverage; no new standalone repo test file is needed.
3. The existing small replay uses M128 for both FCs. Add at least one admitted FC1 two-CTA→FC2 one-CTA full-chain case, or initially constrain both FCs until that publication configuration is exercised. Core FC1 CLC is already present in the N16/N128 probe, but record the effective mode rather than assuming requested mode.
4. Time the actual public-wired candidate through unchanged benchmark/observer entrypoints and fresh native AUTO on both models with all13 tokens, preserving route/source/GPU receipts and excluding tokens1/2 from retention. A fixed three-point prototype screen is not evidence of native AUTO retention.
5. Keep source-specific caches and all evidence local. No PR body performance update until an exact integrated source is retained and its current tables are available.

## Measured single-stage screen

The frozen prototype's V41EP4 fixed N16/M128 C1/Off1/On1/On2/Off2/C2 screen uses10 warmups,100 cold-L2 CUDA-graph CUPTI repetitions on one B300. Off keeps publication true and prefetch false; On enables both. All9 affected points improve in both repeats. Paired clean853/On ratios:

| Format | T32 | T128 | T512 |
|---|---:|---:|---:|
| NVFP4 W4A4 | 1.003737 | 1.003346 | 1.002917 |
| MXFP8 | 1.003614 | 1.002678 | 1.002035 |
| MXFP4×MXFP8 | 1.004062 | 1.005403 | 1.001826 |

`evidence/pdl-weight-prefetch-r2-fixed/summary.json` contains exact medians, repeated ratios and input hashes. This is a modest0.18–0.54% fixed-screen gain, not a broad speedup claim. W4A16 measurements are only unaffected control/noise observations.
