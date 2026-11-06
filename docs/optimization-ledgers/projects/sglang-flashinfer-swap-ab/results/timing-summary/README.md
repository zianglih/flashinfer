# Representative production MoE timing smoke

Single C3 B300, local TP1/EP1 with 32 experts, H7168/I2048, top-k8, SwiGLU. Identical seeded serialized weights, inputs and routes. Both arms use FlashInfer merge 338924c2: legacy forces swap_ab=False; candidate uses swap_ab=True. This is not distributed EP8 or a model-throughput measurement.

Two fresh-process sweeps, legacy→swap then swap→legacy. Each phase uses 10 warmups and 100 untrimmed CUDA-event samples around a whole-forward CUDA graph replay, warm L2. Initial activation quantization is included; precomputed route selection, weight preparation, reload and graph capture are excluded. Default mode-specific tactics, no autotuning. No clock locking or CUPTI timing. Pooled medians use all200 samples per arm/case. Spread is max(two phase medians)/min(two phase medians)-1; all negative rows remain.

| Mode | Tokens | Legacy first µs | Swap second µs | Swap first µs | Legacy second µs | Legacy pooled µs | Swap pooled µs | Speedup | Legacy spread | Swap spread |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| w4a4_scalar | 16 | 146.800 | 251.088 | 250.496 | 146.624 | 146.736 | 250.880 | -41.51% | 0.12% | 0.24% |
| w4a4_scalar | 128 | 152.848 | 143.312 | 143.840 | 153.328 | 153.120 | 143.504 | +6.70% | 0.31% | 0.37% |
| w4a4_scalar | 4096 | 990.592 | 1017.392 | 1003.168 | 974.832 | 988.576 | 1004.000 | -1.54% | 1.62% | 1.42% |
| w4a4_per_token | 16 | 159.712 | 258.528 | 258.560 | 160.496 | 160.160 | 258.528 | -38.05% | 0.49% | 0.01% |
| w4a4_per_token | 128 | 167.088 | 158.912 | 158.880 | 167.280 | 167.168 | 158.912 | +5.20% | 0.11% | 0.02% |
| w4a4_per_token | 4096 | 1057.040 | 1079.952 | 1079.680 | 1056.448 | 1056.576 | 1079.952 | -2.16% | 0.06% | 0.03% |
| w4a16 | 16 | 171.600 | 171.952 | 171.024 | 171.376 | 171.488 | 171.312 | +0.10% | 0.13% | 0.54% |
| w4a16 | 128 | 180.896 | 180.912 | 178.208 | 177.456 | 179.696 | 179.968 | -0.15% | 1.94% | 1.52% |
| w4a16 | 4096 | 2321.936 | 2275.024 | 2304.928 | 2291.664 | 2313.088 | 2290.576 | +0.98% | 1.32% | 1.31% |
