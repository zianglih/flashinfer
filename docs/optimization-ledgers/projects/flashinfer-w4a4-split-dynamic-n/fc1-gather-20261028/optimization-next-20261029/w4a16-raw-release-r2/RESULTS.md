# R2 last-fragment raw release: rejected

Candidate `736bac4ca5a7a11cb2387f00b54d9a0470ad6461eda9b1f72bc57e9996577c40` on retained `b13963b0cc8409aeb92048b9ec7cf3be18f0a57c`. R1 remains separately preserved and rejected. R2 is not committed or pushed.

All16 rows: geometric mean -0.639%; decode -0.850%; prefill -0.427%.14/16 cells are negative. Restoring TP V3 FC2 uniform lowering did not remove its decode loss. Preserve the retained raw-release schedule.

Each phase is100 strict-CUPTI samples; two phase medians averaged per arm. Speedup is `100*((C1+C2)/(A1+A2)-1)`. C-A-A-C is serialized on the same GPU per job; no AUTO/tactic/route changes, no baseline reuse inside this experiment. Original frozen native winners; public functional API and unfused swap layout. W4A16 uses BF16 input directly, so no initial quantizer is timed.

| Model/topology | Tokens | C1 µs | A1 µs | A2 µs | C2 µs | Speedup | C/A spread |
|---|---:|---:|---:|---:|---:|---:|---:|
| ep-kimi-k3-w4a16 | 8 | 84.241 | 84.065 | 84.560 | 84.097 | -0.170% | 0.172% / 0.589% |
| ep-kimi-k3-w4a16 | 4096 | 553.477 | 553.284 | 526.064 | 523.252 | -0.243% | 5.776% / 5.174% |
| ep-nemo3-ultra-w4a16 | 8 | 51.056 | 51.392 | 51.424 | 51.153 | -0.591% | 0.189% / 0.063% |
| ep-nemo3-ultra-w4a16 | 4096 | 390.979 | 391.763 | 390.435 | 391.139 | -0.010% | 0.041% / 0.340% |
| ep-v3-w4a16 | 8 | 68.128 | 68.977 | 68.817 | 68.273 | -1.010% | 0.212% / 0.233% |
| ep-v3-w4a16 | 4096 | 278.755 | 278.113 | 277.938 | 277.890 | +0.107% | 0.311% / 0.063% |
| ep-v41-flash-w4a16 | 8 | 51.008 | 52.225 | 52.113 | 51.073 | -2.163% | 0.127% / 0.215% |
| ep-v41-flash-w4a16 | 4096 | 433.171 | 429.507 | 430.404 | 432.964 | +0.724% | 0.048% / 0.209% |
| tp-kimi-k3-w4a16 | 8 | 87.681 | 88.273 | 88.528 | 87.792 | -0.751% | 0.127% / 0.289% |
| tp-kimi-k3-w4a16 | 4096 | 721.573 | 727.173 | 712.756 | 694.324 | -1.669% | 3.925% / 2.023% |
| tp-nemo3-ultra-w4a16 | 8 | 66.208 | 66.753 | 66.657 | 66.240 | -0.720% | 0.048% / 0.144% |
| tp-nemo3-ultra-w4a16 | 4096 | 546.020 | 547.300 | 546.820 | 546.179 | -0.176% | 0.029% / 0.088% |
| tp-v3-w4a16 | 8 | 56.864 | 57.488 | 57.536 | 56.913 | -1.084% | 0.084% / 0.083% |
| tp-v3-w4a16 | 4096 | 480.661 | 481.298 | 482.595 | 481.156 | -0.215% | 0.103% / 0.269% |
| tp-v41-flash-w4a16 | 8 | 63.761 | 63.872 | 64.064 | 63.793 | -0.300% | 0.050% / 0.301% |
| tp-v41-flash-w4a16 | 4096 | 559.332 | 568.739 | 576.884 | 564.468 | -1.905% | 0.918% / 1.432% |

K3 prefill has large repeat spread: EP5.78/5.17%, TP3.92/2.02%; retain these rows without claiming a stable K3 regression. Several decode losses are much tighter than their C/A spreads. Stock clocks were not changed; all64 cell-phase measurement windows have NVML samples.

Qualification:33 existing exact cases passed; all514 source hashes and628 qualification artifacts verified. Eight paired native FC1/FC2 captures have identical loaded register/local/thread/shared attributes, no locals. All32 performance guard receipts and128 loaded functions passed with zero LOCAL; all6,400 CUPTI samples retained. No sanitizer.

R2 uses the original raw-stage state before advancing it and removes the clone. Generated raw arrival is1 instruction after final LDS for FC1,2 for FC2; decoded fence/commit stays after all eight stores. TP V3 FC2 restores retained BRA133/BRA.U23, but adds4 IMAD.U32. Other FC2 op counts equal retained; each FC1 removes one R2UR. All8 retained control CUBINs match the earlier R1 controls exactly.

Kernel-duration/FC2-after-FC1 frontier deltas are in component-summary.json; overlapping durations must not be summed to reconstruct E2E. These support diagnosis but do not establish which hardware contention caused the loss.

Environment: C3 fi-gather-6be-1029; NVIDIA B300 SXM6 AC, SM103; nvcr.io/nvidia/pytorch:26.05-py3; driver595.91.07, CUDA13.2, CuTe DSL4.8.0. Persistent native/CuTe compilation caches retained. Source, route, frozen-tactic and runtime resource guards apply to both arms.

Reproduce analysis: `python3 audit_qualification.py && python3 analyze_perf.py && python3 analyze_components.py && python3 compare_codegen.py`. Gate and screen launch helpers, full manifests and raw logs are preserved alongside this note.
