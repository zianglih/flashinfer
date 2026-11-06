# DeepSeek V4.1 Flash scheduler source audit

Read-only review of current `bacf4861523ff7a1c1b5ad1e9d7a73a19151564a` versus original `a7103ae2a97f38f4dbbf410c32acc7c6fe99cab1`; scheduler SHA256 `0ff274af0df35c3fa34efbe22a7ba146a43c579c22c4492616962ee787fe1a61`. No code changes, compilation, new tests, GPU work or causal performance claim. Per the user's correction, the decision gate keeps independent AUTO24 selection enabled on both sides; the proposed fixed-winner study was never launched.

**Finding:** no DSV-specific algebraic defect is apparent. Its prefix divisor differs, and its smaller local-expert count reduces the work this optimization can remove. Source alone does not establish that either explains the reported T32 regression.

## Geometry and division

All considered tactics use cluster `(2,1,1)`. M128/one-CTA and M256/two-CTA both have 128 feature rows per CTA and therefore 256 feature rows per scheduler cluster. M128 does **not** double the scheduler's feature-block counts.

| Model | Local experts at EP8 | Gate+up width | FC1 feature blocks F1 | FC2 feature blocks F2 |
|---|---:|---:|---:|---:|
| DSV4.1 Flash | 48 | 4608 | 18 | 20 |
| Kimi K3 | 112 | 6144 | 24 | 14 |
| GLM5 | 32 | 4096 | 16 | 24 |

These counts are static Python integers. The prefix change adds division by F1 once per `_advance_group` invocation. DSV's18 and K3's24 are both non-powers of two; GLM's16 is a power of two. The source uses `cute.fast_divmod_create_divisor`, not a runtime-derived divisor. The same F1 fast-divmod pattern already occurs in original per-tile `_decode_inside_expert`. This source review cannot establish emitted instruction counts, constant folding, live-register changes or spills; it would be incorrect to assert that division by18 is a slow dynamic divide or is uniquely costly.

Sources: [CTA geometry](../flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py#L187), [scheduler axis swap and cluster shape](../flashinfer/flashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/src/moe_nvfp4_swapab/moe_persistent_scheduler.py#L320), [F1/F2 construction](../flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/fc1_fc2_fuse_sched.py#L378), [existing per-tile division](../flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/fc1_fc2_fuse_sched.py#L859).

## What changes at a boundary

The only source delta to the original scheduler is the prefix/fallback block in `_advance_group`. With equal padding and token-tile width C, greedy construction has already accumulated `cumulative_fc1 = F1 * sum(ceil(tokens[e]/C))` through the exclusive whole-expert boundary. Dividing by positive static F1 therefore recovers exactly the token-block prefix; multiplying by C recovers the same padded-row prefix. This identity does not require F1 to be a power of two or group_hint to be divisible by F1. For example, G512 may overshoot to522 for29 one-block DSV experts; 522/18=29 remains exact.

The common greedy group construction, thresholds, FC1/FC2 intervals, phase rewind, atomic claims and work publication are unchanged. Counts are nonnegative; zero experts contribute zero. Sentinel opening starts at the zero prefix. After the replaced walk, common code overwrites expert/phase/tile-end/token-count caches before priming the next group; only the two recovered cursors survive. Unequal padding or runtime/nonpositive F1 uses the original fallback. No new serialized scheduler state, shared memory, synchronization, metadata reads or decoder work is introduced.

There is a plausible cost tradeoff: prefix division/multiply replaces a residual walk that might be empty or short for a particular cluster's work-ID progress. The original walk includes count reads, per-expert state updates and an ending cursor push. Fewer local experts can mean less removed work; that is a mechanism hypothesis, not an observed bottleneck. Compiler changes to loop state/liveness can have effects beyond a literal source-operation count. Warp7 still has the same80-register role; there is no source-level evidence of changed occupancy or spills.

Sources: [changed block and unchanged greedy construction](../flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/fc1_fc2_fuse_sched.py#L730), [residual expert work](../flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/fc1_fc2_fuse_sched.py#L659), [group advance condition](../flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/fc1_fc2_fuse_sched.py#L955), [scheduler warp/register role](../flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py#L1243).

## T32 is particularly bounded

Each token selects an expert at most once. At global T32, each expert's count is at most32. N32/N64/N128 therefore all give exactly one block per nonempty expert, with no multi-block experts. DSV has only48 local experts, so each rank has at most `48*18=864` FC1 work tiles.

- **G1024:** always one group per rank. There is no subsequent residual-expert scan to remove. The prefix block is encountered only when opening the initial group with numerator zero (which may or may not be folded by generated code). Repeated nonzero prefix division cannot explain a T32 penalty for this tactic.
- **G512:** a second group requires at least29 nonempty local experts; otherwise it is likewise a single-group case. Actual seeded rank-local route counts are needed to determine which case occurred. This review does not substitute expected routing for the recorded fixture.

The requested old/new-scheduler AUTO24 sweeps decide retention at the complete-policy level. Selected tactics may change, so these comparisons do not isolate scheduler instruction cost. The completed DSV T32 pair happened to choose the same M128/N32/G1024/epi tactic: OFF130.545us versus ON135.3455us, still slower than original BEFORE122.5935us. This does not establish a generated-code explanation; no attributable ON/OFF binary pair was found in the saved artifacts. See `scheduler-auto-dsv-complete-v1.md` and `dsv-t32-compiled-artifact-audit.md`. No fixed-tactic run or further trace is requested here.
