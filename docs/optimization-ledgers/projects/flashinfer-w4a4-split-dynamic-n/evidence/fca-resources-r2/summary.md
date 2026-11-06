# Retained fca compile-only resource baseline

Source `fca8462cbd9096059d0019a206aa760fb34ca8c4`; GPU0 / B200-92 / CUDA13.2 / CuTeDSL4.7.1. All production files matched the completed final-table source receipt before compilation and after all30cases. No kernel was launched; this is resource/codegen evidence only.

Host knobs match production assignment ASTs (`host-policy-proof.json`). All token-scale pointer types are Float32; only NVFP4 FC1 carries a global-scale pointer. The earlier r1 attempt is marked diagnostic-only because it inherited stale pointer types from its historical harness.

All30cases report zero local memory, no SASS LDL/STL instructions, one active CTA perSM and74active two-CTA clusters. Artifacts retain CUBIN/PTX/SASS and cuobjdump resource output for later static-path comparisons.

| Model | Format | Phase | M/N | Threads | Registers | Dynamic SMEMB | Stages | MMA K |
|---|---|---|---|---:|---:|---:|---:|---:|
| v3 | nvfp4 | fc1 | 256/128 | 288 | 70 | 230272 | 4 | 512 |
| v3 | nvfp4 | fc1 | 256/256 | 288 | 80 | 195456 | 5 | 256 |
| v3 | nvfp4 | fc1 | 512/128 | 288 | 82 | 189312 | 4 | 256 |
| v3 | nvfp4 | fc2 | 256/128 | 288 | 110 | 207232 | 6 | 256 |
| v3 | nvfp4 | fc2 | 256/256 | 288 | 120 | 229760 | 5 | 256 |
| v3 | mxfp8 | fc1 | 256/128 | 288 | 70 | 205696 | 4 | 256 |
| v3 | mxfp8 | fc1 | 256/256 | 288 | 88 | 206720 | 6 | 128 |
| v3 | mxfp8 | fc1 | 512/128 | 288 | 86 | 213376 | 5 | 128 |
| v3 | mxfp8 | fc2 | 256/128 | 288 | 116 | 214528 | 7 | 128 |
| v3 | mxfp8 | fc2 | 256/256 | 288 | 124 | 206720 | 5 | 128 |
| v3 | mxfp4-mxfp8 | fc1 | 256/128 | 160 | 78 | 205696 | 4 | 256 |
| v3 | mxfp4-mxfp8 | fc1 | 256/256 | 160 | 78 | 206720 | 6 | 128 |
| v3 | mxfp4-mxfp8 | fc1 | 512/128 | 160 | 82 | 213376 | 5 | 128 |
| v3 | mxfp4-mxfp8 | fc2 | 256/128 | 288 | 116 | 214528 | 7 | 128 |
| v3 | mxfp4-mxfp8 | fc2 | 256/256 | 288 | 124 | 206720 | 5 | 128 |
| v41-flash | nvfp4 | fc1 | 256/128 | 288 | 77 | 230272 | 4 | 512 |
| v41-flash | nvfp4 | fc1 | 256/256 | 288 | 87 | 195456 | 5 | 256 |
| v41-flash | nvfp4 | fc1 | 512/128 | 288 | 80 | 189312 | 4 | 256 |
| v41-flash | nvfp4 | fc2 | 256/128 | 288 | 110 | 207232 | 6 | 256 |
| v41-flash | nvfp4 | fc2 | 256/256 | 288 | 120 | 229760 | 5 | 256 |
| v41-flash | mxfp8 | fc1 | 256/128 | 288 | 72 | 205696 | 4 | 256 |
| v41-flash | mxfp8 | fc1 | 256/256 | 288 | 88 | 206720 | 6 | 128 |
| v41-flash | mxfp8 | fc1 | 512/128 | 288 | 84 | 213376 | 5 | 128 |
| v41-flash | mxfp8 | fc2 | 256/128 | 288 | 110 | 214528 | 7 | 128 |
| v41-flash | mxfp8 | fc2 | 256/256 | 288 | 120 | 206720 | 5 | 128 |
| v41-flash | mxfp4-mxfp8 | fc1 | 256/128 | 160 | 76 | 205696 | 4 | 256 |
| v41-flash | mxfp4-mxfp8 | fc1 | 256/256 | 160 | 78 | 206720 | 6 | 128 |
| v41-flash | mxfp4-mxfp8 | fc1 | 512/128 | 160 | 82 | 213376 | 5 | 128 |
| v41-flash | mxfp4-mxfp8 | fc2 | 256/128 | 288 | 110 | 214528 | 7 | 128 |
| v41-flash | mxfp4-mxfp8 | fc2 | 256/256 | 288 | 120 | 206720 | 5 | 128 |

The9warp FC1 captures use70–88registers/thread; mixed FC1 uses5warps and76–82registers/thread. An extra scheduler warp therefore does not appear register-capacity-limited at these geometries. This is an inference from the baseline, not a candidate occupancy result. Candidate compilation may change registers, spills, stages or SMEM alignment. NVFP4 FC1M256/N128 has the highest FC1 SMEM use (230272B), so its added scheduler storage deserves particular checking.

The six FC2 pairs across models/dtypes provide control artifacts if a scheduler refactor accidentally changes a compile-time-disabled static path. Source-symbol/address normalization may be needed for codegen comparison; do not equate binary metadata differences with instruction differences.
