# L2 width16 repeat — unpromoted

Complete-file/raw timing audit PASS: `decode13-benchmark/independent-file-timing-audit.json` SHA256 `d4a6f53ccb24be49fec0980935526c87323b6c48ec06cf41d90543fa4e3006d0`. All59 original member files verified (51 compact members plus8 exact SHA-identical A1 output files), with explicit original gzip **not locally verified**. All1300 samples per arm and104 finite/repeat-exact outputs pass; cross-arm104 exact output comparisons pass against primary A3, historical A1 and the original same-source L1. Source/cwd aliases, fresh AUTO4 knob cache, corresponding CuTe/CUDA cache paths, setup, boot and closed process groups are bound. This is full13 performance evidence, not broad native/sanitizer qualification.

Candidate remains exact L1d9d510f7, versus refreshed retained3de A3, same8B300 hu15 boot. Method unchanged: public precomputed-routing forward, EP8/H7168/I2048/E256/K8, O3/AUTO4,3 warmups,100 cold-L2 graph-CUPTI rank-MAX samples. Decode4–512 geometric speedup **1.000462938×**,4/8 wins; all13/13 primary tactics match across all8 ranks. Historical A1/L2 GM=0.991496869× is separately retained. L1/L2 same-source GM=0.987593041×; it is serial repeat evidence, not drift cancellation.

| T | A3 µs | L2 µs | A3/L2 | L1 µs | L1/L2 | A3/L2 MAD µs |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 68.0640 | 66.8000 | 1.018922 | 67.2800 | 1.007186 | 0.8480/1.0875 |
| 2 | 84.8330 | 84.0000 | 1.009917 | 81.0565 | 0.964958 | 2.2080/0.7680 |
| 4 | 97.6650 | 96.8165 | 1.008764 | 88.9125 | 0.918361 | 0.7365/1.1365 |
| 8 | 121.6165 | 122.4170 | 0.993461 | 120.7370 | 0.986276 | 0.8955/0.9755 |
| 16 | 135.9210 | 134.9445 | 1.007236 | 134.8480 | 0.999285 | 0.9280/0.7205 |
| 32 | 162.1290 | 159.6970 | 1.015229 | 159.9530 | 1.001603 | 0.7520/0.7040 |
| 64 | 184.0335 | 185.7925 | 0.990532 | 182.6410 | 0.983038 | 0.7995/0.8480 |
| 128 | 189.2325 | 188.6410 | 1.003136 | 190.5290 | 1.010008 | 0.8485/0.7830 |
| 256 | 190.9920 | 192.8645 | 0.990291 | 192.4800 | 0.998006 | 0.7520/0.7685 |
| 512 | 195.8410 | 196.7535 | 0.995362 | 198.2080 | 1.007392 | 1.2160/0.9600 |
| 4096 | 460.7050 | 462.5325 | 0.996049 | 466.7710 | 1.009164 | 3.5205/3.4415 |
| 8192 | 798.4855 | 766.5295 | 1.041689 | 786.0525 | 1.025469 | 30.0335/5.9815 |
| 16384 | 1499.5880 | 1488.1030 | 1.007718 | 1500.0135 | 1.008004 | 80.8170/39.5350 |

The original T4 gain did not reproduce: A2/L1 was97.6480/88.9125µs, whereas A3/L2 is97.6650/96.8165µs (0.869% lower latency). Allfour arms select the same N64/epi tactic on every rank. Original L1 quarters were[89.120, 88.801, 88.897, 88.736]µs; L2 quarters[97.728, 96.384, 95.968, 96.928]µs. A3 quarters[97.696, 97.569, 97.856, 97.665]µs overlap L2's first quarter. L2's MAD1.1365µs is larger than the0.8485µs median difference from A3; L1/L2 itself shifts by8.890% despite unchanged source/tactic. This does not identify the cause of the original separated L1 distribution.

The apparent8K gain also needs restraint: A3 quarters[764.003, 762.850, 810.499, 826.757]µs and L2 quarters[763.682, 765.378, 761.794, 825.281]µs both contain a late slow interval; their medians weight that temporal pattern differently. The4K guard is0.40% slower,16K0.77% faster; no consistent general benefit is demonstrated.

Do not promote adjacent width16 based on these runs. Preserve the mixed original L1 and nearly neutral L2 separately; do not average or select the favorable run. Matched T4 codegen confirms128-bit halves and unchanged96register/zero-spill reports, but allocation/scheduling also changes before the reducer, so no isolated instruction/sector/latency explanation is established. The separate N1 coalesced mapping is its own trial.

CuTe4.7.1 `cute.compile` forces `no_cache=True`; an empty CuTe cache and a populated CUDA cache establish no compiled-kernel hit or saved-time claim. No sanitizer was run during this iteration.
