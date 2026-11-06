# Early SF completion: rejected

Immutable442d control/candidate on C2 B300, CUDA13.2, nvcr.io/nvidia/pytorch:26.05-py3, CuTe DSL4.7.1. Only the existing cp.async SF producer_commit moves ahead of Gather4. Layout, pipeline stages, arrival counts, arithmetic, and MMA ownership are unchanged. Production remains442d.

All72 paired six-format checks passed (24 FC1 N128,24 FC1 N256,24 FC2 controls), including per-token output and short/tail K. All12 native arms matched final output bytes. No repeatable whole-pipeline improvement at8K/16K; reject and do not broaden to other dtype timings or a primary screen.

| GPU / order | Tokens | Arm | FC1 us | FC2 us | Full us |
|:---|---:|:---|---:|---:|---:|
| 4 / r1 | 8192 | baseline | 146.641 | 88.865 | 294.594 |
| 4 / r1 | 8192 | candidate | 146.913 | 88.864 | 295.235 |
| 4 / r1 | 8192 | baseline | 146.401 | 88.944 | 295.123 |
| 4 / r1 | 16384 | baseline | 242.962 | 144.578 | 504.228 |
| 4 / r1 | 16384 | candidate | 243.635 | 144.817 | 502.692 |
| 4 / r1 | 16384 | baseline | 243.426 | 144.673 | 502.965 |
| 3 / r2 | 8192 | candidate | 147.729 | 88.897 | 294.849 |
| 3 / r2 | 8192 | baseline | 147.425 | 88.928 | 294.322 |
| 3 / r2 | 8192 | candidate | 147.265 | 88.833 | 295.522 |
| 3 / r2 | 16384 | candidate | 242.226 | 144.881 | 504.243 |
| 3 / r2 | 16384 | baseline | 242.034 | 144.657 | 502.323 |
| 3 / r2 | 16384 | candidate | 243.745 | 144.993 | 503.668 |

Every arm uses10 warmups and100 cold-L2 CUDA-graph CUPTI samples with actual native DeepSeek routing (H7168/I2048,top-k8,32localexperts,seed42,unfused finalize,no per-token NVFP4). Fixed N128/FC1logicalM512/FC2M256; source-specific preparation is unchanged. Adjacent order is B/A/B onGPU4 and A/B/A onGPU3; comparisons stay within each device. Full sample arrays remain in JSON, without filtering.

The enclosing C2 checkout stayed13ca1475; executed modules are immutable442d overlays plus its static host ABI, explicitly identified by every source hash. Exact native GPU inventories and software versions are recorded. The initial C1 test was interrupted by devbox loss and contributes no accepted evidence. No old B1 or cross-hardware comparison was used.
