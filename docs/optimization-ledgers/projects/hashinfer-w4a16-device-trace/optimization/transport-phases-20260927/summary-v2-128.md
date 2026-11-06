# Native transport phases: 128 global tokens

Source `f4dc6e1b4990df3a783ab51b43f497a482811d5c`; package+fixture SHA `50e19c04f93b952fdeac634f0fe36e7fb053fe37f1a31c4babb9674bdd767d69`.

EP4, H6144/I2048/E256/top8, 32 tokens per rank; eight distinct experts per token. Full148-CTA/74-cluster grid, with twoCTAs/40warp tracks recorded per rank.

| Candidate | N | Group | Return mode | Rank0 µs | Rank1 µs | Rank2 µs | Rank3 µs | Score µs |
|---:|---:|---:|---|---:|---:|---:|---:|---:|
| 0 | 128 | 512 | epi_warps | 290.111989 | 290.079996 | 289.903998 | 289.983988 | 290.111989 |
| 1 | 128 | 512 | reuse_dispatch_warps | 307.392001 | 306.656003 | 307.216004 | 307.007998 | 307.392001 |
| 2 | 64 | 512 | epi_warps | 267.679989 | 267.616004 | 267.504007 | 267.488003 | 267.679989 |
| 3 | 64 | 512 | reuse_dispatch_warps | 283.807993 | 283.856004 | 283.632010 | 283.519998 | 283.856004 |
| 4 | 128 | 1024 | epi_warps | 290.064007 | 290.176004 | 290.064007 | 290.127993 | 290.176004 |
| 5 | 128 | 1024 | reuse_dispatch_warps | 306.032002 | 305.999994 | 306.192011 | 305.375993 | 306.192011 |
| 6 | 64 | 1024 | epi_warps | 267.488003 | 267.648011 | 267.520010 | 267.520010 | 267.648011 |
| 7 | 64 | 1024 | reuse_dispatch_warps | 283.679992 | 283.791989 | 283.600003 | 283.695996 | 283.791989 |

Fresh winner: candidate6, **267.648011µs** hot graph-event score. All1,600 samples recomputed; this is not a cold-L2 CUPTI benchmark.

| Rank | PID | Output elements | Reference / capture mismatches | Native points | Worst of8 initial sync µs | Worst input-publication wait µs |
|---:|---:|---:|---|---:|---:|---:|
| 0 | 49993 | 196,608 | 0 / 0 | 146 | 534.976 | 532.992 |
| 1 | 49994 | 196,608 | 0 / 0 | 146 | 2420.384 | 2418.400 |
| 2 | 49995 | 196,608 | 0 / 0 | 146 | 9.440 | 7.584 |
| 3 | 49996 | 196,608 | 0 / 0 | 146 | 2741.888 | 2739.648 |

Selected **rank2** by the minimum worst initial dispatch-count synchronization duration across CTA0/1, warps8–11; ties use lower rank. The full uncropped selected file is `/Users/ziangli/playground/projects/hashinfer-w4a16-device-trace/optimization/transport-phases-20260927/audit-v2-128/selected-min-sync-rank2.pftrace` (SHA `8449f1bb1b506b7a46dce3d2d8887ac9219d9b1d0a238e8dde6b32063dce6529`). This metric includes local readiness/publication/scheduler work; it is not pure inter-rank idle time. No cross-GPU timestamp alignment is used.

| Selected rank: phase | Recorded ranges | Median duration µs | Maximum duration µs |
|---|---:|---:|---:|
| `pull_resolve_token_source` | 8 | 1.488 | 1.600 |
| `pull_issue_tma_load_weights` | 8 | 1.808 | 1.888 |
| `pull_wait_input_tma` | 8 | 0.304 | 0.704 |
| `pull_issue_fc1_pool_store` | 8 | 0.032 | 0.064 |
| `pull_wait_fc1_pool_store` | 8 | 0.064 | 0.224 |
| `pull_flush_fc1_ready_tail` | 8 | 0.528 | 2.208 |
| `return_wait_fc2_expert` | 0 | — | — |
| `return_stage_and_issue_output` | 0 | — | — |

All four ranks passed the complete finite-BF16 independent-reference↔baseline and baseline↔capture comparisons (196,608 elements each), source/fixture/PID/config checks, whole-call/phase/K nesting, original native PMTRIG bijection and each JSON trace's own Perfetto nanosecond check. Each capture rank issued exactly one target launch.
Original CUBIN SHA `34f2b189065e2009b97051faca80865de37a262ac57043a0a061d7aac49e4258`; context `f4cc4c4a7d287b47`; maximum native point span176B.

Phase counts are recorded warp scopes in one cluster, not whole-grid totals. TMA issue scopes do not measure asynchronous completion. Pull wait is residual readiness after issue and side work; Pool issue measures only the elected TMA issue; pool wait measures elected commit/completion. Metadata writes and per-batch FC1 publication are outside these narrow spans. Return stage/issue combines elected local FC2 staging and peer issue; return output completion and pacing have no separate phase markers. Their cost remains within the whole return range. Concurrent warp durations must not be summed into hardware occupancy.
