# Geomean Speedups

Speedup = pre-FP16-refactor CUDA no-fast baseline time / PR-head time, geomean over 330 scanned M/K cases.

| Activation scale | Baseline CUDA no-fast geomean (ms) | CUDA no-fast | CUDA fast | CuTe DSL no-fast | CuTe DSL fast |
| --- | ---: | ---: | ---: | ---: | ---: |
| Per-tensor | 0.074336 | 1.000x | 1.668x | 1.434x | 1.738x |
| Per-token | 0.065345 | 0.974x | 1.554x | 2.297x | 3.267x |
