# Affine compact FC2 tail addressing

Control: `1054743780dda2919c1424124c1e3258248b8c19`. Candidate: the same head plus one kernel patch, `e8ee4c6c639fba3512db98dcf8dc4b06b611325d10fb2fc528e49ab2e6441ea0` (+8/−5). Rejected by root; local and remote candidate clones are removed. Canonical, shared control, helpers, artifacts and caches are preserved.

The compact output already has affine row ownership. This patch computes the issuing lane’s output row directly, retaining the expanded-output routing-map path. Arithmetic, rounding, bulk scratch layout, synchronization, allocation, public API and tactics are unchanged.

Exact/codegen: 192 paired replay comparisons, 96 GEMM pairs and 10 combine pairs passed. All 40 affected FC2 pairs remove 12–98 non-NOP instructions and 2–16 shuffles. Registers stay unchanged or decrease by up to 24; shared memory and uniform-register spill/fill counts are unchanged. All unaffected instruction streams/resources are identical; local and stack traffic are zero. No sanitizer was run.

Timing: all four models in EP and TP, tokens 4/64/4096/16384, supported formats, unfused finalization, NV input quantization included. Saved 83df winners and routing are frozen. C-A-A-C uses 10 warmups and 100 cold-L2 CUPTI graph samples per phase. The per-cell ratio is geometric_mean(C1,C2) / geometric_mean(A1,A2), followed by a geometric mean across cells. No retuning or external-baseline rerun. Host allocations and descriptor setup are outside the GPU timer.

All 144 cells / 576 medians / 57,600 raw samples passed independent source, route, winner, cache, GPU identity, argv and timing verification. Only 54 cells use compact FC2: all are prefill. Decode, noncompact prefill and W4A16 are unchanged sanity arms.

| Scope | Cells | Speedup |
|---|---:|---:|
| Compact affected | 54 | -0.065% |
| Compact EP | 30 | -0.102% |
| Compact TP | 24 | -0.018% |
| Noncompact scaled sanity | 58 | +0.011% |
| W4A16 sanity | 32 | -0.156% |

Positive values mean lower candidate latency. The unchanged sanity arms are recorded without attributing their variation to this source patch.

| Topology | Model | Tokens | W4A4 | PER-TOKEN | MXFP4x8 | MXFP8 | W4A16 sanity |
|---|---|---:|---:|---:|---:|---:|---:|
| EP | V3 | 4 | +0.051% | +0.095% | -0.034% | +0.070% | -0.032% |
| EP | V3 | 64 | -0.042% | -0.105% | -0.043% | +0.062% | +0.011% |
| EP | V3 | 4096 | -0.085% | +0.100% | -0.083% | -0.003% | +0.090% |
| EP | V3 | 16384 | -0.102% | -0.070% | +0.152% | +3.530% | -2.563% |
| EP | V41F | 4 | -0.023% | +0.063% | +0.071% | +0.048% | -0.205% |
| EP | V41F | 64 | +0.028% | +0.004% | -0.020% | +0.057% | -0.053% |
| EP | V41F | 4096 | +0.016% | -0.008% | -0.004% | -0.052% | +0.126% |
| EP | V41F | 16384 | -0.055% | +0.561% | -2.435% | -1.528% | -1.404% |
| EP | K3 | 4 | -0.001% | +0.112% | -0.016% | N/A | -0.124% |
| EP | K3 | 64 | -0.017% | -0.069% | -0.014% | N/A | -0.071% |
| EP | K3 | 4096 | -0.159% | +0.153% | -0.150% | N/A | +0.104% |
| EP | K3 | 16384 | -0.163% | +0.102% | +2.924% | N/A | +0.520% |
| EP | N3U | 4 | -0.001% | +0.058% | +0.157% | +0.032% | -0.038% |
| EP | N3U | 64 | +0.012% | +0.000% | -0.075% | -0.052% | -0.045% |
| EP | N3U | 4096 | +0.003% | +0.082% | -0.019% | +0.028% | +0.217% |
| EP | N3U | 16384 | +0.009% | -0.020% | -3.599% | -1.965% | -2.391% |
| TP | V3 | 4 | -0.132% | +0.138% | +0.202% | +0.155% | +0.021% |
| TP | V3 | 64 | +0.050% | +0.059% | -0.203% | +0.025% | -0.129% |
| TP | V3 | 4096 | +0.353% | +0.193% | +0.212% | -0.419% | +0.036% |
| TP | V3 | 16384 | +0.011% | -0.109% | -0.080% | +0.201% | +0.227% |
| TP | V41F | 4 | -0.221% | +0.020% | N/A | N/A | +0.116% |
| TP | V41F | 64 | -0.073% | +0.082% | N/A | N/A | +0.027% |
| TP | V41F | 4096 | +0.002% | -0.026% | N/A | N/A | -1.208% |
| TP | V41F | 16384 | +0.002% | -0.171% | N/A | N/A | +0.022% |
| TP | K3 | 4 | -0.019% | -0.035% | -0.097% | N/A | -0.031% |
| TP | K3 | 64 | -0.100% | -0.100% | +0.010% | N/A | +0.006% |
| TP | K3 | 4096 | +0.307% | +0.199% | +0.063% | N/A | -0.062% |
| TP | K3 | 16384 | +0.141% | +0.167% | -0.621% | N/A | +0.570% |
| TP | N3U | 4 | +0.043% | -0.075% | +0.065% | +0.236% | +0.100% |
| TP | N3U | 64 | +0.023% | +0.108% | +0.059% | +0.022% | +0.041% |
| TP | N3U | 4096 | +0.089% | -0.242% | +0.068% | +0.047% | +0.022% |
| TP | N3U | 16384 | +0.190% | -0.233% | -0.497% | -0.293% | +1.203% |

Largest affected slowdowns:

- EP N3U CuteDSL MXFP4x8 T16384: -3.599%; C1/A1/A2/C2 = 0.764721500/0.783393500/0.787953500/0.750129500 ms.
- EP V41F CuteDSL MXFP4x8 T16384: -2.435%; C1/A1/A2/C2 = 0.819286000/0.834021500/0.807749500/0.782725000 ms.
- EP N3U CuteDSL MXFP8 T16384: -1.965%; C1/A1/A2/C2 = 0.814530000/0.843169500/0.845314000/0.840977500 ms.
- EP V41F CuteDSL MXFP8 T16384: -1.528%; C1/A1/A2/C2 = 0.937446000/0.978086500/0.958934500/0.970167000 ms.
- TP K3 CuteDSL MXFP4x8 T16384: -0.621%; C1/A1/A2/C2 = 1.934792000/1.949159500/1.942360000/1.932568000 ms.

`perf-cells.csv` contains all pass medians and drifts. `gpu-evidence/` and `perf-evidence/` preserve raw outputs and source-bound receipts. The initial bulk32 harness depth attempt failed on unchanged control before candidate compilation; it remains archived and is not counted as a passed gate. The corrected supplement verifies realized 32×1 scratch.

Gate archive SHA256: `ae9ddc4cf3b2836d1d20e3d0e8a2e06fcc415ba3cf5dea7d74644af72c0d5c93`. Timing archive SHA256: `3f067b9392cc47446366f59d3f272abd5ed37a3be236b658ea5d89be345ee443`.

## Focused independent repeat

The three flagged EP T16384 cells were repeated in separate C-A-A-C jobs with the same source, frozen winners, routing and timing contract. The full first screen above is unchanged. All three repeats remain negative; pass variation is recorded without treating it as proof that the source has no effect.

| Model | Format | First screen | Repeat | Repeat C1/A1/A2/C2 (ms) |
|---|---|---:|---:|---|
| N3U | CuteDSL MXFP8 | -1.965% | -4.678% | 0.828054000/0.835188500/0.839349500/0.769220500 |
| N3U | CuteDSL MXFP4x8 | -3.599% | -2.083% | 0.717892500/0.768452500/0.761605000/0.781637000 |
| V41F | CuteDSL MXFP4x8 | -2.435% | -1.218% | 0.806916000/0.826836000/0.776052000/0.775956000 |

Decision: rejected. The instruction and register reductions are real, but the repeated prefill slowdowns lack compensating end-to-end gains. No model/dtype exception or additional timing is proposed.

Repeat archive SHA256: `ec117082ed4ec6e5fb24943f2c7457d5475045476a7aa3d9aa67fd4127f724af` (218 verified files, 12 medians / 1,200 raw samples).
