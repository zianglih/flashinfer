# CLC before versus loop-rotation whole invocation

| Tokens | Before ms | Loop ms | Change | Before tactic | Loop tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.157281 | 0.160994 | +2.361% | N64/F4/epi | N128/F4/epi |
| 2 | 0.279458 | 0.280483 | +0.367% | N128/F8/epi | N128/F8/epi |
| 4 | 0.429859 | 0.431571 | +0.398% | N128/F4/epi | N128/F8/epi |
| 8 | 0.602326 | 0.584901 | -2.893% | N128/F8/epi | N128/F4/epi |
| 16 | 0.715973 | 0.714055 | -0.268% | N64/F8/epi | N64/F8/epi |
| 32 | 0.909385 | 0.905479 | -0.430% | N64/F8/epi | N64/F4/epi |
| 64 | 1.064458 | 1.073177 | +0.819% | N128/F4/epi | N128/F4/epi |
| 128 | 1.100475 | 1.105851 | +0.489% | N64/F4/reuse | N64/F4/reuse |
| 256 | 1.110937 | 1.110124 | -0.073% | N64/F4/epi | N64/F4/epi |
| 512 | 1.121626 | 1.111834 | -0.873% | N128/F8/epi | N128/F8/epi |
| 1024 | 1.150028 | 1.148381 | -0.143% | N128/F4/epi | N128/F8/epi |
| 2048 | 1.265997 | 1.256331 | -0.764% | N128/F8/epi | N128/F8/epi |
| 4096 | 1.875520 | 1.883359 | +0.418% | N128/F8/epi | N128/F8/epi |

8–4096 geometric mean: -0.376683%; 7/10 lower. The1/2/4 rows are excluded.

Whole-invocation CLC8 before versus loop-rotation CLC8. Only clc.py changes; no numerical/native/sample/scorer validators rerun, row replacement or drift correction. Both whole catalogs are measured independently, with unchanged bundle1/S2 and timing/scoring helpers. Timing includes dispatch/compute/finish and unchanged staging/reduction. Tokens are global source tokens, distributed across8 ranks.
