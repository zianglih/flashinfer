# One-CTA wide-N pipeline diagnostic

Frozen13ca control. Immutable overlapping-accumulator code copied from the
NB2/wide-N experiment. `dedicated` enables separate epilogue warps (288 threads)
for one-CTA FC1; `overlap` additionally alternates partially overlapping N256
accumulators. N128 uses two full accumulator banks. No external layout, cache,
tactic, or production source change. `manifest.json` records exact module hashes.

48 paired exact checks passed across six formats, N128/256, per-token and
quantized outputs, short/tail K and repeated persistence. Native isolated phase
output/SF byte checks pass on all rows below. C1 B200 GPUs3/7,26.05 CUDA13.2,
10 warmups/100 cold-L2 graph/CUPTI samples, actual seeded DeepSeek routing.

|Run|Tokens|FC1 median microseconds|
|---|---:|---|
|nv-prefill-r1|4096|baseline 170.8320; dedicated 157.2325; overlap 156.6405|
|nv-prefill-r1|8192|baseline 253.5680; dedicated 229.6650; overlap 229.9840|
|nv-prefill-r1|16384|baseline 428.0970; dedicated 376.6570; overlap 378.8645|
|nv-n128-r1|4096|baseline 149.3440; dedicated 136.1280|
|nv-n128-r1|8192|baseline 251.2010; dedicated 224.2880|
|nv-n128-r1|16384|baseline 428.8810; dedicated 382.8815|
|mx-n256-r1|4096|overlap 266.8970; dedicated 266.1285; baseline 277.4085|
|mx-n256-r1|8192|overlap 355.7775; dedicated 356.4805; baseline 378.8010|
|mx-n256-r1|16384|overlap 584.0175; dedicated 611.8895; baseline 622.5460|

Dedicated epilogue warps improve these previously serialized one-CTA kernels,
but the resulting prefill timings remain slower than existing two-CTA/NB2
options. N256 accumulator overlap adds little for NVFP4. Do not broaden the
production warp policy from this diagnostic alone. No primary sweep or saved
B1 rerun; no new AUTO tactic. Raw logs/JSON preserve every sample and source
manifest. Further pipeline work remains focused on two-CTA/NB2 lifetimes.
