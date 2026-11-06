**C3 rebase validation — `2b473279`: 98 passed executions / 94 unique cases; zero failures, errors or skips.** This covers all four swap-AB quantization modes, exact ClampedRelu2 with non-power-of-two limits and CUDA-graph limit updates, existing SiTU/GeGLU/ReLU², both W4A16 layouts, legacy MX paths, wrapper graphs, PDL forwarding and cache keys. A same-process sequence also passed: clamp → ReLU² → SiTU → clamp. Swap-AB/W4A16 numerical checks retain zero tolerance; legacy checks retain their existing tolerances.

- **Environment:** 8×B300 on C3; `nvcr.io/nvidia/pytorch:26.05-py3`; driver 595.91.07; CUDA 13.2 / NVCC 13.2.78; PyTorch `2.12.0a0+5aff3928d8.nv26.05`; CuTe DSL 4.8.0 (embedded compiler reports CUDA 13.4); pytest 8.4.2. Native compilation caches remain on persistent storage.
- **Broader rebase check:** `95a99823` passed 224 executions / 220 unique cases, including K tails, tactic legality and W4A16 routing boundaries. The final-head run above specifically rechecks the subsequent activation-state/interface cleanup. All 34,759 tracked source files passed postflight hash checks for both epochs.
- **Boundary:** no new benchmark or sanitizer run; existing performance figures remain attributed to their original measured revisions.

Final-head pytest output by group:

```text
clamped-activation
32 passed, 827 deselected, 691 warnings in 40.77s
swap-exact
16 passed, 4 deselected, 633 warnings in 44.27s
activations-exact
18 passed, 944 warnings in 61.27s (0:01:01)
w4-layouts
4 passed, 232 warnings in 10.74s
mx-legacy-and-swap
12 passed, 10 deselected, 834 warnings in 16.60s
wrapper-graphs
8 passed, 40 deselected, 752 warnings in 31.72s
pdl-and-cache-keys
4 passed, 20 warnings in 1.23s
activation-state-sequence
4 passed, 158 warnings in 34.92s
```

Main activation check (existing suites):

```bash
export FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1
export FLASHINFER_DIST_AWARE_AUTOTUNE=0
python -m pytest -q --disable-warnings \
  tests/moe/test_cute_dsl_fused_moe.py tests/moe/test_cute_dsl_mxfp8_moe.py \
  -k 'clamped_relu2 or clamped-relu2'
```
