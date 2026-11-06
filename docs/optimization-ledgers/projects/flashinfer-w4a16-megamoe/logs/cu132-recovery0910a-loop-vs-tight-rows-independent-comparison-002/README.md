# Loop versus tight-row CLC whole invocation

| Tokens | Loop ms | Tight-row ms | Change | Loop tactic | Tight-row tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.160994 | 0.160882 | -0.070% | N128/F4/epi | N64/F4/epi |
| 2 | 0.280483 | 0.277618 | -1.021% | N128/F8/epi | N128/F4/epi |
| 4 | 0.431571 | 0.428227 | -0.775% | N128/F8/epi | N128/F4/epi |
| 8 | 0.584901 | 0.585510 | +0.104% | N128/F4/epi | N128/F4/epi |
| 16 | 0.714055 | 0.696181 | -2.503% | N64/F8/epi | N64/F8/epi |
| 32 | 0.905479 | 0.887624 | -1.972% | N64/F4/epi | N64/F8/epi |
| 64 | 1.073177 | 1.059067 | -1.315% | N128/F4/epi | N128/F4/epi |
| 128 | 1.105851 | 1.101450 | -0.398% | N64/F4/reuse | N128/F4/epi |
| 256 | 1.110124 | 1.112603 | +0.223% | N64/F4/epi | N64/F8/epi |
| 512 | 1.111834 | 1.126745 | +1.341% | N128/F8/epi | N128/F4/epi |
| 1024 | 1.148381 | 1.148827 | +0.039% | N128/F8/epi | N128/F4/epi |
| 2048 | 1.256331 | 1.238333 | -1.433% | N128/F8/epi | N128/F8/epi |
| 4096 | 1.883359 | 1.824915 | -3.103% | N128/F8/epi | N128/F4/epi |

8–4096 geometric mean: -0.910433%; 6/10 lower. The 1/2/4 rows are excluded.

Whole-invocation loop11ea CLC8 versus tight-row4cf CLC8, using the full current columns of each hash-pinned completed reconstruction. No numerical/native/sample/scorer validators rerun, row replacement or drift correction. Both whole CLC catalogs are measured independently with unchanged S2 and timing/scoring helpers. Tokens are global source tokens distributed across 8 ranks.
