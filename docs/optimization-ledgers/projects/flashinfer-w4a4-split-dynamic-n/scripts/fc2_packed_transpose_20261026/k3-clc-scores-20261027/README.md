# K3 NVFP4 T16384 native all-CLC tactic-score diagnostic

Single native bucket selected using public `autotune(tuning_buckets=(16384,))`, isolated empty selection cache, and unchanged source/all-CLC tactics. The benchmark still measures10warmup/100cold-L2 CUDA-graph CUPTI samples with initial quantization included. Source and native compiler-cache namespace match the full all-CLC campaign. This is diagnostic, not a replacement for native full-campaign retention.

Successful W4A4 profiles:160; policy observed directly on every profile: cold-L2 **eager**, not graph. The public benchmark explicitly passes `autotune_use_cuda_graph=False` for NV formats. Thus the measurement differences are balanced synthetic routes/eager event timing versus real sigmoid routes/graph CUPTI, despite both being cold. No policy or production source was changed.

| Candidate | Native profile (µs) |
|---|---:|
| Best N256 (M256/256, K4/4) | 952.784 |
| Best N128 (M256/512, K4/4) | 957.424 |
| Published geometry + CLC (N128 M128/256 K8/4) | 1013.056 |

The new native search repeats the N256 winner; best N128 is only0.49% behind in native profile time. The selected winner measured909.670µs in the public graph/CUPTI timing. These scores are newly captured; original full-campaign INFO logs did not retain per-tactic scores. Raw numeric profile records and100-sample public timings are in observed/results.json; full DEBUG output is driver.log.

The `cutedsl` public selector also profiles unchanged W4A16; its23 successful scores are preserved but excluded from this optimization analysis. No test/benchmark/kernel source or existing selection cache was modified.
