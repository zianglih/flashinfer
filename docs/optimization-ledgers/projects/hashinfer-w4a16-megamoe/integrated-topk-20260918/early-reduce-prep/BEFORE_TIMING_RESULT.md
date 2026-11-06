#04 integrated BEFORE: independent raw timing audit

PASS. Source `04c51ad94738877e67045ece949ed16cd12c6f82`,106file manifest `ea0003b749bb72e483f2bdc3ab3cd4420620e81bafa9b210c1f9255e22f3bc69` on hu-pdx-99.

| Tokens | Median µs | MAD µs | AUTO tile N / return warps |
| ---: | ---: | ---: | --- |
| 1 | 75.729 | 0.848 | 128 / epi_warps |
| 2 | 96.017 | 0.720 | 64 / epi_warps |
| 4 | 106.416 | 0.879 | 64 / epi_warps |
| 8 | 130.529 | 1.185 | 64 / epi_warps |
| 16 | 144.450 | 1.168 | 64 / epi_warps |
| 32 | 170.177 | 1.040 | 64 / epi_warps |
| 64 | 205.394 | 1.152 | 64 / epi_warps |
| 128 | 196.434 | 0.752 | 64 / epi_warps |
| 256 | 197.537 | 0.896 | 64 / epi_warps |
| 512 | 200.866 | 0.784 | 64 / epi_warps |
| 1024 | 221.986 | 0.896 | 64 / epi_warps |
| 2048 | 301.732 | 2.272 | 128 / reuse_dispatch_warps |
| 4096 | 459.796 | 3.569 | 128 / reuse_dispatch_warps |
| 8192 | 749.254 | 13.232 | 128 / reuse_dispatch_warps |

Precomputed-routing public forward: staging, collective MegaMoE compute and deterministic integrated reduction; routing selection excluded.

3 warmups;100 CUPTI cold-L2 CUDA-graph samples per token row, each sample a rank maximum; median of all100 samples. No sample exclusions.

All14 rows /1,400 samples and112 finite BF16 rank/token outputs verified. All ranks chose the same tactic within each row; full configurations and raw sample arrays are retained in the JSON. This standalone arm establishes no speedup or cross-arm numerical result.

Chronology: 2026-09-18T19:18:33.271327+00:00 to 2026-09-18T19:25:58.113532+00:00; process wall 444.842205s. All recorded ownership codegen/native/queued runs finished before timing; empty GPU endpoints and owned-group closure match the setup host/boot/inventory. No continuous GPU monitoring claim.

The8192-token row retains late drift: quarter medians740.902,741.670,760.423,799.559µs; median749.254µs, MAD13.232µs. No samples removed. A later serial AFTER arm cannot cancel temporal drift.

Archive:51files /235,304,003raw bytes /188,698,554archive bytes; SHA256 `9b7e202ba9503f7f417ec84c80fe15a128aa09af89ef3ad86a8609a3464e0402`. The SSH interruption was resumed against the same sealed archive; no benchmark rerun.

Independent audit SHA256 `5a284a1fe2c23f9c100d55d29ac184e698dd18d49683f6f26c1af53ac280a3fd`. Finished-file SHA256 `79474b80ed879297f152632141372cb7955237ae262e2348f8810893d301cd75`.
