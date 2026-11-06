# Scatter4 r2 screen interpretation

Primary results use all 100 CUPTI samples per process. Two source-paired controls bracket two candidate runs. Routes and native tactics are frozen; no new search or external baseline timing. Tokens 4, 64, 4096, 16384 only; this is a retention screen, not a full 13-token publication rerun.

| Model | W4A4 | Per-token | MXFP8 | MXFP4x8 |
|---|---:|---:|---:|---:|
| v3 | +0.289% | +0.262% | +0.002% | -0.049% |
| v41-flash | -0.053% | -0.030% | +0.706% | +0.121% |
| kimi-k3 | -0.362% | +0.201% | +0.182% | +0.633% |
| nemo3-ultra | -0.071% | -0.097% | +0.151% | +0.259% |

Overall standard-median GM +0.134%; decode +0.002%; prefill +0.265%. All 32 prefill cells select the changed 64-token bulk FC2 epilogue; all 32 decode cells select bulk_tokens=0. Compilation metadata has identical staging/scratch/layout across C1/A1/A2/C2. There are no 32-token native winners in this screen.

The clear selected improvements are V3 T16384 W4A4 +0.980% and per-token +0.667%, both stable across passes and sample strata. N3U MXFP4x8 T4096 has a small stable −0.559% cost; V41F MXFP4x8 T4096 is −0.291%. Large T16384 MX positives vary strongly with sample strata and are not evidence of broad robust gains.

For the 32 changed bulk cells, diagnostic GM first 25 +0.104%, last 25 +0.318%, last 50 +0.197%. These are sample-order diagnostics only; full 100-sample medians remain primary.

The corrected descriptor gate covered 64-token/two-stage bulk epilogues. A full-chain 32-token exact GPU case remains absent; no native screen winner uses it. The independent CPU address proof covers both sizes, and standalone copy probes cover all 8 swizzle base phases and tail extents. The earlier wrong descriptor candidate and pre-measurement helper packaging failure are preserved in the epilogue ledger; neither contributes a timing sample here.
