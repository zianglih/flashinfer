# FC2 pointer-pair comparison

One complete source5e9c candidate sweep versus the entire latest source3da repeat6060 control, node59/image26.05, public four F4 tactics, global tokens1–8192,3 warmups and100 cold-L2 CUDA-graph CUPTI samples per row. All14 rows,112 winners/resources,56 candidate rankings and1400 samples passed the sole saved reader; the sole comparator also passed. No source, oracle or benchmark replay.

| Global tokens | Before (µs) | Pointer-pair (µs) | Before / after | Latency change |
|---:|---:|---:|---:|---:|
| 1 | 84.096 | 74.672 | 1.1262× | -11.206% |
| 2 | 100.608 | 97.392 | 1.0330× | -3.197% |
| 4 | 116.401 | 119.873 | 0.9710× | +2.983% |
| 8 | 138.193 | 137.410 | 1.0057× | -0.567% |
| 16 | 146.977 | 151.217 | 0.9720× | +2.885% |
| 32 | 179.329 | 179.298 | 1.0002× | -0.017% |
| 64 | 202.642 | 199.826 | 1.0141× | -1.390% |
| 128 | 209.442 | 205.074 | 1.0213× | -2.086% |
| 256 | 208.738 | 209.858 | 0.9947× | +0.537% |
| 512 | 213.170 | 213.874 | 0.9967× | +0.330% |
| 1024 | 234.385 | 232.210 | 1.0094× | -0.928% |
| 2048 | 310.692 | 313.059 | 0.9924× | +0.762% |
| 4096 | 469.092 | 465.828 | 1.0070× | -0.696% |
| 8192 | 790.761 | 775.094 | 1.0202× | -1.981% |

Over8–8192, latency GM is **-0.295598%**, speedup **1.002965×**, with **7/11** lower rows. All14 GM is -1.097602% with9/14 lower rows. Tokens1/2/4 remain visible but are excluded from retention. All selections are unchanged: N64/F4/epi through1024; N128/F4/reuse at2048/4096/8192.

The observed8+ aggregate improvement is about0.30%, with mixed individual changes. One sweep does not establish a material general latency gain or a causal/statistical conclusion. Hot scores are a separate staged-wrapper/reducer measurement, excluding input staging; they rank the maximum of rank medians, unlike the median of100 per-iteration rank maxima above.

| Matched hot scores | Lower | Equal | Higher |
|---|---:|---:|---:|
| All56 | 25 | 6 | 25 |
| 8–8192 (44) | 21 | 3 | 20 |
| 8+ N64/epi_warps | 3 | 1 | 7 |
| 8+ N128/epi_warps | 7 | 1 | 3 |
| 8+ N64/reuse_dispatch_warps | 2 | 0 | 9 |
| 8+ N128/reuse_dispatch_warps | 9 | 1 | 1 |

[All56 raw fixed-tactic hot score pairs and complete comparison](../../logs/cu132-recovery0911c-fc2-route-pair-vs-fastdiv-repeat-comparison-001/README.md). The newer local assignment cleanup is outside this measured source5e9c.

Native mechanism is address/predicate bookkeeping reduction, not fewer final metadata loads: old PTX already compiled to the same two SASS LDG.E.64 operations. Logical prefetched pointer/valid arrays are halved. Matched C1/direct changes5056→5032 instructions and N64/direct5408→5392; N128/reuse6104 and partial N64/reuse5680 remain byte-exact. The fifth N128/partial/direct capture has5880 instructions without a matched BEFORE claim. All5 retain96 registers,640 threads,zero stack/local bytes and the same stages/shared memory; entry parameters/layouts are unchanged.

Focused correctness passed4 EP1 references,6 EP2 tail/geometry cases per rank and2 C1 routing calls per rank (rounds7/1), with unchanged oracles/tolerances. Native review and all source/native/idle closures passed. Retention and any PR update remain the parent decision; no change to the published source3da Final table is implied.
