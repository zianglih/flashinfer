# Decision: reject the register redistribution

The current retained W4 allocation remains epilogue144 / control80 / dequant96 x2 / gather64. The candidate112/80/112x2/64 gives no demonstrated improvement. No commit or push. No sanitizer.

Source-paired C-A-A-C, retained374ed4c0, two B300 GPUs5/7, CUDA13.2, CuTeDSL4.8.0, image `nvcr.io/nvidia/pytorch:26.05-py3`, actual driver595.91.07. The control is source-equivalent374ed4c0 with remote Git parent1b0; all514 hashes are recorded. Candidate changes only W4 FC1 register allocation. Fixed native winners and routing identities,100 strict CUPTI graph/cold-L2 samples per cell per repeat,10warmups. Positive percentage means candidate faster, `control/candidate - 1`; latencies aggregate the two phase medians per arm.

| Model | Tokens | Control us | Candidate us | Change | Control repeat spread | Candidate repeat spread |
|---|---:|---:|---:|---:|---:|---:|
| ep-kimi-k3-nvfp4 | 4096 | 546.149 | 567.941 | -3.837% | 0.071% | 5.369% |
| ep-kimi-k3-nvfp4 | 8192 | 963.880 | 1050.002 | -8.202% | 6.489% | 0.258% |
| tp-v3-nvfp4 | 8 | 57.056 | 57.176 | -0.209% | 0.114% | 0.140% |
| tp-v3-nvfp4 | 4096 | 480.572 | 480.364 | +0.043% | 0.024% | 0.030% |

The K3 samples show material within-run drift, so the median loss magnitude is not isolated causal proof. Both candidate repeats are slower than both controls, and the stable V3 cases show no useful gain. This is enough to reject rather than widening the experiment. All100samples, first/lastquartile medians and exact repeat spreads remain in `summary.json` and raw results. No clock normalization or selective winner replacement.

Read-only2ms NVML telemetry aligned with CUPTI activity windows reports2032MHz SM and3996MHz memory throughout all16windows, temperatures36–48C. K3EP8K secondcandidate has25samples with event mask4, other windows mask0; coarse/stale clock reporting cannot rule out frequency changes. The power-cap indication could reflect changed utilization, not necessarily an external disturbance. Telemetry is diagnostic and does not convert the observed median loss into a source-only claim.

Validation:33existingW4cases pass;33owned kernels captured,22gather kernels, zero local bytes and no LDL/STL in all gather captures. They cover one/twoCTA, N8/16/32/64/128/192, route tails, legacy layout, SiTU/GeGLU and finalization. Runtime guards passed all8benchmark phases with unchanged compiler options and normal persistent caches. All frozen source/routing/tactic/cache hashes passed.

Harness correction: initialtestattempt stopped before GPUlaunch because its legacy patch hashing appended the separately hash-bound untracked `blackwell/inline_ptx.py`. The corrected runner consistently uses trackedGitdiff plus all514filehashes, matching the measurement manifest. The failed receipt and helper are preserved as `.r0`; candidate source did not change.

Raw phase medians and quartiles (us):

- ep-kimi-k3-nvfp4 T4096: phase medians `[545.956, 553.092, 582.79, 546.342]`; quartiles `[[544.996, 543.14, 588.868, 615.621], [549.381, 550.021, 572.197, 613.413], [549.51, 550.982, 589.542, 585.606], [544.902, 545.158, 546.47, 593.158]]`.
- ep-kimi-k3-nvfp4 T8192: phase medians `[933.591, 1051.353, 1048.651, 994.17]`; quartiles `[[915.079, 915.239, 1053.544, 1057.065], [923.175, 921.8, 1052.841, 1067.977], [922.633, 982.987, 1051.595, 1062.572], [920.074, 917.706, 1023.339, 1056.523]]`.
- tp-v3-nvfp4 T8: phase medians `[57.024, 57.136, 57.216, 57.089]`; quartiles `[[57.024, 57.025, 56.993, 57.025], [56.993, 57.377, 57.057, 57.185], [57.217, 57.473, 57.088, 56.992], [56.992, 56.865, 57.057, 57.152]]`.
- tp-v3-nvfp4 T4096: phase medians `[480.516, 480.292, 480.437, 480.629]`; quartiles `[[480.356, 480.452, 480.579, 480.868], [479.94, 480.196, 480.516, 480.708], [480.517, 480.261, 480.71, 480.325], [480.804, 480.389, 480.485, 480.709]]`.

Evidence archiveSHA256: `299e717079d12fe40ab5137d817327e83cdea58f6b305805c796f7534be8d5c2`. `screen.csv`, `summary.json`, `telemetry-summary.json`, `evidence/perf`, and `evidence/exact` are final. Initial128-dequant/gather32 codegen rejection is in sibling `w4a16-register128/RESULTS.md`.

Aggregation definition: each phase latency is the median of100 CUPTI samples; each arm latency is the median of its two phase medians (for two values this equals their arithmetic mean). Cell speedup is the ratio of those arm latencies minus1. Any reported cross-cell geometric mean is the geometric mean of cell latency ratios, not a geometric average of the raw phase medians. Raw rows are unchanged.
