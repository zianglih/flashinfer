# W4A16 N3U TP8 prefill pipeline diagnosis

Source: retained `02de7785c10847b3528340840bed40bd405d85b4`. This is a read-only diagnostic; no source, compiler flags, tactics, routing, register quotas, or pipeline stages change. Original C2 B300 node GPU0 handles FC1 and GPU1 handles FC2; each lane serializes the bounded native metrics pass and SourceCounters pass. Existing persistent C++ and CuTe caches remain intact.

The fresh full W4 table has N3U TP8/T16384 at 1947.880 us, with 0.122% between-pass spread. It improves 16.32% against pre-PR W4A16 (2265.774 us). TRTLLM W4A4 is 1065.527 us, but that is a different-precision target, not a W4A16 backend-equivalence or regression claim. Against an earlier noninterleaved retained-822 AA campaign, current is 2.73% slower; those independent campaigns do not causally attribute a regression to the small packed-scale helper change.

Current native CUPTI medians, first/second 100-sample pass:

| Stage | First us | Second us |
|---|---:|---:|
| E2E | 1946.6885 | 1949.0725 |
| FC1 | 825.623 | 825.415 |
| FC2 | 816.6625 | 818.6155 |
| Combine | 321.250 | 321.507 |

These kernels overlap; stage spans are not additive. Source records are `evidence/r2-w4-full/1793362889737047000/data/results/tp-nemo3-ultra-w4a16/{analysis.json,0-candidate/results.json,1-candidate/results.json}`. That W4 source is production-equivalent to02de.

The recorded cache choice is `-1`, not a new fallback: the unchanged tuner maps it to `None`, and the unchanged launcher resolves both stages to `((256,128,256),(2,1),True)`. True means raster-M, not CLC. Native configuration receipts independently resolve FC1 CLC=true, FC2=false, both two-CTA and PDL=true; actual logical GEMMs are FC1 M640/K2048 and FC2 M2048/K640. Preserve the recorded cache entry exactly and join the resolved configuration to the same loaded compiled library/resource receipt.

## Why this profile is new

The bounded history search found current-project native PC profiles for swap W4A4 and MXFP8, but none for N3U TP W4A16. The latest post-gather W4 iKET diagnosis in the old project covers gated K3 EP8/4096 and V41F TP4/4096, not this nongated many-expert TP workload. Their output-store and decoded-slot waits were near the32ns marker floor and did not justify moving acquires. See old-project `fc1-gather-20261028/optimization-next-20261029/w4-output-acquire-iket-b52/RESULTS.md` and `CLOSED_LEADS.md`.

Already closed: dequant register redistribution; route-ID batching; raw/decoded inventory balancing; raw wait simplification; per-work-tile lookahead; plain reordering of decoded-slot/raw/SF waits; FC2 late output acquire. The current repeated source `elect_one` calls in W4 MMA lower into a continuous native UMMA sequence and are not evidence of repeated native elections. No new source cleanup is justified from source appearance alone.

## Diagnostic boundary

The existing public benchmark profiler mode replays its frozen native graph under NCU application replay, `--cache-control none --clock-control none`. Metrics and SourceCounters select one actual FC1 or FC2 kernel. NCU perturbs overlap, so its times are diagnostic only and cannot replace native CUPTI retention timing. Every process checks the unchanged cache and route hashes, forbids AUTO/profiling, validates the recorded default resolution, and retains the actual loaded PTX/cubin/SASS with original compile options and native zero-local/register/thread guards. Full13,245-file source inventory is verified once before/after the campaign; the relevant source subset is checked before/after each process.
