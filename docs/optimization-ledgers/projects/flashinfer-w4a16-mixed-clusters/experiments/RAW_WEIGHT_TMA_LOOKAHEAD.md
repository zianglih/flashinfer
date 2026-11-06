# Raw weight and scale TMA lookahead: unapplied experiment

Prepared against candidate3r as [`mixed-raw-weight-try-acquire.patch`](mixed-raw-weight-try-acquire.patch). The live source remains unchanged; no remote operation or GPU run occurred. Application waits for PC/source evidence. Any comparison remains baseline AUTO16 versus optimized mixed-only AUTO18, or an isolated mixed-only AUTO18 comparison between candidate implementations.

The closest precedent is the maintained local W4A16 kernel, not a new scheduling design. Its raw weight/scale producer uses the same `cutlass.pipeline.PipelineTmaAsync` class and already passes a saved `producer_try_acquire` result to `producer_acquire`. It probes initially and after `commit → advance`, keeping the two copies in their original order. If the profile supports investigating this producer, adapting that exact ordering is the smallest grounded experiment. It preserves the current explicit `producer_commit` call and requires no assumption that the call is a no-op.

## Exact source mapping

All links refer to the current project checkout; vendored sources are read-only.

| Current Mega W4A16 | Established local or GenPhase precedent |
| --- | --- |
| [`_weight_task`:972–1053](../flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py#L972): reset count, acquire, packed-A copy, SF copy, commit, advance. | [Local W4A16 producer:1533–1572](../flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py#L1533): initialize Boolean readiness, guarded first probe, acquire with token, same two copies, commit, advance, guarded next probe. |
| [Raw pipeline creation:1297–1309](../flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py#L1297): `PipelineTmaAsync`, one producer, transform-warp consumer group, raw+SF transaction bytes, `mcast_mode_mn=(1,0)`. | [Local W4A16 creation:926–945](../flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py#L926): same pipeline class, consumer accounting and multicast direction. |
| [Raw ring fit:462–485](../flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py#L462) chooses two through five stages; [combined bytes:921–923](../flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py#L921) count packed weights plus SF. | The local W4A16 pattern does not alter ring geometry, data layout, transaction accounting or arithmetic. |
| [Persistent weight worker:1451–1498](../flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py#L1451) carries the producer state across FC1/FC2 work and tails once at exit. | [Local producer tail:1585](../flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py#L1585) and [local transform consumer:489–589](../flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py#L489) already preserve phase/index across tiles while resetting the per-tile count. |
| A possible stronger ordering would save current K/index/barrier, advance and probe the next stage before issuing either current copy. | [SM100 GenPhase A+SF:871–894](../flashinfer/flashinfer/moe_ep/kernel_src/sm100/next_cutedsl_megamoe/src/blackwell_genphase_sources/kernel_src/blackwell/inference/mega/block_scaled_swap_ab_fc12_mainloop_gen_specialized.py#L871) and its FC2 body929–952 use that exact order. [Rubin:889–912](../flashinfer/flashinfer/moe_ep/kernel_src/sm107/next_cutedsl_megamoe/src/sources/kernel_src/rubin/inference/mega/block_scaled_swap_ab_fc12_mainloop_gen_specialized.py#L889) agrees. These examples use TMA-to-UMMA pipelines; [GenPhase creation:684–704](../flashinfer/flashinfer/moe_ep/kernel_src/sm100/next_cutedsl_megamoe/src/blackwell_genphase_sources/kernel_src/blackwell/inference/mega/block_scaled_swap_ab_fc12_mainloop_gen_specialized.py#L684) is not the raw TMA-to-transform pipeline used here. |

## Prepared narrow change

The patch adds the local W4A16 initial/next readiness probes under the compile-time mixed-cluster guard and passes the token to acquire. Its uniform specialization has an identical `_weight_task` AST to candidate3r. The two copies through commit and advance remain an exact text subsequence; their common full-barrier pointer, combined expected bytes, masks, cache hint, per-tile count reset, ring phase/index and final producer tail are untouched. It starts a Boolean readiness token for each work tile, guards both the first and next probe with `state.count < k_count`, and does not probe across scheduler records.

This changes only producer wait scheduling. It does not share weight dequantization between CTA pairs, reduce weight/SF bytes, change cluster packing or modify any math/layout. A guarded post-copy probe is directly supported by the local W4A16 implementation. The stronger GenPhase pre-copy probe is a separate experiment: it needs current K/index/barrier values saved before advance, and pinned CuTe4.7.1 `PipelineTmaAsync.producer_acquire`/`producer_commit` source checked before removing or moving a commit. That specific override has not been inspected in the installed runtime. The saved project `cutlass-sm100-pipeline.py` is CUTLASS-main evidence, not a pinned4.7.1 raw-pipeline proof.

Previously inspected installed4.7.1 inherited `producer_try_acquire` calls one barrier try-wait, and `PipelineState.advance` rebinds its numeric state. The try instruction can suspend the thread; it is not an instantaneous readiness query. A stale false probe remains safe because the subsequent acquire waits normally. No gain is implied by adding a probe, and probing directly before a wait may add instructions without useful overlap.

## Preparation checks and application boundary

[`raw-weight-validation.json`](raw-weight-validation.json) records the exact hashes and commands:

- Candidate3r base kernel: `664a74fde4f0d60957a2ddb07839c95f393d477f7ee84d5ce4415bb56bf4d939`.
- Proposed kernel: `b81f05569d18ca838820b4b6c04f2f1fd69b275c9b7276d5a84a4a82f792c435`.
- Patch: `a39d51a36446e90081c01854f983632b2d5929f919e90c1af62605159f929395`.
- AST, Ruff lint and Ruff format checks passed. Forward application produced the exact proposed bytes; reverse application restored the exact base bytes in a temporary project-local tree. Non-weight AST and the weight task's uniform specialization matched the base. The live kernel bytes were checked unchanged afterward.

These are static checks. CuTe compilation/type joins, native AUTO liveness and GPU behavior remain untested for this patch. Both preferred and fallback physical clusters take the mixed specialization. Uniform2 and uniform4 retain the original acquire path. No dependency on a no-op commit is introduced: the current `producer_commit(state)` remains immediately after both TMA copies and before `state.advance()`.

If selected after profiling, apply only this isolated patch atop candidate3r:

```bash
cd /Users/ziangli/playground/projects/flashinfer-w4a16-mixed-clusters/flashinfer
shasum -a 256 flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py
git apply --check ../experiments/mixed-raw-weight-try-acquire.patch
git apply ../experiments/mixed-raw-weight-try-acquire.patch
```

Require the base hash above before application, and record the proposed hash before the coordinated native AUTO run. Do not reapply the already present B-TMA or registration patches. Application and remote synchronization are deliberately deferred.

## Profile decision

Map raw-producer samples to `weight_wait_raw_smem_slot_free`/the acquire at [1030–1032](../flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py#L1030), and distinguish them from the weight worker's scheduler wait. Also inspect the transform raw-ready wait at [local helper503–507](../flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py#L503) and its decoded-TMEM-slot wait519–523. Raw buffers are released only after raw/SF reads at [Mega override124–128](../flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py#L124). A producer waiting on a full raw ring can therefore reflect downstream transform/MMA backpressure; a readiness probe cannot create additional buffer capacity. Samples at the consumer raw-ready barrier motivate closer inspection of producer/TMA timing, but do not establish that this ordering is the limiting cause.

Keep source-correlated samples per rank and compare selected AUTO tactics. Large scheduler/collective startup skew can dominate these profiles. No measured bottleneck, expected percentage gain or implementation recommendation beyond this bounded feasibility check is claimed.
