# Numerical, layout, and caller-contract audit — 2026-09-28

Audited rebased head `bde427290b33c55489e39c75d7e2a25365358ca0` against upstream `07e519fcc149f39e6dd00264149c092c2e37767e`; traced upstream changes since the old base `eb5f05be1f8e3ef8aa017a66dcbd5d80119b1095`. Read `docs/code_review_guidance.md`. This audit did not execute GPU work or modify repository source.

**No demonstrated numerical or memory-correctness blocker in the rebased diff.** New upstream callers enlarge the validation scope: W4A8 can now request unfused finalize, and the MXFP4 planned path has a separate expanded-row reduction. GPU validation remains required; the scripts below are prepared, not results.

## Contract checks

- **Rebase integration is correct.** `fused_moe.py:687–711` preserves the `skip_unpermute` branch, caller-owned partial buffer, dictionary of arguments, and `_prepared_launches["unpermute"]` registration. Only the reduction callable is replaced. Fixed-address replay keeps the input/map tensors alive through that dictionary and resolves the current stream on invocation.
- **New W4A8 scope is real.** Upstream `_moe_core_impl` removed its old unfused rejection (`fused_moe.py:337–353`); it produces the same BF16 expanded-row FC2 output as W4A4. It requires BF16 output and FP32 routing weights (`fused_moe.py:148–175`). The new helper accepts both. Do not describe W4A8 unfused as still unsupported or validated merely by the existing fused W4A8 tests.
- **No FP16 regression.** W4A16 runner still rejects output other than BF16 (`tuner.py:1047–1048`). W4A4/8 FC2 is invoked with `out_dtype="bfloat16"`; its output-dtype guard rejects a mismatched provided tensor before reduction (`blockscaled_contiguous_grouped_gemm_finalize_fusion.py:625–634`). These guards predate the PR. The low-level native reducer's broader standalone dtype support does not establish a public FP16 MoE contract.
- **MXFP4 planned reduction is preserved.** `mxfp4.py:2362–2416` passes BF16 caller-owned workspace rows plus `skip_unpermute=True` in experimental dense two-stage mode; `Mxfp4MoEPlan._prepare` binds its separate `plan_finalize_rows(..., expanded_rows=True)` at lines 774–782. That path does not call the new helper. It does execute the changed unfused FC2 kernel, so prepared replay / dual-tile tests remain relevant. Workspace and output intervals are explicitly checked for overlap at lines 2285–2311.
- **Native arithmetic parity.** `moeUtils.cu:160–208` is unchanged since the old base: ascending top-k accumulation in float, one final BF16 conversion, negative-map routes skipped before expert-row load. Its JIT retains default `-use_fast_math` (`jit/core.py:702,740–741`; `jit/moe_utils.py` does not opt out). The helper's explicit `fma.rn.ftz.f32` and final BF16 cast preserve this contract. This is parity with the native fast-math reducer, not exact-real or non-FTZ FP32 arithmetic.
- **Masking and offsets.** `moe_finalize.py:115–155` checks map validity before expert reads, keeps permuted row zero valid, and uses the map only as a validity mask for expanded rows. All-masked rows retain positive zero. Data offsets widen the row/token to Int64 before multiplying by hidden size. Routing indices remain Int32 as in upstream routing/native reduction; the PR does not expand that interface's supported range.
- **Vector bounds and alignment.** The host requires contiguous matrices, same CUDA device, positive hidden size divisible by eight, matching row capacities, and 16-byte input/output alignment (`moe_finalize.py:186–212`). Every vector begins on an eight-element boundary, so `vector_column < hidden_size` implies all eight BF16 elements are in bounds, including partial CTA tiles. Threads beyond the hidden tail neither read nor write expert data.
- **Aliasing and metadata preconditions.** The internal helper documents separate input/output and in-range nonnegative permuted indices; it does not synchronize to inspect map values or perform overlap scans. Production W4A4/8 and W4A16 callers allocate separate intermediate/output storage. No newly reachable aliasing caller was found. Its pre-wait metadata loads rely on completed routing: W4A4/8 core sort remains non-PDL; W4A16's existing sort→permute→FC1→FC2 waits provide the chain. The rebased callback path preserves these launches.
- **Cache / graphs.** Cache identity includes device, hidden size, top-k, scale dtype, both launch regimes, PDL flag, and row layout; runtime token count and all tensor pointers are passed on every invocation. Thresholds at 8/9 and 1024/1025 select different specializations deliberately. No graph-captured pointer was added to the global cache. Warm the kernel before graph capture, as existing native tests do.
- **Architecture boundary unchanged.** Rubin still rejects unfused finalize upstream, before the replacement helper. SM12x and BF16/Hopper MoE implementations are separate paths and are outside this diff.

## Validation prepared for the parent

`scripts/run_native_tests.sh` runs bounded existing upstream nodes in three independently logged phases, preserving commands, exit codes and JUnit XML:

1. Deterministic accuracy for W4A4 per-tensor/per-token and W4A16; cluster padding/partial tiles; all 48 W4A16 route-boundary cases; both finalize modes of wrapper graph replay and simulated EP8; new gather K-tail cases; W4A8 fused API/tactic controls; poisoned routing and odd tile-count controls.
2. Existing MXFP4 prepared replay tests for dual-route selection, route preprocessing with PDL, and cluster-split schedules, using default fused finalization.
3. Dual-route and cluster-split replay tests with `MXFP4_DENSE_TWO_STAGE=1`, covering the retained `skip_unpermute` path and independent finalizer. The fused memset-policy test is deliberately excluded from this phase because its assertions require fused output clearing.

Existing `test_w4a8_fused_moe_tactics_and_apis` only tests the default fused setting; the generic mode matrix excludes W4A8. `scripts/check_w4a8_unfused.py` closes that precise gap without adding repository tests:

- Fixed legal one-CTA tactic; H=256, I=128, E=256, local E=32, top-k=8.
- N=1,17,1025; EP8 offsets 0 and 128; PDL off/on: 12 pipeline configurations.
- Four phases: mixed local/nonlocal, changed activation and routing weights, all nonlocal, restored; three graph replays per phase.
- 96 BF16 bitwise comparisons against the native reducer consuming the **same** FC2 rows, plus graph/eager, PDL off/on, all-masked zero, and restored-input equality. These checks isolate the reduction and synchronization contracts; they are not an independent GEMM accuracy oracle.

Both new task-only scripts pass host syntax checks. No GPU outcome is claimed here. Existing broader coverage still does not exhaust signed/subnormal routing weights, >2 GiB data offsets, all standalone scale dtypes, concurrency, or every launch threshold; prior archived tests for these remain historical until rerun at this head.

## Optional cleanup

The helper docstring's routing explanation currently names W4A4 but also applies to W4A8. Changing that one label to “W4A4/W4A8” would make the newly reachable scope explicit; this is documentation only, not a correctness blocker. No fallback dtype branch or new overlap scan is justified by a demonstrated supported caller.
