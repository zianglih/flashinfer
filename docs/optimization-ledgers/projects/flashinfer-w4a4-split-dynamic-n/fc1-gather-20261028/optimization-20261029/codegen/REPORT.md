# R6 codegen audit

Two N3U TP8 prefill FC1 specializations spill. Other sampled FC1 specializations, including the severe K3 EP8 slowdown, are spill-free. All22cubins were captured from the exact frozen R6 source and saved benchmark winners; no autotune was run.

| Case | Tokens | Backend | N / CTA | CLC | Stages | Regs | Stack B | LDL / STL sites | R2UR.FILL sites |
|---|---:|---|---|---|---:|---:|---:|---:|---:|
| ep-kimi-k3-mxfp | 4096 | CuteDSL MXFP4x8 | 128 / 2 | False | 9 | 81 | 0 | 0 / 0 | 0 |
| ep-v3-nvfp4 | 16384 | CuteDSL W4A4 | 256 / 2 | False | 5 | 94 | 0 | 0 / 0 | 0 |
| ep-v3-nvfp4 | 16384 | CuteDSL PER-TOKEN | 128 / 2 | False | 8 | 104 | 0 | 0 / 0 | 0 |
| ep-v41-flash-mxfp | 8 | CuteDSL MXFP8 | 32 / 2 | True | 5 | 84 | 0 | 0 / 0 | 0 |
| ep-v41-flash-mxfp | 8 | CuteDSL MXFP4x8 | 32 / 2 | True | 11 | 74 | 0 | 0 / 0 | 0 |
| ep-v41-flash-mxfp | 4096 | CuteDSL MXFP8 | 128 / 2 | True | 4 | 82 | 0 | 0 / 0 | 5 |
| ep-v41-flash-mxfp | 4096 | CuteDSL MXFP4x8 | 128 / 2 | False | 9 | 76 | 0 | 0 / 0 | 0 |
| tp-nemo3-ultra-mxfp | 256 | CuteDSL MXFP8 | 16 / 2 | True | 11 | 112 | 0 | 0 / 0 | 0 |
| tp-nemo3-ultra-mxfp | 256 | CuteDSL MXFP4x8 | 16 / 1 | False | 10 | 108 | 0 | 0 / 0 | 0 |
| tp-nemo3-ultra-mxfp | 16384 | CuteDSL MXFP8 | 256 / 1 | True | 4 | 168 | 208 | 26 / 46 | 47 |
| tp-nemo3-ultra-mxfp | 16384 | CuteDSL MXFP4x8 | 256 / 1 | True | 4 | 168 | 208 | 26 / 46 | 47 |

AllFC1 kernels use384threads and .minnctapersm1. No PTX .maxnreg or setmaxnreg directive appears. The N3U N256/1CTA/CLC kernels hit168registers/thread and208bytes of stack with26LDL/46STL static instruction sites. cuobjdump reportsLOCAL0 even for these spilling kernels; STACK and SASS must be checked together. These are static sites, not dynamic executed counts. R2UR.FILL is a register-bank transfer, not itself an HBM spill.

N3U spilling artifacts: `evidence/3-tp-nemo3-ultra-mxfp/capture/004-fc1.*` (MXFP8) and `006-fc1.*` (MXFP4x8). K3 clean artifact: `evidence/0-ep-kimi-k3-mxfp/capture/000-fc1.*`. Each directory contains PTX,CUBIN,SASS,resourceusage,and source-bound capture receipt; parent bindings.json ties its routes/winners to existing public benchmark results.

The four jobs ran onB300 GPUs0–3 with600second process-group timeouts. Alljobs passed source/winner/route/cache checks and allGPUs were idle at export. Eight-byte SHARED accounting is not used: exact dynamic shared storage is recorded from SharedStorage.size_in_bytes in summary.json; cuobjdumpSHARED1024 is static-only. Container nvcr.io/nvidia/pytorch:26.05-py3; generated PTX records NVVM CUDA13.4.59 from the DSL toolchain. Diagnostic timings are excluded from retention.

No production files were changed by this audit. Persistent native compilation caches and frozen winner caches remain intact.
