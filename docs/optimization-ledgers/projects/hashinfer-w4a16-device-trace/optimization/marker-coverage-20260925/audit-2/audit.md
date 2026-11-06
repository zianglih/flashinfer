# Expanded dispatch marker audit

PASS: `cd7cc07c02300553ef9b8e6af0a4044f0b5dc8a7`; source+fixture `d19f31dc6400a2f20d3bd6c64f539baea16841f88771d05aef55cc83a6d03bb9`.

| Candidate | N | Group | Return | Rank0 µs | Rank1 µs | Rank2 µs | Rank3 µs | Score µs |
|---:|---:|---:|---|---:|---:|---:|---:|---:|
| 0 | 128 | 512 | epi_warps | 296.831995 | 296.799988 | 297.071993 | 296.927989 | 297.071993 |
| 1 | 128 | 512 | reuse_dispatch_warps | 317.040011 | 316.848010 | 317.023993 | 316.992015 | 317.040011 |
| 2 | 64 | 512 | epi_warps | 274.320006 | 274.271995 | 274.448007 | 274.432003 | 274.448007 |
| 3 | 64 | 512 | reuse_dispatch_warps | 292.383999 | 291.983992 | 292.496011 | 292.383999 | 292.496011 |
| 4 | 128 | 1024 | epi_warps | 296.559989 | 296.655998 | 296.736002 | 296.703994 | 296.736002 |
| 5 | 128 | 1024 | reuse_dispatch_warps | 314.847991 | 313.759997 | 315.024003 | 315.135986 | 315.135986 |
| 6 | 64 | 1024 | epi_warps | 273.935989 | 273.967996 | 274.095997 | 274.111986 | 274.111986 |
| 7 | 64 | 1024 | reuse_dispatch_warps | 292.608008 | 292.656004 | 292.896003 | 292.815998 | 292.896003 |

Fresh winner 6, 274.111986 µs hot graph-event score; all 1,600 samples recomputed.

| Rank | PID | Whole-call prep / sync / pull | Local wait / count publish / input publication | Original PMTRIG points | Tiles / K |
|---:|---:|---|---|---:|---|
| 0 | 104249 | 8 / 8 / 8 | 8 / 4 / 8 | 133 | 34 / 480 |
| 1 | 104250 | 8 / 8 / 8 | 8 / 4 / 8 | 133 | 35 / 488 |
| 2 | 104251 | 8 / 8 / 8 | 8 / 4 / 8 | 133 | 35 / 488 |
| 3 | 104252 | 8 / 8 / 8 | 8 / 4 / 8 | 133 | 35 / 488 |

All four ranks pass reference↔baseline and baseline↔capture finite-BF16 bit checks (196,608 elements each), exact eight-WG2 coverage, publication ownership/order/nesting, compute/transform checks, original PMTRIG bijection, and own-Perfetto nanosecond checks.

Each rank's 40 recorded warp tracks cover one two-CTA cluster of the unchanged 148-CTA grid.
JSON establishes CTA/warp coverage; source guards establish warp-uniform publication participation. No per-lane trace is claimed.
Full original traces bind to their own Perfetto timestamps and native PMTRIG sites. Only the reused compute validator sees an explicitly labeled representative dispatch projection.
The harness records source file identity before launch; the driver also records matching clean Git HEAD/status after capture. There is no separate after-run per-file hash receipt. Tracker and capture are separate profiler passes.
Hot autotuner scores are not cold-CUPTI timings; GPU clocks are not aligned across ranks. CPU reads/cuobjdump only.
