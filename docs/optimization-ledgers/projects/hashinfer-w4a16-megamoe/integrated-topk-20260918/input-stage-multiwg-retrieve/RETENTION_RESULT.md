# Three-warp-group staging retention result

Retain `7dc96269`. The three-warp-group candidate `b215a7d2` has no aggregate gain: the 8–8192 geometric speedup is **0.995738×** (7dc/b215), with 5 of 11 rows faster. All 14 selected tactics are unchanged.

| Tokens | 7dc µs (MAD) | b215 µs (MAD) | 7dc/b215 | Selected tactic |
|---:|---:|---:|---:|---|
| 1 | 72.2730 (0.9750) | 72.0325 (0.7360) | 1.003339× | N64 / epi_warps |
| 2 | 90.4650 (0.6720) | 87.0410 (0.7680) | 1.039338× | N64 / epi_warps |
| 4 | 101.8410 (0.9120) | 100.6890 (0.8160) | 1.011441× | N64 / epi_warps |
| 8 | 123.2810 (0.8800) | 124.8005 (0.7360) | 0.987825× | N64 / epi_warps |
| 16 | 135.0890 (1.4240) | 148.5615 (1.0715) | 0.909314× | N64 / epi_warps |
| 32 | 163.0100 (0.7370) | 161.6015 (0.8485) | 1.008716× | N64 / epi_warps |
| 64 | 185.1535 (0.7045) | 186.7375 (0.9285) | 0.991518× | N64 / epi_warps |
| 128 | 189.7135 (0.9115) | 186.1290 (0.7840) | 1.019258× | N64 / epi_warps |
| 256 | 191.2185 (0.9130) | 191.2810 (0.8965) | 0.999673× | N64 / epi_warps |
| 512 | 195.8260 (0.7845) | 196.5465 (1.0085) | 0.996334× | N64 / epi_warps |
| 1024 | 222.7545 (1.1365) | 219.2980 (0.7045) | 1.015762× | N64 / epi_warps |
| 2048 | 300.3705 (1.4245) | 300.8030 (1.5520) | 0.998562× | N128 / reuse_dispatch_warps |
| 4096 | 467.4920 (3.9995) | 457.2370 (3.7285) | 1.022428× | N128 / reuse_dispatch_warps |
| 8192 | 768.8085 (11.8255) | 762.1380 (26.3860) | 1.008752× | N128 / reuse_dispatch_warps |

At 16 tokens, latency rises **9.973%**, from 135.0890 to 148.5615 µs; both runs selected N64 epilogue return on all eight ranks. The quarter medians are consistently separated:

| Arm | Samples 1–25 | 26–50 | 51–75 | 76–100 |
|---|---:|---:|---:|---:|
| 7dc | 134.753 | 135.489 | 134.593 | 135.265 |
| b215 | 149.249 | 148.545 | 148.705 | 148.257 |

All 100 samples per row are retained, including the first-sample outlier in both arms. MAD and quarter medians show within-arm spread; they do not remove temporal drift between serial runs. These are reused, sealed same-node controls—not a fresh alternating pair. No retiming is required for the decision to retain 7dc.

Validation: all 112 rank/token outputs are finite and bit-exact against 7dc; fixture/source/environment/sample and recorded validation-overlap checks passed. Native 48 logical cases, the two strict 1024-token cases exercising every copy WG, and 96 queued cases remain separate receipts.

The original audit JSON is authoritative. Its generated Markdown has a stale “4d AUTO” heading; the underlying candidate data is b215. This report labels it correctly without changing the sealed audit.
