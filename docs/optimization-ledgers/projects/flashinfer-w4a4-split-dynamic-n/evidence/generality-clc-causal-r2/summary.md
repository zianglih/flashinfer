Fixed FC1 scheduler diagnostic. Speedup >1 favors static.

| Model | Tokens | Backend | C1 µs | A1 µs | A2 µs | C2 µs | Static/CLC speedup |
|---|---:|---|---:|---:|---:|---:|---:|
| kimi-k3 | 4096 | CuteDSL W4A4 | 412.7215 | 390.0500 | 390.4020 | 412.8825 | 1.057854× |
| kimi-k3 | 4096 | CuteDSL PER-TOKEN | 582.9790 | 557.7470 | 557.4595 | 583.4435 | 1.045925× |
| kimi-k3 | 4096 | CuteDSL W4A16 | 680.6280 | 629.4910 | 682.5795 | 665.5560 | 1.026776× |
| v41-flash | 4 | CuteDSL W4A4 | 35.7280 | 36.0160 | 36.0320 | 35.6490 | 0.990686× |
| v41-flash | 4 | CuteDSL W4A16 | 41.4400 | 41.5050 | 41.4400 | 41.5040 | 0.999988× |
| kimi-k3 | 4096 | CuteDSL MXFP8 | 672.3075 | 652.0515 | 651.2190 | 671.9725 | 1.031467× |
| kimi-k3 | 4096 | CuteDSL MXFP4x8 | 426.7860 | 398.1780 | 398.5305 | 425.8270 | 1.070169× |

All captured pipeline stage/layout fields are identical between CLC and static for these selected tactics. Register allocation was not sampled. W4A16 is unchanged and reports timing noise. These are fixed-tactic causal diagnostics; they do not establish a global scheduler retention policy.
