# Single-GPU native backend comparison

- **Source:** FlashInfer `97e8d0c8bb86b352ccb42f2654ddc2ab9a8e6939`, unchanged `benchmarks/bench_moe_deepseek.py::_benchmark_single`. No production edits.
- **Workload:** H7168, I2048, 256 global experts, 32 local experts (offset 0), simulated EP8/TP1, top-k 8, 8 groups / top 4 groups, routed scale 2.5, SwiGLU. Tokens: `1,2,4,8,16,32,64,128,256,512,4096,8192,16384`.
- **Inputs:** native `create_inputs` resets seed 42 for every row; bias scale 0.01. Same BF16 source activation/weight generator and FP32 routing logits; native backend weight quantization/layout preparation remains unchanged. CuTe uses unit global weight scales; TRTLLM uses native per-expert global weight scales. This is a backend performance comparison, not a claim of identical quantized values or numerical outputs.
- **Routing:** `routing_input_mode="logits"` in every arm, so both include their native DeepSeek routing, packing, expert compute and finalize. The TRTLLM `routed` option is deliberately unused: it changes the benchmark's route distribution and routing rule.
- **CuTe W4A16:** BF16 activations, NVFP4 weights decoded for BF16 MMA, FP32 accumulation, BF16 output. `CuteDslMoEWrapper`, `use_fused_finalize=False`.
- **TRTLLM W4A4:** NVFP4 activations and weights, BF16 output, native TRTLLM finalize. `use_per_token_activation=False`, so this is the per-tensor global-scale mode, with the NVFP4 format's 16-element FP8 block scales still present. TRTLLM's route weights and internal rounding differ from CuTe; no identical combine or precision claim is made.
- **Quant excluded:** native `fp4_quantize(hidden, hidden_global_scale, 16, False, True)` executes before timing; the timed call receives packed FP4 activation and FP8 scale buffers.
- **Quant included:** the same quantization runs inside the timed closure, which receives BF16 input. This includes FP4 packing and FP8 block-scale generation using the precomputed tensor-global scale. Both modes exclude the global amax/calibration calculation in `create_inputs`, as well as all weight preparation. Quantization uses the native CUDA backend (`fp4_quantize` default).
- **Single GPU:** real communication is excluded. All six measured sweeps run serially on GPU 0 of the same new allocation, with hardware UUID and no competing compute processes recorded before every sweep. The new CuTe control is used for this table; preserved results from a previous device are not its denominator.
- **Timing:** unchanged native `_measure_or_profile`, 10 warmups and 100 cold-L2 CUDA-graph CUPTI samples per row. Event fallback is an error. The observer returns the native sample array unchanged and saves its 100 values after completion; the reported native median must match exactly.
- **Selection:** fresh normal AUTO in each independent process; no tactic forcing, saved-selection loading, minima, or sample pooling. `FLASHINFER_DIST_AWARE_AUTOTUNE=0`, `FLASHINFER_AUTOTUNER_LOAD_FROM_FILE=0`, PDL enabled. The observer saves each completed row's tactic cache for audit only.
- **Order:** `cute-w4a16-r1`, `trtllm-w4a4-excluded-r1`, `trtllm-w4a4-included-r1`, `trtllm-w4a4-included-r2`, `trtllm-w4a4-excluded-r2`, `cute-w4a16-r2` (A-B-C-C-B-A). Shared compiled native artifacts can be reused because every arm uses the same unchanged source, but AUTO decisions remain independent.
- **Metrics:** show both repeat medians. The paired speedup is `sqrt((TRTLLM_R1 / CuTe_R1) * (TRTLLM_R2 / CuTe_R2))`; above 1 means CuTe is faster. Report quant-excluded and quant-included separately. Overall/decode/prefill summaries are geometric means of paired ratios over T4–16384, T4–512, and T4096/8192/16384 respectively; T1/T2 are run and shown but excluded from every aggregate. Two repeats are not a statistical significance claim. The inclusive-minus-exclusive difference is not an isolated quantization-kernel cost because independent AUTO selections can differ.
- **Validation scope:** source, environment, hardware, timing samples, input histograms, and tactic-cache provenance only. No new correctness matrix or sanitizer campaign is requested or run.

## Exact campaign command

The GPU owner installs the same pinned CUDA 13.2 environment used for the distributed K3 run, finishes all K3 timing first, and optionally warms the native TRTLLM module before this campaign. `run_comparison.sh` records the complete environment and source hashes.

```bash
bash <uploaded-trtllm-dir>/run_comparison.sh \
  /workspace/flashinfer-w4a16-regular-tma/candidate \
  /workspace/flashinfer-w4a16-regular-tma/.venv/bin/python \
  /workspace/flashinfer-w4a16-regular-tma/final-comparison/trtllm-results
```

Equivalent upstream calls for one sweep of each backend (run each command in a fresh process, in the campaign order above):

```bash
cd /workspace/flashinfer-w4a16-regular-tma/candidate
export CUDA_VISIBLE_DEVICES=0 TRTLLM_ENABLE_PDL=1
export FLASHINFER_DIST_AWARE_AUTOTUNE=0 FLASHINFER_AUTOTUNER_LOAD_FROM_FILE=0
export OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1
export FLASHINFER_WORKSPACE_BASE=/root MAX_JOBS=32 FLASHINFER_NVCC_THREADS=1
unset FLASHINFER_AUTOTUNE_TIMER
tokens=1,2,4,8,16,32,64,128,256,512,4096,8192,16384
py=/workspace/flashinfer-w4a16-regular-tma/.venv/bin/python

"$py" benchmarks/bench_moe_deepseek.py --num-tokens "$tokens" \
  --ep 8 --tp 1 --warmup 10 --iters 100 --routing-input-mode logits \
  --backends cutedsl --profile-backend cute-dsl-w4a16 --no-fused-finalize

"$py" benchmarks/bench_moe_deepseek.py --num-tokens "$tokens" \
  --ep 8 --tp 1 --warmup 10 --iters 100 --routing-input-mode logits \
  --backends trtllm-nvfp4 --profile-backend trtllm-nvfp4 --no-fused-finalize

"$py" benchmarks/bench_moe_deepseek.py --num-tokens "$tokens" \
  --ep 8 --tp 1 --warmup 10 --iters 100 --routing-input-mode logits \
  --backends trtllm-nvfp4 --profile-backend trtllm-nvfp4 --no-fused-finalize \
  --include-activation-quant
```

`--profile-backend` only selects the measured backend here; `--profile-cuda` is absent. `--no-fused-finalize` affects CuTe and CUTLASS only; TRTLLM retains its native finalize. Omitting `--use-per-token-activation` selects the requested per-tensor activation scaling.
