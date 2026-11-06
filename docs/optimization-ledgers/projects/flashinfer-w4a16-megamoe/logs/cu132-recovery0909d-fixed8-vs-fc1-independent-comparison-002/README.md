# Fixed8 versus FC1 post-scratch release — completed whole runs

Root retains FC1 on the ten-row policy after the original checks passed. All four regressions remain disclosed below.

Retention8–4096: **-1.099524% latency GM**, 6/10 wins; regressions at128,256,512,2048. Full13 secondary: -2.826011% GM, 9/13 wins. No1/2/4 row enters retention.

| Tokens | Fixed8 ms | FC1 ms | Change | Fixed8 tactic | FC1 tactic |
|---:|---:|---:|---:|:---|:---|
| 1 | 0.092689 | 0.092465 | -0.242% | M256/N64, C2, F4, epi, S2 | M256/N64, C2, F4, epi, S2 |
| 2 | 0.122017 | 0.107905 | -11.566% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 4 | 0.135169 | 0.117889 | -12.784% | M256/N64, C2, F4, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 8 | 0.148738 | 0.140817 | -5.325% | M256/N64, C2, F4, epi, S2 | M256/N64, C2, F4, epi, S2 |
| 16 | 0.165250 | 0.163169 | -1.259% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 32 | 0.192369 | 0.188706 | -1.904% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 64 | 0.214466 | 0.211186 | -1.529% | M256/N64, C2, F4, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 128 | 0.218194 | 0.218674 | +0.220% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 256 | 0.220193 | 0.223778 | +1.628% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 512 | 0.227042 | 0.231954 | +2.163% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 1024 | 0.245235 | 0.236642 | -3.504% | M256/N64, C2, F4, epi, S2 | M256/N64, C2, F4, epi, S2 |
| 2048 | 0.331411 | 0.331523 | +0.034% | M256/N128, C2, F4, reuse, S2 | M256/N128, C2, F8, reuse, S2 |
| 4096 | 0.485093 | 0.478853 | -1.286% | M256/N128, C2, F4, reuse, S2 | M256/N128, C2, F4, reuse, S2 |

Tactics changed at 4, 64, 2048; 10 same-choice rows. Same-choice variation: T1 -0.242%; T2 -11.566%; T8 -5.325%; T16 -1.259%; T32 -1.904%; T128 +0.220%; T256 +1.628%; T512 +2.163%; T1024 -3.504%; T4096 -1.286%. These sequential AUTO runs do not isolate a fixed-tactic kernel effect.

Benchmark subprocess 616.903775s versus retained 581.615758s; outer 620.238064s, timing utility 5.984077s. Full-run setup/tuning cost is separate from each shape's primary latency.

Complete13×100 cold-L2 CUPTI samples,13×8 secondary HOT selection rankings,104 actual winners/resources. Actual B stages {'3': 104}, raw stages {'4': 16, '5': 88}, scheduler stages {'2': 104}, local bytes {'0': 104}.

Current source96c9 changes the FC1 epilogue on retained fixed8/kernel7e. Completed16-rank/40-object numerical audit47a9 and native review are reused as code evidence, without reruns. Same physical hu-pdx-115 GPUs, loaded-stack matchb7d5 and exact6+7 input-pack match7051 support direct395a baseline reuse. Current native inventory grew12→23 through11 recorded first-build additions; original checks accept no existing non-diagnostic changes. No old native inventory identity is claimed.

Only completed0909d002/83972 contributes current rows. Old0909c interrupted6/13 and0909d001 pre-import failure stay separate. Original83972/idle76713/fetch26573 closed0; completion12b58147, original reconstructiona2222979. No original or baseline/native validator was rerun by this arithmetic check.

[Full comparison and pins](comparison.json) · [Original reconstructed result](../cu132-recovery0909d-fc1-direct-auto-reconstruction-002/README.md) · [Numerical audit](../cu132-recovery0909c-fc1-post-scratch-release-numerics-independent-001/audit.json)
