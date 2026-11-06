# NVFP4 checkpoint 65392416 screening

One baseline and one candidate sweep; this is not a completed ABBA comparison. The checkpoint is not retained. Both use GPU0, native normal AUTO, deterministic unfused finalize, and the frozen 13-point methodology.

| Tokens | Before us | Checkpoint us | Before / checkpoint |
|---:|---:|---:|---:|
| 1 | 27.439 | 32.416 | 0.846x |
| 2 | 37.184 | 42.464 | 0.876x |
| 4 | 52.512 | 63.839 | 0.823x |
| 8 | 69.792 | 83.680 | 0.834x |
| 16 | 79.200 | 91.696 | 0.864x |
| 32 | 111.120 | 133.408 | 0.833x |
| 64 | 143.999 | 175.615 | 0.820x |
| 128 | 147.648 | 181.120 | 0.815x |
| 256 | 154.928 | 189.823 | 0.816x |
| 512 | 157.408 | 197.535 | 0.797x |
| 4096 | 208.463 | 450.719 | 0.463x |
| 8192 | 297.456 | 854.606 | 0.348x |
| 16384 | 472.464 | 1657.277 | 0.285x |

Geometric means (screening only):
- decode: 0.825x
- prefill: 0.358x
- retention: 0.657x

T1/T2 are reported but excluded from retention. Raw source/environment/tactic records and successful stdout are archived in the adjacent `raw/` directory. Preserve these results; later kernel changes require a new candidate record, not replacement of this screen.
