# PR #7196 integration audit

Scope: read-only comparison of merged #7196 (`03d7f4a399a47e72d93631e19becd804147fc47b`), retained #7290 (`ee88cf2acc59748a64ee2614fed2f16f05f67988`), and new base `fb022756415cc9cad1e1a64ee918860e17638fe8`. Original #7290 base: `215f83cb27e39b6b973c0691b93fc378a53a10e4`. No canonical source edits, ref changes, fetches, GitHub operations, or GPU jobs were performed.

## Required semantic integration

The textual merge can succeed while breaking the shared exact oracle and Rubin W4A16. #7290 prepares gated FC1 weights/scales in `[up16, gate16, ...]` order on SM100/SM103 and preserves `[up64, gate64, ...]` on SM107. Its W4A16 kernel change removes the original 64-to-16 decode composition unconditionally. Merged #7196 explicitly uses this shared kernel on SM107, including custom SwiGLU and GeGLU-tanh. The merged reference adapter also assumes 64-row groups unconditionally.

Use `7196-suggested.patch` after replaying #7290. It makes three narrowly scoped changes:

- The W4A16 launcher locally imports the existing production selector `prepare._cute_dsl_gated_weight_group_size(weight.device)` and passes a private integer through `_get_compiled_kernel`, its cache key, and the kernel constructor. There is no public argument or tactic change, no new architecture flag, and no duplicate production policy.
- The kernel accepts only group sizes 16/64. It retains the original upstream weight-and-scale composition for gated group64, while group16 directly decodes its already prepared row order. The upstream composition and explanatory comment are preserved. Nongated FC1/FC2 behavior is unchanged.
- `canonical_split_w4a16_weights` independently selects 16 for SM100/SM103 and 64 for SM107, explicitly rejecting unsupported devices, and undoes the matching interleave for both packed codes and scales. All callers already pass device-resident prepared tensors, so no caller/API change is necessary. All other shared reference functions, including dense and MegaMoE arithmetic, remain unchanged.

The patch is against the logical replayed source: latest-main versions of these three files, plus the sole retained #7290 W4A16 kernel change removing the composition. These three upstream files did not change between #7196 and the new main head. There is exactly one production constructor call, in `moe_w4a16.py`.

## Exact overlapping files

The intersection of #7196's changed paths and the full retained #7290 diff contains only four files:

| File | Integration rule |
| --- | --- |
| `flashinfer/fused_moe/cute_dsl/blackwell/moe_finalize.py` | Keep #7290 packed FP32-pair/vectorization and launch work while retaining #7196's arithmetic contract: actual slot zero uses separate `mul.rn`, subsequent slots use ordered `fma.rn`, no FTZ, masked slots never load, all-masked output is positive zero. The retained packed implementation already states and implements this contract. |
| `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py` | Preserve all merged runtime-N, two-CTA activation partition, epilogue retirement, PDL, and activation arithmetic changes. Apply only the explicit 16/64 prepared-row control described above. |
| `tests/moe/test_cute_dsl_fused_moe.py` | Keep merged shared exact W4A16 checks, unfused W4A16 parameterizations, and SM107 W4A16 exemption. Preserve #7290's distinct MX dtype/SiTU and new-kernel tactic coverage. |
| `tests/moe/test_unified_moe.py` | Keep merged W4A16 exact typed-activation/reference checks and counterfactual controls, alongside #7290's MX activation/backend support coverage. |

The shared reference path is a semantic overlap even though #7290 did not previously edit it.

## Merged contracts that must remain

- W4A16 runtime MMA N follows the live routed-token count with 8-token alignment for one CTA and 16-token alignment for two CTAs; the peer CTA B load follows the runtime midpoint. Inactive epilogue subtiles are skipped and accumulator release occurs after the last active subtile. Preserve empty-tile handling and static fallback for unsupported internal layouts.
- Keep the merged `moe_w4a16_prepare.py` and launcher use intact: persistent 256-thread BF16 copy, valid-row predicates, 256-bit copies for 32-byte alignment and explicit 128-bit fallback for 16-byte alignment, zero-capacity no-op, and the established sort/permute/FC1 PDL publication order. No workspace ownership change.
- Preserve exact parameterized SwiGLU/SiTU behavior and the common non-FTZ ordered combine rounding contract, including signed zero. Do not reintroduce a separate split reference or a dedicated finalizer/dynamic test file.
- `tests/test_helpers/w4a16_reference.py` remains the shared bit-exact reference for unfused split W4A16 functional/wrapper/MoELayer APIs, deterministic W4A16 MegaMoE, and standard full-K `mm_bf16_fp4(..., backend="cute-dsl")` on SM100/SM103/SM107. Exact assertions require finite BF16 output and equality of the `int16` bit views with zero tolerance.
- Preserve the shared reference's controlled cuBLASLt BF16 accumulation, separate alpha multiply, TF32-off and split-K/reduced-precision-reduction restrictions. No dense split-K/stream-K, CAKE, GEMV, other backend, or fused-TMA-reduce exactness expansion.
- Keep migrated callers in `tests/moe_ep/`, `tests/gemm/test_mm_bf16_fp4.py`, and the trace test. Do not restore `tests/moe_ep/w4a16_reference.py`. MegaMoE production remains untouched; its atomic-combine tests retain their existing tolerance boundary.

## Focused verification after application

1. Check the new row-size argument is in the launcher call, compile cache key, and kernel constructor; assert unsupported row sizes reject explicitly. Verify the public W4A16 API/tactics and existing production selector remain unchanged.
2. Run the existing `TestCuteDslMoeW4A16` scale-update, scale-mapping, and route-tile-boundary tests. They cover serving-owned in-place scale updates, one/two CTA and clustered mapping, runtime-N boundaries, and empty/tail routes.
3. Run existing W4A16 custom SwiGLU, clamp, SiTU and GeGLU-tanh tests; wrapper/CUDA-graph, functional-versus-wrapper, unified typed-activation, and EP route checks. Retain bit equality and negative activation controls. These exercise the changed split adapter and packed combine in the normal pipeline.
4. Execute the same gated W4A16 cases on SM107 when hardware is available; absent SM107 hardware, explicitly report that boundary and prove the group64 composition equals merged upstream by source/layout checks. Do not claim Rubin GPU validation from Blackwell runs.
5. Existing full-K dense and deterministic MegaMoE reference tests are useful integration smoke checks, but no new reference behavior or coverage scope is required. Fused W4A16 combine remains outside requested coverage.
6. Scoped lint/format/AST checks and inspect the final diff for merged tests accidentally dropped, old reference resurrected, or upstream W4A16 runtime-N/preparation changes replaced.

## Completed checks

`7196-suggested-checks.json` binds source and proposed-file hashes plus the patch hash. All three proposed modules parse. AST comparison confirms the only modified shared-reference function is `canonical_split_w4a16_weights`. Forty-eight index-only CPU cases cover 1/3 experts, 64/128/256/1024 rows per half, groups16/64, and row widths1/8/64; both preparations reconstruct identical canonical gate/up order. The upstream `((16,2),4)` / `((1,64),16)` decode mapping is a bijection and maps up64/gate64 storage exactly to up16/gate16 decode order. These are structural checks, not GPU or arithmetic-exactness validation.
