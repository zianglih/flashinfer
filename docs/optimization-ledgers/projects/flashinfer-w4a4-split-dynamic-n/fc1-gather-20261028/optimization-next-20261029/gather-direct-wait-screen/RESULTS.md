# Direct one-CTA Gather4 completion — full24 screen

Candidate `c5373aa1` on retained `b52e4e09`; its inactive review is retired after source/patch proof. One-CTA FC1 MMA waits on the original local payload/SF barrier; two-CTA relay, operand reuse, arithmetic, PDL, FC2, W4A16, shared storage and tactics are unchanged.

**Decision: rejected.** The affected20-cell aggregate is **+0.0062%**, effectively neutral. The user rejects additional kernel complexity (`gather_relay` and the one-/two-CTA policy split) without a useful performance gain. The24-cell aggregate is+0.0398%; neither is a speedup claim. Tight N3U TP16K W4A4−0.430% and N3U EP8 MXFP4x8−0.408% remain alongside tight V41F TP8 W4A4+0.415% and N3U TP4K W4A4/per-token+0.261/+0.253%. The earlier instruction-sanity retention recommendation was superseded by this explicit user criterion. No commit or publication includes this experiment. The dead-relay-storage cleanup direction is stopped before implementation.

## Qualification and boundary

- 41 existing exact cases /80 captures passed all matched geometry/quota/resource guards.78 zero-local captures; two inherited M512/K8 MX synthetic captures remain128B stack/16LDL/16STL. No new spill. No sanitizer.
- 26 compile-only captures:8 affected FC1 kernels remove24–46 non-NOP instructions and6–14 branch/control sites;18 unaffected binaries identical. Expanded exact captures: all70 unaffected PTX identical;69 CUBINs identical. FC2 index35 differs only in12 uniform-register operands with identical2328-op sequence/resources; retained in qualification notes.
- 24 predeclared cells across4 models,EP/TP,4 formats;6 per format,20 one-CTA affected/4 two-CTA controls,11 CLC/13 static. Frozen native winners; no retune. Existing MXFP8 prefill winners are two-CTA, so affected MXFP8 coverage reaches512 tokens while16K is an unchanged control.
- Same physicalGPU per complete C–A–A–C on B300 GPUs2/3, CUDA13.2, CuTe4.8, stock clocks.100 strict CUPTI samples/phase,10 warmups,cold-L2 CUDA graphs, normal compiler/cache.84 phases /9,600 samples;184 loaded native functions pass zero-local/runtime guards. No historical baseline rerun.
- Primary cell formula: `100*(sqrt(C1*C2/(A1*A2))-1)` using phase medians. Aggregate is geometric across all listed ratios. Decode≤256,middle257–512,prefill≥4096 as declared before timing.11 negative rows retained; no clock/spread exclusion.
- All NVML quartile windows observed. Largest repeat spreads: control3.689% (V3 EP16K MXFP4x8),candidate6.249% (N3U EP16K MXFP8). These unchanged controls' apparent gains are inconclusive.

## Aggregate

|Scope|Cells|E2E|FC1 span|FC2 span|
|---|---:|---:|---:|---:|
|all|24|+0.0398%|-0.0102%|-1.3072%|
|affected|20|+0.0062%|+0.0392%|-1.6130%|
|unchanged|4|+0.2079%|-0.2567%|+0.2360%|

FC durations overlap under PDL and must not be summed or interpreted as isolated throughput. In V3 EP8 MXFP8 T8, FC2 starts46.6→31.3µs after chain start, but ends at≈87.2µs in both arms; its longer measured span drives the FC2 aggregate without a comparable E2E loss. All four timeline medians are preserved in `timeline-analysis.json`. N3U TP16K W4A4 has a real measured FC1-span loss of1.131% with tight repeats; this is not hidden by the aggregate.

## Complete E2E results

|Model / mode|Tokens|Format|C1 µs|A1 µs|A2 µs|C2 µs|Speedup|C spread|A spread|
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
|V3 EP8|16|W4A4|68.017|68.080|67.984|68.049|+0.001%|0.047%|0.140%|
|K3 EP8|32|W4A4|173.665|173.985|174.145|173.985|-0.138%|0.184%|0.092%|
|V41F TP4|8|W4A4|52.417|52.208|52.192|52.416|+0.415%|0.002%|0.031%|
|N3U TP8|4096|W4A4|377.827|376.786|377.010|377.938|+0.261%|0.030%|0.059%|
|N3U TP8|16384|W4A4|1183.159|1188.183|1188.376|1183.190|-0.430%|0.003%|0.016%|
|N3U EP8|16384|W4A4|592.899|593.172|593.508|592.564|-0.102%|0.057%|0.057%|
|V3 EP8|8|PER-TOKEN|62.192|62.192|62.047|62.256|+0.168%|0.102%|0.234%|
|K3 TP8|8|PER-TOKEN|80.833|80.720|80.896|80.928|+0.090%|0.118%|0.218%|
|V41F TP4|8192|PER-TOKEN|743.012|742.277|742.133|742.629|+0.083%|0.052%|0.019%|
|N3U TP8|4096|PER-TOKEN|554.979|554.083|553.635|555.538|+0.253%|0.101%|0.081%|
|N3U TP8|16384|PER-TOKEN|1801.674|1798.842|1797.899|1801.914|+0.190%|0.013%|0.053%|
|K3 EP8|8192|PER-TOKEN|640.532|640.404|640.516|639.988|-0.031%|0.085%|0.018%|
|N3U EP8|8|MXFP4x8|46.688|46.880|46.912|46.721|-0.408%|0.071%|0.068%|
|V41F EP4|32|MXFP4x8|118.736|118.769|118.769|118.625|-0.074%|0.094%|0.000%|
|V3 TP8|8|MXFP4x8|51.088|50.928|50.896|50.945|+0.205%|0.283%|0.064%|
|K3 TP8|512|MXFP4x8|348.386|348.642|349.074|348.754|-0.083%|0.105%|0.124%|
|N3U TP8|8192|MXFP4x8|684.963|683.828|688.755|682.371|-0.382%|0.380%|0.721%|
|V3 EP8|16384|MXFP4x8|648.068|647.172|668.869|671.972|+0.301%|3.689%|3.353%|
|V3 EP8|8|MXFP8|89.056|89.089|89.120|89.008|-0.081%|0.054%|0.035%|
|V3 EP8|512|MXFP8|246.242|246.178|246.098|245.873|-0.033%|0.150%|0.032%|
|V41F EP4|128|MXFP8|461.859|461.651|462.002|462.002|+0.023%|0.031%|0.076%|
|V3 TP8|8|MXFP8|70.945|70.976|70.928|71.072|+0.079%|0.179%|0.068%|
|N3U TP8|32|MXFP8|180.449|180.514|180.513|180.545|-0.009%|0.053%|0.000%|
|N3U EP8|16384|MXFP8|867.732|887.956|835.732|866.644|+0.666%|0.126%|6.249%|

## All FC1/FC2 components

|Job|Tokens|Format|E2E|FC1|FC2|
|---|---:|---|---:|---:|---:|
|ep-v3-w4a4-w4a4|16|CuteDSL W4A4|+0.001%|+0.000%|-0.207%|
|ep-kimi-k3-w4a4-w4a4|32|CuteDSL W4A4|-0.138%|-0.236%|-0.267%|
|tp-v41-flash-w4a4-w4a4|8|CuteDSL W4A4|+0.415%|+0.434%|+0.002%|
|tp-nemo3-ultra-w4a4-w4a4|4096|CuteDSL W4A4|+0.261%|+0.928%|+0.126%|
|tp-nemo3-ultra-w4a4-w4a4|16384|CuteDSL W4A4|-0.430%|-1.131%|-0.293%|
|ep-nemo3-ultra-w4a4-w4a4|16384|CuteDSL W4A4|-0.102%|-0.141%|-0.225%|
|ep-v3-per-token-per-token|8|CuteDSL PER-TOKEN|+0.168%|-0.090%|+0.139%|
|tp-kimi-k3-per-token-per-token|8|CuteDSL PER-TOKEN|+0.090%|+0.041%|-0.155%|
|tp-v41-flash-per-token-per-token|8192|CuteDSL PER-TOKEN|+0.083%|+0.362%|+0.036%|
|tp-nemo3-ultra-per-token-per-token|4096|CuteDSL PER-TOKEN|+0.253%|+0.753%|+0.157%|
|tp-nemo3-ultra-per-token-per-token|16384|CuteDSL PER-TOKEN|+0.190%|+0.479%|+0.279%|
|ep-kimi-k3-per-token-per-token|8192|CuteDSL PER-TOKEN|-0.031%|-0.074%|-0.156%|
|ep-nemo3-ultra-mxfp-w4a8|8|CuteDSL MXFP4x8|-0.408%|-0.345%|-0.390%|
|ep-v41-flash-mxfp-w4a8|32|CuteDSL MXFP4x8|-0.074%|-0.053%|+0.112%|
|tp-v3-mxfp-w4a8|8|CuteDSL MXFP4x8|+0.205%|+0.129%|+0.330%|
|tp-kimi-k3-mxfp-w4a8|512|CuteDSL MXFP4x8|-0.083%|-0.116%|-0.319%|
|tp-nemo3-ultra-mxfp-w4a8|8192|CuteDSL MXFP4x8|-0.382%|-0.482%|-0.711%|
|ep-v3-mxfp-w4a8|16384|CuteDSL MXFP4x8|+0.301%|+0.096%|+0.278%|
|ep-v3-mxfp-mxfp8|8|CuteDSL MXFP8|-0.081%|-0.079%|-27.184%|
|ep-v3-mxfp-mxfp8|512|CuteDSL MXFP8|-0.033%|+0.071%|-0.070%|
|ep-v41-flash-mxfp-mxfp8|128|CuteDSL MXFP8|+0.023%|-0.000%|+0.226%|
|tp-v3-mxfp-mxfp8|8|CuteDSL MXFP8|+0.079%|+0.054%|+0.090%|
|tp-nemo3-ultra-mxfp-mxfp8|32|CuteDSL MXFP8|-0.009%|+0.083%|+0.121%|
|ep-nemo3-ultra-mxfp-mxfp8|16384|CuteDSL MXFP8|+0.666%|-0.904%|+1.053%|

No repeat, tactic change, source mutation, or unused relay-storage cleanup was folded into this screen. The proposed storage cleanup was read-only and is stopped without source changes.
