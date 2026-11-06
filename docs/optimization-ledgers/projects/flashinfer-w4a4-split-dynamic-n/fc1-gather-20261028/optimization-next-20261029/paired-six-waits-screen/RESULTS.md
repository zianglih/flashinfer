# Paired transpose: six-wait completion contract on retained7739

Ready for parent review as a correctness/ordering improvement. The helper keeps entry completion, all three store-to-load waits and both load-to-overwriting-store waits. Every original caller/terminal wait remains; final register consumers use the documented true-dependency guarantee. This avoids a redundant unconditional final-helper wait. Pairing is preferred to serial-fixed based on the separate repeated stable N3U comparisons; those seven-wait measurements are not substituted into this table.

- Source: `77391e28d12a01e371196e76e56d4b46ace122df` control versus that commit plus frozen kernel `3326ba09b3139824ac26e657a4fdbe89bccf1ab3e9230468ab13e4fa93cc756c`. Only `moe_swap_ab_kernel.py` differs; no tree/SF-owner composition and no W4A16 change.
- Validation: source/region/caller proof and independent peer review pass. Scoped pre-commit passes. Fresh16 paired codegen kernels retain registers and have no new spills/branches.39 existing exact cases and76 matched per-compilation guards pass. Two inherited synthetic M512/K8 MX cases retain160B stack and20 LDL/20 STL sites; all other74 qualification captures are spill-free.
- Timing: sameGPU per-job C-A-A-C, frozen native winners/routes, public API, unfused, input quantizer included forNVFP4 family,10 warmups and100 strictCUPTI samples per phase. Persistent native/CuTe caches retained; no retuning, fallback timer, diagnostic compile flags or clock-setting changes. C3 `fi-gather-6be-1029`, B300 SM103, image `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2, CuTe4.8.0, driver595.91.07.
- Metric: `100 * (sqrt(C1*C2) / sqrt(A1*A2) - 1)`; positive means the six-wait candidate is faster. Aggregate is geometric across all16 cell ratios. Raw arrays, all four phase medians, source/observer/tactic/route hashes and telemetry remain saved.
- Full result: **-0.166%** overall, decode **-0.132%**, prefill **-0.201%**. All10 negative rows remain. This quantifies the required completion contract's cost versus the original helper; it is not evidence to omit required waits.
- Evidence audit: all6400 samples,32 source-bound guard receipts and128 native loaded functions pass; native runtimeLOCAL0. All514 source hashes/arm and seven observer hashes verified.
- Variability: four prefill rows exceed2% repeat spread; maximum control/candidate spreads are7.725%/2.497%. Clock quartiles available=256/256, sampled SM medians=[1522, 1732, 1920.0, 1965.0, 2002, 2024.5, 2032.0], sampled reason codes=['0', '4']; stock clocks were unchanged. No stable-gain attribution for the noisy positive rows and no exclusion of noisy negative rows.

| Model/topology | Mode | Tokens | C1 µs | A1 µs | A2 µs | C2 µs | Paired six-wait | C/A spread |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| K3 EP | PER-TOKEN | 8 | 83.1365 | 83.1680 | 83.2010 | 83.0890 | -0.086% | 0.057% / 0.040% |
| K3 EP | PER-TOKEN | 16384 | 1051.7880 | 1046.1720 | 1020.6835 | 1049.7590 | +1.686% | 0.193% / 2.497% |
| N3U EP | W4A4 | 8 | 47.7610 | 47.6810 | 47.6810 | 47.7610 | +0.168% | 0.000% / 0.000% |
| N3U EP | W4A4 | 16384 | 585.1590 | 590.1670 | 590.5670 | 585.4625 | -0.856% | 0.052% / 0.068% |
| V3 EP | MXFP8 | 8 | 88.5130 | 88.3850 | 88.4180 | 88.3695 | +0.045% | 0.162% / 0.037% |
| V3 EP | MXFP8 | 16384 | 705.4510 | 715.5120 | 724.9070 | 759.9470 | +1.666% | 7.725% / 1.313% |
| V41F EP | MXFP4x8 | 8 | 49.8570 | 49.9365 | 49.8400 | 49.7930 | -0.127% | 0.129% / 0.194% |
| V41F EP | MXFP4x8 | 16384 | 788.6660 | 817.1625 | 835.1625 | 827.4345 | -2.215% | 4.916% / 2.203% |
| K3 TP | MXFP4x8 | 8 | 79.9050 | 79.8090 | 79.7770 | 79.7125 | +0.020% | 0.241% / 0.040% |
| K3 TP | MXFP4x8 | 16384 | 1585.7890 | 1616.5920 | 1629.6950 | 1626.4950 | -1.055% | 2.567% / 0.811% |
| N3U TP | PER-TOKEN | 8 | 63.6810 | 63.9840 | 63.7770 | 63.5685 | -0.400% | 0.177% / 0.325% |
| N3U TP | PER-TOKEN | 16384 | 1784.9105 | 1802.4465 | 1801.8070 | 1785.3490 | -0.943% | 0.025% / 0.035% |
| V3 TP | MXFP8 | 8 | 70.8325 | 71.1040 | 71.1365 | 70.8650 | -0.382% | 0.046% / 0.046% |
| V3 TP | MXFP8 | 16384 | 1346.9585 | 1341.6910 | 1337.5340 | 1340.3350 | +0.301% | 0.494% / 0.311% |
| V41F TP | W4A4 | 8 | 52.3685 | 52.4800 | 52.5445 | 52.3530 | -0.288% | 0.030% / 0.123% |
| V41F TP | W4A4 | 16384 | 1041.3360 | 1043.1125 | 1043.0640 | 1042.1845 | -0.127% | 0.081% / 0.005% |

The two low-spread N3U prefill costs are−0.856% and−0.943%. CUPTI shows FC1 exposed-end movement dominates: N3U EPW4A4 FC1 end+4.664µs versus E2E+5.056µs; N3U TPper-token FC1 end+15.672µs versus E2E+16.997µs. FC2 duration changes overlap preceding work and must not be added to FC1 duration. `component-summary.json` retains every component delta and repeat-spread flag.

Reproduction and raw evidence: `plan.json`, `evidence/perf-config.json`, `run_perf.py`, `harness-proof.json`, `audit_raw.py`, `raw-audit.json`, `cells.csv`, `summary.json`, and `evidence/results/*`. Qualification is in sibling `paired-six-waits-7739`. Previous R1/R2, the original16 fixed-vs-fixed cells and separate3-cell repeat are immutable. Active review remains unstaged; parent owns integration/push.
