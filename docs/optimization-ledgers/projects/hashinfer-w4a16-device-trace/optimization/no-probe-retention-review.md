# Both-probe removal: reject for retention

Keep R1/Store16. The candidate has a verified native instruction reduction, but the completed measurements do not establish a consistent incremental runtime benefit. Raw-probe-only removal is a separate candidate still under native qualification.

| Scope | Speedup versus Store16 |
|---|---:|
| Native EP4 decode geometric mean, T4–512 | 1.012110× |
| Native EP8 decode geometric mean, T4–512 | 0.970334× |
| Original uniform target comparison | 0.986079× |
| Fresh uniform AUTO target comparison | 0.988853× |
| Fixed EP8 T4 ABBA, 200 samples/arm | 0.974025× |

Ratios are baseline median / candidate median; greater than one is faster. Native rows use H7168/I2048/E256/K8 and global token counts. The uniform target uses H6144, global1024/EP4 (256/rank), with uniform routing. All timings use cold-L2 CUDA-graph CUPTI with 3 warmups and 100 untrimmed per-iteration rank-MAX samples per run. Native comparisons are one ordered pair per EP, against earlier retained-control measurements.

## Complete native rows

| Global tokens | EP4 Store16 µs | EP4 both removed µs | Ratio | EP8 Store16 µs | EP8 both removed µs | Ratio |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 67.841 | 64.736 | 1.047964× | 64.944 | 79.297 | 0.819002× |
| 2 | 93.936 | 91.632 | 1.025144× | 90.945 | 91.024 | 0.999127× |
| 4 | 119.185 | 114.001 | 1.045469× | 98.849 | 107.872 | 0.916355× |
| 8 | 159.138 | 153.697 | 1.035401× | 122.961 | 127.952 | 0.960989× |
| 16 | 196.258 | 205.939 | 0.952991× | 137.234 | 145.457 | 0.943464× |
| 32 | 269.443 | 264.211 | 1.019802× | 164.977 | 170.802 | 0.965899× |
| 64 | 294.435 | 292.147 | 1.007833× | 193.745 | 193.841 | 0.999502× |
| 128 | 320.212 | 317.587 | 1.008265× | 193.522 | 190.065 | 1.018189× |
| 256 | 330.323 | 322.611 | 1.023905× | 191.746 | 196.546 | 0.975581× |
| 512 | 346.707 | 344.659 | 1.005944× | 203.169 | 205.970 | 0.986406× |
| 4096 | 795.143 | 804.920 | 0.987853× | 460.692 | 465.873 | 0.988879× |
| 8192 | 1484.748 | 1485.775 | 0.999309× | 786.690 | 785.973 | 1.000913× |
| 16384 | 2857.385 | 2842.151 | 1.005360× | 1480.067 | 1524.231 | 0.971026× |

All EP4 selected tactic dictionaries are identical. EP8 changes N64→N128 and G512→G1024 at T1, and changes only G at T2/8/16/256/512. Return mode does not change. T4 uses the same tactic in the AUTO pair. Per-shape logged tactics are authoritative: small global shapes share a capacity cache key, so the final cache contains only its last winner. The audit verifies that final keyed winner, not every superseded shape winner.

## Fresh target isolation and EP8 T4 confirmation

| Target variant | Median µs | Ratio vs fresh Store16 | AUTO group |
|---|---:|---:|---:|
| Store16 | 326.4505 | 1.000000× | 512 |
| Remove raw-ready probe only | 324.6420 | 1.005571× | 512 |
| Remove TMEM-free probe only | 328.9945 | 0.992267× | 1024 |
| Remove both probes | 330.1305 | 0.988853× | 1024 |

All four target runs use N64/epi; raw-only matches the fresh control tactic while the other two choose G1024. Thus the AUTO target comparisons include selector changes. Each has four-rank independent BF16-bit reference checks, finite/repeated-output checks, identical input/weight/output hashes, matching frozen source closure, and a matching final knob-cache winner. A small single-pass raw-only improvement is not retention qualification.

The fixed diagnostic uses the actual R1 EP8 T4 winner, N64/G1024/epi, in A1→B1→B2→A2 order. The remote and local driver hashes match the explicit fixed-knob provenance. These logs emit null AUTO winners, so the tactic is driver-attested, not inferred from defaults. A1/B1/B2/A2 medians are 102.1765/106.657/107.793/109.2165 µs. Pooled medians are 104.4165 versus 107.201 µs (0.974025×), with 200 retained samples per arm. The controls drift upward by 7.040 µs; this is not a clean causal measurement of a 2.6% penalty. It provides no convincing positive confirmation. It also does not replace the complete AUTO matrix. Fixed T4 checks output hashes, finiteness and repeatability, but has no independent reference call.

## Instruction evidence and validation boundary

Matched stacked, uninstrumented N64/G512 uniform codegen gives whole native instructions 5112→5072, FC1 per-K 225→215, and FC2 per-K 231→217. Four x16 weight stores and 136 convert/scale instructions per K-step are unchanged. REG 96, STACK 0, LOCAL 0 and zero LDL/STL are unchanged; the four outlined blocking wait helpers retain the same five-opcode sequences. This is a real instruction reduction, not an inferred saving from Python lines. It is specialization-specific static evidence, not proof of faster execution or a fixed saving on every readiness path. See `no-probe-stacked-codegen.md` and the fingerprinted `native-codegen-no-probe-r1-analysis/` extracts.

Both complete native sweeps pass fixture, output-hash, finite/repeat and source-closure checks (52 paired rank/shape rows for EP4; 104 for EP8). Their independent reference applies only to T128, on every rank. The uniform studies reference-check T1024 on every rank. Other native rows establish paired output parity, not independent-oracle coverage. No sanitizer or final ownership-port validation is claimed.

The unchanged environment is hu-pdx-38, boot 1b51b917-b064-4570-afbb-5acd4c450cd9, B300 SXM6 AC, nvcr.io/nvidia/pytorch:26.05-py3, torch 2.12.0a0+5aff3928d8.nv26.05, CUDA 13.2, CUPTI 13.4.0. Exact source identity is the SHA256 of the frozen Python tree; the common declared base002ef145 is not the candidate final commit.

- Store16 SHA256: `7a48709ed07bc8496908625b921927b04dbcca495d7a3b1ced9a7bd28d072234`.
- Both-probes SHA256: `2cb93b9d3b679898341b103a5ccb9b19f8cdf7ddd1f0f245f922fab6c9137b64`.

Artifacts: `no-probe-performance-audit.json`, three `no-probe-{uniform,ep4,ep8}-review-r1` summaries, three fresh target summaries, `no-probe-ep8-t4-fixed-review`, and this report’s companion JSON preserve all rows, raw samples, complete tactics and hashes. Raw completed logs/caches are in `results/`; only allowlisted completed evidence was copied. No causal report or compiler cache was overwritten.
