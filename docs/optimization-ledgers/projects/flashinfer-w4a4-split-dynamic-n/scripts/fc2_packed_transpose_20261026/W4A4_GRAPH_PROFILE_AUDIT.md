# W4A4 CUDA-graph profiling: read-only audit

The public API currently permits `autotune_use_cuda_graph=True` for standard and per-token W4A4. Only W4A16 has an explicit rejection. The wrapper forwards this flag to both W4A4 runners, and the runner passes it to `TuningConfig.use_cuda_graph`. Its hash and cache extras distinguish graph profiling (`"cuda_graph"`), so existing eager-profiled winners must not be relabeled or reused as graph-profiled results.

Source references in the frozen7f4/R4 copy:

- `flashinfer/fused_moe/cute_dsl/fused_moe.py:1054`: documented profiling control, distinct from wrapper stream/event resource control.
- `fused_moe.py:1083`: only W4A16 rejects the flag.
- `fused_moe.py:1140` and `:1160`: standard/per-token runner forwarding.
- `flashinfer/fused_moe/cute_dsl/tuner.py:685`: cold-L2 config plus graph flag.
- `tuner.py:720` and `:748`: hash and cache separation.
- `benchmarks/bench_moe_deepseek.py:747` and `:791`: benchmark explicitly forces False for NV while forwarding graph mode for MX.

Git blame traces the explicit benchmark branch to squashed `65c2c5c4`. The retained local planning documents explain its purpose: preserve prior NV tuning defaults while moving the already graph-profiled MX assembly onto the public wrapper/function. See project-root `PUBLIC_API_FINAL_BENCHMARK_PLAN_2026-10-25.md:22-29` and `scripts/public_mxfp_moe_experiment/README.md:10`.

Upstream commit `35821bcb` (Rubin locality support) introduced the runner's optional `use_cuda_graph=False`, forwards it to TuningConfig and adds the cache-key distinction. The inspected history does not identify a current Blackwell W4A4 failure requiring False. The benchmark's older comment about illegal access when prewarm/autotuning runs on a non-default stream explains why tuning happens before timed graph capture; it does not document a ban on the autotuner's own internal graph profiling.

Current exact public-chain gates exercise W4A4 CUDA graphs, but do not establish that every native graph-profiling tactic succeeds. The existing explicit MX API test asserts that the flag is wired, but uses an explicit tactic rather than profiling the full list. A bounded native graph-profile diagnostic is therefore the appropriate runtime boundary before changing benchmark policy. No production source, benchmark policy, or routing-profile contract was modified in this audit, and no extra GPU run was launched.
