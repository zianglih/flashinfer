# Inactive wide FC2 cache-policy audit

Integrated and cache-tier sources generate **byte-identical PTX, cubin, SASS and resource reports** for all three actual public M256/N256 two-CTA FC2 paths. No symbol or instruction normalization was used. The integrated call omits cache-policy keywords; tier passes explicit zero. Both publication/prefetch behaviors are inactive in this geometry.

All nine changing-route replays (three formats × distributed, concentrated, zero-local routing) have identical input, route and output hashes. All 83 source pins and patch hashes were verified before/after; neither frozen source changed.

| Format | Registers | Local bytes | Dynamic SMEM | Active blocks/SM | Stages | Threads |
|---|---:|---:|---:|---:|---:|---:|
| w4a4 | 118 | 0 | 229760 | 1 | 5 | 288 |
| mxfp8 | 124 | 0 | 206720 | 1 | 5 | 288 |
| w4a8 | 124 | 0 | 206720 | 1 | 5 | 288 |

Geometry: H7168, I2048, 32 local experts, 33 tokens, top-k8; M256/N256, cluster(2,1). Same B300 GPU4, CuTe4.7.1, CUDA13.2 runtime, and compile options. This is generated-code/resource evidence, not latency attribution or proof for every inactive specialization. Full hashes/receipts are in `comparison.json` and `raw/`.
