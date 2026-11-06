# Finalizer geometry and prefetch experiment

The reference `rounding.py` is byte-identical to PR7196 commit `36740c36a32a6c6d1c7d8162823fe823912de741` at `flashinfer/fused_moe/cute_dsl/blackwell/moe_finalize.py`; SHA256 `485c1c0c74ad1b687c33760453a90a014e2d4f04fd414fe8b1fb230d3d820aee`. Production source was not edited by this experiment. C1 native capture used candidate13ca1475; the selected patch applies to parent1904964, whose finalizer has the same reference bytes.

## Selected policy

`divisor.py` changes only host geometry: expanded inputs with more than1024 tokens retain four vectors/thread when the hidden dimension is already exactly tiled; otherwise select the largest exact divisor among seven/six/five vectors/thread. This removes partially occupied hidden CTAs without using the eight-vector geometry that regressed aligned rows. Permuted inputs and shorter batches keep their existing policy. The original kernel, first-slot FP32 multiply, subsequent ordered FP32 FMAs, signed-zero/subnormal behavior, PDL ordering,16-byte alignment and API are unchanged. The existing kernel-cache key already includes vectors/thread.

`selected-policy.patch` is the eight-line production proposal. No stricter alignment or silent alignment fallback is added.

## Evidence and scope

- C1 B200, GPUs2/5, existing CUDA13.2 image `nvcr.io/nvidia/pytorch:26.05-py3`, CuTe4.7.1. `environment.json` in the archive records exact runtime package metadata and source state.
- All timings use10 warmups/100 samples, cold L2, CUDA graph, CUPTI; event fallback is fatal. Standalone proxy uses PDL off and random1/8 valid routing. Native capture preserves actual `bench_moe_deepseek.py` routing, inputs, `input_is_expanded=True`, and PDL=True.
- Native preparation is per-tensor NVFP4, unfused finalize, with fixed upstream tactic `(128, ((512,128),(2,1),False), ((128,128),(1,1),False))`. The captured finalizer is timed in isolation, so results are not full-pipeline gains.
- Selected policy passed14 paired shape cases (H5120/6144/7168/8192/10240/14336/16384, both layouts), six actual-native token cases (8/128/1024/2048/8192/16384), and18 focused prefill edge cases (five/six/seven vectors, FP32/BF16/FP16 scales, top-k1/2/8/16, zeros/subnormals/extremes/masking). Full output bytes are compared, not floating-point tolerance. Initial variants each passed72 edge cases plus their timing cases.
- H7168 native T16384 repeated controls85.888us versus selected82.976us; T8192 controls46.208/46.3515us versus44.736us; T2048 controls15.472/15.456us versus15.104us. Earlier forward/reverse native runs of identical seven-vector geometry reproduce the gain. Full raw sample arrays and route-count histograms are in the archive JSON files.
- General proxy shape screen shows benefits from eliminating partial tiles; aligned H8192/H16384 and permuted inputs retain unchanged geometry. Do not generalize the rejected unbounded one-row geometry, which regressed aligned H8192.
- Rejected axes retained locally: wide256-bit loads with packed FP32 arithmetic, one-warp CTAs, selective scale loads, warp-coalesced metadata, and broad prefetch/row policies. Some permuted-only proxy gains were not included because the current optimization targets the native expanded path and broad geometry regressed other hidden sizes.
- A short NCU pair shows the finalizer is DRAM bound: reference68.6% versus exact-row geometry70.8% peak DRAM throughput. Metadata/math-focused changes did not help. Profiles are diagnostic, not primary timing evidence.
- Initial NCU/native harness attempts failed before kernel profiling/timing because a helper named `profile.py` shadowed Python's standard-library module; it was renamed `probe_profile.py`. Failure logs are preserved; subsequent runs completed.
- No new GPU timings launch while the parent's monitored-pair investigation requests quiescence. GPUs2/5 were released after the18-case exact check.

## Reproduction

Run from the effort root to synchronize task-local helpers, then use managed `/usr/local/bin/h` to execute inside the candidate checkout. The selected native command is:

```bash
CUDA_VISIBLE_DEVICES=5 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 PYTHONPATH=. \
TRTLLM_ENABLE_PDL=1 FLASHINFER_DIST_AWARE_AUTOTUNE=0 FLASHINFER_AUTOTUNER_LOAD_FROM_FILE=0 \
../.venv/bin/python ../scripts/finalize_geometry_experiment/probe_native.py \
  --repo . --output ../logs/finalize-geometry/divisor-native-r1.json \
  --tokens 8,128,1024,2048,8192,16384 --variants rounding,divisor,rounding
```

Use a new output path when repeating; overwrites are rejected. Shape and exact helpers are `probe_shapes.py` and `probe_retained.py`; the latter runs the18 selected prefill edge cases. `collect.py` performs CPU-only archiving and generated-code inspection.
