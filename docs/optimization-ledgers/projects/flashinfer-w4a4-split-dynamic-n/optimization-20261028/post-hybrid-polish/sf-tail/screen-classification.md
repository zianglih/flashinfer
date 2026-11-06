# Frozen SF-prefix screen classification

112 scaled cells: 31 affected FC2 cells and 81 aligned controls. FC1 is aligned in every cell. The 32 unchanged W4A16 cells are additional controls, outside this count.

| Topology | Model | Format | Tokens | FC2 K / tile K | SF words/bank | Copy words removed/tile |
|---|---|---|---|---|---|---|
| EP | v41-flash | CuteDSL PER-TOKEN | 4 | 2304 / 512 | 8 → 4 | 8 |
| EP | v41-flash | CuteDSL PER-TOKEN | 64 | 2304 / 512 | 8 → 4 | 8 |
| TP | v3 | CuteDSL W4A4 | 4 | 256 / 512 | 8 → 4 | 12 |
| TP | v3 | CuteDSL PER-TOKEN | 4 | 256 / 512 | 8 → 4 | 12 |
| TP | v3 | CuteDSL W4A4 | 64 | 256 / 512 | 8 → 4 | 12 |
| TP | v41-flash | CuteDSL W4A4 | 4 | 576 / 256 | 4 → 1 | 6 |
| TP | v41-flash | CuteDSL PER-TOKEN | 4 | 576 / 256 | 4 → 1 | 9 |
| TP | v41-flash | CuteDSL W4A4 | 64 | 576 / 256 | 4 → 1 | 6 |
| TP | v41-flash | CuteDSL PER-TOKEN | 64 | 576 / 256 | 4 → 1 | 6 |
| TP | v41-flash | CuteDSL W4A4 | 4096 | 576 / 512 | 8 → 1 | 14 |
| TP | v41-flash | CuteDSL PER-TOKEN | 4096 | 576 / 512 | 8 → 1 | 21 |
| TP | v41-flash | CuteDSL W4A4 | 16384 | 576 / 256 | 4 → 1 | 9 |
| TP | v41-flash | CuteDSL PER-TOKEN | 16384 | 576 / 256 | 4 → 1 | 9 |
| TP | kimi-k3 | CuteDSL W4A4 | 4 | 384 / 256 | 4 → 2 | 6 |
| TP | kimi-k3 | CuteDSL PER-TOKEN | 4 | 384 / 512 | 8 → 6 | 6 |
| TP | kimi-k3 | CuteDSL W4A4 | 64 | 384 / 512 | 8 → 6 | 6 |
| TP | kimi-k3 | CuteDSL PER-TOKEN | 64 | 384 / 512 | 8 → 6 | 6 |
| TP | kimi-k3 | CuteDSL W4A4 | 4096 | 384 / 512 | 8 → 6 | 6 |
| TP | kimi-k3 | CuteDSL PER-TOKEN | 4096 | 384 / 256 | 4 → 2 | 6 |
| TP | kimi-k3 | CuteDSL W4A4 | 16384 | 384 / 512 | 8 → 6 | 6 |
| TP | kimi-k3 | CuteDSL PER-TOKEN | 16384 | 384 / 512 | 8 → 6 | 6 |
| TP | nemo3-ultra | CuteDSL W4A4 | 4 | 640 / 256 | 4 → 2 | 4 |
| TP | nemo3-ultra | CuteDSL PER-TOKEN | 4 | 640 / 256 | 4 → 2 | 4 |
| TP | nemo3-ultra | CuteDSL W4A4 | 64 | 640 / 512 | 8 → 2 | 12 |
| TP | nemo3-ultra | CuteDSL PER-TOKEN | 64 | 640 / 256 | 4 → 2 | 4 |
| TP | nemo3-ultra | CuteDSL W4A4 | 4096 | 640 / 256 | 4 → 2 | 6 |
| TP | nemo3-ultra | CuteDSL PER-TOKEN | 4096 | 640 / 256 | 4 → 2 | 6 |
| TP | nemo3-ultra | CuteDSL W4A4 | 16384 | 640 / 256 | 4 → 2 | 6 |
| TP | nemo3-ultra | CuteDSL PER-TOKEN | 16384 | 640 / 256 | 4 → 2 | 6 |
| TP | nemo3-ultra | CuteDSL MXFP4x8 | 4 | 640 / 256 | 2 → 1 | 2 |
| TP | nemo3-ultra | CuteDSL MXFP8 | 64 | 640 / 256 | 2 → 1 | 3 |

All winners are read from the source-bound saved A2 result selected by the current screen configuration. The CSV retains every aligned control and exact FC1/FC2 K-step, tile-K, row-bank and copy-word derivation. This classification does not infer speedup from instruction counts.
