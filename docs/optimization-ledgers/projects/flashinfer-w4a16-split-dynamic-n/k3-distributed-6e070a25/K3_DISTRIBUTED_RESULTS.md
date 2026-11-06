# Kimi-K3 distributed W4A16 results

Baseline `316faec37a4706a2ecc7d46265087f8190b40baa`; candidate `6e070a25f6cdd3c07c715590dd2b0554aaecda0c`. ABBA order: baseline R1, candidate R1, candidate R2, baseline R2.

Synthetic routed-expert core: EP8, H=3584, I=3072, E=896, top-k=16, SiTU beta=4 and linear beta=25. Native CUPTI timing, 10 warmups, 100 rank-MAX samples per case, cold L2, CUDA graphs, precomputed routing, deterministic unfused finalize, and routing weights applied after FC2. PDL enabled.

Validated four successful runs, 32 rank receipts, 416 tactic-cache hashes, 52 native medians, and all 5,200 finite positive samples. Printed native medians agree within 0.5e-6 ms. Runtime source hashes differ only in the split W4A16 kernel and finalizer; their hashes match the pinned Git objects, and benchmark/timer sources match. Baseline checkouts are clean; candidate diffs contain only the exact three recorded vendor-header symlinks to baseline.

The archived launch script sets `FLASHINFER_AUTOTUNER_LOAD_FROM_FILE=0` and `FLASHINFER_DIST_AWARE_AUTOTUNE=0`; these are recorded launch settings, not independently observed runtime environment values.

All median columns are microseconds. Repeat speedup = B/A; combined speedup = sqrt(B1 × B2 / (A1 × A2)); >1 favors the candidate. Statistics use unrounded sample medians. T=1 and T=2 remain visible but are excluded from aggregates.

| Global tokens | Before R1 (us) | After R1 (us) | Before R2 (us) | After R2 (us) | R1 speedup | R2 speedup | Combined speedup | Direction differs |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :---: |
| 1 | 89.472500 | 91.040500 | 89.296500 | 87.808500 | 0.982777x | 1.016946x | 0.999715x | yes |
| 2 | 97.072500 | 96.113000 | 103.009000 | 108.769000 | 1.009983x | 0.947044x | 0.978007x | yes |
| 4 | 123.505000 | 130.545000 | 131.106000 | 142.417500 | 0.946072x | 0.920575x | 0.933237x | no |
| 8 | 162.033000 | 161.473000 | 158.402000 | 160.145000 | 1.003468x | 0.989116x | 0.996266x | yes |
| 16 | 180.273000 | 169.761500 | 180.593500 | 178.481500 | 1.061919x | 1.011833x | 1.036574x | no |
| 32 | 252.610000 | 245.234000 | 245.154000 | 250.883000 | 1.030077x | 0.977165x | 1.003272x | yes |
| 64 | 329.603000 | 327.491500 | 334.356000 | 332.179500 | 1.006447x | 1.006552x | 1.006500x | no |
| 128 | 383.812000 | 381.763000 | 388.389000 | 385.075000 | 1.005367x | 1.008606x | 1.006985x | no |
| 256 | 427.874500 | 408.483500 | 422.916000 | 418.821000 | 1.047471x | 1.009777x | 1.028451x | no |
| 512 | 433.315500 | 432.996000 | 436.182000 | 436.101500 | 1.000738x | 1.000185x | 1.000461x | no |
| 4096 | 773.671000 | 676.374000 | 776.871000 | 682.967000 | 1.143851x | 1.137494x | 1.140668x | no |
| 8192 | 1444.335000 | 1221.305000 | 1442.107000 | 1225.019000 | 1.182616x | 1.177212x | 1.179911x | no |
| 16384 | 2379.889000 | 2307.601000 | 2364.713500 | 2256.029000 | 1.031326x | 1.048175x | 1.039716x | no |

| Aggregate | Tokens | R1 geometric mean | R2 geometric mean | Combined geometric mean |
| --- | --- | ---: | ---: | ---: |
| overall_11 | 4, 8, 16, 32, 64, 128, 256, 512, 4096, 8192, 16384 | 1.039828x | 1.023825x | 1.031796x |
| decode_8 | 4, 8, 16, 32, 64, 128, 256, 512 | 1.012152x | 0.990047x | 1.001039x |
| prefill_3 | 4096, 8192, 16384 | 1.117386x | 1.119642x | 1.118513x |

Repeat direction disagreements: global tokens 1, 2, 8, 32; aggregates decode_8. A disagreement means one repeat is strictly faster and the other strictly slower; exact ties are not counted. Directions use unrounded ratios, including the separately reported T=1 and T=2 rows.

`K3_DISTRIBUTED_RESULTS.json` retains every timing sample, native model/timing record, rank metadata, input hash, and unrounded statistic. Tactic JSON files remain in the original arm directories.
