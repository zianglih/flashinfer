# Finalizer vector-bound diagnostic: closed

Clean `e2728a290`, B300/CUDA13.2/CuTe DSL4.8, GPU0. No source checkout was
modified. The helper compiles the existing finalizer with its normal four
vectors per thread and with that count capped by the row extent. Geometry,
128-bit memory accesses, arithmetic order and outputs otherwise remain the
same. All three paired output-bit checks pass.

| Hidden dimension | Normal / capped vectors | SASS instructions, both | Registers, both |
|---:|---:|---:|---:|
| 2048 | 4 / 2 | 736 | 58 |
| 1024 | 4 / 1 | 576 | 34 |
| 1536 | 4 / 2 | 976 | 64 |

All variants have zero local memory/stack. The compiler already eliminates
the unused vectors. No production edit or timing campaign is justified by
this source-level simplification. Raw artifacts are in the matching
`optimization-20261027/finalize/codegen` directory on persistent C3 storage;
`probe.py` and `launch_remote.py` reproduce this diagnostic.
