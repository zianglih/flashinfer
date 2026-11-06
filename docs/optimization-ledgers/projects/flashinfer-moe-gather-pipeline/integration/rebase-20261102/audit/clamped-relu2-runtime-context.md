# Runtime activation state on the local epilogue

Source snapshot: `017d91be1`; implementation inspected without source edits.

- The kernel makes a shallow Python copy of the compile-time epilogue template in the epilogue warpgroup. This preserves the cached template and avoids retaining SSA values on the cached kernel object.
- `clamped_relu2_limit[0]` and its Float32 reciprocal are bound once to that local copy after the existing PDL wait and before the persistent tile loop. The existing runtime pointer handoff and graph mutation semantics are unchanged.
- Both overlapping and ordinary epilogue paths call the local object. `_activate` reads its invariant runtime attributes. Other activations compile out the attribute loads and arithmetic; they require no placeholder arguments or new object fields.
- Removed the clamp parameter tuple from the activation, token group, overlapping FC1, and ordinary epilogue helper interfaces. No wrapper tuple or new configuration axis replaces it.

## Why no MLIR extraction protocol is required

`3rdparty/cutlass/python/CuTeDSL/cutlass/base_dsl/dsl.py:1602-1615` implements nested `@cute.jit` calls by directly executing the transformed function body when an MLIR insertion point is already active. A nested bound epilogue method therefore receives the local Python `self` directly; it is not turned into a separate MLIR function parameter. The bound Float32 values refer to SSA definitions in the dominating epilogue branch. All uses remain in that branch or nested regions, after their definitions.

The generic extraction fallback at `dsl.py:98-123` returns no values for a plain Python object; reconstruction at `dsl.py:155-193` preserves such an object when there are zero values. Neither generic mechanism needs to walk these runtime attributes for nested inlined methods.

This is the same lifetime pattern as the kernel-local MegaMoE contexts:

- `flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/epilogue.py:119-130` constructs FC1 and FC2 epilogue objects inside `@cute.jit run`.
- `epilogue.py:202-219` binds runtime thread IDs and tensors on the FC2 context.
- `flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/tmem_epilogue.py:357-379` supplies that context's immutable wrapper and an explicit empty MLIR extraction protocol. Its empty protocol has the same no-argument outcome as a plain local object; our implementation reuses the existing epilogue class instead of adding another wrapper type.

## Validation boundary

Ruff format/check and Python compilation passed before the commit. Source-level dominance, cached-object lifetime, activation specialization, and both call paths were inspected. C3 kernel compilation, exact output checks, and runtime CUDA graph mutation checks are delegated to the ongoing validation run; this note does not claim those results.

## C3 compile follow-up

The first C3 compile of `017d91be1` found a separate AST limitation: `epilogue.run(...)` marks the local epilogue as a potentially mutated loop-carried object (`ast_preprocessor.py:979-981`), which a plain Python context cannot lower. The nested JIT dispatch reasoning above remains valid, but is insufficient for receiver mutation analysis. A `Constexpr` local annotation is not consulted by that analysis.

The minimal follow-up uses explicit unbound calls (`Sm100BlockScaledMoeEpilogue.run(epilogue, ...)` and `.run_overlapping_fc1(epilogue, ...)`). The context is then a read-only argument captured from the enclosing epilogue branch, avoiding the conservative mutable-receiver classification. This does not change the method implementation, device arithmetic, object lifetime, or runtime kernel ABI. Ruff and Python compilation pass; fresh C3 compilation is pending.
