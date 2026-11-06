# R4 broader correctness qualification

**12/12 passed**: 10 bit-exact cases and 2 existing tolerance/cosine cases. No skips, failures or timeouts.

Base `d35fcfda03875077b3af8455575cc1d20e866a8c`, kernel `6fae1558326e72aa8beab25520c9e7be1734e03b6ff39d190025f2445d09ed2a`. Every case verified all513 source hashes, full patch and persistent native-cache links before/after execution. `nvcr.io/nvidia/pytorch:26.05-py3`; B300 GPUs4–7. No performance measurement or sanitizer run.

| Case | PDL | Actual schedule | CTA / N | Assertions |
|---|---|---|---|---|
| nvfp4-clc-off | off | CLC FC1+FC2 | 2 / 128 | bit exact |
| per-token-clc-off | off | CLC FC1+FC2 | 2 / 128 | bit exact |
| mxfp8-clc-off | off | CLC FC1+FC2 | 2 / 128 | existing tolerance/cosine |
| nvfp4-clc-on | on | CLC FC1+FC2 | 2 / 128 | bit exact |
| per-token-clc-on | on | CLC FC1+FC2 | 2 / 128 | bit exact |
| mxfp8-clc-on | on | CLC FC1+FC2 | 2 / 128 | existing tolerance/cosine |
| nvfp4-n16-off | off | static | 1 / 16 | bit exact |
| per-token-n16-off | off | static | 1 / 16 | bit exact |
| mxfp4x8-n16-off | off | static | 1 / 16 | bit exact |
| mxfp4x8-n128-off | off | static | 2 / 128 | bit exact |
| mxfp4x8-n16-on | on | static | 1 / 16 | bit exact |
| mxfp4x8-n128-on | on | static | 2 / 128 | bit exact |

All cases also assert FC1 Gather4 uses384 threads, FC2 regular TMA uses256, and compiled PDL/geometry match the requested values. The six CLC cases explicitly verify enabled CLC after occupancy policy. MXFP4x8 uses static fixtures only.

Full logs, JUnit XML and compile-mode receipts are in `broader-evidence/broader/gpu*/`. `broader-qualification.json` binds the archived evidence and every case log by SHA256. GPUs4–7 were released after completion; no further GPU commands are planned.
