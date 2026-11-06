# CLC metadata queue depth experiment

Source is b85eff41 plus identical frozen six-field all-CLC policy. Control patch97cf417d; candidate patch5920de4f. The candidate adds automatic metadata depth equal to accumulator stages, retaining explicit positive overrides. It changes only the Blackwell core and two wrapper defaults relative to control. Both source-private remote copies are frozen; local candidate remains unstaged.

The prior occupancy-bounded ticket design is rejected and is not present. CLC still assigns one tile per ticket and acquires a metadata slot before cancelling another ticket.

## Validation

64 source-paired exact graph replays passed: standard/per-token NVFP4,MXFP8,MXFP4x8; PDL on/off; N16/N128 and one/two CTA; balanced/skewed/empty/reactivated routes. Inputs and router weights change across replays. Cross-source byte hashes and zero-tolerance comparisons agree, source pins unchanged, metadata depth2 actually compiled for all formats. All operand depths and K choices in the gate remain identical. Independent review passed1,280 host accounting assertions and checked installed-SDK phase/index/tail behavior; see `scripts/clc_metadata_single_owner_20261026/depth-review.{json,md}`.

This first formula intentionally leaves single-accumulator partial-TMEM-window geometries at depth1. No dedicated sanitizer or exhaustive geometry product was run. The current decode screen below confirms a repeatable tradeoff; the automatic policy is not retained.

## Timing

GPU7 B300/SM103, image `nvcr.io/nvidia/pytorch:26.05-py3`,CUDA13.2,CuTe4.7.1. Public10warmup100cold-L2 CUPTI graph samples, initial input quantization included for NV, fused finalize disabled. Current all-CLC versus candidate in CAAC order; exact saved native geometry/routing retained, scheduler flags explicitly set allTrue in private cache copies. First K3 published geometry, then V41 mixed and K3 native-all-CLC geometry. These are fixed causal diagnostics, not native AUTO retention. Prefill CAAC complete; decode safety screen complete. All observed operand depths and K choices are unchanged across the pair.

| Geometry/backend | Current CLC ms | Derived-depth ms | Speedup |
|---|---:|---:|---:|

|kimi-k3-native-clc/CuteDSL W4A4|0.905563|0.904834|1.0008×|
|kimi-k3-native-clc/CuteDSL PER-TOKEN|1.231939|1.204483|1.0228×|
|kimi-k3-published/CuteDSL W4A4|1.031610|0.990811|1.0412×|
|kimi-k3-published/CuteDSL PER-TOKEN|1.270963|1.227948|1.0350×|
|v41-flash/CuteDSL MXFP4x8|0.911914|0.915683|0.9959×|

K3 native-all-CLC W4A4 keeps its single-accumulator metadata depth1 and is neutral as expected; its per-token FC1 uses two accumulators and benefits. V41 mixed is neutral within drifting controls. V3T16 all-format decode CAAC is complete; this automatic policy is not retained because of repeatable decode regressions.

## Completed V3 EP8 T16 decode screen

Same saved geometry, routes, source-paired CAAC and100cold-L2 CUPTI samples per run. Both controls and candidates repeated twice. These are fixed diagnostics, not native AUTO retention.

|Backend|Control ms|Candidate ms|Speedup|
|---|---:|---:|---:|
|CuteDSL MXFP8|0.11136800|0.11496825|0.96868×|
|CuteDSL MXFP4x8|0.06892825|0.07393625|0.93227×|
|CuteDSL W4A4|0.06949600|0.06991225|0.99405×|
|CuteDSL PER-TOKEN|0.07480050|0.07488825|0.99883×|

All runs completed,100samples per backend, matching routes and exact saved hits, source/cache pins unchanged. Every observed operand depth and K choice stays unchanged: MX uses five operand stages and two accumulator stages; NV uses four operand stages and two accumulator stages. The metadata queues expand1→2 or1→3. The regressions do not establish tile reservation as the sole cause; codegen/resource and phase profiles are being collected separately. **Do not retain this automatic policy.**

## Final policy decision

Keep the single-stage metadata queue and the180-tactic, four-field all-CLC search. Both universal deeper defaults are rejected by the decode evidence. No metadata-depth autotune axis is pursued: adding one would defeat the requested reduction in search space. Further work, if justified, must simplify the single policy rather than add model/dtype dispatch or more tuning dimensions. No additional GPU runs or cancellation-timeline captures are scheduled.
