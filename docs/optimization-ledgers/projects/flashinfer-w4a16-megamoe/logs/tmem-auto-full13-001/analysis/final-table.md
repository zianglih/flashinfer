# Final performance

Tested source `6315f94ceb279db53ec3149a7d81e19b332c8dd0`; same replacement node and source for both processes. B300 ×8, H7168/I2048/E256/top-k8; global tokens; BF16 activations/wire and NVFP4 weights. Three warmups,100 CUPTI iterations, CUDA graphs, cold L2, split `--no-fused-finalize`. Latency is median per-iteration maximum-rank GPU span, in ms. Online host-ranking scores are excluded.

Fixed control: M256/N128/K256, flag4, epi return; all arms use two decode groups. Ratios >1 favor auto. Each displayed latency is the original raw printed value.

| Global tokens | Split fixed-run | Fixed Mega | Split auto-run | Auto Mega | Split/auto | Fixed/auto | Actual auto choice |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 0.084656 | 0.078992 | 0.077057 | 0.078384 | 0.983× | 1.008× | M128/N64, F4, epi |
| 2 | 0.099537 | 0.114193 | 0.108113 | 0.123761 | 0.874× | 0.923× | M256/N128, F4, reuse |
| 4 | 0.142113 | 0.139169 | 0.136913 | 0.132977 | 1.030× | 1.047× | M256/N128, F8, epi |
| 8 | 0.157409 | 0.156321 | 0.153633 | 0.158385 | 0.970× | 0.987× | M128/N64, F8, reuse |
| 16 | 0.182721 | 0.177345 | 0.180289 | 0.186434 | 0.967× | 0.951× | M256/N128, F4, reuse |
| 32 | 0.204289 | 0.204049 | 0.206737 | 0.208850 | 0.990× | 0.977× | M128/N64, F8, reuse |
| 64 | 0.209154 | 0.235665 | 0.224273 | 0.224417 | 0.999× | 1.050× | M128/N64, F8, epi |
| 128 | 0.235793 | 0.239442 | 0.220817 | 0.227986 | 0.969× | 1.050× | M256/N64, F8, epi |
| 256 | 0.230530 | 0.255202 | 0.243474 | 0.231026 | 1.054× | 1.105× | M256/N64, F4, epi |
| 512 | 0.238689 | 0.245569 | 0.241681 | 0.235009 | 1.028× | 1.045× | M256/N64, F8, epi |
| 1024 | 0.261329 | 0.268049 | 0.255842 | 0.252481 | 1.013× | 1.062× | M256/N64, F8, epi |
| 2048 | 0.338770 | 0.343922 | 0.350083 | 0.325554 | 1.075× | 1.056× | M256/N128, F4, reuse |
| 4096 | 0.552915 | 0.508131 | 0.538869 | 0.487970 | 1.104× | 1.041× | M256/N128, F4, reuse |

One process median per arm; repeat close/unstable points before promotion. Split control changes include fresh tactic selection, so they are context rather than confidence bounds. All52 raw values are shown above;208 original split selections and104 rank confirmations of13 Mega choices are retained in comparison.json. Capacity1 cache ends at T8; earlier choices come from their actual row records.
