# Current K3 T64 chain diagnostic

Source `f7182d5c871b367f4641d6d7e2098254d63147e3`; current public AUTO winners, B300 GPU7, CUDA 13.2 image `nvcr.io/nvidia/pytorch:26.05-py3`. The NVFP4 public contract includes initial input quantization, PDL, unfused CuTe combine, and precomputed K3 routing. No retuning or production edits. Persistent native C++ and source-bound DSL caches are reused.

Three cold-L2 graph replays per backend are captured with NSYS. This is diagnostic evidence, not the 100-sample CUPTI retention measurement. The current public medians are 237.762 us CuTe and 235.379 us TRTLLM. Do not add kernel medians because PDL permits overlap.

| Mean chain endpoint contribution | CuTe, us | TRTLLM, us | CuTe minus TRTLLM, us |
|---|---:|---:|---:|
| Through FC1 | 164.480 | 165.472 | -0.992 |
| FC2 extension | 72.053 | 67.744 | +4.309 |
| Combine tail | 2.795 | 2.432 | +0.363 |
| Whole chain | 239.328 | 235.648 | +3.680 |

CuTe FC2 overlaps FC1 more (median 6.880 vs 4.512 us), but its exposed extension is still longer. The current bottleneck is consequently FC2, not an observed FC1 startup deficit. This does not establish whether memory traffic, instruction issue, scheduling or the epilogue is responsible. The old `0def` NCU results used different source/tactics and cannot serve as current causal evidence.

Selected CuTe tactic: N32, M128/one CTA for each FC, K8/K8, shared CLC enabled. TRTLLM tactic `[8,99]`. Exact cache, source/helper hashes, commands, environment and successful completion are in `evidence/receipt.json`; local collection hashes are in `evidence/collection.json`. `analyze_nsys.py` produces `evidence/nsys-summary.json` from the collected CSV traces. GPU7 was verified idle after completion.
