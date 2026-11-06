# Megatron NVFP4 fused QDQ

Durable workspace for the standalone fused CuTe DSL NVFP4 fake-QAT follow-up to
[`radixark/Megatron-LM#75`](https://github.com/radixark/Megatron-LM/pull/75).

- `Megatron-LM/`: independent clone; local branch `nvfp4-qdq-cute`, pushed to
  `fork/agent/nvfp4-qdq-cute`
- `flashinfer/`: upstream reference at `ff22228d2fa144e9ac6a0d841f2e9ba767ba0f0a`
- `TransformerEngine/`: upstream reference at `ea1a165decdd09c1ef98b273d965796c89c47473`
- `hai/`: project-local HAI checkout used with the macOS-managed `/usr/local/bin/h`
- `PR_BODY.md`: self-contained draft PR body and rolling performance history
- `artifacts/`: retained full test, benchmark, grid-sweep, and profiling logs

Current head `3408ef861840d4920368d42c8fa253f26755819c` uses a contiguous rank-2
`[M,N]` kernel API and TE's default independently stored grouped-linear weights.
The wrapper mirrors INT4 QAT with one
`fake_nvfp4_quantization_ste(w, config)` call per weight. It does not use TE's
experimental single-grouped-parameter layout; the earlier packed `[G,M,N]`
prototype and its profiling artifacts are retained only as discarded history.
The head is a test-only follow-up to runtime commit `57b52f735`: its real TE 2.17
wrapper test locks the discrete parameter registry and verifies exact fused
FP32 `main_grad` accumulation.

Final target evidence at the pushed head:

- strict tests: `938 passed, 1 skipped`; the skipped two-device case passes
  separately;
- performance proxy: eight independent `[4096,6144]` Parameters, logical
  8x `6144x4096`, BF16 then FP16 sequentially on B300;
- geomean: 1.606x versus the complete eight-weight naive TE QDQ loop
  (1.608x BF16, 1.605x FP16);
- current full test logs: `ec7b9c34...` (938 passed, 1 skipped) and
  `9b4cd7a9...` (the skipped two-device case passes separately);
- draft PR: <https://github.com/radixark/Megatron-LM/pull/87>.

The PR currently conflicts with `miles-main` after that base branch was
force-updated from `2e64d788b` to `235952df6`; resolving the parent #75 stack
against the rewritten base is intentionally left as separate follow-up work.

Validation devbox: `nvfp4-qdq-discrete`, C2 `ziangli`, 8x B300, bare image
`radixark/miles:dev-202608241212`
(`sha256:c60775b5b11e6aac47c1f076fbef7a29506de3442ac8bbfef1efeef29e1c90b2`).
The devbox is intentionally retained.
