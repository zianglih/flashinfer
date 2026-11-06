# Valid-route payload copy experiment

Independent actual source clone: `flashinfer-regular-tma-validcopy`, base442; all three regular-TMA source changes remain unstaged. Relative to frozen LDG256, the only source change is `if row<payload_rows` → `if valid`. Canonical SF zeroing, physical allocation/descriptor extents, grid, PDL, and fused GEMM epilogue are unchanged.

`probe_poison.py` imports the actual modified host/preparation/core plus the frozen442 host/core for comparisons. Scratch allocation is transparently initialized to FP8 NaN/Inf byte patterns; invalid mapping entries are poison. Valid payload bytes, complete SF atoms, all FC1 output/SF bytes, downstream FC2/combine final bytes, and suffix canaries must match their explicit contracts. Invalid private payload remains canary. Graph reuse tests counts0→1→5→2→0 without resetting payload between replays. Historical source and oracles are unchanged.

All six FC1 input formats cover generated quantized output and original-token scaling; the latter's BF16 intermediate passes through the native per-token NVFP4 quantizer for downstream NVFP4 FC2. E5M2 FC1 generated E4M3 output continues through E4M3 FC2. This low-level diagnostic does not claim new public per-token API support.

After exact checks, `run_phase.sh` measures only preparation with actual native routing: NV8K/N128, NV16K/N256, MXFP8 16K/N256. Both actual source classes share input/routing buffers; ABA/BAB uses the existing10-warmup/100-sample cold-L2 CUDA-graph CUPTI timer, preserving all samples and compiled resources. No full-chain/primary rerun or old baseline refresh.

Initcheck is not requested or run. Poison initialization demonstrates numerical isolation; default `torch.empty` can leave physically read invalid padding uninitialized. No correctness mismatch or initcheck warning is waived.
