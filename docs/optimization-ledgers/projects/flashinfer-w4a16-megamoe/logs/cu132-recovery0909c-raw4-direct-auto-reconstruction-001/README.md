Direct Raw4 AUTO saved reconstruction

Original benchmark subprocess completed successfully. This is a saved reconstruction, not an original run_full13 result.

| Global tokens | Accepted fixed8 ms | Raw4 ms | Raw4 / fixed8 | Raw4 tactic |
|---:|---:|---:|---:|---|
| 1 | 0.092689 | 0.083473 | 0.900571 | M256/N64, C2, F4, epi, S2 |
| 2 | 0.122017 | 0.107697 | 0.882639 | M256/N64, C2, F8, epi, S2 |
| 4 | 0.135169 | 0.128113 | 0.947799 | M256/N64, C2, F4, epi, S2 |
| 8 | 0.148738 | 0.153761 | 1.033771 | M256/N64, C2, F8, epi, S2 |
| 16 | 0.165250 | 0.171426 | 1.037374 | M256/N64, C2, F8, epi, S2 |
| 32 | 0.192369 | 0.187906 | 0.976800 | M256/N64, C2, F4, epi, S2 |
| 64 | 0.214466 | 0.215554 | 1.005073 | M256/N64, C2, F8, epi, S2 |
| 128 | 0.218194 | 0.224386 | 1.028378 | M256/N64, C2, F4, epi, S2 |
| 256 | 0.220193 | 0.219794 | 0.998188 | M256/N64, C2, F4, epi, S2 |
| 512 | 0.227042 | 0.232882 | 1.025722 | M256/N64, C2, F4, epi, S2 |
| 1024 | 0.245235 | 0.250946 | 1.023288 | M256/N64, C2, F8, epi, S2 |
| 2048 | 0.331411 | 0.331396 | 0.999955 | M256/N128, C2, F4, reuse, S2 |
| 4096 | 0.485093 | 0.508406 | 1.048059 | M256/N128, C2, F4, reuse, S2 |

Retention8–4096: geometric mean ratio 1.017447830; lower latency in 3/10 rows. All13 secondary geometric mean ratio: 0.991558543.

All 13×8 rounded secondary CUDA-event rankings and 13×100 primary CUPTI samples are retained in reconstructed-result.json. No candidate replay sample arrays are invented.
