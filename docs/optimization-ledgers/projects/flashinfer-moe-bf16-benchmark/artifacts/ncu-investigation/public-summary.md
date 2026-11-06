### Nsight Compute: fixed normal-tuned tactics

- **Scope:** inference per-token, EP8/TP1, B300 GPU 0, NCU 2026.1.1, source `2079fa00`. Tactics were recorded during normal tuning before NCU injection, then fixed by a diagnostic helper; all captured calls had tuning disabled. Each report contains exactly FC1 (with SwiGLU) and FC2, nine replay passes each. Node replay flushes caches and isolates PDL kernels: these durations are diagnostics, not additive end-to-end latency.
- **Tactics:** TRTLLM BF16: `(8, 37)` at 32; `(128, 1)` at 4096. CuteDSL W4A16 uses the same tactic for both GEMMs: `((128, 8, 256), (2, 1), True)` at 32; `((256, 128, 256), (2, 1), True)` at 4096.

Raw counters below: R/W = DRAM bytes; D/T/S = DRAM throughput / tensor-pipe activity / SM throughput (% of sustained elapsed peak); LD/ST = local-memory sectors; warps = active warps per active SM cycle; A/T = achieved/theoretical occupancy (%).

| Tokens | Backend | GEMM | R bytes | W bytes | ns | D/T/S % | LD/ST | Warps | Occupancy A/T % | Registers/thread | Shared bytes/block |
| ---: | --- | --- | ---: | ---: | ---: | --- | --- | ---: | --- | ---: | ---: |
| 32 | TRTLLM BF16 | FC1 | 1233656832 | 3507200 | 176896 | 91.17/2.42/25.37 | 0/0 | 11.33 | 17.70/18.75 | 168 | 181904 |
| 32 | TRTLLM BF16 | FC2 | 616784896 | 4100096 | 93760 | 86.35/2.27/23.87 | 0/0 | 7.95 | 12.42/12.50 | 255 | 216720 |
| 4096 | TRTLLM BF16 | FC1 | 2064285184 | 17972224 | 323040 | 84.03/40.83/45.78 | 0/0 | 10.84 | 16.94/18.75 | 168 | 187032 |
| 4096 | TRTLLM BF16 | FC2 | 960271104 | 50072064 | 152864 | 86.17/44.00/48.40 | 0/0 | 6.98 | 10.91/12.50 | 255 | 219800 |
| 32 | CuteDSL W4A16 | FC1 | 349258752 | 3499264 | 65632 | 70.11/6.61/53.35 | 0/0 | 15.86 | 24.77/25.00 | 128 | 215040 |
| 32 | CuteDSL W4A16 | FC2 | 174409728 | 3022592 | 37504 | 61.78/5.74/49.50 | 0/0 | 15.61 | 24.39/25.00 | 128 | 206880 |
| 4096 | CuteDSL W4A16 | FC1 | 637545728 | 13989120 | 165696 | 51.26/87.20/87.81 | 0/0 | 15.84 | 24.75/25.00 | 128 | 223232 |
| 4096 | CuteDSL W4A16 | FC2 | 322100992 | 7225344 | 148096 | 28.99/44.90/46.44 | 0/0 | 15.06 | 23.53/25.00 | 128 | 215168 |

Remaining launch counters (all eight kernels): occupancy limits = 32 blocks, 1 block by registers, 1 by shared memory; warp limit = 5/8 blocks for BF16 FC1/FC2 and 4 for W4A16. Cluster dimensions = `(2,1,1)`, except BF16 at 32 uses `(1,1,1)`. `occupancy_cluster_pct` = 3.12%; `occupancy_cluster_gpu_pct` = 0.59/0.39% for BF16 FC1/FC2 and 0.78% for both W4A16 kernels (launch estimates, not measured GPU activity). Full raw CSV/report metadata is retained.

**Interpretation:** at 4096, BF16 still reaches 84–86% DRAM throughput with 41–44% tensor activity; W4A16 FC1 reaches 87% tensor activity. BF16 reads 3.025 GB versus W4A16's 0.960 GB. EP8 leaves 3715 local assignments across 32 experts (116/expert); 4096 is not each expert's GEMM M. No local load/store traffic was measured in any kernel. Registers and shared memory both limit residency to one block/SM; low occupancy alone does not establish an avoidable defect. These counters support a bandwidth explanation and do not demonstrate a spilling or launch-overhead bug.
