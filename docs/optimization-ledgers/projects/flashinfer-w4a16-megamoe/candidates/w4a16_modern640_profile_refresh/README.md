# Refresh profiles for the current five-warpgroup kernel

This is a queued profiling plan, not a capture result. Run after the next
kernel's numerical checks and full fixed 1–4096 sweep, under the performance
agent's existing exclusive source/cache/GPU window. It does not require an
autotuned sweep merely to establish a completed source owner.

The older `zero-dest512-recovery0908b` NSYS and NCU reports used 512 threads
and REG128. They remain historical mechanism evidence and do not describe
the current 640-thread, REG96, two-decode-warpgroup kernel. Refreshing them
will help choose general pipeline/register work without targeting token2048.

## Reuse the working capture paths

- NSYS: reuse `w4a16_dispatch_decode_reuse512_ep8_nsys/entrypoint.py`'s
  scoped benchmark-script substitution and the benchmark's own profile parent.
  Keep EP8, H7168/I2048/E256/top8, fixed CONTROL, global32 and4096, three
  warmups, two captured iterations, `cuda-sw`, and finite natural exit with
  `--nsys-capture-range-end=none`. Keep ordinary `enable_iket=false`.
- NCU: reuse the successful standalone adaptation from
  `profiles/zero-dest512-recovery0908b-ncu-standalone-002`, together with
  `w4a16_dispatch_decode_reuse512_ep1_ncu/entrypoint.py`. Keep EP1,
  H7168/I2048/E256/top8/T4096, application replay, exact Mega kernel selection,
  two captured actions and the previous PC-sampling metric set. For one rank,
  preserve the successful removal of the six peer/lockstep communicator flags;
  do not retry the known-invalid single-participant TCP communicator.
- Replace only source-owner/resource admission with the current completed
  source and its existing `resource_gate640` implementation. The original
  512-thread helper and old owner hashes are not current admission. The actual
  loaded function must report REG96, 640 threads, exactly two decode groups,
  a 61,440-register initial pool and local0 before its first Mega launch.
  Retain consensus and cached-function identity behavior from the current gate.
- Preserve the benchmark, capture range, staging, final reduction and worker
  cleanup. Do not add a parallel profiler framework or alter `__file__`.
  Keep source/helper hashes, actual frontend/MRO identities, real input
  descriptors and loaded libraries in each worker record.

Use the unchanged same-node C++ native cache from the completed current run;
pin its actual post-run inventory, including the JIT log. Use separate fresh
DSL/driver output directories for the two profilers and record lineinfo.
Do not use a profiler-created cache as an unverified performance owner.
The existing setup recorded NSYS2026.2.1.210 and NCU2026.1.1/build37634170;
record the actual binaries used by the new capture as well.

## Minimum analysis that changes the next experiment

For NSYS, require all eight CUDA devices and exactly two Mega actions per
device at each token count, with all16 resource/source worker records. Keep
external staging/reduction actions in the exported SQLite analysis. Inspect
rank skew and the fraction of the full forward spent in the fused kernel;
profiler durations do not replace CUPTI benchmark latency.

For NCU, first admit the real EP1 production specialization before the profile,
then recheck every application replay worker. Require both requested device0
actions and exact source correlation. Partition PC samples by actual warpgroup
role and distinguish raw-weight waits, decoded-stage acquire, MMA input waits
and epilogue accumulator waits. Inspect the current partial-decode packet's
dependencies, register allocation and LDS/decode/TMEM-store sequence. A sampled
predicate-dependent branch alone does not establish HBM starvation.

EP1 has256 local experts and4096 local rows; EP8 has32 experts and512 local
rows at global4096. Keep that limitation explicit. Use the PC data to select
general-purpose source changes, then retain them using the ordinary EP8
full13 fixed100 sweep. Independent saved-report review can proceed while the
next admitted GPU experiment runs.
