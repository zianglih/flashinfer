# R10: vectorized Gather4 route metadata

R6 plus four-index128-bit routing loads, with scalar predication only for partial groups. Kernel SHA `09c7e4d348997dd0e3e86ab4de36b65e3fe410040c5241d7d6df75b6287872af`. FC1 retains four producer warps; FC2 and W4A16 are unchanged. Source is frozen and unretained.

All44 existing selected tests passed (32 primary plus12 supplemental; zero errors/failures/skips). The supplemental launch first failed in argparse because the old harness restricted GPU IDs to4–7. Only that harness allowlist was broadened; failed logs and helper SHA receipts are preserved. No GPU test began during that failed launch.

Four matched same-GPU C-A-A-C jobs, tokens8/256/4096/16384,32cells and12,800 strict CUPTI samples, frozen routes/winners and source checks. Each cell uses100 cold-L2 CUDA-graph samples per phase,10 warmups; NVFP4 includes input quantization; finalize is unfused. B300, CUDA13.2, image `nvcr.io/nvidia/pytorch:26.05-py3`. Geometric mean speedup `100*(control/candidate-1)` versus retained d35:

| Group | R10 vs d35 | Earlier R6 vs d35 |
|---|---:|---:|
| V3 EP8 NVFP4 + per-token | −30.85% | −30.69% |
| V41F EP4 MXFP8 + MXFP4x8 | −47.30% | −47.54% |
| K3 EP8 MXFP4x8 | −64.55% | −64.85% |
| N3U TP8 MXFP8 + MXFP4x8 | −17.83% | −18.44% |

R6 and R10 were measured nonadjacently on different GPU assignments; these differences do not establish a causal R10/R6 improvement. The unchanged W4A16 control is−0.27% in the R10 campaign. Raw cells and audited receipts are in `report/` and `evidence/`.

Codegen audit: all11 captured FC1 variants emit real `LDG.E.128` loads (1–16 static sites). No register/stack/spill growth. K3 registers81→77; V41 mixed76→72; N3U prefill168→166. N3U retains the prior208-byte stack and26LDL/46STL sites, while `R2UR.FILL` sites drop47→16. All11 FC2 PTX and SASS outputs are byte-identical to R6. The independent capture is diagnostic; its timings are excluded. Complete source-bound codegen evidence and comparison are under `../optimization-20261029/metadata/codegen/`.

This improves metadata instruction width but does not resolve the large Gather4 end-to-end regression. No PR retention/push or sanitizer run.
