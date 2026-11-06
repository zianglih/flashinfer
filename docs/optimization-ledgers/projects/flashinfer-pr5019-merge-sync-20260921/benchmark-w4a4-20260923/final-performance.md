## Final performance

Two full native sweeps per EP, with Split W4A16 → Mega W4A16 → Mega W4A4 in that fixed order for every token count. Each cell is the pooled median of 200 untrimmed rank-MAX CUPTI activity spans (100 per sweep), in microseconds. Each sweep starts with a fresh knob cache and uses full native autotuning.

`Split / Mega W4A16` and `Mega W4A4 / Mega W4A16` are speedups of Mega W4A16; a value above 1 means Mega W4A16 is faster. The comparison uses BF16 inputs, the same canonical NVFP4 weights and precomputed FP32 routes, FC2 routing placement and disabled in-kernel FC2 reduction. W4A4 adds activation quantization within its native public forward.

### EP4

| Global tokens | Split W4A16 µs | Mega W4A16 µs | Split / Mega W4A16 | Mega W4A4 µs | Mega W4A4 / Mega W4A16 |
|---:|---:|---:|---:|---:|---:|
| 1 | 76.9445 | 75.0725 | 1.0249× | 82.9285 | 1.1046× |
| 2 | 101.2965 | 90.2090 | 1.1229× | 105.4730 | 1.1692× |
| 4 | 141.2010 | 109.7440 | 1.2866× | 128.0650 | 1.1669× |
| 8 | 181.4890 | 151.3610 | 1.1990× | 167.8090 | 1.1087× |
| 16 | 222.2730 | 201.8890 | 1.1010× | 203.6650 | 1.0088× |
| 32 | 279.7940 | 259.8415 | 1.0768× | 257.9375 | 0.9927× |
| 64 | 334.1150 | 292.0170 | 1.1442× | 289.7140 | 0.9921× |
| 128 | 330.7695 | 319.2820 | 1.0360× | 314.0185 | 0.9835× |
| 256 | 365.2510 | 328.7865 | 1.1109× | 316.0660 | 0.9613× |
| 512 | 370.2420 | 345.2815 | 1.0723× | 320.8815 | 0.9293× |
| 4096 | 946.8700 | 786.5500 | 1.2038× | 448.8035 | 0.5706× |
| 8192 | 1660.2490 | 1524.5505 | 1.0890× | 611.1875 | 0.4009× |
| 16384 | 3062.9085 | 2843.3560 | 1.0772× | 1019.8765 | 0.3587× |

Decode 4–512 geometric speedup of Mega W4A16: **1.1259× over Split W4A16; 1.0153× over Mega W4A4**. Tokens 1/2 are reported but excluded from this summary; inspect each prefill row separately.

| Global tokens | Mega W4A16 tactic, sweep 1 | Mega W4A16 tactic, sweep 2 | Mega W4A4 tactic, sweep 1 | Mega W4A4 tactic, sweep 2 |
|---:|---|---|---|---|
| 1 | `G1024/M256N128K256/F4/epi` | `G512/M256N128K256/F4/epi` | `G512/M256N128K256/F4/epi` | `G512/M256N128K256/F8/epi` |
| 2 | `G1024/M256N64K256/F4/epi` | `G1024/M256N64K256/F4/epi` | `G512/M256N128K256/F8/epi` | `G512/M256N128K256/F8/epi` |
| 4 | `G1024/M256N64K256/F4/epi` | `G1024/M256N64K256/F4/epi` | `G512/M256N128K256/F8/epi` | `G512/M256N128K256/F4/epi` |
| 8 | `G1024/M256N64K256/F4/epi` | `G512/M256N64K256/F4/epi` | `G512/M256N128K256/F8/epi` | `G512/M256N128K256/F8/epi` |
| 16 | `G1024/M256N64K256/F4/epi` | `G1024/M256N64K256/F4/epi` | `G512/M256N128K256/F8/epi` | `G512/M256N128K256/F4/epi` |
| 32 | `G1024/M256N64K256/F4/epi` | `G1024/M256N64K256/F4/epi` | `G512/M256N128K256/F8/epi` | `G512/M256N128K256/F8/epi` |
| 64 | `G1024/M256N64K256/F4/epi` | `G1024/M256N64K256/F4/epi` | `G512/M256N128K256/F4/epi` | `G512/M256N128K256/F8/epi` |
| 128 | `G1024/M256N64K256/F4/epi` | `G1024/M256N64K256/F4/epi` | `G512/M256N128K256/F8/epi` | `G512/M256N128K256/F8/epi` |
| 256 | `G1024/M256N64K256/F4/epi` | `G1024/M256N64K256/F4/epi` | `G512/M256N128K256/F8/epi` | `G512/M256N128K256/F8/epi` |
| 512 | `G1024/M256N64K256/F4/epi` | `G1024/M256N64K256/F4/epi` | `G512/M256N128K256/F8/epi` | `G512/M256N128K256/F8/epi` |
| 4096 | `G1024/M256N128K256/F4/dispatch` | `G1024/M256N128K256/F4/dispatch` | `G512/M256N256K256/F4/dispatch` | `G512/M256N256K256/F4/dispatch` |
| 8192 | `G1024/M256N128K256/F4/dispatch` | `G1024/M256N128K256/F4/dispatch` | `G512/M256N128K256/F4/dispatch` | `G512/M256N256K256/F4/dispatch` |
| 16384 | `G512/M256N128K256/F4/dispatch` | `G1024/M256N128K256/F4/dispatch` | `G512/M256N256K256/F8/dispatch` | `G512/M256N256K256/F8/dispatch` |

All ranks agree on each effective MegaMoE tactic within each sweep. `G` is group_hint, `M/N/K` the MMA tile and `F` flag_batch; `epi`, `standalone` and `dispatch` mean epi_warps, standalone_warps and reuse_dispatch_warps. Full configurations, all-rank samples, per-sweep medians and successive 25-sample medians are retained in the JSON/evidence files.

### EP8

| Global tokens | Split W4A16 µs | Mega W4A16 µs | Split / Mega W4A16 | Mega W4A4 µs | Mega W4A4 / Mega W4A16 |
|---:|---:|---:|---:|---:|---:|
| 1 | 81.1690 | 71.4575 | 1.1359× | 78.4810 | 1.0983× |
| 2 | 111.0570 | 88.0805 | 1.2609× | 106.4175 | 1.2082× |
| 4 | 135.1055 | 101.2970 | 1.3338× | 128.1930 | 1.2655× |
| 8 | 153.3775 | 123.0890 | 1.2461× | 154.4975 | 1.2552× |
| 16 | 174.2900 | 136.0490 | 1.2811× | 156.3855 | 1.1495× |
| 32 | 195.8100 | 160.9620 | 1.2165× | 174.5305 | 1.0843× |
| 64 | 212.8985 | 183.4250 | 1.1607× | 197.2980 | 1.0756× |
| 128 | 223.6825 | 186.7535 | 1.1977× | 198.9625 | 1.0654× |
| 256 | 231.7455 | 191.7940 | 1.2083× | 202.1140 | 1.0538× |
| 512 | 231.6975 | 196.8170 | 1.1772× | 204.9620 | 1.0414× |
| 4096 | 534.2625 | 453.7795 | 1.1774× | 292.6270 | 0.6449× |
| 8192 | 909.7225 | 790.4095 | 1.1510× | 381.2195 | 0.4823× |
| 16384 | 1665.5020 | 1501.4710 | 1.1092× | 605.8780 | 0.4035× |

Decode 4–512 geometric speedup of Mega W4A16: **1.2265× over Split W4A16; 1.1208× over Mega W4A4**. Tokens 1/2 are reported but excluded from this summary; inspect each prefill row separately.

| Global tokens | Mega W4A16 tactic, sweep 1 | Mega W4A16 tactic, sweep 2 | Mega W4A4 tactic, sweep 1 | Mega W4A4 tactic, sweep 2 |
|---:|---|---|---|---|
| 1 | `G512/M256N64K256/F4/epi` | `G1024/M256N64K256/F4/epi` | `G512/M256N128K256/F8/epi` | `G512/M256N128K256/F8/epi` |
| 2 | `G512/M256N64K256/F4/epi` | `G1024/M256N64K256/F4/epi` | `G512/M256N128K256/F8/epi` | `G512/M256N128K256/F4/epi` |
| 4 | `G1024/M256N64K256/F4/epi` | `G512/M256N64K256/F4/epi` | `G512/M256N128K256/F8/epi` | `G512/M256N128K256/F4/epi` |
| 8 | `G512/M256N64K256/F4/epi` | `G1024/M256N64K256/F4/epi` | `G512/M256N128K256/F8/epi` | `G512/M256N128K256/F8/epi` |
| 16 | `G1024/M256N64K256/F4/epi` | `G1024/M256N64K256/F4/epi` | `G512/M256N128K256/F8/epi` | `G512/M256N128K256/F4/epi` |
| 32 | `G512/M256N64K256/F4/epi` | `G1024/M256N64K256/F4/epi` | `G512/M256N128K256/F8/epi` | `G512/M256N128K256/F8/epi` |
| 64 | `G512/M256N64K256/F4/epi` | `G512/M256N64K256/F4/epi` | `G512/M256N128K256/F8/epi` | `G512/M256N128K256/F8/epi` |
| 128 | `G1024/M256N64K256/F4/epi` | `G1024/M256N64K256/F4/epi` | `G512/M256N128K256/F8/epi` | `G512/M256N128K256/F8/epi` |
| 256 | `G1024/M256N64K256/F4/epi` | `G512/M256N64K256/F4/epi` | `G512/M256N128K256/F4/epi` | `G512/M256N128K256/F8/epi` |
| 512 | `G1024/M256N64K256/F4/epi` | `G1024/M256N64K256/F4/epi` | `G512/M256N128K256/F8/epi` | `G512/M256N128K256/F8/epi` |
| 4096 | `G1024/M256N128K256/F4/dispatch` | `G1024/M256N128K256/F4/dispatch` | `G512/M256N128K256/F4/dispatch` | `G512/M256N128K256/F4/dispatch` |
| 8192 | `G1024/M256N128K256/F4/dispatch` | `G1024/M256N128K256/F4/dispatch` | `G512/M256N128K256/F4/dispatch` | `G512/M256N128K256/F4/dispatch` |
| 16384 | `G1024/M256N128K256/F4/dispatch` | `G1024/M256N128K256/F4/dispatch` | `G512/M256N256K256/F4/dispatch` | `G512/M256N256K256/F4/dispatch` |

All ranks agree on each effective MegaMoE tactic within each sweep. `G` is group_hint, `M/N/K` the MMA tile and `F` flag_batch; `epi`, `standalone` and `dispatch` mean epi_warps, standalone_warps and reuse_dispatch_warps. Full configurations, all-rank samples, per-sweep medians and successive 25-sample medians are retained in the JSON/evidence files.

Outputs are checked by two extra untimed eager forwards after each full row. Every logical output must be finite; W4A16 repeats must match raw BF16 bits. W4A4 repeat-bit outcomes are reported without imposing a cross-precision or bit-exact W4A4 acceptance criterion. This does not check every timed graph replay or establish independent numerical equivalence.

| EP | Variant | Finite rank/output rows | Repeated bit-equal rows |
|---:|---|---:|---:|
| 4 | w4a16 | 104 / 104 | 104 / 104 |
| 4 | w4a16_megamoe | 104 / 104 | 104 / 104 |
| 4 | w4a4_megamoe | 104 / 104 | 104 / 104 |
| 8 | w4a16 | 208 / 208 | 208 / 208 |
| 8 | w4a16_megamoe | 208 / 208 | 208 / 208 |
| 8 | w4a4_megamoe | 208 / 208 | 208 / 208 |
