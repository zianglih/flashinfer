# FlashInfer SM100 MoE cache effort

Local workspace for the SM100 W4A4/W4A16 CuTe DSL persistent-cache
investigation and closed draft PR
[flashinfer-ai/flashinfer#4424](https://github.com/flashinfer-ai/flashinfer/pull/4424).

## Layout

- `flashinfer/`: independent Git clone on
  `agent/sm100-moe-cute-dsl-disk-cache` at tested commit
  `896bcd69c73d2e7fd1603550aa80893029514c48`.
- `.codex/sm100_moe_cache_benchmark.py`: reusable cold/warm benchmark harness.
- `.codex/sm100_moe_cache_benchmark_final.txt`: complete B200 benchmark output.
- `.codex/sm100_moe_cache_validation_workflow.md`: pinned-image devbox and
  validation runbook.
- `.codex/pr-body.md`: final draft PR evidence before closure.

The PR was closed because the measured fresh-process end-to-end gain did not
justify the additional cache, ABI, and maintenance complexity. The harness and
evidence are retained for future startup-profile investigations.
