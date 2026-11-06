# N3U TP prefill: K640 cache identity

Both frozen T4096 and T16384 intermediate quantizers select BF16 K640, recipe 23 (precise base/MSE256 fast error), 64 threads, one SF block per lane, SF 128×4, row group 256/SF group 256, valid rows and row limits. Each arm's copied cached cubin is **byte-identical to its K640 native pilot**:

| Arm | Cubin prefix | Registers | Non-NOP | Local / stack | Pilot driver capacity |
|---|---|---:|---:|---|---:|
| Control |ff00cf52|61|743|0 / 0|16 CTAs/SM|
| Candidate |83a6345e|48|695|0 / 0|20 CTAs/SM|

The pilot resource reduction therefore applies to these exact source-bound cache specializations. The performance harness did not capture quantizer load handles, so this is not an exact-loaded-ELF assertion. The extracted objects and module metadata remained byte-stable; all strict source fingerprints and native payload hashes passed. No cache mutation, compilation, CUDA module load, driver call or GPU run occurred.

The unchanged total grid is 2368 CTAs on 148 SMs, averaging 16 CTAs/SM. This is **not an enforced per-SM cap or a measured residency trace**. Higher capacity may redistribute quantizer CTAs or permit earlier dependent FC2 scheduling even though total grid size is unchanged. The native pilot's capacity query does not establish actual concurrent occupancy during the MoE graph.

| Tokens | Capacity / valid padded / live rows | E2E change | Repeat spread C / A | Intermediate exposed delta | FC2 start C → A | FC2 exposed delta |
|---|---|---:|---|---:|---|---:|
|4096|220672 / 131840 / 90112|−2.827503%|0.0979 / 0.0900%|+14.768µs|271.978 →187.201µs|−0.016µs|
|16384|491008 / 426752 / 360448|−3.693679%|0.0534 / 0.0244%|+63.961µs|994.918 →601.100µs|+0.449µs|

All observed clocks for these cells are 2032 MHz/reason0. FC2 duration rises 204.626→305.186µs and 525.499→986.983µs respectively, while its exposed tail stays nearly constant. The intervals establish a changed overlap pattern, not its physical residency cause. Lower registers/instruction counts do not negate these tight losses, and there is no spill-based explanation. No rescue timing or policy change is proposed.

`analyze.py` verifies extraction hashes, whole-cubin pilot identity, recipe/tactic/source joins, all 8 phase/token symbol joins and exact row geometry. `summary.json` preserves the full two primary cells and their component medians. Raw timing remains in `evidence/paired-4over6-error-combined/1793402557132732000/data/results/tp-nemo3-ultra-per-token`.
