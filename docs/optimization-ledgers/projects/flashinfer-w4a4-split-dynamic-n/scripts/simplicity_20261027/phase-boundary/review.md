# Blackwell FC1/FC2 module boundary

Read-only review of clean canonical `54f5c682bbaa52a23a46b6bb76e3cfdce347ec97`. References are the existing Rubin and Hopper CuTe DSL modules only. Exact source hashes and definition locations are recorded in `source.json`.

## Recommendation

Keep the current shared implementation and both existing phase entry modules. The physical split is asymmetric, but the dependency direction is coherent and there is no duplicated mainloop or numerical implementation. Under the user's minimum-unnecessary-diff priority, another source move is not warranted merely to make the file sizes similar. The `finalize_fusion` filename is historical: its module docstring already states that FC1 and FC2 share this kernel, and the FC1 file explicitly identifies itself as a capability adapter.

Existing docstrings already make this ownership explicit. No additional comment, class hierarchy, callback interface, alias, compatibility module, or other source change is needed.

## Current ownership

All paths below are relative to `flashinfer/fused_moe/cute_dsl/`.

| Owner | Current responsibility |
|---|---|
| `blackwell/blockscaled_contiguous_gather_grouped_gemm_act_fusion.py:42` | FC1 capability adapter, logical activation/weight argument order, output-type restrictions; delegates common geometry admission to the shared kernel. It does not define a second device implementation. |
| `blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py:1281` | Shared host resource planning, operand descriptors/layouts, TMA and scale transport, CLC/static scheduling, accumulator pipeline, PDL, kernel launch and teardown. |
| Same module, `Sm100BlockScaledMoeEpilogue:364` | Shared TMEM ownership, load/transpose/store machinery and epilogue synchronization. Activation/quantization methods serve FC1; scatter/bulk/finalize methods serve FC2. The common token-group path dispatches compile-time behavior and shares its TMEM machinery. |
| Same module, FC2 adapter at `3204` | Logical argument order and output/final-scale type restrictions. |
| Outer FC1 wrapper, `blockscaled_contiguous_gather_grouped_gemm_act_fusion.py:947` | Selects activation, input preparation, routed intermediate output, overlap behavior and startup PDL publication. |
| Outer FC2 wrapper, `blockscaled_contiguous_grouped_gemm_finalize_fusion.py:940` | Selects no activation, expanded-row scatter or fused output, routed per-token scaling, and producer-exit PDL publication. |
| Same outer finalize module, `_run_blockscaled_gemm:85` | One common compile/cache/launch path; constructs `Sm100BlockScaledGroupedGemmKernel` directly at line 270. Both phases provide semantic behavior settings. |

The existing phase adapters and package exports retain their original import paths. Current host wrappers use the adapters for capability checks and the shared class for compilation. The tuner also admits shared geometry directly. There is no reverse import from the shared core into the FC1 adapter.

`call-graph.json` records the AST-derived imports, inheritance and relevant calls in all six implementation/wrapper/export modules. It verifies that the FC1 adapter owns only `can_implement` and that the shared core has no reverse FC1 adapter import. Direct source anchors: [FC1 adapter](/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_gather_grouped_gemm_act_fusion.py:42), [shared core](/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py:1281), [shared launch](/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/flashinfer/flashinfer/fused_moe/cute_dsl/blockscaled_contiguous_grouped_gemm_finalize_fusion.py:270).

## What Rubin/Hopper demonstrate

- Rubin FC1 (`rubin/blockscaled_contiguous_gather_grouped_gemm_swiglu_fusion.py:197`) has its own gather-A/SFA producer, optional gather4 transport and fused activation/quantization epilogue. Its activation helpers remain methods of that kernel (`3341`, `3413`, `3512`). Rubin FC2 (`rubin/blockscaled_contiguous_grouped_gemm_finalize_fusion.py:157`) has a separate contiguous-TMA kernel and finalization epilogue (`1505`). They do not import each other's complete phase implementation.
- Hopper FC1 (`hopper/contiguous_gather_grouped_gemm_act_fusion.py:91`) uses a token-gather cp.async pipeline alongside the weight TMA pipeline (module description at `20–45`). Hopper FC2 (`hopper/contiguous_grouped_gemm_finalize_fusion.py:50`) has its own contiguous input and scatter/finalize pipeline. Their epilogues remain in their kernel modules (`835` and `661`); reusable primitives come from shared utilities.

Those architectures support the ownership principle already applied here—kernel-specific epilogue orchestration belongs with its kernel, while reusable primitives stay in utilities. Their separate full phase kernels reflect materially different producer/pipeline implementations. Blackwell's retained design instead prepares FC1 input before the GEMM and shares regular TMA plus the same operand/scheduling pipeline with FC2. Copying the Rubin/Hopper physical split literally would reintroduce duplicated policy and synchronization work that this PR intentionally unified.

Source anchors: [Rubin gather transport](/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/flashinfer/flashinfer/fused_moe/cute_dsl/rubin/blockscaled_contiguous_gather_grouped_gemm_swiglu_fusion.py:197), [Rubin FC2 contiguous TMA](/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/flashinfer/flashinfer/fused_moe/cute_dsl/rubin/blockscaled_contiguous_grouped_gemm_finalize_fusion.py:731), [Hopper FC1 separate gather pipeline](/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/flashinfer/flashinfer/fused_moe/cute_dsl/hopper/contiguous_gather_grouped_gemm_act_fusion.py:20), [Hopper FC2 output pipeline](/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/flashinfer/flashinfer/fused_moe/cute_dsl/hopper/contiguous_grouped_gemm_finalize_fusion.py:18).

## Alternatives and cost

Moving only `_activate`/FC1 overlap methods into the current FC1 adapter would make the core depend on a module that already imports the core. Avoiding that cycle needs a new base module or injected epilogue selection, increasing abstraction and touching validated compiler-visible ownership. Moving the entire shared core to a neutral `blockscaled_contiguous_grouped_gemm.py` would be structurally symmetric, but requires a roughly 3.2k-line move and updates across wrappers, tuner and test imports. That is a possible future rename if these internal module names become a maintenance problem, not a necessary fix for this PR.

No source edits, clones, imports requiring CUDA, tests or GPU jobs were performed. This is an ownership/readability assessment, not a new correctness or performance claim.
