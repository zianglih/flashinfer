# Plain decoded-slot acquire: rejected

Unstaged candidate `55ce35c53c32df89ceb70e55e92f482f93af43caaaf15367d0761c896f628dc1` on retained `b13963b0cc8409aeb92048b9ec7cf3be18f0a57c`. Not committed or pushed.

All16 rows: geometric mean -1.325%; decode -1.541%; prefill -1.108%.15/16 cells are negative. Retain the existing decoded-slot lookahead.

This candidate only removed cached decoded-slot producer_try_acquire/token plumbing. Both raw-input peeks, the original post-store raw release, stage resets/advances, publication fence/commit, stages, tactics, quotas and arithmetic were preserved. The preceding raw-ready wait provides work/latency that a speculative decoded-slot check can overlap; the screen rejects removing it but does not isolate the exact hardware stall mechanism.

Each phase is100 strict-CUPTI samples; two phase medians averaged per arm. Speedup is `100*((C1+C2)/(A1+A2)-1)`. C-A-A-C on the same GPU per job; fixed native winners, public functional API, unfused swap layout, no retuning or external-baseline reuse. W4 uses BF16 input directly, so no initial input quantizer is timed.

| Model/topology | Tokens | C1 µs | A1 µs | A2 µs | C2 µs | Speedup | C/A spread |
|---|---:|---:|---:|---:|---:|---:|---:|
| ep-kimi-k3-w4a16 | 8 | 84.001 | 84.128 | 84.161 | 83.873 | -0.247% | 0.152% / 0.039% |
| ep-kimi-k3-w4a16 | 4096 | 538.212 | 528.403 | 564.916 | 525.604 | -2.699% | 2.399% / 6.910% |
| ep-nemo3-ultra-w4a16 | 8 | 51.264 | 51.680 | 51.552 | 51.169 | -0.774% | 0.187% / 0.249% |
| ep-nemo3-ultra-w4a16 | 4096 | 390.659 | 390.931 | 391.251 | 390.435 | -0.139% | 0.058% / 0.082% |
| ep-v3-w4a16 | 8 | 67.985 | 68.753 | 68.704 | 68.225 | -0.908% | 0.353% / 0.071% |
| ep-v3-w4a16 | 4096 | 278.642 | 278.978 | 278.627 | 278.435 | -0.095% | 0.074% / 0.126% |
| ep-v41-flash-w4a16 | 8 | 51.104 | 50.753 | 50.912 | 51.104 | +0.535% | 0.000% / 0.313% |
| ep-v41-flash-w4a16 | 4096 | 434.115 | 433.572 | 435.411 | 434.340 | -0.061% | 0.052% / 0.424% |
| tp-kimi-k3-w4a16 | 8 | 87.665 | 87.889 | 87.713 | 87.648 | -0.164% | 0.019% / 0.201% |
| tp-kimi-k3-w4a16 | 4096 | 696.182 | 713.877 | 737.188 | 716.580 | -2.640% | 2.930% / 3.265% |
| tp-nemo3-ultra-w4a16 | 8 | 66.192 | 67.057 | 66.961 | 66.193 | -1.218% | 0.001% / 0.144% |
| tp-nemo3-ultra-w4a16 | 4096 | 546.164 | 548.164 | 546.467 | 545.412 | -0.279% | 0.138% / 0.311% |
| tp-v3-w4a16 | 8 | 56.944 | 59.312 | 59.200 | 56.880 | -3.955% | 0.113% / 0.189% |
| tp-v3-w4a16 | 4096 | 480.754 | 481.475 | 481.701 | 481.269 | -0.120% | 0.107% / 0.047% |
| tp-v41-flash-w4a16 | 8 | 63.745 | 67.473 | 67.425 | 63.809 | -5.444% | 0.100% / 0.070% |
| tp-v41-flash-w4a16 | 4096 | 563.173 | 591.332 | 562.148 | 558.356 | -2.770% | 0.863% / 5.191% |

TP V3/V41 decode losses are tight relative to repeat spread. K3 EP/TP prefill and V41 TP prefill are high-spread cases (candidate6.91/3.27/5.19%); all remain included, without a stable-regression claim. No clocks were changed; all64 cell-phase windows have NVML samples.

Qualification:33 existing exact cases passed, all514 source hashes and628 qualification files verified. Eight native FC1/FC2 pairs have unchanged loaded REG/LOCAL/thread/shared attributes, no locals. The raw arrival remains after decoded stores/fence in all8. Codegen removes one branch and1–2 TRYWAIT sites; total non-NOP changes are FC1+3/+3/+3/+4 and FC2−9/−9/+7/−2. It is not a universal static-instruction reduction.

Performance: all6,400 strict-CUPTI samples,32 source-bound runtime guard receipts and128 loaded functions verified; LOCAL0, no missing clock windows. No sanitizer or new tests. Component medians are in component-summary.json; do not sum overlapping kernel durations.

Environment: C3 fi-gather-6be-1029; NVIDIA B300 SXM6 AC, SM103; nvcr.io/nvidia/pytorch:26.05-py3; driver595.91.07, CUDA13.2, CuTe DSL4.8.0. Persistent native/CuTe caches preserved. Both source arms and all route/tactic/runtime guards are frozen.

Reproduce CPU analysis with audit_qualification.py, analyze_perf.py, analyze_components.py. Full source/patch, gate, raw timing logs and manifests are preserved locally.
