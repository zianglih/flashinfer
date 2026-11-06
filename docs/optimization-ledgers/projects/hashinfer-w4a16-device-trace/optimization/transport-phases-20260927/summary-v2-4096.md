# Native transport phases: 4096 global tokens

Source `f4dc6e1b4990df3a783ab51b43f497a482811d5c`; package+fixture SHA `50e19c04f93b952fdeac634f0fe36e7fb053fe37f1a31c4babb9674bdd767d69`.

EP4, H6144/I2048/E256/top8, 1024 tokens per rank; eight distinct experts per token. Full148-CTA/74-cluster grid, with twoCTAs/40warp tracks recorded per rank.

| Candidate | N | Group | Return mode | Rank0 µs | Rank1 µs | Rank2 µs | Rank3 µs | Score µs |
|---:|---:|---:|---|---:|---:|---:|---:|---:|
| 0 | 128 | 512 | epi_warps | 681.119978 | 681.232005 | 681.327999 | 681.312025 | 681.327999 |
| 1 | 128 | 512 | reuse_dispatch_warps | 586.319983 | 586.304009 | 586.495996 | 586.335987 | 586.495996 |
| 2 | 64 | 512 | epi_warps | 744.159997 | 743.551999 | 743.776023 | 743.536025 | 744.159997 |
| 3 | 64 | 512 | reuse_dispatch_warps | 693.872005 | 693.872005 | 693.551987 | 693.904012 | 693.904012 |
| 4 | 128 | 1024 | epi_warps | 705.615997 | 705.648005 | 705.887973 | 705.983996 | 705.983996 |
| 5 | 128 | 1024 | reuse_dispatch_warps | 586.367995 | 585.824013 | 585.040003 | 586.223990 | 586.367995 |
| 6 | 64 | 1024 | epi_warps | 767.151982 | 767.072022 | 767.280012 | 767.296016 | 767.296016 |
| 7 | 64 | 1024 | reuse_dispatch_warps | 690.768003 | 690.752000 | 690.991998 | 691.295981 | 691.295981 |

Fresh winner: candidate5, **586.367995µs** hot graph-event score. All1,600 samples recomputed; this is not a cold-L2 CUPTI benchmark.

| Rank | PID | Output elements | Reference / capture mismatches | Native points | Worst of8 initial sync µs | Worst input-publication wait µs |
|---:|---:|---:|---|---:|---:|---:|
| 0 | 51407 | 6,291,456 | 0 / 0 | 150 | 736.512 | 733.312 |
| 1 | 51408 | 6,291,456 | 0 / 0 | 150 | 916.224 | 912.608 |
| 2 | 51409 | 6,291,456 | 0 / 0 | 150 | 11.552 | 7.520 |
| 3 | 51410 | 6,291,456 | 0 / 0 | 150 | 588.480 | 584.000 |

Selected **rank2** by the minimum worst initial dispatch-count synchronization duration across CTA0/1, warps8–11; ties use lower rank. The full uncropped selected file is `/Users/ziangli/playground/projects/hashinfer-w4a16-device-trace/optimization/transport-phases-20260927/audit-v2-4096/selected-min-sync-rank2.pftrace` (SHA `3db25c0bfdf076a4a21a4718351bcfcfb05d23a951ff2917f23e2ae5c5acb05d`). This metric includes local readiness/publication/scheduler work; it is not pure inter-rank idle time. No cross-GPU timestamp alignment is used.

| Selected rank: phase | Recorded ranges | Median duration µs | Maximum duration µs |
|---|---:|---:|---:|
| `pull_resolve_token_source` | 112 | 0.816 | 2.880 |
| `pull_issue_tma_load_weights` | 112 | 2.432 | 10.464 |
| `pull_wait_input_tma` | 112 | 1.040 | 7.712 |
| `pull_issue_fc1_pool_store` | 112 | 0.032 | 0.128 |
| `pull_wait_fc1_pool_store` | 112 | 0.128 | 0.768 |
| `pull_flush_fc1_ready_tail` | 8 | 1.600 | 5.760 |
| `return_wait_fc2_expert` | 105 | 23.104 | 598.272 |
| `return_stage_and_issue_output` | 106 | 0.672 | 3.168 |

All four ranks passed the complete finite-BF16 independent-reference↔baseline and baseline↔capture comparisons (6,291,456 elements each), source/fixture/PID/config checks, whole-call/phase/K nesting, original native PMTRIG bijection and each JSON trace's own Perfetto nanosecond check. Each capture rank issued exactly one target launch.
Original CUBIN SHA `0560cd651a8bfc608f96a3cef5ed1fa2ae2c56560d67a0221224baa1ecb611e4`; context `48d891dd047a567d`; maximum native point span176B.

Phase counts are recorded warp scopes in one cluster, not whole-grid totals. TMA issue scopes do not measure asynchronous completion. Pull wait is residual readiness after issue and side work; Pool issue measures only the elected TMA issue; pool wait measures elected commit/completion. Metadata writes and per-batch FC1 publication are outside these narrow spans. Return stage/issue combines elected local FC2 staging and peer issue; return output completion and pacing have no separate phase markers. Their cost remains within the whole return range. Concurrent warp durations must not be summed into hardware occupancy.
