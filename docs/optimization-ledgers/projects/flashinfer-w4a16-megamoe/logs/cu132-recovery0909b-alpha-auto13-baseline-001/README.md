# Fresh 0909b alpha Mega-only AUTO baseline

All original saved validators pass for published alpha `2e8dc30` / source `487b6260`: 13 rows, 104 rank-confirmed choices and compiled objects, 13 complete catalog16 rankings, and 1,300 samples. Every compiled object is REG96 / 640 threads / two decode groups / pool61440 / local0.

| Global tokens | Mega ms | Actual selected tactic |
|---:|---:|---|
| 1 | 0.093617 | M128/N64, C1, F4, epi |
| 2 | 0.120785 | M256/N64, C2, F4, epi |
| 4 | 0.131585 | M128/N64, C2, F8, epi |
| 8 | 0.154864 | M256/N64, C2, F4, epi |
| 16 | 0.158690 | M256/N64, C2, F4, epi |
| 32 | 0.205185 | M256/N64, C2, F4, epi |
| 64 | 0.227841 | M256/N64, C2, F8, epi |
| 128 | 0.235425 | M256/N64, C2, F8, epi |
| 256 | 0.230385 | M256/N64, C2, F4, epi |
| 512 | 0.235474 | M256/N64, C2, F4, epi |
| 1024 | 0.285155 | M256/N64, C2, F8, epi |
| 2048 | 0.347970 | M256/N128, C2, F4, reuse |
| 4096 | 0.499300 | M256/N128, C2, F4, reuse |

Image: `nvcr.io/nvidia/pytorch:26.05-py3`; node `hu-pdx-115`, fresh0909b container. Primary metric: median of 100 per-iteration maximum-rank cold-L2 graph-CUPTI samples, 3 warmups. AUTO selection uses hot staged-wrapper/reducer events, a distinct scope. Process wall 899.177618708s; timing utility 5.848272062s. This is the new same-phase Mega-only baseline; no split rows or historical paired/fixed substitution.

Original70476, full fetch62062 and canonical idle52358 closed successfully. Native inventory grows12→22 entries with ten dsv3_fused_routing build files and the included JIT log change; no removals. The compact [accepted receipt](accepted-baseline.json) retains every row, actual104 winners and 74 direct file hashes. Saved numerical association is reused without rerunning the four gates or older suites. No source promotion or PR change follows from this baseline alone.
