# W4 late shared-store acquisition experiment

Only source delta versus full-gate-03: `moe_w4a16_kernel.py`, SHA256 `777baf6bb832a5152022f8f3e9364f3bddba944c3e17fa2913f68170ea562110`.

Move the existing TMA store-pipeline acquire and epilogue warpgroup barrier to immediately before the next shared-memory write. This leaves TMEM loading and epilogue arithmetic free to overlap the preceding store while retaining the required shared-stage reuse dependency.

- Both source snapshots are immutable; current review edits remain unstaged.
- Control is full-gate-03, candidate is full-gate-04.
- Bounded first screen: TP V3 W4A16, tokens64 and16384, GPU0, same historical UUID, frozen saved tactics, C-A-A-C, strict CUPTI100samples and10warmups, cold-L2 CUDA graphs, no AUTO.
- Only after neutral/winning bounded results, extend to32W4cells across4models EP/TP. Blockscaled kernels are unchanged and will not be rerun.
- Native C++ compilation cache links are reused, managed tactic caches are independently copied and verified immutable.
