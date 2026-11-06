# Fixed-N and dynamic-N TMEM comparison

EP8 B300, H7168/I2048/E256/top8. Same-run split W4A16 uses the same packed
weights. 100 CUPTI iterations, rank-MAX spans then median, cold L2, graphs.
Preparation, compilation, tuning, capture, and L2 flush are excluded.

| Global tokens | Fixed-run split ms | Fixed Mega ms | Dynamic-run split ms | Dynamic Mega ms | Mega change |
|---:|---:|---:|---:|---:|---:|
| 1 | 0.068002 | 0.111233 | 0.089297 | 0.114145 | +2.62% |
| 8 | 0.161280 | 0.304322 | 0.161008 | 0.302516 | -0.59% |
| 32 | 0.203074 | 0.411557 | 0.196082 | 0.409203 | -0.57% |
| 128 | 0.235889 | 0.479267 | 0.233681 | 0.469539 | -2.03% |
| 4096 | 0.551635 | 0.724197 | 0.553395 | 0.712356 | -1.64% |

Both candidates trail split. The small fixed/dynamic differences do not
establish a material performance gain. The global token count 1 split control changed
from 0.068002 to 0.089297 ms (+31.32%); its fixed-run winner was not recorded,
so that change cannot be attributed to the Mega architecture.

## Actual tactics from the dynamic run

Tuple format is `(M,N,K), cluster, raster_along_m`; the final boolean is
the raster flag. M128 uses one-CTA MMA even with cluster (2, 1); M256 uses
two-CTA MMA. All observed tactics use cluster (2, 1) and raster=True.

| Global tokens | FC1 tile | FC2 tile | Ranks selecting it |
|---:|---|---|---|
| 1 | (128, 8, 256) | (128, 8, 256) | [0] |
| 1 | (128, 16, 256) | (128, 16, 256) | [1, 2, 4, 5, 7] |
| 1 | (128, 16, 256) | (256, 16, 256) | [3, 6] |
| 8 | (128, 8, 256) | (128, 8, 256) | [0] |
| 8 | (128, 16, 256) | (128, 16, 256) | [1, 2, 4, 5, 7] |
| 8 | (128, 16, 256) | (256, 16, 256) | [3, 6] |
| 32 | (128, 8, 256) | (128, 8, 256) | [0, 3] |
| 32 | (128, 16, 256) | (128, 16, 256) | [1, 2, 7] |
| 32 | (128, 16, 256) | (256, 16, 256) | [4, 6] |
| 32 | (256, 16, 256) | (128, 16, 256) | [5] |
| 128 | (128, 8, 256) | (128, 8, 256) | [4, 5] |
| 128 | (128, 16, 256) | (128, 16, 256) | [0, 1, 2, 6, 7] |
| 128 | (256, 16, 256) | (128, 16, 256) | [3] |
| 4096 | (256, 128, 256) | (256, 128, 256) | [0, 1, 3, 4, 5, 6] |
| 4096 | (256, 192, 256) | (256, 192, 256) | [2, 7] |

The fixed-run recorder missed the CuteDslRunner wrapper and wrote zero
records on every rank. Dynamic records must not be presented as fixed
winners. All 40 dynamic selections and actual input shapes are preserved
in `comparison.json` and the raw per-rank tactic files.

## Numerical boundary

All 12 EP1/EP2 tests passed with unchanged tolerances. The fresh EP8 global8
diagnostic found 458,752/458,752 per-route FC2 values bitwise identical to
split; Mega's final all-route oracle had zero mismatches. The three final
Mega/split differences reproduce split's BF16 rank-partial rounding.
All raw diagnostics, including the split oracle's six mismatches, remain
in `comparison.json` and `logs/diagnostic-swap-global8/comparisons.json`.
The diagnostic deliberately exits after saving; its durations are excluded.

## Evidence

- `logs/swap-tmem-fixedn-paired-002.{log,provenance.log}`
- `logs/swap-tmem-dynamicn-paired-001.{log,provenance.log}`
- `logs/swap-tmem-dynamicn-paired-001/tactics/rank*.json`
- `controls/fixed_n_timed_002/manifest.json`
- `controls/dynamic_n_validated_001/manifest.json`
- `CODEGEN.md`: fixed-N direct-TMEM proof and FC2 local-array attribution

Paths beginning `logs/` are relative to the effort root. Rebuild this
report with `python3 candidates/w4a16_swap/build_comparison_report.py`.
