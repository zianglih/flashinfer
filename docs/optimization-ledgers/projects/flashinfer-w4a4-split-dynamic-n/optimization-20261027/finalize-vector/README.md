# Vector-outer finalize experiment

Rejected after the three-case codegen/byte screen; see `RESULTS.md`. No28-case
follow-up or timing was run. GPU2 is released and the source-only review clone
is closed. All evidence/helpers remain here; the combined snapshot is untouched.

Source: independent `../../flashinfer-finalize-vector-perf-review` checkout of
e2728a2908f38cbcfa997c031bea059e3724ccde. The sole unstaged change is
`flashinfer/fused_moe/cute_dsl/blackwell/moe_finalize.py`; both Git directories are
inside this project. The source and artifact paths were absent before creation,
and the clone was clean before editing. `control_finalize.py` is the exact
baseline file. `manifest.json` records both source hashes and the patch.

The patch makes vector the outer loop, resetting four packed FP32 accumulators
for each vector and storing its result immediately after the ascending-slot
reduction. Original slot zero still uses the separate multiply; later valid
slots still use ordered FMA, and all-masked rows remain positive zero. Metadata
loads, the PDL wait/trigger, launch geometry, vector width, alignment, masks,
helpers, original comments and license are unchanged. There are no new args,
tactics, branches by dtype/model, or changes to the active preparation candidate.

The rationale and historical exclusions are in
`../prepare/finalizer-ownership-audit.md`. This may reduce accumulator lifetime,
but can also lengthen metadata lifetime, duplicate route/control work or reduce
load/math overlap. No speedup is claimed.

## Codegen first

When capacity is released, deploy this independent source and this directory to
persistent project storage; retain the existing native C++ workspace while using
an isolated strict CuTe cache. Use the established CuTe4.8/CUDA13.2 Python and
`cuobjdump` from CUDA13.2. The managed transport remains
`../../swap-ab-exact-20261027/remote.py`; no new devbox is needed.

```sh
python probe.py --repo /path/to/independent/source --mode codegen --output codegen/result.json
python analyze_codegen.py codegen/result.json
```

This runs three source-paired cases: single-vector H128/top-k8; native seven-
vector H7168/top-k8; and small-hidden H2048/top-k22. It saves actual PTX, cubin,
SASS and resource output for each compilation and checks exact output bytes and
canaries. Inspect actual live accumulator ownership and control duplication,
not just totals. Reject before timing if code generation is unchanged or clear
overhead defeats the register-lifetime hypothesis.

## Bounded exact follow-up

Only after the codegen result is useful:

```sh
python probe.py --repo /path/to/independent/source --mode exact --output exact/result.json
python analyze_codegen.py exact/result.json
```

The 28 cases cover expanded/permuted inputs, all three routing-scale dtypes,
all BF16 bit patterns, rounding/subnormal boundaries, signed zeros, invalid
original slot zero, all-masked poisoned scales, 16-byte-only alignment, zero
tokens, top-k1/2/8/22, partial hidden tiles, native seven-vector geometry, PDL
off/on and three CUDA-graph replays per nonempty arm. This is source-paired
kernel exactness, not new repository testing or sanitizer coverage.

If retained for timing, use the existing fixed-native-winner CUPTI10/100 CAAC
public-chain screen for V3 MXFP4x8 and N3U NVFP4 at4/128/4096/16384 tokens, using
fresh combined-candidate native winners. This includes decode to catch reduced
instruction overlap, alongside prefill. Timing is deliberately absent from
the source/codegen helpers; profiling is only needed if codegen is unclear.
