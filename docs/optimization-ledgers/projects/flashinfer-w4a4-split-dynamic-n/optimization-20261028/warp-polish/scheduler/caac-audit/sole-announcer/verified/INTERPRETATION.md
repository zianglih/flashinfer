# Sole-announcer screen interpretation

Primary results use all 100 CUPTI samples per process. Two source-paired controls bracket two candidate runs. Routes and native tactics are frozen; no new search or external baseline timing. Tokens 4, 64, 4096, 16384 only; this is a retention screen, not a full 13-token publication rerun.

| Model | W4A4 | Per-token | MXFP8 | MXFP4x8 |
|---|---:|---:|---:|---:|
| v3 | +0.017% | -0.156% | +0.225% | +0.617% |
| v41-flash | +0.044% | +0.069% | -0.275% | +0.021% |
| kimi-k3 | +0.114% | -0.297% | -0.413% | +0.552% |
| nemo3-ultra | +0.135% | +0.125% | -0.714% | -0.401% |

Overall standard-median GM −0.022%; decode +0.065%; prefill −0.109%. The appropriate interpretation is neutral performance with fewer redundant full-barrier announcements. This does not establish an end-to-end speedup.

V3 MXFP4x8 T4096 is a stable small regression: −1.057%, with 0.071% control and 0.035% candidate pass spreads; first 25 / last 50 diagnostics remain −0.949%/−1.015%. Large 16K gains and losses depend on sample stratum and pass, consistent with the pre-existing bimodality. Keep the full 100-sample medians as primary; do not replace them with favorable strata.

Across all cells, diagnostic GM first 25 −0.068%, last 25 −0.391%, last 50 −0.119%. These are sample-order diagnostics, not alternative retention metrics. GPU clocks/power or source effects are not separately isolated by this screen.

The independent gate confirms 176 paired storage-bit replays and 88 compiled kernels with no spills. Source barriers retain one empty wait per producer stage; only the weight role announces combined bytes. Config 7 FC2 has compiler-driven 18-way activation-loop unrolling rather than 2-way, increasing static wait code size while preserving executed waits. See the independent codegen report for exact register deltas.
