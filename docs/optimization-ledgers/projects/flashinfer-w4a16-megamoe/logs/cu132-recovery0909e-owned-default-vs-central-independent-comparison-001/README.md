# Owned default versus central default whole invocation

| Tokens | Owned ms | Central ms | Change | Owned tactic | Central tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.088081 | 0.095521 | +8.447% | N64/F8/epi | N64/F4/epi |
| 2 | 0.097697 | 0.114609 | +17.311% | N64/F4/epi | N64/F4/epi |
| 4 | 0.120145 | 0.116753 | -2.823% | N64/F4/epi | N64/F8/epi |
| 8 | 0.142850 | 0.140369 | -1.737% | N64/F4/epi | N64/F8/epi |
| 16 | 0.150097 | 0.153313 | +2.143% | N64/F8/epi | N64/F8/epi |
| 32 | 0.180274 | 0.185074 | +2.663% | N64/F4/epi | N64/F8/epi |
| 64 | 0.205010 | 0.210722 | +2.786% | N64/F4/epi | N64/F4/epi |
| 128 | 0.214977 | 0.208066 | -3.215% | N64/F4/epi | N64/F4/epi |
| 256 | 0.206642 | 0.218787 | +5.877% | N64/F4/epi | N64/F4/epi |
| 512 | 0.202609 | 0.218546 | +7.866% | N64/F8/epi | N64/F4/epi |
| 1024 | 0.229410 | 0.237154 | +3.376% | N64/F4/epi | N64/F4/epi |
| 2048 | 0.332499 | 0.322643 | -2.964% | N128/F4/reuse | N128/F8/reuse |
| 4096 | 0.479478 | 0.470949 | -1.779% | N128/F4/reuse | N128/F4/reuse |

8–4096 geometric mean: +1.437759%; 4/10 lower. The1/2/4 rows are excluded.

Whole-invocation owned098c default8 versus central57e2 default8, using the full current columns of each hash-pinned completed reconstruction. No numerical/native/sample/scorer validators rerun, row replacement or drift correction. Both whole default catalogs are measured independently with unchanged S2 and timing/scoring helpers. Tokens are global source tokens distributed across8 ranks.
