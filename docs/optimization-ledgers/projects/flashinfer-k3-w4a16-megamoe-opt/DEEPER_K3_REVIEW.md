# Additional K3 source review after flat tactic probes

The next distinct, narrow candidate is a cooperative scan of the scheduler's 112 local expert counts; its [standalone patch, proof and CPU integer audit](COOPERATIVE_GROUP_SCAN_REVIEW.md) preserve the current greedy group boundaries. It changes the scan mechanism, unlike the already tested group-size/depth tactics. It remains an uncompiled hypothesis and has no measured speedup.

## Explicit packed alpha is probably redundant

The FC1 `gate.store(gate.load() * weight_alpha)` and matching `up` expression look scalar in Python, but an earlier native-code audit of this exact idiom already found packed `FMUL2`: 16 instructions for gate alpha and 16 for up across the two emitted half-subtiles, identical on all eight ranks. The same capture already used paired FP32-to-BF16 conversion. [Historical source/codegen audit](../flashinfer-w4a16-megamoe/W4A16_ACTIVATION_AUDIT_001.md:9); [raw PCs and hashes](../flashinfer-w4a16-megamoe/logs/w4a16-activation-audit-001.json).

That capture used CuTe DSL 4.7.1's bundled CUDA 13.3.27 compiler and the old `fe4f813` source; it is not proof of current K3 codegen. Inspect current alpha PCs before considering an explicit pair-loop rewrite. If the current compiler also emits `FMUL2`, an explicit rewrite has no instruction-removal rationale. No specific historical timed explicit-alpha rewrite was found; the prior decision was based on generated code, not a failed performance comparison.

## FC1 activation/TMEM interleaving is a conditional prefill direction

The active W4A4 epilogue preloads both halves' four gate/up fragments, applies the complete first-half activation, transposes the second half, applies its complete activation, then transposes the first half. W4A16 executes each half's gate/up read, alpha, activation, transpose and output store before starting the next half. Cross-half preloading and ordering could expose independent TMEM/MUFU work without changing arithmetic association. [Active W4A4 implementation](flashinfer/flashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/src/moe_nvfp4_swapab/epilogue_refactor.py:1535); [kernel import](flashinfer/flashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/src/moe_nvfp4_swapab/kernel_fc12.py:26); [W4A16 half loop](flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/epilogue.py). The finer-grained `SwigluCompute.fold` interleaving in legacy `epilogue.py` is not the active K3 path and is not evidence of the current SiTU schedule.

This is not the best next decode probe. The saved K3 decode routes have fewer than 32 tokens in every active expert; keeping the otherwise empty second half live could add registers without useful work. The existing epilogue has a 144-register budget. Preloading both halves increases FP32 fragment liveness and needs a deliberate release/wait schedule. The half-guard and scalar/packed/native-tanh probes have not shown a clear gain. Consider interleaving only if a fresh dense-prefill trace shows exposed epilogue/TMEM waits, rather than applying it broadly from the source comparison.

## Closed directions verified in the earlier ledgers

- FC2 decode-fragment size 32 is deliberate. Earlier controlled split-MoE trials retained 128→64 and later 64→32; 32→16 was rejected. Repeating generic fragment-size sweeps lacks a new K3-specific mechanism. [Split ledger](../flashinfer-w4a16/w4a16_optimization_experiments.md:5385).
- Per-K FC1→FC2 readiness masks were implemented, compiled and validated earlier, then rejected after the full AUTO sweep showed a negligible/mixed approximately 0.2% gain. They were not merely postponed. K3 E3072 also needs more mask coverage than the earlier E2048 case. [Final mask result](../flashinfer-w4a16-megamoe/w4a16_optimization_experiments.md:8459).
- LDG256, combine register-budget restoration, FC1 early-wait removal, generic stage/group/geometry changes and activation math rewrites are already covered by existing rejected/flat evidence. None is presented here as a new K3 opportunity. [Prior review](LEDGER_REVIEW.md); [secondary tactic audit](SECONDARY_TACTICS.md); [K16 combine audit](K16_COMBINE_REVIEW.md).

The cooperative boundary scan is the only new candidate prepared in this review. Source analysis does not establish that any remaining scheduler or epilogue work is exposed in K3 timing; fresh compiled artifacts or traces should decide the next step if this isolated candidate is flat.
