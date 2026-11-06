Historical comparison covers static unit alphas and the default external FP32 weighted combine.
Pre-merge `4d183b83` was measured on node `hu-pdx-15`; post-merge `4bc27889` and final `1098a348` were measured sequentially on `hu-pdx-129`. Recorded workload, software, canonical weights, inputs and routes match across all eight ranks. The archived prepared unit-alpha hash matches both new effective FC1/FC2 alpha hashes. Each row is the median of 100 sample-wise rank-MAX cold-L2 CUDA-graph CUPTI timings, in milliseconds.

| Global tokens | Pre-merge 4d183b83, node15 ms | Post-merge 4bc27889, node129 ms | Final 1098a348, node129 ms | Pre-merge / final | Post-merge / final |
|---:|---:|---:|---:|---:|---:|
| 1 | 0.09014400 | 0.08523200 | 0.07782500 | 1.158291× | 1.095175× |
| 2 | 0.10812850 | 0.10328100 | 0.09678500 | 1.117203× | 1.067118× |
| 4 | 0.12156850 | 0.11499300 | 0.12000100 | 1.013062× | 0.958267× |
| 8 | 0.13854500 | 0.13825700 | 0.13724800 | 1.009450× | 1.007352× |
| 16 | 0.15334400 | 0.15192100 | 0.15315300 | 1.001247× | 0.991956× |
| 32 | 0.17864100 | 0.17900950 | 0.18024200 | 0.991117× | 0.993162× |
| 64 | 0.20481750 | 0.19942600 | 0.20163400 | 1.015789× | 0.989049× |
| 128 | 0.20307250 | 0.20404900 | 0.20102500 | 1.010185× | 1.015043× |
| 256 | 0.20268900 | 0.20769700 | 0.20184150 | 1.004199× | 1.029010× |
| 512 | 0.21280050 | 0.21197000 | 0.21166550 | 1.005362× | 1.001439× |
| 1024 | 0.23352100 | 0.23075350 | 0.23417700 | 0.997199× | 0.985381× |
| 2048 | 0.31181000 | 0.30880200 | 0.30745700 | 1.014158× | 1.004375× |
| 4096 | 0.46798550 | 0.46523450 | 0.46510800 | 1.006187× | 1.000272× |
| 8192 | 0.78488100 | 0.75983200 | 0.77635800 | 1.010978× | 0.978713× |

8–8192 geometric means: pre-merge / final **1.005964×**; post-merge / final **0.999521×**.
Values above 1 favor the final implementation. Cross-node results do not isolate source effects; sequential same-node runs also retain temporal drift. The historical sequence was PR5279 then PR5019; current runs are post-merge baseline then final. Current codegen dumps and additional hashes are outside timing. No performance claim is made for runtime alpha overrides or opt-in in-kernel reduction.

Archived output hashes available for comparison: post-merge 0/112; final 0/112. The historical archive contains finite/exact-repeat flags but no output hashes, so cross-version bitwise output parity is not asserted. Separate numerical tests establish correctness.
