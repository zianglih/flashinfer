# Current442 pipeline profiles

Production442d2aa53, C1 B200 GPU4, nvcr.io/nvidia/pytorch:26.05-py3,
CUDA13.2, CuTe DSL4.7.1. Native NVFP4 at16K, H7168/I2048, top-k8,
32 local experts; saved AUTO geometry FC1 logical M512/N128 and FC2 M256/N128.
No historical primary baseline was rerun. All outputs/SF bytes remained exact
against the uninstrumented current kernel. These are profiler diagnostics,
not primary performance/retention timings.

NCU full metric set,40 replay passes perphase: FC1 270.624us, tensor-active
45.95%,80 registers/thread,189312 dynamic SMEM bytes,634.332MB DRAM reads.
FC2 155.136us, tensor-active38.45%,110 registers/thread,178688 dynamic SMEM,
284.441MB DRAM reads. The complete report, CSV including units, source hashes,
routing histogram and logs are retained under results/native-ncu.
Six unsupported CTC metrics were reported; all requested kernel replays completed.

First-two-cluster iKET sampling (task-local only; production keeps all-CTA
opt-in markers) captured six launches; the summary reports the last launch.
Leader FC1 mean accumulator-empty wait is1.174us/tile, compared with4.328us
in the earlier13ca trace; epilogue body is4.266us versus4.334us. The reduced wait
supports the intended overlap mechanism. Marker overhead and different source
versions prevent treating these intervals as additive uninstrumented timings.
Current per-K waits: local SF90.2ns, peer SF79.1ns, TMA-ready59.1ns;
producer SF-ring empty157.6ns and TMA-ring empty78.5ns. Stage counts and instruction
issue order remain worthwhile independent experiments. Raw compressed traces
and all CTA/warp intervals are in results/iket442-nb2*.

Reproduction uses immutable build.py snapshots, probe_iket.py, and the established
../native-ncu-comparison/profile_phases.py. Command receipts are in the local
session log; expected-head guards and full hashes are in output JSONs. NCU
export uses --print-units base (the initial --units spelling failed only during
CSV export and was corrected without rerunning a kernel).
