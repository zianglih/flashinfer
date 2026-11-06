# EP4 uniform4096 native IKET audit

PASS: `679828c1f757a3ecfcb55a5650b7690ab9f297e2`, source+fixture `2156bd7a52f8fae316a92c51e61592cb87f9b1acd9d43c190399640521ccb32c`.

1,024 tokens/rank; 4,096 global tokens; 32,768 routes; 128 tokens/expert, 32/source/expert; 6,291,456 BF16 output elements/rank.

| Candidate | N | Group | Return | Rank0 µs | Rank1 µs | Rank2 µs | Rank3 µs | Score µs |
|---:|---:|---:|---|---:|---:|---:|---:|---:|
| 0 | 128 | 512 | epi_warps | 681.167990 | 681.103975 | 681.039989 | 681.023985 | 681.167990 |
| 1 | 128 | 512 | reuse_dispatch_warps | 587.168008 | 586.975992 | 586.800009 | 586.847991 | 587.168008 |
| 2 | 64 | 512 | epi_warps | 744.543999 | 744.367987 | 744.512022 | 744.623989 | 744.623989 |
| 3 | 64 | 512 | reuse_dispatch_warps | 693.904012 | 694.191992 | 693.680018 | 694.319993 | 694.319993 |
| 4 | 128 | 1024 | epi_warps | 705.184013 | 705.152005 | 705.567986 | 704.623997 | 705.567986 |
| 5 | 128 | 1024 | reuse_dispatch_warps | 588.864028 | 588.272005 | 588.111997 | 587.967992 | 588.864028 |
| 6 | 64 | 1024 | epi_warps | 766.479999 | 766.927987 | 766.847998 | 766.847998 | 766.927987 |
| 7 | 64 | 1024 | reuse_dispatch_warps | 688.032001 | 687.391996 | 687.184006 | 687.247992 | 688.032001 |

Fresh winner 1; 587.168008 µs hot graph-event score; all1,600 raw samples checked.

| Rank | Capture PID | Bit mismatches | Prep / sync / pull | Local wait / publish / input wait | Return wrapper / combine | Tiles / K | Native points |
|---:|---:|---:|---|---|---|---|---:|
| 0 | 38154 | 0 | 8 / 8 / 8 | 8 / 4 / 8 | 8 / 336 | 35 / 504 | 133 |
| 1 | 38155 | 0 | 8 / 8 / 8 | 8 / 4 / 8 | 8 / 336 | 34 / 496 | 133 |
| 2 | 38156 | 0 | 8 / 8 / 8 | 8 / 4 / 8 | 8 / 336 | 34 / 496 | 133 |
| 3 | 38157 | 0 | 8 / 8 / 8 | 8 / 4 / 8 | 8 / 336 | 34 / 496 | 133 |

Only cluster0's twoCTAs/40warps are recorded from the normal148CTA/74CGA grid; no full-grid utilization inference.
Counter-based combine multiplicities derive from current worker mapping; no T128 active-warp assumption is carried forward.
Hot tuner samples are not cold-CUPTI performance. TMA/MMA issue scopes are asynchronous issue, not completion.
Each JSON trace is validated against its own Perfetto nanosecond endpoints; no cross-GPU clock alignment.
Original trace/config/native binary binding is unchanged; the explicitly described legacy compute projection synthesizes no events.
