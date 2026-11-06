# Replacement inventory

`fi-fc1-gather-1028`, C3 / ziangli, requested image `nvcr.io/nvidia/pytorch:26.05-py3`. Read-only inventory ran after parent readiness confirmation.

- All eight B300 GPU UUIDs exactly match the previous box. All were idle, with0MiB allocated, and there were no compute processes.
- Retained d35 and R4 sources each passed their513-file and full-patch checks. All18 native cache symlinks (nine per source) resolve to the expected existing persistent targets. The Python environment and dependency directory remain available.
- CUDA13.2.78; Nsight Compute2026.1.1; PyTorch2.12.0a0+5aff3928d8.nv26.5.50603568; CUTLASS DSL4.8.0; pytest9.1.1; apache-tvm-ffi0.1.15.post1.
- The old NCU controller was interrupted during the first retained/control process. Its log contains only profiler startup and connection; no `.ncu-rep`, exported counters or `selection.json` exists. The candidate process never started. There is no completed counter evidence to recover.
- No source, cache or remote artifact was modified by the inventory. No profiling, compilation or GPU test was resumed; parent owns new reservations.

`recovery-inventory.json` contains all command outputs, source/cache checks and partial-artifact hashes. `recovery-summary.json` compares the new GPU UUIDs with the pinned R3 performance receipts.
