# Direct trace128 audit

PASS: source `40d0ceb67aa67dbf366ff61f85309e8ef53aa743`, 32 tokens/rank, 128 global; package+fixture digest `9a673e60c3e54ad5ebf064c2c32ad307a02cc73c20477dc79f13940c4f5447ee`.

| Candidate | N | Group | Return | Rank0 µs | Rank1 µs | Rank2 µs | Rank3 µs | Score µs |
|---:|---:|---:|---|---:|---:|---:|---:|---:|
| 0 | 128 | 512 | epi_warps | 296.640009 | 297.040001 | 297.567993 | 297.024012 | 297.567993 |
| 1 | 128 | 512 | reuse_dispatch_warps | 314.799994 | 315.280005 | 315.903991 | 315.183997 | 315.903991 |
| 2 | 64 | 512 | epi_warps | 273.744002 | 274.255991 | 274.944007 | 274.304003 | 274.944007 |
| 3 | 64 | 512 | reuse_dispatch_warps | 293.008000 | 293.871999 | 293.520004 | 293.728009 | 293.871999 |
| 4 | 128 | 1024 | epi_warps | 296.608001 | 297.008008 | 297.152013 | 297.040001 | 297.152013 |
| 5 | 128 | 1024 | reuse_dispatch_warps | 314.352006 | 315.008014 | 315.072000 | 315.183997 | 315.183997 |
| 6 | 64 | 1024 | epi_warps | 273.424000 | 273.840010 | 274.703994 | 273.840010 | 274.703994 |
| 7 | 64 | 1024 | reuse_dispatch_warps | 290.895998 | 291.776001 | 291.584015 | 291.103989 | 291.776001 |

Winner 6; 274.703994 µs hot graph-event score. All 1,600 native samples recomputed; this is not cold-CUPTI performance.

| Rank | Capture PID | Bit mismatches | Native points | Tiles / K | Grid CTAs / recorded CTAs / warps |
|---:|---:|---:|---:|---|---|
| 0 | 12928 | 0 | 115 | 34 / 480 | 148 / 2 / 40 |
| 1 | 12929 | 0 | 115 | 35 / 488 | 148 / 2 / 40 |
| 2 | 12930 | 0 | 115 | 35 / 488 | 148 / 2 / 40 |
| 3 | 12931 | 0 | 115 | 35 / 488 | 148 / 2 / 40 |

Each rank passes the independent baseline reference and capture-baseline bit comparison for 196,608 BF16 elements. All four ranks pass balanced/nested ranges, four ordered transform subsections per K, three dispatch subsections, PID/metadata/config/original-CUBIN PMTRIG binding, and own-Perfetto nanosecond validation.

Direct harness records a source snapshot before launch; no causal-driver or after-run source-closure receipt exists.
Tracker and instrumented capture are separate profiler passes; bind cubin/context/name/config rather than equating their PIDs.
JSON proves CTA/warp ownership, not lane uniformity. No cross-GPU clock alignment, full-grid utilization, or cold-CUPTI speedup claim.
The auditor performs only CPU reads and cuobjdump of a hash-matched original cubin; no GPU launch.
