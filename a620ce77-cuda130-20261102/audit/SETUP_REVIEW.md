Independent setup review — 2026-11-02

Static review passes for paired smoke, followed by the full 104-cell campaign
if the runtime qualification passes. This is a benchmark-only experiment; no
kernel optimization or source math change is included.

- Before is `002529e17b22567a071091053c6c4dc2a55e050e`, with the exact published
  old-workload benchmark adapter SHA256
  `8078d09b8be9c5a992d8904ffc59fbcdb28fd2e34324a69e4fe250ed79477eab`.
  After is retained `a620ce7790b32f7f0ae524a811417d2c6cee1152`.
- Both source archive hashes match their manifests. `flashinfer/testing/utils.py`
  is byte-identical across the source arms. Runtime verifies all tracked files
  at setup, and dispatch/JIT/kernel Python sources before and after each phase.
- Both use BF16 activations and NVFP4 weights, functional API, unfused finalize.
  Gated FC1 weights use the old 64-row layout before and the swap-AB 16-row
  layout after. Non-gated N3U has no gate/up row interleaving.
- Model configuration ASTs match exactly. All historical 104 pairs have equal
  route identities, and each arm's repeat has stable frozen choices. The fresh
  CUDA13.0 environment must independently produce equal cross-arm routes;
  historical routing agreement is diagnostic, because Torch differs.
- Native/managed autotune entries preserve each arm's published choices. Only
  environment metadata is rebound for the fresh runtime; profiling is forbidden.
  The current arm has 10 cached `-1` defaults, not cache misses. Their actual
  FC1/FC2 resolution remains recorded by the after observer.
- Four phases are before/after/after/before on the same GPU per job, with
  10 warmups and 100 strict CUPTI samples per phase, CUDA graphs and cold L2.
  Event fallback is trapped, including fallback without warning. No tactic
  search is admitted; cache identities and immutability are checked per phase.
- The 104 cases comprise four models, EP and TP, and 13 token counts. Tokens
  1 and 2 stay in raw evidence and are excluded from the 88 retention rows.
  The full campaign must contain 41,600 raw end-to-end samples.
- Both arms use the same C3 image `nvcr.io/nvidia/pytorch:25.11-py3`, native
  Torch `2.10.0a0+b558c986e8.nv25.11`, CUDA toolkit/nvcc `13.0.88`, and shared
  CuTe DSL 4.8. CuTe embeds NVVM 13.4.59; this is explicitly distinct from the
  system toolkit and Torch CUDA 13.0. No CUDA13.2 compilation cache is imported.
- Compiler/source-bound caches are private to this new campaign and persistent
  on C3 storage. Timing includes the full MoE chain and excludes weight setup.
  The initial quantization flag does not time a quantizer for W4A16 BF16 input.

Audit artifacts:

- `audit_historical.py` and `historical-inputs.json`: independently verified
  historical workloads, source/result hashes, routes, per-arm choices and
  after resolved configurations for all 104 cells.
- `analyze_cuda130.py`: replays raw CUPTI launch/activity spans, verifies each
  median and repeat, route identities and frozen choices, preserves telemetry,
  and derives only fresh CUDA13.0 before/after tables. It does not publish or
  mutate the source/evidence inputs.

Remaining runtime boundary: smoke and complete fresh evidence were not yet
available when this static review was issued. Reported performance requires
the raw replay audit, completed receipts, source/cache binding, and clock data.
