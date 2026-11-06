# Fixed channel-tiling screen

Prepared only; parent owns launch after the exact gate. Stage the entire `fixed-screen/` directory without regenerating its frozen plan.

Runs the source-native functional public benchmark on the channel candidate for every arm. NV includes the initial quantizer; MX inputs remain prequantized. Existing 10 warmups / 100 cold-L2 CUPTI CUDA-graph samples and unfused finalize are unchanged. No AUTO search runs.

Each case uses Native → Matched → FC1 → Both → Both → FC1 → Matched → Native. K3 MX omits the duplicate Matched controls. Native denotes the previously selected 0b7 winner run on the candidate source, not a fresh AUTO result.

| Case | Native tactic | Matched changes | Unique blockscaled phases |
|---|---|---|---:|
| v3-nvfp4 | `[256, [[256, 256], [2, 1], False], [[256, 256], [2, 1], False], [4, 4], False]` | `[{'field': '0', 'before': 256, 'after': 128}, {'field': '1', 'before': [[256, 256], [2, 1], False], 'after': [[256, 128], [2, 1], False]}, {'field': '2', 'before': [[256, 256], [2, 1], False], 'after': [[256, 128], [2, 1], False]}]` | 6 |
| v3-mxfp | `[256, [[256, 256], [2, 1], False], [[256, 256], [2, 1], False], [4, 4], False]` | `[{'field': '0', 'before': 256, 'after': 128}, {'field': '1', 'before': [[256, 256], [2, 1], False], 'after': [[256, 128], [2, 1], False]}, {'field': '2', 'before': [[256, 256], [2, 1], False], 'after': [[256, 128], [2, 1], False]}]` | 6 |
| kimi-k3-nvfp4 | `[128, [[128, 128], [1, 1], False], [[256, 128], [2, 1], False], [8, 4], False]` | `[{'field': '1', 'before': [[128, 128], [1, 1], False], 'after': [[256, 128], [2, 1], False]}, {'field': '3', 'before': [8, 4], 'after': [4, 4]}]` | 5 |
| kimi-k3-mxfp | `[128, [[256, 128], [2, 1], False], [[256, 128], [2, 1], False], [4, 4], False]` | `[]` | 4 |

Matched uses shared N128, both phase M256/group2/K4; FC1 changes only its group to1; Both additionally changes FC2 group to1. Every arm preserves the native raster and CLC flag. The V3 native N256 comparisons therefore include routing retiling, and K3 NV native comparisons also include FC1 M/K changes. Matched-versus-FC1/Both isolates the corresponding CTA/channel geometry changes.

Only one selected backend is measured per process. The derived observer differs from the frozen ROUND observer only in its exact row-count assertion and descriptive boundary; timer and dispatch-observation ASTs are identical. Each MX experimental tactic is registered only in that process. Production candidate lists are unchanged. Missed caches, unexpected dispatches, source drift, route mismatch or altered caches fail the screen.

Upper bound:21 distinct blockscaled phase configurations, plus existing prepare/quantizer/combine specializations. Already compiled kernels may be reused from the source-private cache. This is not a guaranteed compile count or wall-time estimate.

The source-bound 8,640-case old-geometry CPU equivalence proof justifies a same-source fixed-geometry diagnostic. It does not replace a later fresh cross-source retention pair.

Command after staging:
```bash
/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/control-0def601d/.venv/bin/python /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/old-cute-comparison-20261027/channel-tiling/fixed-screen/run_fixed_screen.py --deployment /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/old-cute-comparison-20261027/sources/channel-tiling-d75af95cf1b4/deployment.json --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/old-cute-comparison-20261027/channel-tiling/perf-fixed-r1 --gpu 5
```

Use `--case v3-nvfp4` (or the other case IDs above) with a separate fresh output directory to split execution. The runner does not acquire GPU ownership; parent coordinates reservations. No launch was made during preparation.
