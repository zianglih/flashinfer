# W4A16 static-weight-extents and synchronization audit

The frozen candidate specializes known weight M/K, keeps token N dynamic, and keys the compiled kernel by M/K. It changes two source files, 6 additions and 6 removals, and changes no numerical or synchronization contract. Keep as an instruction-sanity simplification if the composed AUTO gate remains acceptable; this isolated screen does not establish a latency gain.

- Base: `1496b557f9b606f3a0bb36bcebf5293d3e11555a`.
- Unstaged source: `../../flashinfer-w4a16-sync-review` relative to this directory; exact patch: `static-weight-extents.patch`.
- Full-index deployment patch SHA256: `6f859e6262735ef8606615adf1eb81ab4e7a6f3ee136412ebbd594a1fa7b2222`.
- Runtime deployment and persistent native cache proof: `deployment.json`, `evidence/source.json`, `evidence/cache.json`. Eight existing native artifacts/cache directories reused only after native source parity verification; CuTe source objects remain private. No AUTO timing cache was copied.
- Full resource/barrier map and independent composition review: `audit.md`. No synchronization blocker found. Distinct transformed-weight and activation rings remain independent; all publication/reuse hazards and `pipeline_init_wait` are preserved.

## Correctness and dynamic cache behavior

Existing focused W4A16 coverage: **39 passed, 695 deselected**, including exact weight-scale mapping, routed tails, one/two-CTA and cluster-2 variants, SiTU, GeGLU and graph replay. Logs and selected node IDs: `evidence/screen/gpu4/exact.log`, `exact-selection.json`, `exact-junit.xml`. No production tests were added for this candidate. Scoped pre-commit, Python compilation and `git diff --check` passed.

All six fixed-tactic source pairs below produced identical complete output-byte hashes, with finite outputs. For each of V3/V4.1/K3, the same weight tensors at N=16 and N=15 reused exactly the same W4A16 cache entries and did not invoke another core compilation. Cache keys contain M/K; N remains absent and is still passed through the runtime ABI.

## Isolated fixed-tactic timing screen

The helper calls the existing public W4A16 benchmark implementation with fused finalize disabled. One reserved B300 per model screen; native graph+CUPTI, cold L2, 10 warmups and 100 samples per arm; order C/A/A/C. T16 uses `(128,16,256)/(1,1)`, T4096 uses `(256,128,256)/(2,1)` for both FCs. Model settings are V3 EP8, V4.1-Flash EP4 and K3 EP8. These timings isolate static extents, before root's CLC/preparation composition.

| Model | Tokens | C0 ms | A0 ms | A1 ms | C1 ms | mean(C medians)/mean(A medians) |
|---|---:|---:|---:|---:|---:|---:|
| V3 | 16 | 0.0735200 | 0.0733920 | 0.0733610 | 0.0733925 | 1.0011x |
| V3 | 4096 | 0.2913780 | 0.2913780 | 0.2917620 | 0.2907220 | 0.9982x |
| V4.1-Flash | 16 | 0.0688170 | 0.0689445 | 0.0689280 | 0.0689760 | 0.9994x |
| V4.1-Flash | 4096 | 0.4442755 | 0.4467560 | 0.4461630 | 0.4577475 | 1.0102x |
| K3 | 16 | 0.1179690 | 0.1180330 | 0.1180480 | 0.1181290 | 1.0001x |
| K3 | 4096 | 0.5321150 | 0.5325480 | 0.5322120 | 0.5483400 | 1.0147x |

Decode is neutral. V4.1/K3 ending controls drifted about 3%; their apparent prefill gains are not retained as performance claims. Additional C/A rechecks were noisy in opposite directions (V4.1: 0.445891→0.455107 ms; K3: 0.575188→0.5328835 ms), so use root's composed AUTO comparison for performance retention.

All 2,400 raw samples and source/hash evidence are in `evidence/`; `analyze.py` selects only complete points. Valid V3 points are from `screen/gpu5`; corrected V4.1/K3 points are from `screen-v2/gpu4` and `screen-v2/gpu5`. Earlier incomplete helpers are excluded (wrong initial tactic tuple, then stale precomputed routes during the N=15 cache check). `evidence.zip` SHA256: `a4bc3c212aac8feb5080a7170a001ef7c9f7732cd66ede173021667b47110d8b`.

## Verified generated code

Initial parallel same-CWD artifact captures were inconsistent and are excluded. The replacement capture uses separate per-core CWD/cache directories, serial compilation, documented `CUTE_DSL_NO_CACHE=1`, and immediate PTX/cubin extraction. It verifies all 24 source/native-cache-key matches, PTX/cubin names, artifact hashes, activation signatures and resources. K3 SiTU has the expected 24/48 exp2 sites for the two tilers in both PTX and SASS; FC2 has none. The helper also corrects unused FC2 activation parameters to exactly match the native launcher cache key.

| Model | Tokens | FC1 non-NOP SASS C→A | FC2 non-NOP SASS C→A |
|---|---:|---:|---:|
| V3 | 16 | 1472→1448 | 1582→1501 |
| V3 | 4096 | 1611→1575 | 1704→1629 |
| V4.1-Flash | 16 | 1500→1476 | 1582→1498 |
| V4.1-Flash | 4096 | 1667→1632 | 1704→1625 |
| K3 | 16 | 1599→1575 | 1582→1501 |
| K3 | 4096 | 1867→1832 | 1704→1629 |

Across these 12 corresponding cores: **19,574→18,921 non-NOP static instructions (-653, 3.34%)**, with 128 registers/thread, zero stack/local memory and no LDL/STL throughout. Including padding, the counts are 19,912→19,264 (-648), reducing each core by 24–80 instructions. The reductions include uniform loop/bound predicates, integer address/division work and reconvergence instructions; UMMA opcode counts are unchanged. These are static compiled instruction counts, not a measurement of executed instructions or a latency estimate.

Fresh core compile API medians were 2.497s control and 2.505s candidate (one fresh compile/core; observational, not a controlled compile-speed result). Shape specialization requires a variant when M/K changes, while preserving reuse across token counts. The three requested models already differ in expert count and therefore already required distinct cache entries before this change.

Validated artifacts and opcode deltas: `codegen-isolated/analysis.json`; reproducible checker: `codegen_analyze.py`. Archive SHA256: `519a9936dfb9bc72e9e1b4e5f05638022c267bd07b33fa75176bc3f82e202d9c`. GPU7 was released after capture. GPUs4/5 were previously released after the runtime screen.

Root's composed candidate also includes `max_active_clusters` in the kernel key to fix a preexisting static scheduler-capacity cache omission, and is independently testing changed SM capacities. That correction is not part of this isolated patch or timing screen.
