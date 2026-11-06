# DeepSeek MoE pure BF16 benchmark extension

## Scope

Extend upstream `benchmarks/bench_moe_deepseek.py` to compare pure TRT-LLM
BF16 MoE with CuTe DSL W4A16, CuTe DSL W4A4, and the existing TRT-LLM
NVFP4 baseline. The user selected this scope after the source audit found
that standalone CuTe DSL BF16 MoE requires Hopper; Blackwell's BF16
MegaMoE has a different execution and communication contract.

- Independent FlashInfer clone: `flashinfer/`.
- Upstream starting commit: `3a75b4e353ce113171c4d075fc2d3cb5b7dd6c08`.
- Prior benchmark contract: upstream PR #4048, captured in `artifacts/pr4048.json`.
- GPU target: C2 B300, eight GPUs reserved; single-GPU benchmark.
- Retain devbox `flashinfer-moe-bf16-0904` in `c2/ziangli` after completion.
  The user explicitly requested keeping it and its warm JIT caches for more
  performance benchmarks. Do not delete it during task cleanup.
- Image: `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2.1.
- Image selection checked against the live NVIDIA NGC catalog and release notes
  on 2026-09-04 (local date). Releases 26.06 and later moved to CUDA 13.3+.
- Project-local `hai/` is an independent clone used only as the required working
  directory for the managed `/usr/local/bin/h` CLI.

## Workload and comparison

Use PR #4048's isolated EP8 shape simulation: H=7168, I=2048, E=256,
32 local experts, top-k=8, eight routing groups/top-four groups, routing
scale=2.5, routing bias scale=0.01; tokens 1 through 4096 in powers of two.
This benchmark excludes inter-GPU communication. The initial activation
quantization is timed for W4A4; W4A16 and BF16 consume BF16 directly.
Weights are generated from the same fixed seed and quantized only for
the quantized backends. Weight preparation and autotuning are outside timing.

- Inference per-tensor: `Per-token activation: False`, no 4over6, FP4
  quantization fast math enabled, CuTe DSL fused finalize. Omitting
  `--use-per-token-activation` also enables the existing default CUTLASS arm.
- Inference per-token: per-token activation scaling, no 4over6, FP4 quantization fast
  math enabled; CuTe DSL fused finalize enabled.
- Deterministic RL configuration: per-token 4over6 MSE, E4M3 max 256,
  4over6 error fast math enabled, FP4 quantization fast math disabled;
  CuTe DSL two-stage finalize.
- TRT-LLM retains native separate finalize in both modes. The CuTe finalize
  flag does not change TRT-LLM, and a performance sweep alone does not prove
  full-model numerical parity or bitwise training determinism.
- Default logits routing keeps the DeepSeek routing rule in all backends.
  Native TRT-LLM route weights are BF16; CuTe route weights are FP32.
- CUDA graphs and CUPTI enabled, cold L2, 10 warmups and 100 iterations.

## Current source and validation

- Upstream PR: https://github.com/flashinfer-ai/flashinfer/pull/4985
- PR is ready for review; all nine raw tables, three configuration commands,
  and both W4A16 speedup columns are published in the body. Full validation
  output and helpers are linked in comments. The published body is verified
  against `pr-body-three-configs.md` and copied to `pr-body.md`.
- Performance source: `1ac2233d43df747af455ed4a8406d7439d686d9f`.
- Updated implementation: `2079fa00c4a2a0fb2e95bb284978a703653a4830`.
- `bench_trtllm` now shares BF16/NVFP4 setup and timing, inlines routing
  preparation, and explicitly rejects unsupported precision values.
  Display names are `TRTLLM NVFP4` / `TRTLLM BF16`; CLI selectors are
  `trtllm-nvfp4` / `trtllm-bf16` for both backend selection and profiling.
  Explicit backend selection also rejects an excluded profiler backend.
- Branch: `zianglih/bench-deepseek-moe-bf16` on `zianglih/flashinfer`.
- File-scoped pre-commit, Ruff and compilation checks pass.
- Existing BF16 reference/graph/EP-offset tests: 7 passed, 310 deselected.
- Project-local benchmark-helper checks: 8 numerical cases passed at
  `rtol=atol=0.03`, with exact eager repeats and CUDA-graph replays.
- Eight Nsight Systems traces and six Nsight Compute reports are retained;
  four NCU reports freeze normally tuned tactics and are the primary counter evidence.
- Refactor validation: 43 paired cases passed with exact kernel arguments,
  finalized outputs, timing inputs, eager repeats and graph replays; invalid
  precision rejection and the renamed CLI/profiling selectors also passed.
  Full evidence: https://github.com/flashinfer-ai/flashinfer/pull/4985#issuecomment-5549433238
- Original seven-test/eight-case validation is preserved in full at
  https://github.com/flashinfer-ai/flashinfer/pull/4985#issuecomment-5549485234
- Remote workspace: `/workspace/flashinfer-moe-bf16-benchmark`.
- Kernel caches: `/root/.cache/flashinfer` (preserve).
- The full run driver alternates inference/RL for three sweeps on GPU 0.
  Raw tables plus unrounded per-row JSON are in remote `artifacts/` and
  are copied to this project's `artifacts/`.
- `collect_env` records the initial editable-install metadata commit
  `e713467f`; the checkout used for helper validation and timing is `1ac2233d`.
  The intervening commit changes only the benchmark's routed-input sharing.

## Artifacts

Setup scripts, validation scripts, raw logs, result tables and PR-body drafts
remain at this project root. Only the requested benchmark extension belongs
in the upstream PR.

## Completed measurements

All nine runs completed successfully: three per-tensor inference sweeps with
five backends, three per-token inference sweeps with four backends, and three
RL sweeps with four backends. Every sweep contains 13 token counts.
The three-config report builder validates all 507 unrounded latency records
against the printed tables. The original six sweeps remain unchanged.

W4A16 speedup ranges (baseline median latency / W4A16 median latency):

| Configuration | Over TRTLLM NVFP4 | Over TRTLLM BF16 |
| --- | --- | --- |
| Inference per-tensor | 0.65–1.56x | 1.29–2.60x |
| Inference per-token | 0.87–1.66x | 1.28–2.60x |
| Deterministic RL | 0.91–1.73x | 1.34–2.61x |

Values above 1 mean W4A16 is faster; values below 1 mean it is slower.
Raw logs, unrounded JSON, run manifest and SHA-256 sums remain in `artifacts/`.

The three additional per-tensor inference sweeps completed through
`run_inference_per_tensor.py`, preserving the same measured commit and all
previous evidence. Their files use the separate `inference-per-tensor-` prefix
and `runs-inference-per-tensor.json` manifest. The default CUTLASS baseline
requires an additional JIT build; retain the new cache along with existing ones.

The final PR body was generated by `build_three_config_pr_body.py` after
all nine runs validated. It includes all three configurations, all nine raw tables,
and W4A16 speedups over both TRTLLM NVFP4 and BF16 (baseline median / W4A16 median).
Full test logs and helpers live in the linked comments to fit GitHub's body limit.
The remote checkout remained at the performance commit until all sweeps finished;
the reviewed source was validated from an exported file on GPU 1 during the
CUTLASS CPU build, with its bytes verified against the Git object.
It is now updated to the implementation commit for future benchmark runs.

Reuse the devbox with the managed CLI from `hai/`:

```bash
command -v h
/usr/local/bin/h ssh flashinfer-moe-bf16-0904 -c c2 -n ziangli
```

Do not delete this devbox or its caches: retained at the user's explicit request.

## Performance investigation and publication policy

Update PR #4985's body only. The user explicitly requested no further PR comments.
Historical validation comments remain linked; do not create more comments.

The naming-only commit is `d0caa842fe040a19f621bb0d9e0462bfe71402cb`.
Profiler-only commit `2079fa00c4a2a0fb2e95bb284978a703653a4830` adds the
`moe`/`l2_flush` NVTX ranges and an Nsight Systems example. It is independently
revertible. No kernel or normal timing logic changed. The benchmark helpers and
non-profile timing branch are AST-identical to the 43-case refactor source a3fce87d;
that historical GPU validation is not relabeled as having run at the later head.

- The original 18 raw log/capture files, both run manifests and three refactor
  validation logs retain their prior hashes. All 507 performance values remain
  unchanged. The body normalizes names/spacing and prints identical configuration
  headers once per three-run group, retaining all nine complete result tables.
- BF16 native tuning executed 2,852 successful profiles over 21 buckets. All ten
  measured API dispatches hit cached nonfallback tactics outside tuning mode.
  Three tuned/default pairs and every enumerated actual-input candidate were
  checked (352 at 32 tokens, eight at 4096, plus the default). The best actual
  candidate improves the 32-token result by only about 1%; the selected 4096
  candidate wins. This does not claim enumeration covers every compiled cubin.
- Eight Nsight Systems traces cover inference/RL, W4A16/TRTLLM BF16 and 32/4096
  tokens. All 160 graph replays and their GPU activities are independently
  accounted for. The roughly 68 us L2 flush is excluded. Kernel intervals overlap
  through PDL; device span is distinct from the sum of kernel durations.
- Twelve timer-control cases cover both modes/backends and 1/32/4096 tokens.
  Single-call, explicitly flushed CUDA graph events corroborate normal CUPTI.
  Event timing adds roughly 4–6 us while retaining the performance ordering.
- Primary NCU evidence freezes tactics observed in normal tuning, with nine node
  replay passes per GEMM. At 4096, BF16 FC1/FC2 reach 84.03%/86.17% DRAM throughput,
  40.83%/44.00% tensor-pipe activity and zero local load/store sectors. Registers
  (168/255) and shared memory limit residency, but high memory throughput means
  low occupancy alone does not prove an avoidable implementation defect.
- The 4096-input EP8 case has 3,715 local routes across 32 experts (~116/expert),
  with 40 tile128 token tiles/5,120 padded slots. Its ideal BF16 arithmetic
  intensity is ~108–116 FLOP/byte versus the advertised B300 dense roofline
  crossover ~281 FLOP/byte. Measured reads are 3.025 GB for BF16 versus 0.960 GB
  for W4A16. This supports a bandwidth explanation at 4096 as well as 32.
- The user conditionally authorized an upstream issue if the investigation
  establishes a concrete suboptimal implementation. No such defect was
  established: no missed fast enumerated tactic, spill traffic, timed setup or
  host-launch artifact. No issue was filed on the basis of this comparison alone.

`investigation-report.md` is built by `build_investigation_report.py`; the combined
body is built by `build_three_config_pr_body.py --investigation-report investigation-report.md`.
Full profiles, raw counters, tactic/caching checks and timers live in `artifacts/`.
Helpers include `run_nsys_investigation.py`, `analyze_nsys_investigation.py`,
`verify_nsys_investigation.py`, `audit_bf16_autotuning.py`, `timed_control.py`,
`run_ncu_investigation.py`, `run_ncu_fixed_investigation.py` and
`fixed_tactic_benchmark.py`. The public CLI cache workflow was smoke-tested in
fresh processes: the second run logged a target cache hit, did not retune,
preserved the cache hash and exited zero.
