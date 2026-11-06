# Kimi-K3 distributed W4A16 results

Baseline `316faec37a4706a2ecc7d46265087f8190b40baa`; candidate `97e8d0c8bb86b352ccb42f2654ddc2ab9a8e6939`. ABBA order: baseline R1, candidate R1, candidate R2, baseline R2.

Synthetic routed-expert core: EP8, H=3584, I=3072, E=896, top-k=16, SiTU beta=4 and linear beta=25. Native CUPTI timing, 10 warmups, 100 rank-MAX samples per case, cold L2, CUDA graphs, precomputed routing, deterministic unfused finalize, and routing weights applied after FC2. PDL enabled.

Validated four successful runs, 32 rank receipts, 416 tactic-cache hashes, 52 native medians, and all 5,200 finite positive samples. Printed native medians agree within 0.5e-6 ms. Runtime source hashes differ only in the four expected split W4A16 production files; every tracked source hash matches pinned Git objects, and benchmark/timer sources match. Both checkout diffs contain only the exact three recorded vendor-header symlinks to baseline.

The archived launch script sets `FLASHINFER_AUTOTUNER_LOAD_FROM_FILE=0` and `FLASHINFER_DIST_AWARE_AUTOTUNE=0`; the observer also verifies those runtime settings and the loaded NCCL 2.30.7 library in all 32 rank receipts.

All median columns are microseconds. Repeat speedup = B/A; combined speedup = sqrt(B1 × B2 / (A1 × A2)); >1 favors the candidate. Statistics use unrounded sample medians. T=1 and T=2 remain visible but are excluded from aggregates.

| Global tokens | Before R1 (us) | After R1 (us) | Before R2 (us) | After R2 (us) | R1 speedup | R2 speedup | Combined speedup | Direction differs |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :---: |
| 1 | 111.376500 | 77.984500 | 91.425500 | 79.200500 | 1.428188x | 1.154355x | 1.283992x | no |
| 2 | 108.385500 | 88.288000 | 102.449500 | 108.368500 | 1.227636x | 0.945381x | 1.077304x | yes |
| 4 | 131.121000 | 132.193000 | 129.121500 | 131.825000 | 0.991891x | 0.979492x | 0.985672x | no |
| 8 | 164.145500 | 162.722000 | 156.290000 | 149.873000 | 1.008748x | 1.042816x | 1.025641x | no |
| 16 | 179.569000 | 177.634500 | 179.234000 | 178.929000 | 1.010890x | 1.001705x | 1.006287x | no |
| 32 | 255.011000 | 246.114000 | 273.635000 | 249.986000 | 1.036150x | 1.094601x | 1.064975x | no |
| 64 | 336.019000 | 333.058000 | 354.404500 | 334.724000 | 1.008890x | 1.058796x | 1.033542x | no |
| 128 | 392.212000 | 386.979000 | 390.467000 | 390.100000 | 1.013523x | 1.000941x | 1.007212x | no |
| 256 | 430.467000 | 421.316000 | 420.885000 | 419.890500 | 1.021720x | 1.002368x | 1.011998x | no |
| 512 | 444.355000 | 438.995000 | 439.732000 | 435.157000 | 1.012210x | 1.010513x | 1.011361x | no |
| 4096 | 795.573500 | 709.380500 | 806.647500 | 690.647500 | 1.121505x | 1.167958x | 1.144496x | no |
| 8192 | 1448.026500 | 1215.912000 | 1427.468500 | 1223.375500 | 1.190897x | 1.166828x | 1.178801x | no |
| 16384 | 2480.445500 | 2346.150500 | 2428.405500 | 2335.190000 | 1.057241x | 1.039918x | 1.048543x | no |

| Aggregate | Tokens | R1 geometric mean | R2 geometric mean | Combined geometric mean |
| --- | --- | ---: | ---: | ---: |
| overall_11 | 4, 8, 16, 32, 64, 128, 256, 512, 4096, 8192, 16384 | 1.041555x | 1.049636x | 1.045588x |
| decode_8 | 4, 8, 16, 32, 64, 128, 256, 512 | 1.012935x | 1.023291x | 1.018100x |
| prefill_3 | 4096, 8192, 16384 | 1.121889x | 1.123253x | 1.122571x |

Repeat direction disagreements: global tokens 2; aggregates none. A disagreement means one repeat is strictly faster and the other strictly slower; exact ties are not counted. Directions use unrounded ratios, including the separately reported T=1 and T=2 rows.

`K3_DISTRIBUTED_RESULTS.json` retains every timing sample, native model/timing record, rank metadata, input hash, and unrounded statistic. Tactic JSON files remain in the original arm directories.
