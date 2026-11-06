# Mixed registration before the metadata wait

`mixed-registration-overlap.patch` is **unapplied**, based on candidate2. It moves only mixed+atomic `scheduler.internal_init()` immediately before `sched_warp_pre_init_wait()` in scheduler warp7. It applies cleanly on candidate3 as well; applying registration and producer lookahead in either order produces identical bytes. The live kernel remains candidate2.

## Established ordering and dependencies

Rubin already uses this exact ordering: common cluster initialization, register donation, `initialize_fallback_group()`, expert-size readiness wait, then `gen_next_work()` ([source lines993–1013](https://github.com/flashinfer-ai/flashinfer/blob/316faec37a4706a2ecc7d46265087f8190b40baa/flashinfer/moe_ep/kernel_src/sm107/next_cutedsl_megamoe/src/sources/kernel_src/rubin/inference/mega/block_scaled_swap_ab_mega_moe_kernel.py#L993-L1013)). W4A16 currently performs registration after its metadata wait.

The reused SM100 [registration helper](https://github.com/flashinfer-ai/flashinfer/blob/316faec37a4706a2ecc7d46265087f8190b40baa/flashinfer/moe_ep/kernel_src/sm100/next_cutedsl_megamoe/src/blackwell_genphase_sources/kernel_src/schedulers/work_id_claim.py#L503-L543) performs one fallback-registration atomic and one broadcast within each physical fallback cluster. It advances that broadcast channel's producer/consumer states and assigns `fallback_group_idx`/`in_group_idx`. It does not read expert metadata, claim a work ID, touch fallback group-token storage, or advance the token generation. Preferred clusters skip the registration transaction. The maintained scheduler then derives the fallback channel offset and sets its compile-time first-advance marker ([scheduler line582](/Users/ziangli/playground/projects/flashinfer-w4a16-mixed-clusters/flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/fc1_fc2_fuse_sched.py:582)).

The patch preserves these dependencies:

1. Common `pipeline_init_wait()` completes before registration uses DSMEM/mbarriers. Warpgroup register donation also remains before scheduler-warp divergence.
2. Mixed atomic initialization runs exactly once. Its advanced broadcast state is retained for the later first claim; no barrier phase is reset or duplicated.
3. Static initialization remains after metadata readiness because it decodes a work tile. Uniform atomic initialization retains its existing early preclaim before common pipeline initialization.
4. All `gen_next_work()` calls and publications remain after metadata readiness. The first mixed work-counter claim and inter-fallback token handoff therefore remain after that wait.
5. Registration storage remains zeroed on allocation and in the previous invocation's local-prefix tail cleanup; dispatch does not clear it during startup. No reset or storage layout changes are included.

W4A16's readiness primitive is named barrier9. Dispatch publishes with `arrive()` and continues payload pull, while the scheduler uses `arrive_and_wait()` ([dispatch source](https://github.com/flashinfer-ai/flashinfer/blob/316faec37a4706a2ecc7d46265087f8190b40baa/flashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/src/src/token_comm.py#L1807-L1817)). Moving registration before the scheduler arrival does not make dispatch wait for registration. Registration itself waits only for its physical cluster peers, not its eventual fallback partner. Arrival ordering can change which fallback clusters become partners; the established protocol already permits that.

## Value and measurement boundary

This can hide the one-time fallback registration behind dispatch metadata preparation. It cannot remove the steady-state fallback group-token handoff, increase activation reuse, or reduce weight/dequant/MMA work. Preferred clusters have no registration transaction to hide, and the remaining metadata wait may already be short. A benefit is plausible but unmeasured, with the most direct opportunity at startup-sensitive token counts.

If selected, compare the same optimized mixed-only AUTO12 catalog with and without this patch on the retained kernel at GLM5 EP8 global T32/T4096. Keep the baseline AUTO16 as the external control. Native AUTO eager preparation supplies compilation/liveness; separate correctness or sanitizer runs remain deferred unless a failure requires diagnosis. Isolate this move from producer lookahead when attributing a result.

## Validation and application

Python AST, repository-configured Ruff lint/format, forward/reverse application with exact byte restoration on both candidate2 and candidate3, and both patch application orders passed locally. No source or remote checkout changes and no GPU runs were made. Detailed commands and source hashes are in [`mixed-registration-validation.json`](mixed-registration-validation.json). Patch SHA256: `4f31b40b26b521b4bf36060cdc0e3c662859458e3b6cf66b75c24c4264685ed4`.

When selected and no capture owns the checkout:

```sh
cd /Users/ziangli/playground/projects/flashinfer-w4a16-mixed-clusters/flashinfer
git apply --check ../experiments/mixed-registration-overlap.patch
git apply ../experiments/mixed-registration-overlap.patch
```

Reverse only this patch to restore the chosen candidate2/candidate3 control. This source review establishes the intended ordering; CUDA compilation and runtime liveness of the reordered variant remain untested.
