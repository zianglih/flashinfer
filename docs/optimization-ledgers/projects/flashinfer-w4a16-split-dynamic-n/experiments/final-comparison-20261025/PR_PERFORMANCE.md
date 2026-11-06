### Performance

Full-PR comparisons use original baseline `316faec37a4706a2ecc7d46265087f8190b40baa` and current head `97e8d0c8bb86b352ccb42f2654ddc2ab9a8e6939`. Each comparison uses the same physical GPU(s) within its campaign. The backend comparison uses current head and its own fresh CuTe control on the same GPU as TRTLLM.

| Comparison / ratio | Overall | Decode | Prefill |
| --- | ---: | ---: | ---: |
| H7168 full PR — Before / After | 1.042567× | 1.037350× | 1.056607× |
| Kimi K3 EP8 full PR — Before / After | 1.045588× | 1.018100× | 1.122571× |
| TRTLLM W4A4 input quant excluded / CuTe W4A16 | 0.842392× | 0.971708× | 0.575604× |
| TRTLLM W4A4 input quant included / CuTe W4A16 | 0.869279× | 0.987195× | 0.619216× |

**Ratios above 1 favor current CuTe W4A16.** Backend comparisons change activation precision and native finalization; they are not matched-precision ablations.

- **Grid:** `1,2,4,8,16,32,64,128,256,512,4096,8192,16384`, following #6277. T1/T2 are measured and shown with `*`, but excluded from every aggregate. Decode is T4–512; prefill is T4096/T8192/T16384. Workloads are reported separately, not pooled.
- **Timing:** ten warmups and 100 cold-L2 CUDA-graph CUPTI samples per row, PDL enabled, fresh normal AUTO in every process. Full-PR campaigns use before R1 → after R1 → after R2 → before R2. The backend campaign uses CuTe → input quant excluded → input quant included → included → excluded → CuTe. Compilation, tuning, input/weight setup and graph capture are untimed; no forced tactics, saved-selection loading, minima or sample pooling.
- **Metric:** every absolute table cell is a native median in microseconds. Two-repeat ratios are `sqrt((Reference R1 × Reference R2)/(CuTe R1 × CuTe R2))`; group ratios are geometric means over included tokens. Normal AUTO includes tactic-selection variation. Two repeats do not establish statistical significance.

- **Environment:** `nvcr.io/nvidia/pytorch:26.05-py3`, NVIDIA B300 SXM6 AC (SM103), 1100 W power limit, driver `595.91.07`; Python `3.12.3`, PyTorch `2.12.0a0+5aff3928d8.nv26.05` / CUDA `13.2`, system nvcc `13.2.78`, loaded CuTe DSL `4.7.1`, TVM-FFI `0.1.15.post0`, cupti-python `13.4.0` / CUPTI library `13.4.58`, CUDA compiler/NVVM packages `13.3.73`. K3 loads NCCL `2.30.7`; PyTorch's compiled NCCL version is `2.30.4`.
- **Devices and execution:** H7168 before/after ran on one GPU of `hu-pdx-38` (`GPU-ae94371a-b05f-a1b5-d520-67157ffd295f`), 2026-10-25 19:34–19:37 UTC. K3 ran on all eight NVLink-connected B300s of `hu-pdx-7`, 20:03–20:15 UTC; the backend comparison then used GPU 0 of that node (`GPU-edf3141e-7e43-ff20-2c4e-a0e11b5ae000`), 20:25–20:31 UTC. Every campaign preserves its own device identities across arms; the backend table uses its freshly measured CuTe control. No other GPU compute processes were present before each sweep.

#### H7168/I2048 — full-PR single-GPU comparison

Native `benchmarks/bench_moe_deepseek.py`: 256 global experts, top-k 8, groups 8/top-groups 4, routed scaling 2.5, seed 42, bias scale 0.01, SwiGLU; simulated EP8/TP1 with 32 local experts at offset 0. BF16 activations/output, NVFP4 weights, FP32 accumulation. Whole-MoE timing includes routing, permutation, FC1/activation/FC2 and deterministic unfused finalize; inter-GPU communication is excluded.

| Tokens | Before R1 (µs) | Before R2 (µs) | After R1 (µs) | After R2 (µs) | Before / After |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1* | 34.2720 | 34.0800 | 31.6160 | 31.1360 | 1.089268× |
| 2* | 39.7445 | 41.2965 | 36.8805 | 36.8160 | 1.099457× |
| 4 | 55.0730 | 56.8640 | 51.1050 | 51.2965 | 1.092981× |
| 8 | 69.7290 | 69.6165 | 66.6730 | 65.3760 | 1.055307× |
| 16 | 78.1450 | 77.7925 | 75.2965 | 75.3770 | 1.034934× |
| 32 | 110.6570 | 110.5770 | 108.4490 | 107.8410 | 1.022862× |
| 64 | 144.9930 | 145.5045 | 140.8170 | 142.1770 | 1.026525× |
| 128 | 147.9055 | 148.2570 | 144.3375 | 144.3690 | 1.025825× |
| 256 | 155.1680 | 156.0490 | 153.4570 | 152.8495 | 1.016029× |
| 512 | 160.8815 | 160.8970 | 156.5935 | 156.8975 | 1.026437× |
| 4096 | 312.2745 | 313.0420 | 290.4185 | 291.5550 | 1.074477× |
| 8192 | 595.8130 | 607.1090 | 573.8440 | 572.8210 | 1.049016× |
| 16384 | 1238.7945 | 1182.6020 | 1153.3055 | 1159.7695 | 1.046552× |

| Aggregate | R1 ratio | R2 ratio | Two-repeat ratio |
| --- | ---: | ---: | ---: |
| Overall | 1.041782× | 1.043352× | 1.042567× |
| Decode | 1.034149× | 1.040561× | 1.037350× |
| Prefill | 1.062416× | 1.050830× | 1.056607× |

All 11 retention points improve in both repeats. Complete active FC1/FC2 AUTO records match across all four arms only at T512 (1.026437×) and T8192 (1.049016×). At T4096/T16384, baseline selects N128 and current head selects N192. These results cover the whole PR, including preparation, runtime N, arithmetic and normal-AUTO selection changes.

#### Kimi K3 — full-PR distributed EP8 comparison

Native `benchmarks/bench_cute_dsl_moe_distributed.py --model kimi-k3`: H3584/I3072, 896 experts, top-k 16, SiTU gate/linear scales 4/25, routed scaling 1.0; real EP8/TP1 with 112 experts per GPU. Global T is divided as `T // 8 + (rank < T % 8)`, including empty ranks at small T. BF16 activations/output, NVFP4 weights, FP32 accumulation. Seeds are weights `1000+rank`, activations `42+rank`, routing logits 137 and bias 911.

Timing includes NVLink one-sided dispatch, activation packing, local FC1/SiTU/FC2, deterministic unfused finalize and return combine. Routing is precomputed on CPU. Outer projections, shared experts, router GEMM and attention are excluded. Each sample is the maximum of eight rank-local CUPTI activity spans; latency is the median of 100 such maxima. This includes activity gaps/overlap, not a sum of kernel durations or a maximum of rank medians.

| Global tokens | Before R1 (µs) | Before R2 (µs) | After R1 (µs) | After R2 (µs) | Before / After |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1* | 111.3765 | 91.4255 | 77.9845 | 79.2005 | 1.283992× |
| 2* | 108.3855 | 102.4495 | 88.2880 | 108.3685 | 1.077304× |
| 4 | 131.1210 | 129.1215 | 132.1930 | 131.8250 | 0.985672× |
| 8 | 164.1455 | 156.2900 | 162.7220 | 149.8730 | 1.025641× |
| 16 | 179.5690 | 179.2340 | 177.6345 | 178.9290 | 1.006287× |
| 32 | 255.0110 | 273.6350 | 246.1140 | 249.9860 | 1.064975× |
| 64 | 336.0190 | 354.4045 | 333.0580 | 334.7240 | 1.033542× |
| 128 | 392.2120 | 390.4670 | 386.9790 | 390.1000 | 1.007212× |
| 256 | 430.4670 | 420.8850 | 421.3160 | 419.8905 | 1.011998× |
| 512 | 444.3550 | 439.7320 | 438.9950 | 435.1570 | 1.011361× |
| 4096 | 795.5735 | 806.6475 | 709.3805 | 690.6475 | 1.144496× |
| 8192 | 1448.0265 | 1427.4685 | 1215.9120 | 1223.3755 | 1.178801× |
| 16384 | 2480.4455 | 2428.4055 | 2346.1505 | 2335.1900 | 1.048543× |

| Aggregate | R1 ratio | R2 ratio | Two-repeat ratio |
| --- | ---: | ---: | ---: |
| Overall | 1.041555× | 1.049636× | 1.045588× |
| Decode | 1.012935× | 1.023291× | 1.018100× |
| Prefill | 1.121889× | 1.123253× | 1.122571× |

Ten of 11 retention points improve in both repeats; **T4 regresses in both** (0.985672×). Only excluded T2 changes direction between repeats. Overall, decode and prefill improve in both repeats. This is a whole-PR normal-AUTO comparison; rank-local FC1/FC2 selections can differ.

#### H7168/I2048 — current CuTe W4A16 vs TRTLLM W4A4

Same native H7168 workload and BF16 source-input generator, with logits routing in all three arms. Every arm includes its native routing, expert compute and finalize. CuTe keeps BF16 activations and deterministic unfused finalize; TRTLLM uses NVFP4 activations/weights and native finalize. Native weight global scales, route-weight precision and intermediate rounding also differ; identical quantized values or outputs are not assumed.

TRTLLM uses **per-tensor global activation scaling**, with NVFP4's 16-element FP8 block scales still present. Table label **Input-Q** refers only to input activation quantization. **Input quant excluded** runs `fp4_quantize(hidden, hidden_global_scale, 16, False, True)` before timing. **Input quant included** runs the same packing and block-scale generation inside the timed closure using the precomputed tensor-global scale. Global input-amax calibration and all weight preparation are outside both timings. Both include the native MoE's internal activation processing/requantization and finalize. The gap between these independently tuned arms is not an isolated quantization-kernel cost.

| Tokens | CuTe R1 (µs) | CuTe R2 (µs) | TRT input-Q excl R1 (µs) | TRT input-Q excl R2 (µs) | TRT input-Q incl R1 (µs) | TRT input-Q incl R2 (µs) | Input-Q excl / CuTe | Input-Q incl / CuTe |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1* | 31.5210 | 31.5520 | 24.5440 | 26.5280 | 25.1200 | 24.8485 | 0.809117× | 0.792221× |
| 2* | 37.8565 | 36.8325 | 33.2800 | 33.3445 | 35.1680 | 37.4720 | 0.892109× | 0.972168× |
| 4 | 51.1845 | 50.9925 | 48.0960 | 52.1770 | 50.8965 | 50.3685 | 0.980554× | 0.991063× |
| 8 | 66.0810 | 66.8645 | 62.2720 | 61.8410 | 62.9600 | 63.3610 | 0.933574× | 0.950183× |
| 16 | 75.5850 | 75.5045 | 72.8480 | 73.4570 | 74.0810 | 73.8570 | 0.968325× | 0.979141× |
| 32 | 107.3605 | 107.5205 | 103.5690 | 103.6650 | 105.0885 | 105.4090 | 0.964413× | 0.979599× |
| 64 | 142.2735 | 141.6325 | 138.5135 | 139.5530 | 141.4730 | 140.5770 | 0.979427× | 0.993460× |
| 128 | 144.3215 | 144.4490 | 140.4495 | 141.0735 | 142.8650 | 143.9215 | 0.974900× | 0.993123× |
| 256 | 153.0890 | 153.3130 | 149.7295 | 150.6260 | 153.7285 | 152.7370 | 0.980262× | 1.000202× |
| 512 | 156.6895 | 156.6735 | 155.6655 | 155.6180 | 158.4490 | 158.6735 | 0.993364× | 1.011997× |
| 4096 | 295.8585 | 294.5305 | 212.0660 | 212.4665 | 225.3775 | 225.4900 | 0.719074× | 0.763681× |
| 8192 | 621.9085 | 587.5090 | 331.2345 | 330.9465 | 357.1540 | 357.0270 | 0.547742× | 0.590756× |
| 16384 | 1215.4500 | 1190.1060 | 582.0210 | 582.6775 | 632.8675 | 633.0295 | 0.484197× | 0.526268× |

| Aggregate | Input-Q excl / CuTe R1 | R2 | Two-repeat | Input-Q incl / CuTe R1 | R2 | Two-repeat |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Overall | 0.835537× | 0.849304× | 0.842392× | 0.866573× | 0.871993× | 0.869279× |
| Decode | 0.965947× | 0.977504× | 0.971708× | 0.988076× | 0.986314× | 0.987195× |
| Prefill | 0.567544× | 0.583779× | 0.575604× | 0.610722× | 0.627828× | 0.619216× |

TRTLLM has lower latency in all three aggregates in both input-quantization modes and repeats. With input quantization included, T512 favors CuTe by 1.011997×; T256 is effectively tied (1.000202×) with mixed repeat direction. Input-quant-excluded T4 also changes direction between repeats. These are native backend comparisons with the precision and finalization differences described above.

**Evidence audit:** all 18,200 native samples reproduce the 182 median values above. Source snapshots match the pinned Git objects; execution order, runtime settings, GPU identities, 32 distributed-rank receipts and all 546 saved tactic-cache hashes were checked. The single-GPU comparisons have matching diagnostic input-route histogram summaries; these do not establish identical actual routes inside different backends. Full sample vectors and provenance are preserved with the local campaign artifacts. Benchmark completion and timings do not establish numerical correctness.
