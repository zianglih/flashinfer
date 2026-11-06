# Occupancy-bounded CLC work experiment

Current frozen candidate: `7f4e1703` plus full patch `3a8fca08c1c1862e879f1b40eea4698371a6a9cb6939754d63665af1cdc03875`, containing frozen all-CLC policy and the isolated two-file bounded-grid mapping. Local source is `flashinfer-clc-bounded-work-20261026`, all changes unstaged. No native AUTO or retained performance claim.

The physical ticket count is derived from resident CTA groups and the existing one-slot metadata lookahead: Q = (SM count / CTA group size) × (1 + metadata slots). Each ticket owns a balanced contiguous interval of the runtime live tile count; the next ticket is reserved only at the current interval's last tile after its metadata slot is acquired. See the mapping proof and source pins in `scripts/clc_bounded_work_20261026`.

## Exact gate

The second helper run passed 96 source-bound exact replays: 64 control (static/static and current CLC/CLC) and 32 candidate. It covers standard/per-token NVFP4, MXFP8, MXFP4x8, PDL on/off, N16/N128, one/two CTA, SiTU/SwiGLU, changing input and router weights, balanced/skewed/empty/reactivated routes, and multiple live FC2 tiles per ticket in every format. Cross-source output byte hashes and within-source zero-tolerance comparisons agree. Both source trees and all 87 pinned files remained unchanged.

The first helper attempt used the all-CLC source as its static reference. It completed 32 NV control replays, then failed the existing MX all-CLC tactic-admission assertion before executing the candidate. This was a control-helper mismatch; no result from that incomplete run is a correctness or timing claim. The successful gate instead uses the frozen finalguard source for static control.

PDL placement was reviewed in actual source: pre-wait live-count reads remain guarded by the established `prefetch_weights_before_wait` contract. With prefetch disabled the new first interval is derived only after `griddepcontrol_wait`. PDL=true/prefetch=false is covered by source inspection, not a dedicated GPU case. CPU mapping proof 212 cases covers gap/overlap freedom, arbitrary cancellation ordering, zero/partial/Int32-max counts and both CTA ranks. No sanitizer or exhaustive geometry cross-product was run.

## Fixed performance screen

GPU7, B300/SM103, `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2, CuTe4.7.1. Public benchmark 10 warmup / 100 cold-L2 CUPTI graph samples, no fused finalize, initial activation quantization included for NV. Scheduler bits are explicitly overridden on private copies of saved native caches; geometry, routes, source pins and native caches are verified unchanged.

Per geometry: static → current CLC → bounded CLC → bounded CLC → current CLC → static. V41 mixedT16384 first, then K3 NV T16384 at both native all-CLC and published native geometry. These are causal fixed-tactic diagnostics, not replacements for native AUTO retention evidence. All three fixed-geometry screens completed; this candidate is rejected. No decode or broad AUTO follows. Values below are the median of two100-sample public medians, in milliseconds. W4A16 was incidental and is not an affected arm.

| Geometry / backend | Static | Current CLC | Bounded CLC | Bounded vs CLC | CLC vs static |
|---|---:|---:|---:|---:|---:|
|kimi-k3-native-clc / CuteDSL W4A4|0.860578|0.907642|1.001091|0.9067×|0.9481×|
|kimi-k3-native-clc / CuteDSL PER-TOKEN|1.162602|1.231355|1.307508|0.9418×|0.9442×|
|kimi-k3-published / CuteDSL W4A4|0.822106|1.047267|1.080691|0.9691×|0.7850×|
|kimi-k3-published / CuteDSL PER-TOKEN|1.091123|1.273212|1.303084|0.9771×|0.8570×|
|v41-flash / CuteDSL MXFP4x8|0.897194|0.931331|1.031402|0.9030×|0.9633×|

Every process returned successfully and verified source/cache immutability, matching routes, cache hits, and100raw samples. The existing CLC cost is largest at published K3 N128 geometry; native all-CLC geometry retuning partly mitigates that cost. This does not establish the cause of CLC cost or prove padded cancellation dominates. Follow-up investigates metadata queue coupling while preserving one tile per ticket. Raw records, logs and source receipts:75collected artifacts in collection.json.
