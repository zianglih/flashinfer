Complete auto16 sweep: unchanged 100-iteration CUPTI benchmark, global tokens, EP8. Each row reports its actual returned winner; no minimum across runs or row substitution.

| Global tokens | Split W4A16 ms | Mega W4A16 ms | Split / Mega | Actual choice |
| ---: | ---: | ---: | ---: | --- |
| 1 | 0.079473 | 0.090274 | 0.880x | M256/N64, C2, F8, epi |
| 2 | 0.112546 | 0.104161 | 1.081x | M128/N64, C1, F4, epi |
| 4 | 0.155762 | 0.128353 | 1.214x | M128/N64, C1, F8, epi |
| 8 | 0.160402 | 0.154546 | 1.038x | M256/N64, C2, F4, epi |
| 16 | 0.189234 | 0.165234 | 1.145x | M256/N64, C2, F8, epi |
| 32 | 0.212481 | 0.200450 | 1.060x | M256/N64, C2, F8, epi |
| 64 | 0.233811 | 0.226434 | 1.033x | M256/N64, C2, F8, epi |
| 128 | 0.242899 | 0.231266 | 1.050x | M256/N64, C2, F8, epi |
| 256 | 0.255139 | 0.236579 | 1.078x | M256/N64, C2, F4, epi |
| 512 | 0.244706 | 0.243122 | 1.007x | M256/N64, C2, F4, epi |
| 1024 | 0.271139 | 0.260115 | 1.042x | M256/N64, C2, F4, epi |
| 2048 | 0.363364 | 0.345348 | 1.052x | M256/N128, C2, F4, reuse |
| 4096 | 0.573590 | 0.507012 | 1.131x | M256/N128, C2, F4, reuse |
