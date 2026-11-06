# CTA-scoped gather relay: retained instruction cleanup

Retained by parent for instruction sanity, with no speedup claim. Ten decode cells average **−0.108%**. The two stable prefill cells are **−0.273%** (N3U TP W4A4) and **+0.084%** (N3U TP per-token). All stable cells lie between −0.390% and +0.084%. The raw all-cell aggregate is +0.219%, but its positive prefill contribution is dominated by noisy N3U EP16K repeats and is not retention evidence for a performance gain.

Only the two gather publication helpers and their existing call arguments change: CTA-local release/acquire for one CTA, unchanged mapped cluster publication for two. Same local completion, proxy fence, barrier counts, warp ownership, stage reuse, tactics and PDL. The unstaged source remains frozen in `flashinfer-fc1-gather-relay-scope-review` at f63 plus patch `80c35c3c…`; source hash `8d64a6c4…`. Parent owns composition/commit/push.

Qualification: 23 exact tests; all 44 generated instances have zero stack/local storage. All 14 two-CTA FC1 and 21 FC2 binaries are byte-identical to retained source; nine one-CTA instances lose4–16 instructions with unchanged branches/register allocation. Applicable pre-commit hooks passed. See `GATE.md` and `codegen-comparison.json`. No sanitizer.

Measurement: nine jobs,14 cells,36 verified phases,5,600 strict-CUPTI samples on dedicated B300 GPUs3/4, image `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2/CuTeDSL4.8. C-A-A-C,100 cold-L2 graph samples/phase,10 warmups, public functional API, frozen retained native winners, no tuning. NVFP4 includes the input quantizer and the established per-token recipe. Both sources use f63 quantization; only relay helpers differ. All source, routing, tactic, sample-count, cache and executable register guards passed. GPU3 UUID `GPU-828e523f-00a8-c70b-c818-2837a056cc49`; GPU4 `GPU-3261f865-1c9c-c213-fbce-ab9118a88205`. Both released after zero process/zero MiB checks.

Positive means candidate faster: `100*(sqrt(C1*C2/(A1*A2))-1)`. C1/A1/A2/C2 below are each100-sample medians in microseconds. Repeat spread is `100*(max/min-1)`; all rows are retained.

| Model | Topology | Tokens | Format | C1 | A1 | A2 | C2 | Delta | C spread | A spread |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| N3U | EP | 8 | MXFP8 | 70.3525 | 70.3680 | 70.3040 | 70.4005 | +0.058% | 0.068% | 0.091% |
| N3U | EP | 8 | MXFP4x8 | 47.1205 | 47.2320 | 47.1360 | 47.1525 | -0.101% | 0.068% | 0.204% |
| N3U | EP | 16384 | MXFP8 | 913.3800 | 892.1805 | 920.4695 | 907.3010 | +0.455% | 0.670% | 3.171% |
| N3U | EP | 16384 | MXFP4x8 | 841.5415 | 770.5640 | 841.9410 | 832.9645 | +3.946% | 1.030% | 9.263% |
| N3U | TP | 8 | W4A4 | 59.2170 | 59.4250 | 59.4240 | 59.1680 | -0.390% | 0.083% | 0.002% |
| N3U | TP | 4096 | W4A4 | 389.3010 | 389.9410 | 390.6125 | 389.1245 | -0.273% | 0.045% | 0.172% |
| N3U | TP | 4096 | PER-TOKEN | 554.3230 | 554.2750 | 553.9560 | 554.8355 | +0.084% | 0.092% | 0.058% |
| V3 | EP | 8 | PER-TOKEN | 62.0485 | 62.1130 | 62.1610 | 62.0490 | -0.142% | 0.001% | 0.077% |
| V3 | TP | 8 | MXFP8 | 70.8160 | 71.0085 | 70.7845 | 70.8160 | -0.113% | 0.000% | 0.316% |
| V3 | TP | 8 | MXFP4x8 | 49.8725 | 49.9040 | 49.9520 | 49.9200 | -0.064% | 0.095% | 0.096% |
| V41F | TP | 8 | PER-TOKEN | 57.4080 | 57.4885 | 57.4730 | 57.3770 | -0.154% | 0.054% | 0.027% |
| K3 | TP | 8 | W4A4 | 77.5370 | 77.6185 | 77.6335 | 77.5365 | -0.115% | 0.001% | 0.019% |
| K3 | EP | 4 | W4A4 | 50.7200 | 50.8640 | 50.6080 | 50.7210 | -0.030% | 0.002% | 0.506% |
| V41F | EP | 4 | W4A4 | 32.3845 | 32.3520 | 32.3680 | 32.3200 | -0.024% | 0.200% | 0.049% |

The N3U EP16K MXFP8/MXFP4x8 candidate spreads are3.171%/9.263%; apparent +0.455%/+3.946% is not a stable gain. Raw phases remain unchanged and no sample was filtered. Read-only10ms NVML sampling contains masks0/1/4 (including software power cap), but this reused frozen observer has no per-cell timing envelope. Those samples span the entire subprocess, including import, initialization, compilation, cold-cache work and timing. They cannot identify clocks during a specific cell, establish iso-clock behavior, or explain the timing delta causally. No clocks/power settings changed and no normalization was applied.

Evidence archive SHA: `587e120d398a9e47f2ef836617549ce970b1134bf6c3538ce4a0f7b4e16b24ab`; all raw phase results,100-sample vectors, source/runtime/route/cache receipts and NVML logs under `screen-evidence/`. `analysis.json` retains full identities and phase-clock boundaries; `cells.csv` retains all four medians. Regenerate with `python3 analyze_screen.py`. The copied historical `runtime.json` contains an older source HEAD label; current source identity is established by the per-role514-file manifests, not that label.
