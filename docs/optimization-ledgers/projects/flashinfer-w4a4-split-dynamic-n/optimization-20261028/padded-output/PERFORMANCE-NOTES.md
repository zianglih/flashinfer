# Routed output performance boundary

The accepted simplification removes compact-output offsets, the FC2-produced inverse map, and all output-workspace threading. It uses padded BF16 routed output plus the original inverse routing map, like W4A16. R2 additionally stores every nonempty bulk slab directly with TMA, including its ignored padding.

The R1 component probe isolates the persistent narrow-decode tradeoff. N3U, four tokens, MXFP4x8, frozen tactics/routes:

| Topology | Prepare, old/new us | FC2, old/new us | Combine, old/new us | Full PDL-on chain, old/new us |
|---|---:|---:|---:|---:|
| TP8 | 3.264 / 3.232 | 16.881 / 16.400 | 4.384 / 13.408 | 36.417 / 40.385 |
| EP8 | 2.944 / 2.943 | 18.464 / 18.320 | 3.104 / 4.096 | 35.409 / 35.921 |

Components use ready inputs with PDL disabled; they are diagnostic and must not be added to predict the overlapped PDL-on chain. Output changes from 88x2048 BF16 to 1408x2048 for TP, 1040x2048 for EP. Both use FC2 N16, so neither executes the bulk-tail path changed in R2. Source bits, route identities, tactics and final exact output were verified. Raw evidence: `r1/component/evidence`; receipt: `r1/component/AUDIT.json`.

The measured loss is in combine's routed gather. This probe does not distinguish sparse address locality, cache-set behavior, address generation or load scheduling; no NCU claim is warranted. The full-chain loss is about 4 us for TP and 0.5 us for EP, not the sum of isolated component deltas.

A possible future general optimization is to issue several independent routed-input vector loads before the ordered FMA chain, with compile-time bounded register storage and no public knobs. Preserve first-slot multiply/subsequent ordered FMA exactly. This is only a hypothesis, not an implemented or retained optimization. Do not reintroduce compact routing metadata or shape-specific output layouts without new evidence.
