# Curated W4A16 autotune and comparison plan

Use the existing shim autotuner and extended distributed benchmark. The initial four-shape N64 baselines did not establish a universal M preference, and both N64 geometries regressed at T4096 against the adjacent M256/N128 control. The third decoded-stage experiments test that limitation before the broader curated sweep. Every future candidate keeps **two dequantization warp groups**.

## Complete current stage gates

Preserve the existing two-stage results. Finish the current N64 third-stage numerical, codegen and four-shape CUPTI comparisons for M256 and M128. Check actual fitted raw depth, decoded stages, dynamic shared allocation, CTA register pool and source-correlated local operations. The N64 third-stage rule uses unused TMEM columns without increasing the allocated 512 columns or group count; its benefit requires measured evidence.

Freeze the validated derived-stage policy for the auto experiment. Stage counts remain internal to the established resource fitters. Keep the benchmark version identical across fresh candidate/control runs and preserve the older benchmark hash distinction. If a stage result is near observed variation, repeat its adjacent matching control.

## Existing representation, 12 candidates

The approved search uses ordinary knob dictionaries from `w4a16_candidates()`:

| Axis | Values |
| --- | --- |
| `(M,N,K)` | `(256,128,256)`, `(256,64,256)`, `(128,64,256)` |
| Flag batch | 4, 8 |
| Token return | `epi_warps`, `reuse_dispatch_warps` |

Fix cluster `(2,1,1)`, group hint 512, atomic scheduling, epilogue flag batch `(2,4)`, two dequantization warp groups, and external post-FC2 reduction. Derive one/two-CTA instructions from M128/M256 and pipeline depths from the current fitter. Keep precision, routing weights, global alphas and clamps fixed. Exclude M128/N128 until its numerical/resource gate, and exclude unsupported N256, standalone return and in-kernel reduction. This extends the current curated shim lifecycle rather than searching every configuration field.

## Collective setup and final measurement

After merged host/CPU checks, run a bounded EP8 auto bringup with prevalidated candidates and identical candidate order on every rank. Tuning occurs in eager warmup before capture. Retain the complete rank-0 ranking and each rank's `MEGAMOE_TACTIC_JSON`, including global/live/capacity tokens. Preserve the external runner timeout. The generic tuner assumes deterministic all-rank candidate failures and provides neither a numerical oracle nor asymmetric-fault/GPU-hang recovery.

Use `--megamoe-knobs auto` and an effort-specific `FLASHINFER_MOE_EP_KNOB_CACHE`. Online ranking is MAX of per-rank median synchronized host-forward time; it is setup evidence. Final latency uses the unchanged CUPTI graph benchmark: 100 iterations, three warmups, cold L2, median of per-iteration MAX rank GPU span. Keep these metrics separate.

Run all 13 global token counts, powers of two from 1 through 4096, with identical canonical weights/routes and split-finalization contract. Capture fresh split tactics and actual Mega winners at each shape/rank. Repeat close finalists with adjacent explicit-knob CUPTI runs before claiming a selector/default advantage. Preserve all regressions and same-run split rows. No new one-group arms are permitted.

The cache keys capacity: EP8 global 1/2/4/8 all map to capacity 1, so later tuning can overwrite that entry. Preserve per-invocation winner records and use fresh cache files across source/input scenarios. Do not imply that one cached capacity winner is optimal for every live-rank distribution.

## Launch recipe after merge and GPU handoff

Root selects frozen source and owns the GPU slot. This uses the existing effort runner; the adapter/backend must be merged and validated first.

```bash
cd /workspace/flashinfer-w4a16-megamoe
autotune_run='tmem-autotune-<fresh-name>'
export FLASHINFER_BENCHMARK_ENTRYPOINT="$PWD/capture_benchmark_tactics.py"
export FLASHINFER_TACTIC_CAPTURE_DIR="$PWD/logs/$autotune_run/tactics"
export FLASHINFER_BENCHMARK_SOURCE_SHA='<actual frozen source/overlay label>'
export FLASHINFER_MOE_EP_KNOB_CACHE="$PWD/logs/$autotune_run/knob-cache.json"
bash run_benchmark_ep8.sh "$autotune_run" 1,2,4,8,16,32,64,128,256,512,1024,2048,4096 100 cupti --megamoe-knobs auto
```

A full13 paired run yields 26 raw latency rows, 104 actual split tactics and 104 rank/shape Mega winner records. Save explicit required-source/test manifests, input hashes, environment/compiler versions and online rankings. Historical manifest omissions remain disclosed rather than backfilled.
