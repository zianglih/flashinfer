# SF-prefix screen

Verified 2,000 archived files, 348 source files per role, 15 jobs, 60 passes, 144 cells and 57,600 raw CUPTI samples. The sole source change is `flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py` at `3b926e6ffb54542f8cd540a117bbfab7547c5c93f8d7bc747562d187538bf2c8`.

Same-GPU C-A-A-C; frozen winners and routes; cold-L2 CUDA graphs, 10 warmups and 100 CUPTI samples. Positive means candidate faster: `geomean(C1,C2) / geomean(A1,A2) - 1`, using all 100 samples for each pass median. No timing substitution, tuning or external baseline rerun.

FC1 K is aligned in all 112 scaled cells. FC2 has a partial stage in 31 cells (2 EP, 29 TP); 81 scaled cells are aligned controls. W4A16 is unchanged in 32 additional controls.

| Class | Topology | Range | Cells | Speedup |
|---|---|---|---:|---:|
| all_scaled | ALL | all | 112 | +0.078% |
| all_scaled | ALL | decode | 56 | +0.056% |
| all_scaled | ALL | prefill | 56 | +0.100% |
| all_scaled | EP | all | 60 | +0.081% |
| all_scaled | EP | decode | 30 | +0.006% |
| all_scaled | EP | prefill | 30 | +0.156% |
| all_scaled | TP | all | 52 | +0.075% |
| all_scaled | TP | decode | 26 | +0.115% |
| all_scaled | TP | prefill | 26 | +0.034% |
| affected_fc2 | ALL | all | 31 | +0.115% |
| affected_fc2 | ALL | decode | 19 | +0.157% |
| affected_fc2 | ALL | prefill | 12 | +0.049% |
| affected_fc2 | EP | all | 2 | +0.126% |
| affected_fc2 | EP | decode | 2 | +0.126% |
| affected_fc2 | TP | all | 29 | +0.114% |
| affected_fc2 | TP | decode | 17 | +0.160% |
| affected_fc2 | TP | prefill | 12 | +0.049% |
| aligned_control | ALL | all | 81 | +0.064% |
| aligned_control | ALL | decode | 37 | +0.005% |
| aligned_control | ALL | prefill | 44 | +0.113% |
| aligned_control | EP | all | 58 | +0.079% |
| aligned_control | EP | decode | 28 | -0.003% |
| aligned_control | EP | prefill | 30 | +0.156% |
| aligned_control | TP | all | 23 | +0.025% |
| aligned_control | TP | decode | 9 | +0.030% |
| aligned_control | TP | prefill | 14 | +0.021% |
| w4a16_control | ALL | all | 32 | -0.013% |
| w4a16_control | ALL | decode | 16 | +0.041% |
| w4a16_control | ALL | prefill | 16 | -0.066% |
| w4a16_control | EP | all | 16 | -0.192% |
| w4a16_control | EP | decode | 8 | -0.006% |
| w4a16_control | EP | prefill | 8 | -0.377% |
| w4a16_control | TP | all | 16 | +0.167% |
| w4a16_control | TP | decode | 8 | +0.088% |
| w4a16_control | TP | prefill | 8 | +0.245% |

| Class | Backend | Cells | Speedup |
|---|---|---:|---:|
| affected_fc2 | CuteDSL MXFP4x8 | 1 | -0.080% |
| affected_fc2 | CuteDSL MXFP8 | 1 | +0.011% |
| affected_fc2 | CuteDSL PER-TOKEN | 15 | +0.034% |
| affected_fc2 | CuteDSL W4A4 | 14 | +0.224% |
| aligned_control | CuteDSL MXFP4x8 | 27 | +0.093% |
| aligned_control | CuteDSL MXFP8 | 19 | +0.073% |
| aligned_control | CuteDSL PER-TOKEN | 17 | -0.018% |
| aligned_control | CuteDSL W4A4 | 18 | +0.088% |
| w4a16_control | CuteDSL W4A16 | 32 | -0.013% |

## Affected cells

| Model | Topology | Tokens | Backend | FC2 tileK/tailK | SF copies removed per final stage | Speedup | C spread | A spread |
|---|---|---:|---|---|---:|---:|---:|---:|
| v41-flash | EP | 4 | CuteDSL PER-TOKEN | 512/256 | 8 | +0.205% | 0.080% | 0.000% |
| v41-flash | EP | 64 | CuteDSL PER-TOKEN | 512/256 | 8 | +0.046% | 0.000% | 0.061% |
| kimi-k3 | TP | 4 | CuteDSL W4A4 | 256/128 | 6 | -0.018% | 0.000% | 0.180% |
| kimi-k3 | TP | 4 | CuteDSL PER-TOKEN | 512/384 | 6 | -0.033% | 0.134% | 0.199% |
| kimi-k3 | TP | 64 | CuteDSL W4A4 | 512/384 | 6 | +0.327% | 0.045% | 0.065% |
| kimi-k3 | TP | 64 | CuteDSL PER-TOKEN | 512/384 | 6 | -0.046% | 0.229% | 0.062% |
| kimi-k3 | TP | 4096 | CuteDSL W4A4 | 512/384 | 6 | +0.078% | 0.030% | 0.027% |
| kimi-k3 | TP | 4096 | CuteDSL PER-TOKEN | 256/128 | 6 | +0.256% | 0.037% | 0.082% |
| kimi-k3 | TP | 16384 | CuteDSL W4A4 | 512/384 | 6 | +0.137% | 0.480% | 0.381% |
| kimi-k3 | TP | 16384 | CuteDSL PER-TOKEN | 512/384 | 6 | +0.227% | 0.065% | 0.017% |
| nemo3-ultra | TP | 4 | CuteDSL MXFP4x8 | 256/128 | 2 | -0.080% | 0.158% | 0.155% |
| nemo3-ultra | TP | 64 | CuteDSL MXFP8 | 256/128 | 3 | +0.011% | 0.065% | 0.029% |
| nemo3-ultra | TP | 4 | CuteDSL W4A4 | 256/128 | 4 | +0.192% | 0.115% | 0.038% |
| nemo3-ultra | TP | 4 | CuteDSL PER-TOKEN | 256/128 | 4 | -0.016% | 0.033% | 0.345% |
| nemo3-ultra | TP | 64 | CuteDSL W4A4 | 512/128 | 12 | +0.172% | 0.069% | 0.115% |
| nemo3-ultra | TP | 64 | CuteDSL PER-TOKEN | 256/128 | 4 | +0.059% | 0.279% | 0.074% |
| nemo3-ultra | TP | 4096 | CuteDSL W4A4 | 256/128 | 6 | +0.152% | 0.039% | 0.016% |
| nemo3-ultra | TP | 4096 | CuteDSL PER-TOKEN | 256/128 | 6 | +0.053% | 0.018% | 0.052% |
| nemo3-ultra | TP | 16384 | CuteDSL W4A4 | 256/128 | 6 | -0.029% | 0.044% | 0.088% |
| nemo3-ultra | TP | 16384 | CuteDSL PER-TOKEN | 256/128 | 6 | +0.015% | 0.072% | 0.005% |
| v3 | TP | 4 | CuteDSL W4A4 | 512/256 | 12 | +0.633% | 0.130% | 0.786% |
| v3 | TP | 4 | CuteDSL PER-TOKEN | 512/256 | 12 | +0.134% | 0.039% | 0.076% |
| v3 | TP | 64 | CuteDSL W4A4 | 512/256 | 12 | +0.532% | 0.011% | 0.046% |
| v41-flash | TP | 4 | CuteDSL W4A4 | 256/64 | 6 | +0.776% | 0.088% | 0.399% |
| v41-flash | TP | 4 | CuteDSL PER-TOKEN | 256/64 | 9 | -0.038% | 0.155% | 0.153% |
| v41-flash | TP | 64 | CuteDSL W4A4 | 256/64 | 6 | -0.004% | 0.201% | 0.100% |
| v41-flash | TP | 64 | CuteDSL PER-TOKEN | 256/64 | 6 | +0.130% | 0.015% | 0.067% |
| v41-flash | TP | 4096 | CuteDSL W4A4 | 512/64 | 14 | +0.086% | 0.007% | 0.026% |
| v41-flash | TP | 4096 | CuteDSL PER-TOKEN | 512/64 | 21 | -0.592% | 0.043% | 0.051% |
| v41-flash | TP | 16384 | CuteDSL W4A4 | 256/64 | 9 | +0.101% | 0.135% | 0.114% |
| v41-flash | TP | 16384 | CuteDSL PER-TOKEN | 256/64 | 9 | +0.110% | 0.007% | 0.040% |

## Negative diagnostics

The table below lists the ten worst scaled primary medians. `Separated` means both candidate pass medians are slower than both control pass medians. Strata are diagnostics, not significance tests, replacements or retention rules.

| Model/topology | Tokens | Backend | Class | Primary | First25 | Last25 | Last50 | Separated | C/A spread |
|---|---:|---|---|---:|---:|---:|---:|---|---|
| v41-flash EP | 16384 | CuteDSL MXFP8 | aligned_control | -1.975% | -0.846% | -3.095% | -1.303% | False | 6.607%/5.032% |
| v3 TP | 16384 | CuteDSL MXFP4x8 | aligned_control | -1.015% | -0.158% | -0.462% | -0.678% | True | 0.171%/0.874% |
| v3 EP | 16384 | CuteDSL MXFP4x8 | aligned_control | -0.768% | +0.413% | -1.997% | -1.173% | False | 1.462%/6.383% |
| v41-flash TP | 4096 | CuteDSL PER-TOKEN | affected_fc2 | -0.592% | -0.559% | -0.639% | -0.591% | True | 0.043%/0.051% |
| kimi-k3 TP | 16384 | CuteDSL MXFP4x8 | aligned_control | -0.366% | +0.584% | +0.476% | +0.254% | False | 1.200%/0.148% |
| kimi-k3 EP | 16384 | CuteDSL MXFP4x8 | aligned_control | -0.341% | +0.944% | -0.457% | +5.159% | False | 4.525%/4.006% |
| kimi-k3 EP | 4 | CuteDSL PER-TOKEN | aligned_control | -0.291% | -0.416% | -0.469% | -0.387% | True | 0.029%/0.001% |
| v3 TP | 16384 | CuteDSL MXFP8 | aligned_control | -0.208% | -0.029% | +0.028% | +0.122% | False | 0.451%/0.380% |
| nemo3-ultra EP | 4 | CuteDSL PER-TOKEN | aligned_control | -0.188% | -0.186% | -0.152% | -0.337% | True | 0.000%/0.150% |
| kimi-k3 EP | 4 | CuteDSL MXFP4x8 | aligned_control | -0.186% | -0.218% | +0.063% | -0.140% | True | 0.094%/0.217% |

## Qualification boundary

The separate source-paired gate passed 532 byte-exact replays and 152 GEMM pairs, including 24 aligned PTX identities. The gate has three one-CTA per-token FC2 uniform spill/fill increases: +26 pairs for static/PDL-off, +4 for CLC/PDL-off, and +4 for CLC/PDL-on. No local/stack spills were introduced. These are codegen exceptions even if selected screen cells show no loss.

0 screen cells match that captured FC2 M128/N128/one-CTA/Ksteps8/tail128/CLC/PDL-on geometry. This does not prove other uncompiled geometries have no spill growth. Timing cannot identify uniform-spill causality.

The shared operand TMA volume, transaction-barrier bytes, synchronization and MMA update plans are unchanged. Only the valid final-stage SMEM-to-TMEM SF-word prefix is copied. Full-stage/aligned codegen has separate captured identity evidence; aligned screen cells remain controls rather than speedup attribution.

No sanitizer, broad pytest or new source variant was run for this screen. Raw samples, routing, tactics, managed caches, clock/temperature snapshots and source/helper hashes remain in the archive and `classified-audit.json`.

## Assessment

The affected-stage aggregate is near neutral, with a small positive decode result. V41F TP per-token T4096 has a consistent 0.5925% prefill cost: both candidate passes are slower than both controls, and first25/last25/last50 diagnostics remain negative. Preserve this tradeoff; the aggregate does not erase it.

The largest negative scaled primary median is an aligned V41F EP MXFP8 T16384 cell (−1.975%) with 6.61%/5.03% control/candidate spread. Aligned V3 TP MXFP4x8 T16384 is −1.015% with separated pass medians and all negative strata, although the magnitude varies across strata. Both remain in the results; neither is evidence that reducing partial-stage copies caused the change. The gate proves full-stage PTX identity only for its captured configurations.

These measurements support judging the patch as removal of redundant final-stage SF-copy work with near-neutral end-to-end timing, not as closure of the broader performance gaps. Retention and final-composition decisions belong to the parent campaign.
