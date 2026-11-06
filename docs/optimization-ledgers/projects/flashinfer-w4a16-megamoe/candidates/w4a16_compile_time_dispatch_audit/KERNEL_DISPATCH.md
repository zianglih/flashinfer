# Kernel and mainloop compile-time dispatch audit

Audited retained commit `586994d8a054470a17c3dab05be8209c75a33128`, before the small epilogue/scheduler changes under review. This is a source audit with selected existing native evidence, not a fresh performance measurement.

## Conclusion

No additional change is warranted in `megamoe_kernel.py`, `dynamic_mainloop.py`, the split-W4A16 transform hook, or the PR's shared shim adapters. The fixed kernel choices already specialize during Python construction or CuTe tracing. The remaining device branches represent warp roles, CTA ranks, routed work, FC1/FC2 phases, pipeline state, and live token tails.

Paths below are relative to `flashinfer/flashinfer/`.

| Area | Evidence and decision |
|---|---|
| `moe_ep/cute_dsl/megamoe/nvfp4_w4a16/megamoe_kernel.py` constructor and `_make_mixed` | MMA geometry, C1/C2 instruction form, BF16 formats, return mode, scheduler mode, register allocation, and stage fitting are Python configuration. Stage-fitting loops execute while constructing the kernel. Adding `const_expr` to ordinary host code would not remove GPU work. |
| Launch preparation | Counter allocation, dispatch return, scheduler initialization, and activation-load C2 specialization already use `cutlass.const_expr`. Fixed H/I reconstruct the GEMM tensor layouts before launch; dynamic row counts remain appropriate for routed activation storage. |
| Raw-weight and activation K loops | Each call receives the fixed FC1/FC2 K tile count. These loops deliberately remain rolled (`unroll=1`) to execute the asynchronous pipeline without duplicating the large body. In saved retained H7168/I2048 N64 PTX, loop bounds are immediate28 and8 at lines1925/2021 and2377/2523. A runtime loop counter is necessary execution state, not a runtime configuration choice. |
| Decode paths | FC1 uses a128-element transform fragment and FC2 uses32. Their per-work phase branch selects different compile-time layouts; the bodies cannot be merged as identical. Split `_transform_tile` has constant fragment loops and constant last-fragment dispatch. Its K loop and prefetch readiness remain dynamic. The `Int32` wrappers around fixed K counts are not by themselves evidence of missed specialization: the saved decoder bounds are immediate28/8 at PTX3462/4284. |
| Shared MMA loop | One body handles both runtime FC phases. It uses phase-selected K bounds and the actual pipeline state. Duplicating the16-atom MMA body just to spell constant loop bounds is not justified. First-K accumulation and valid-token dynamic-N descriptors depend on real work. |
| `dynamic_mainloop.py` | `bf16_static_idesc`, shape checks, CTA-group string choice and the inner K16 emission loop execute in Python tracing (`@dsl_user_op`, without `@cute.jit` on the issuer). They already generate specialized code. Saved N64 PTX contains16 C2 BF16 MMA atoms. Only the first atom uses the runtime first-K accumulation predicate; subsequent atoms accumulate unconditionally. |
| Warp/CTA dispatch | Warp role conditionals choose concurrently active roles in one640-thread CTA. C2's leader/nonleader test is necessary; C1's constant rank mapping can fold. Neither should be changed to a configuration-time choice of a single warp's behavior. |
| Split transform hook | The PR extracts `_finish_transform_stage` and the Mega subclass overrides it. Python method resolution occurs during tracing; there is no device virtual dispatch. Its static TMEM choice and store fence remain specialized. |
| Shared shim adapters | `kernel_helpers.py` adds lazy import symbols; `tuner.py` selects W4A16 host profiles. These are import/setup decisions, not branches inside the GEMM. No edits to vendored transport or other dtypes are needed for this audit. |

## Native evidence

Existing retained-source capture:
`profiles/cu132-recovery0911b-epilogue-constructor-cleanup-candidate-n64-f4-direct-i2048/codegen/result.json`.
Despite its historical candidate-directory name, its recorded source ID is the current retained `2e3b651a854779edcd83f060cd78ff3144c01be5b71b5241b3ad6a26b778864b`; this was verified before using the PTX. Config: H7168/I2048, M256/N64/K256, C2, atomic scheduler, direct return, F4, S2. Register96,640 threads, zero local/stack bytes, B3/raw5/decode3. Line numbers above refer to the saved `.sm_103a.ptx` in that directory.

The C1/static counterpart is `profiles/cu132-recovery0911c-retained5869-before-m128c1-f4-direct-i2048/codegen/`, also recorded source `2e3b...`, with H256/I2048, M128/N64/K256, C1, S3. Its scheduler exposes a compiler-lowering issue discussed in the scheduler audit; it does not imply that phase selection itself can be made constexpr.

## Scope boundary

Fixed model geometry can remove a bounds check only after proving the scheduled CTA is in range. Live token counts, expert skew, phase changes, atomic claims, peer metadata, mbarrier phases, and weight/global-scale tensor values must remain runtime values. Explicit constexpr annotations and full unrolling are tools, not retention criteria: confirm that emitted code improves and preserve the numerical/tail contracts.
