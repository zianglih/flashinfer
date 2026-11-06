# Composed gather experiment: complete EP/TP validation

This local campaign measures the control-warp register budget change (80 → 112)
and universal weight-scale copy ordering together. The candidate is the unstaged
kernel in `flashinfer-fc1-gather-composed-review`; both arms start from
`fb66a27e6b40bdbbefd1b8bf0c0fc3f3ada8af90`. This comparison is against the clean
gather experiment, not upstream PR #7290's retained `d35fcfda` head.

- Candidate kernel SHA256:
  `0d44e4d71465b29a565995febdad42ef168060d1ae2858df5b2611ca998f70ee`.
- Control kernel SHA256:
  `d6324703ae6dc905160d100e8b1e30445a7affa64c9b7d6083fcd33a88e2d3fd`.
- Patch SHA256:
  `37d5ef817e11ca2e4214bc9c65e241b4c8bf2e9d892261151ed6757c98330ed5`.
- C3 B300, `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2, GPUs 4/6/7.
- Runtime donation policy: control 112, gather 128, epilogue 256 registers.
  The guard checks loaded cubin limits before launch without changing compiler
  options. It reports local memory; it does not claim every warp is spill-free.

## Fixed-tactic comparison

Fifteen jobs cover V3 EP8/TP8, V41F EP4/TP4, K3 EP8/TP8, and N3U EP8/TP8.
Tokens are `1,2,4,8,16,32,64,128,256,512,4096,8192,16384`. V41F TP MX modes and
K3 MXFP8 remain unsupported. Every job runs same-GPU C-A-A-C with 100 strict-CUPTI
samples per phase, cold L2, frozen routing and original frozen tactics, no
autotune traversal, unfused swap-AB output, and input quantization included for
the NVFP4 family. This is 468 raw cells and 187,200 timed samples.

The plotted 396 cells omit tokens 1–2. Aggregates also exclude unchanged W4A16,
leaving 308 affected cells. Decode means tokens 4–64, middle means 128–512, and
prefill means 4096–16384. Speedup is `100 * (control / candidate - 1)` using the
geometric mean of each arm's two phase medians.

The campaign requires all seven existing exact tests plus eight local M512
checks (four formats × CLC on/off) to pass before benchmarking. The local checks
are experiment helpers, not repository test additions. No sanitizer is run.

## Separate native-tactic follow-up

The planned twelve-cell native-tactic follow-up was paused before launching any
measurement, at the parent's request. It is deferred until the next metadata
candidate is evaluated and composed. The prepared helpers and previously tuned
native caches remain available. Future candidate-only passes will reuse the
same GPU and full-campaign controls; their report must distinguish source and
tactic-selection effects from the fixed-tactic comparison.

## Reproduce local analysis

From the project root, after the evidence archive has been extracted. The
retuned analysis commands apply only if that deferred follow-up is later run:

```sh
python3 fc1-gather-20261028/optimization-next-20261029/composed/full-validation/analyze_perf.py \
  fc1-gather-20261028/optimization-next-20261029/composed/full-validation/evidence/perf \
  --output fc1-gather-20261028/optimization-next-20261029/composed/full-validation/report
python3 fc1-gather-20261028/optimization-next-20261029/composed/full-validation/analyze_retuned.py \
  fc1-gather-20261028/optimization-next-20261029/composed/full-validation/evidence \
  --fixed-report fc1-gather-20261028/optimization-next-20261029/composed/full-validation/report \
  --output fc1-gather-20261028/optimization-next-20261029/composed/full-validation/optimized/report
fc1-gather-20261028/plot-venv/bin/python \
  fc1-gather-20261028/optimization-next-20261029/composed/full-validation/plot_heatmap.py \
  fc1-gather-20261028/optimization-next-20261029/composed/full-validation
fc1-gather-20261028/plot-venv/bin/python \
  fc1-gather-20261028/optimization-next-20261029/composed/full-validation/plot_optimized_heatmap.py \
  fc1-gather-20261028/optimization-next-20261029/composed/full-validation/optimized
```
