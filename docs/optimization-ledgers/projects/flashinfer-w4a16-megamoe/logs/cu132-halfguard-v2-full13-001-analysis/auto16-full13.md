Complete auto16 sweep: unchanged 100-iteration CUPTI benchmark, global tokens, EP8. Each row reports its actual returned winner; no minimum across runs or row substitution.

| Global tokens | Split W4A16 ms | Mega W4A16 ms | Split / Mega | Actual choice |
| ---: | ---: | ---: | ---: | --- |
| 1 | 0.097457 | 0.102640 | 0.950x | M128/N64, C2, F4, reuse |
| 2 | 0.116353 | 0.111473 | 1.044x | M128/N64, C2, F8, epi |
| 4 | 0.137825 | 0.116625 | 1.182x | M128/N64, C2, F4, epi |
| 8 | 0.162593 | 0.168450 | 0.965x | M256/N128, C2, F4, reuse |
| 16 | 0.178177 | 0.176801 | 1.008x | M128/N64, C2, F4, reuse |
| 32 | 0.206738 | 0.209570 | 0.986x | M128/N64, C2, F4, reuse |
| 64 | 0.224658 | 0.230178 | 0.976x | M128/N64, C2, F4, epi |
| 128 | 0.224433 | 0.234642 | 0.956x | M128/N64, C1, F8, epi |
| 256 | 0.245058 | 0.235025 | 1.043x | M256/N64, C2, F8, epi |
| 512 | 0.238961 | 0.235105 | 1.016x | M256/N64, C2, F8, epi |
| 1024 | 0.260721 | 0.249202 | 1.046x | M256/N64, C2, F4, epi |
| 2048 | 0.344435 | 0.339139 | 1.016x | M256/N128, C2, F8, reuse |
| 4096 | 0.551669 | 0.498100 | 1.108x | M256/N128, C2, F4, reuse |
