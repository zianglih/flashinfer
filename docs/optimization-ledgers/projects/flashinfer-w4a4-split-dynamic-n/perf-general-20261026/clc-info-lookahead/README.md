# CLC metadata lookahead beyond accumulator slots

Frozen candidate b85eff41 + ab24777c; matched control b85eff41 +97cf417d all-CLC policy. Source: `flashinfer-clc-info-lookahead-20261027`. Only the private metadata depth default/accounting differs from control, with explicit positive overrides retained and one tile per CLC ticket. This is a separate experiment from depth=acc_stages.

Automatic depth is acc_stages+1. It gives a two-window partial-TMEM-overlap geometry depth2, and ordinary double-buffered accumulators depth3. The extra slot is intended to let operand producers obtain metadata beyond occupied accumulator slots; it may instead hoard work or add instructions. No model, dtype, dimension or cluster threshold is introduced.

The64-replay source-paired exact gate passed onGPU6: all four affected formats, PDL on/off, one/two CTA, N16/N128, empty and reactivated routes. Non-power-of-two metadata depth3 was compiled and exercised. Source pins and output byte hashes match; every observed operand-stage count and K choice is unchanged. Dynamic shared memory grows by0 or128bytes after alignment. `validation.json` gives per-phase resources. Independent SDK phase/index/tail and accounting review covers arbitrary positive depth.

Fixed CAAC timing runs onGPU6 at K3 native-all-CLC geometry, V41 mixed and K3 published geometry, allT16384. Public10warmup100cold-L2 CUPTI graph samples, initial input quantizer included for NV, fused finalization disabled, saved tactics and routes verified. These are explicit all-CLC fixed-geometry comparisons, not native AUTO retention. All prefill and decode comparisons are complete. No sanitizer or exhaustive geometry product.

## Completed V3 EP8 T16 decode screen

Same saved geometry, routes, source-paired CAAC and100cold-L2 CUPTI samples per run. Both controls and candidates repeated twice. These are fixed diagnostics, not native AUTO retention.

|Backend|Control ms|Candidate ms|Speedup|
|---|---:|---:|---:|
|CuteDSL MXFP8|0.11147225|0.11524050|0.96730×|
|CuteDSL MXFP4x8|0.06900825|0.07388875|0.93395×|
|CuteDSL W4A4|0.06960825|0.07230450|0.96271×|
|CuteDSL PER-TOKEN|0.07487250|0.07716000|0.97035×|

All runs completed,100samples per backend, matching routes and exact saved hits, source/cache pins unchanged. Every observed operand depth and K choice stays unchanged: MX uses five operand stages and two accumulator stages; NV uses four operand stages and two accumulator stages. The metadata queues expand1→2 or1→3. The regressions do not establish tile reservation as the sole cause; codegen/resource and phase profiles are being collected separately. **Do not retain this automatic policy.**

## Completed T16384 prefill screen

|Geometry/backend|Control ms|Candidate ms|Speedup|
|---|---:|---:|---:|
|kimi-k3-native-clc/CuteDSL W4A4|0.90330725|0.89031575|1.01459×|
|kimi-k3-native-clc/CuteDSL PER-TOKEN|1.22722875|1.19115725|1.03028×|
|kimi-k3-published/CuteDSL W4A4|1.02794050|0.97451675|1.05482×|
|kimi-k3-published/CuteDSL PER-TOKEN|1.26815750|1.21865325|1.04062×|
|v41-flash/CuteDSL MXFP4x8|0.90733225|0.89464300|1.01418×|

K3 gains repeat with both geometries. V41 controls drift .920548→.8941165ms, so its1.014× paired result is not a strong independent signal. These prefill improvements do not outweigh the decode regressions.

## Final policy decision

Keep the single-stage metadata queue and the180-tactic, four-field all-CLC search. Both universal deeper defaults are rejected by the decode evidence. No metadata-depth autotune axis is pursued: adding one would defeat the requested reduction in search space. Further work, if justified, must simplify the single policy rather than add model/dtype dispatch or more tuning dimensions. No additional GPU runs or cancellation-timeline captures are scheduled.
