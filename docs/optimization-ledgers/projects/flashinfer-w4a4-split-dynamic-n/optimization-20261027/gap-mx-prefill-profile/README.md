# V3 MXFP4x8 16K: separate memory stages explain the remaining fused-baseline gap

Frozen native selections and measured sources from retained `1e69d0a39` are
used unchanged. Swap-AB is unfused; the legacy MXFP4x8 path requires fused
finalize. Both use the public functional API, V3 EP8, prequantized MX inputs,
and 20 CUDA-graph replays on the existing C3 B300/CUDA13.2 devbox. No tuning or
production edit occurs in this diagnostic.

`analyze.py` independently checks the source/cache/command receipts, parses
the Nsight SQLite files, and includes the legacy output memset. The archive
contains 12 files, SHA256
`4254b5cb9dc4ba8b1d6c11a78c23c6d6fcaf282abc4221fbdfd7c98452b51bab`.

| Stage | Swap-AB duration us | Legacy duration us | Swap-AB critical extension us | Legacy critical extension us |
|---|---:|---:|---:|---:|
| Top-k | 30.225 | 30.208 | 30.225 | 30.208 |
| Routing initialization | 3.281 | 3.360 | 0.768 | 0.752 |
| Routing indices | 7.408 | 7.088 | 7.216 | 6.896 |
| Prepare | 39.872 | — | 39.649 | — |
| FC1 | 306.929 | 332.514 | 298.322 | 332.306 |
| Output zero | — | 42.512 | — | 22.752 |
| FC2 | 203.457 | 204.497 | 186.401 | 204.658 |
| Combine | 86.817 | — | 83.921 | — |
| Full graph | **645.796** | **597.588** | | |

PDL permits overlap, so duration sums are not elapsed graph time. Critical
extension counts only each operation's additional end time beyond prior
operations; it can include intervening gaps. Per-stage medians need not sum
exactly to the median graph span. The legacy 234,881,024-byte zero-fill overlaps
part of FC1 and contributes 22.752 us beyond it. Ignoring this memcpy-engine
activity would incorrectly attribute that time to FC2.

The two GEMMs together save about 52.24 us of critical extension. Prepare and
the separate combine add 123.57 us, partly offset by avoiding the legacy
22.75 us output-zero extension. These additional memory stages explain the
remaining roughly 48 us graph gap in this trace. This does not show an intrinsic
regression in the GEMM core, and does not justify another core rewrite on its
own. It also does not measure HBM utilization or prove a memory-bandwidth limit;
that would need appropriate profiler counters.

Swap-AB uses N128, two-CTA M256 for both GEMMs, K4/K4 and static scheduling.
Legacy uses the same logical 128-token tile, with its existing 256-channel
FC1/FC2 geometry. Both winners and cache keys are recorded in
`evidence/*-selection.json`. The ongoing independent synthetic-routing
experiment may change the selected geometry; this profile remains tied to
the retained selection above.

These 20-replay Nsight spans are diagnostic, not replacement CUPTI retention
measurements. They are deliberately absent from the PR speedup table. The
complete fresh 100-sample CUPTI campaign remains the published evidence.
