# Native baseline phase diagnostic

This is a new isolated phase diagnostic, not a repeated primary baseline sweep. It identifies the remaining optimization gap at T16384 using the baseline AUTO winner from the existing B1 cache. GPU3 was idle and used only for this diagnostic; the primary NVFP4 campaign remains on GPU0 and reuses its existing B1.

Baseline a65d5b09e7e4c4c5c160b0161c48becd100b3970, C1 B200, image nvcr.io/nvidia/pytorch:26.05-py3. Native input preparation and actual routing, H7168/I2048, 32 local experts, top-k8; deterministic unfused finalize. Fixed tactic: route256, FC1/FC2 MMA(256,256), cluster(2,1). Ten warmups and100 cold-L2 CUDA-graph CUPTI samples per phase and whole pipeline. Isolated phases do not add exactly to whole-pipeline latency.

16280 local routes,77 routing tiles, maximum733 routes/expert.

| Phase | Median us |
|---|---:|
| route | 26.9440 |
| sort | 7.8400 |
| fc1 | 218.0650 |
| fc2 | 128.9125 |
| combine | 86.1120 |
| full pipeline | 480.4010 |

Raw JSON retains all100 samples per phase, routing histograms, GPU inventory, source/harness hash and runtime metadata. Existing primary GPU0 baseline median is472.464us and is not replaced by this480.401us GPU3 diagnostic.
