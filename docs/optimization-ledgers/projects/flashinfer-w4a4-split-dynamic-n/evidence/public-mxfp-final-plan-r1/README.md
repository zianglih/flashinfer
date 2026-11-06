# Prepared final public benchmark campaign

This plan is not launched. Re-run prepare_final.py with the final source receipt/path once kernel retention settles; it supports clean or unstaged sources.

V3 EP8 uses GPU2 NV and GPU4 MX; V4.1-Flash EP4 uses GPU3 NV and GPU7 MX. Per-model sequence is clean8b control C1, final public A1, final public A2, closing clean8b C2. A1 emits four complete default public tables with matching TRT/BF16 arms and no CUTLASS. Other phases are CuTe-only. Source-bound compiler artifacts are reused across repeats; AUTO selections are fresh.

A separate V3 mixed-only A1/A2 job on GPU6 supplies final medians on the original mixed-format GPU. Combined with the NV/GPU2 and homogeneous MX/GPU4 final observations, these support the archived-original-control bridge. Original a65 controls are never rerun. That comparison is explicitly archived controls plus fresh candidate, not a new bracketed C–A–A–C.

All sources include api.py, prepare.py, trace/templates/moe.py and the focused test file after clean commit. Runtime receipts include actual CuTe, Torch CUDA, CUPTI, nvidia-nvvm/nvidia-cuda-nvcc and system nvcc separately. The runner/observer bytes are preserved under helpers/. Deployment and launch require parent coordination; source receipts bind the proposed source only, and no timing has occurred from this plan.
