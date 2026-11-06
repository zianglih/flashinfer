# FC1 regular-TMA six-warp experiment

CPU preparation only; no CUDA compilation, GPU correctness or timing yet. Wait
for the current 98fd profile and parent release before GPU work.

Actual source lives in the independent `../../flashinfer-fc1-tma-roles-review`
clone, based on `98fd3566b5f945c100f48cddacf25deb2432cbc2`. Exactly one tracked
core file is modified, unstaged. No overlays, production changes or API changes.
`manifest.json` pins baseline and candidate source plus the complete patch.

## Scope and prior evidence

Compact only FC1 with `tma_sfb` and `overlap_epilogue`: regular payload and SF
TMA at N128/N256, currently the homogeneous two-CTA geometries (including logical
M512/N128). Small-N SF cp.async, one-CTA inline FC1, mixed-format inline FC1, and
all FC2 configurations keep their existing role mapping. No tactics, stages,
layouts, arithmetic, alignment, cache policy or preparation changes.

The prior [FC2 six-warp experiment](../fc2_roles_experiment/README.md) was exact
but neutral/inconsistently slower and remains rejected. This FC1 experiment is
distinct because retained regular-TMA FC1 no longer requires its old four-warp
Gather4/SF producer. Nevertheless, fewer launched warps are not evidence of a
speedup; large tiles remain constrained by shared memory.

## Role and ownership audit

| Role | Retained overlap kernel | Compact FC1 |
|---|---|---|
| Epilogue | Physical warps4–7 | Physical warps0–3 |
| TMA issue | Warp0 within producer warps0–3 | Warp4 |
| MMA | Warp8 | Warp5 |
| CTA threads | 288 | 192 |

The epilogue occupies a complete physical warpgroup; software thread indices
become0–127 without changing physical TMEM lane ownership. TMA-producing guards
(acquire/A/SFA/B, SFB, and producer tail) all move together. The single-thread
TMA producer group and transaction-byte accounting stay unchanged.

TMEM allocator warp0 is now an epilogue warp. Allocation/retrieval happen before
role dispatch; the allocator's warp restriction stays untouched. Whole-CTA
retrieve/teardown barriers3/1 inherit192 threads. The first128-thread teardown
cohort, barrier2, epilogue transpose barrier6, accumulator consumer count128 per
CTA, and two-CTA deallocation protocol remain unchanged. The complete MMA branch,
TMEM release/ownership calculations, stage lifecycle and PDL tail are byte-identical.
No `setmaxnreg` is introduced.

`check_source.py` reverses the declared changes to exact baseline bytes/AST,
checks only one unstaged file, verifies independent Git metadata and unchanged
MMA/teardown/marker regions, and enumerates all eight combinations of phase,
TMA-SFB and overlap selection. Every compact case has four physical epilogue
warps, one producer and one MMA warp. This is structural evidence only.

```bash
python3 scripts/fc1_tma_roles_experiment/check_source.py
```

Future bounded GPU validation must use this actual source copy, preserve native
cache/data resolution, and inspect emitted resources as well as exact bytes/SF.
Use actual-routing captured FC1 NV8K/16K and MX16K, saved native AUTO geometry,
and unchanged 10/100 cold-L2 CUDA-graph CUPTI ABA/BAB timing. No primary baseline
rerun or FC2 timing axis is part of this proposal.

## Result: not retained

Completed bounded native NVFP4 FC1 wrapper comparisons on GPU3 with actual
saved AUTO geometries. Output and SF bytes match before and after all12 arms;
all1200 cold-L2 graph/CUPTI samples are preserved. Preparation is included.

| Tokens / route N | Control / compact / control, µs | Compact / control / compact, µs | Geometric control/compact |
|---|---|---|---:|
|8192 /128|148.8165 /148.9765 /149.792|149.328 /148.9765 /149.793|0.998855×|
|16384 /256|220.4485 /220.065 /220.5285|220.080 /220.385 /220.512|1.001068×|

Neither case shows a meaningful repeatable improvement. No MX extension,
full-chain timing, primary campaign or integration. GPU3 is released. Source
remains unstaged. Archive `../../evidence/fc1-tma-roles-98fd/raw.tar.gz`, SHA256
`cb0ec1e10dd23bdc9780530693562474f61a10403bf0dfafb57f0978374ad5e0`.
The local archive verifies every median against its100 samples.

No PTX/CUBIN files were found at the requested environment dump path for these
processes. We therefore make no emitted register, occupancy or SASS claim. The
source role mapping is CPU-checked and the actual-source native comparisons
are exact; those boundaries should remain distinct. Further codegen work is
not warranted by the negligible timing delta.
