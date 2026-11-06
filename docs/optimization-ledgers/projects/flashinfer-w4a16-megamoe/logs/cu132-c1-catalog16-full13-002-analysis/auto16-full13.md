Complete auto16 sweep: unchanged 100-iteration CUPTI benchmark, global tokens, EP8. Each row reports its actual returned winner; no minimum across runs or row substitution.

| Global tokens | Split W4A16 ms | Mega W4A16 ms | Split / Mega | Actual choice |
| ---: | ---: | ---: | ---: | --- |
| 1 | 0.076320 | 0.078849 | 0.968x | M256/N64, C2, F8, epi |
| 2 | 0.116817 | 0.111169 | 1.051x | M256/N64, C2, F4, epi |
| 4 | 0.127905 | 0.117873 | 1.085x | M128/N64, C1, F4, reuse |
| 8 | 0.162465 | 0.156593 | 1.037x | M128/N64, C1, F8, reuse |
| 16 | 0.178929 | 0.168001 | 1.065x | M256/N64, C2, F8, reuse |
| 32 | 0.204545 | 0.208241 | 0.982x | M128/N64, C1, F4, epi |
| 64 | 0.218737 | 0.226865 | 0.964x | M128/N64, C1, F8, epi |
| 128 | 0.233841 | 0.223873 | 1.045x | M256/N64, C2, F4, epi |
| 256 | 0.242785 | 0.230241 | 1.054x | M256/N64, C2, F8, epi |
| 512 | 0.239474 | 0.234833 | 1.020x | M256/N64, C2, F8, epi |
| 1024 | 0.260801 | 0.248578 | 1.049x | M256/N64, C2, F4, epi |
| 2048 | 0.350498 | 0.334978 | 1.046x | M256/N128, C2, F4, reuse |
| 4096 | 0.562021 | 0.501842 | 1.120x | M256/N128, C2, F4, reuse |
