# Narrow epilogue co-design: unretained

Unretained: intended codegen/resource reductions and exactness passed, but full-chain0.996049x atT32 and1.000514x atT128 are neutral.

Both arms use corrected `aab93f854054de834447bdd8985b8bbd653fb3c8`. The candidate remains two unstaged files in independent `flashinfer-epilogue-codesign-review`. Production was not changed. GPU2 is released; no further tuning on this axis.

|Tokens|Phase|Control medians (us)|Candidate medians (us)|Control/candidate|
|---:|---|---|---|---:|
|32|full_chain|107.3125, 107.3920, 108.0960|107.6485, 107.9365, 108.4960|0.996049x|
|32|fc1|66.3360, 66.9440, 67.0880|66.5605, 66.9600, 66.6080|1.001188x|
|32|fc2|35.5200, 35.4560, 35.5200|35.4240, 35.5520, 35.5200|1.000001x|
|128|full_chain|145.1520, 144.8970, 145.1680|144.8805, 144.9125, 145.2005|1.000514x|
|128|fc1|89.5690, 90.1600, 90.4480|89.6490, 90.0005, 89.6000|1.003438x|
|128|fc2|48.2245, 48.2080, 48.0480|48.1755, 48.2240, 48.2080|0.999120x|

Same actual native input/routing and fixed N16 tactic, adjacent ABA/BAB,10 warmups/100 cold-L2 CUDA-graph CUPTI samples perarm. All36 phase/full arms and3600 samples are archived. Input activation quantization excluded; regular preparation included in fullchain/FC1. GPU2 B200-92 UUID `GPU-7e973000-5213-bf29-4ca1-25a6d947f8e3`, NVIDIA PyTorch `26.05-py3`,CUDA13.2.78. No old-node/TRT or primary/AUTO comparison.

The candidate uses physical B/C16, native up/gate loads, the same three packed-FP4 shuffles, +0-seeded maxNum, two distinct-value packed scale conversions, one distributed SF store, and an accumulator release immediately after native loads complete. Four operand stages/two accumulator stages,288threads,148CTA grid,128TMEM columns and `min_blocks_per_mp=1` stay unchanged. Existing SF publication and all aab proxy-order fixes remain. There is no explicit max-register cap or setmaxnreg specialization.

Generated NVFP4 N16 FC1 only; explicit per-token exclusion leaves its BF16 path unchanged. The redundant terminal wait in shared `run` is removed, with both callers retaining core drains on other paths; the direct branch skips its late drain/release after the earlier one. All existing core iKET calls are unchanged. No new weight layout, SF publisher, extra kernel, or broader architecture is introduced.

Fresh corrected-aab versus candidate checks passed seven persistent/tail cases (K64/384/1216, per-token fallback, zero routes), two exceptional-input cases (all E4M3 SF NaN and negative-zero FP4 payload), and native T32 FC1/SF/FC2/full output bytes. A separate one-specialization scalar/vector SF probe passed1016 values covering every positive finite E4M3 midpoint with adjacent FP32 values, signs,±0,±Inf,NaN; both SF bytes and decoded reciprocal/clamp FP32 bytes matched at norm1 (not exhaustive over every norm). This is bounded exactness, not broad dtype/API or sanitizer coverage.

|Resource/codegen|Control|Candidate|
|---|---:|---:|
|Registers/thread|64|45|
|Dynamic SMEM bytes|197504|181120|
|Local bytes / spills|0 / none|0 / none|
|Driver active CTA/SM|1|1|
|TMEM load sites|7|2|
|TMEM store sites|3|0|
|TMEM load-wait sites|2|1|
|SF encode pair sites|1 (duplicate scalar)|2 (four distinct scales)|
|SF byte-store sites|1|1|
|Static SASS excl. final padding|1141|1093|

Candidate PTX loads are lines514/520; wait525; accumulator arrival527, before activation. The intended improvement relative to prior physicalN16 is four SF stores→one and four duplicate-pair SF conversions→two distinct-pair conversions. Static site counts do not establish a causal speedup.

Core SHA `8623cdbdf786d24a2c9b12437bc939b33cf85f6b73426e2fa558b07ab6edec60`; utils SHA `a9a3754a0d2e95594f202d0814352b6caf33ae6ea606c3f8645704e9752bb4af`. Raw archive SHA `9e490bdd61df3571ebcc1c09c84b8c2d9c6df2f8d0003cd76fda70799047b24c`. Source/helper/raw timing/codegen/environment pins are in `summary.json`, `fetch-receipt.json` and `files-sha256.json`.

Reproduce the bounded workflow with `scripts/epilogue_codesign_experiment/run_smoke.sh` then its local archived `run_pairs.sh` on the same environment after provisioning exact manifest sources. The executed timing command was the same two-token loop directly through managed h; the initially copied remote run_pairs helper was not invoked (it retained an already-completed compile-only step). No existing measurement is rerun by these archival scripts.
