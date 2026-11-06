# Physical N16 epilogue: source and codegen audit

CPU-only, 2026-10-25. No GPU launches, runtime source changes, or new timing.
The retained checkout is `aab93f854054de834447bdd8985b8bbd653fb3c8`;
its `blackwell/utils.py` is byte-identical to measured98fd (`9811c53e...`).
The physical-N16 prototype uses utils `e14d3300...`. The accompanying JSON
pins both sources and the archived control/prototype SASS. Codegen below is
the saved98fd physical-N16 specialization, not a fresh aab93f compilation.

## What actually became more expensive

The direct path already does the useful structural work: two
`Ld16x256b(Repetition.x2)` loads, eight activated values per lane, no accumulator
transpose or TMEM stores. It halves EX2 sites16→8, packed FMUL sites48→24 and
final FP4 pair-conversion sites8→4. There is no evidence that final FP4
conversion itself expanded or an avoidable FP32→BF16→FP4 roundtrip appeared.

Its register ownership instead holds four different tokens' two channels per
lane. That changes one per-lane scale block into four separately lowered
blocks. In the contiguous first-LDTM through last-STG span:

| Static sites | Retained | Physical N16 |
|---|---:|---:|
| Total |288|367|
| SF FP32→E4M3 pair-conversion |1|4|
| SF E4M3→F16 decode |1|4|
| SF byte stores |1|4|
| Branches |1|4|
| PRMT |13|31|
| LOP3 |9|34|
| SHFL |0|15|

The four SF stores occupy four separately guarded address/reconvergence
regions (candidate PCs0x2380–0x2d60), while three more shuffles plus integer
masks transpose the packed FP4 nibbles. Twelve shuffles are the four independent
eight-lane scale reductions. Whole-kernel static sites grow1144→1224. These
counts are not executed instruction counts or a causal latency attribution.
The old measurements were neutral/mixed: direct-load-only FC1 T32 ratio0.997577;
physical-N16 full-chain T32/T128 ratios0.996584/1.005456. Repeating the unchanged
15-shuffle path is not a new optimization.

Sources: retained utils206–271,455–529,555–597; e14 utils218–249,565–660;
`scripts/physical_n16_experiment/raw/resources-r1/*.sass`;
`scripts/narrow_ld256_epilogue_experiment/README.md`.

## Numerical constraint that must be repaired in any revival

Retained `_absmax` starts at +0 and uses non-NaN-propagating `fmax`. A live block
containing only NaNs therefore has scale maximum +0. e14 starts from two
absolute inputs and applies XOR4/8/16 without the zero seed: an all-NaN block
remains NaN. Its finite/random exact cases do not establish this boundary.
TRT's `reduce_group_max_abs_f32` explicitly filters NaNs with max(abs(x),0)
before the same eight-lane shuffle reduction (`CutlassUtils.h:833–875`).

Use an explicit max-with-+0 for each local two-channel maximum. The CPU model
checks104 signed-zero, subnormal, finite, infinity and NaN patterns; it exposes
the missing-seed difference and shows the seeded tree matches the retained
maximum under maxNum semantics. This is not a GPU exceptional-value test.

Keep every activation and quantization rounding point: alpha multiplication,
the existing clamp and exp2/approx-reciprocal sequence, beta addition and final
up×gate; then `(amax * FP32(1/6)) * norm_const`, rounded SF encode, decoded SF,
approx reciprocal, multiplication by norm_const, finite clamp, value scaling
and RN-saturating FP4 conversion. TRT's pre-reduction scale multiplication and
zero-SF reciprocal branch are different contracts and must not be imported.
Do not fuse multiplies, use FP16 arithmetic, or substitute a different
reciprocal to make the code resemble TRT.

## Two concrete implementations worth considering

1. **Direct loads with one distributed SF store and packed SF conversion.**
   Keep the proved raw mapping and three packed-nibble swaps. Collect the four
   rounded SF bytes; set `g=lane>>2`, and let only `g<4` store `SF[g]` for token
   `2*(lane&3)+(g&1)+8*(g>>1)`. This yields one guarded canonical-SF address/store
   site using16 lanes, replacing four sites using four lanes each. The CPU
   proof covers every valid count0…16 and all136 valid writers exactly once.
   Explicit scalar selects should lower without a dynamically indexed rmem
   array. Pack the four SF encodes as two RN-satfinite E4M3x2 conversions,
   preserving each rounded byte; paired E4M3→F16→FP32 decoding is exact for
   representable SF values and still must preserve NaN handling. Final FP4
   already has four pair-conversion instructions; retain those.

   This is the strongest first change: it directly targets the repeated
   address work visible in SASS. Require one SF store site, fewer address/
   reconvergence sites and two SF encode sites before GPU timing. Published
   TRT N16 source uses packed-four SF conversion at3497–3501 and distributed
   SF ownership at3563–3615. Its layout/math are not interchangeable with ours.

   A secondary compile-only reduction option is four masked
   `redux.sync.max.f32` operations instead of12 SHFL+max pairs, using
   `0x11111111 << (lane&3)` after zero seeding. Each subgroup has eight lanes
   owning the same token, and all32 lanes must execute each reduction outside
   token-valid branches. PTX supports the mask/type on SM100a. However TRT
   deliberately chooses SHFL for group8 and REDUX only for group>=16, so do
   not assume a win: reject if lowering expands to whole-warp neutralization
   loops, adds expensive mask dispatch, or fails to emit four native reductions.

2. **Release the narrow accumulator bank immediately after its native reads.**
   Current core1310–1325 waits until `_run_narrow_fp4` finishes activation,
   scaling and stores before releasing its two-bank accumulator. The direct
   path no longer uses accumulator storage as transpose scratch. After both
   up/gate loads, all128 epilogue participants can perform the existing TMEM
   load-completion fence and one `acc_pipe.consumer_release` before FP32 math.
   Suppress the later duplicate release under exactly that static direct-load
   path, keeping state advance once per tile. This gives MMA an earlier empty
   bank without changing layout, arithmetic, stages or adding a pipeline.
   It requires all channel fragments read first and is initially safe only for
   the single-channel-tile N16 path; do not extend it to NB2 by analogy.
   The shared/native output buffers remain owned until their ordinary store
   completion. This could improve overlap, but no saved timing proves a gain.

## Proof and validation gates

Raw mapping is token `2*(lane&3)+(i&1)+8*(i//4)`, channel
`lane//4+8*((i//2)%2)`. XOR4/8/16 spans only the16 channels of that same token.
Keep up16/gate16 offsets0/16, true C16 ping-pong alignment, output nibble order,
canonical SF layout and all invalid-row predicates. SF32 crosses the adjacent
warp's same-token block and cannot simply reuse the SF16 reduction. Per-token
scales must be applied to matching original tokens before activation. Retain
explicit existing paths until those formats are proved.

Before timing: coordinate/byte proof, emitted instruction inspection, existing
focused output/SF cases, plus all-NaN/mixed-NaN, ±0, subnormals, infinities and
SF/FP4 half-way boundaries. Check valid0/1/7/8/15/16, M384 channel tails and
at least three persistent tiles/bank phase wrap. Early release needs an actual
load-completion fence and exactly one128-participant arrival per bank use.
No new repository test file or primary campaign is proposed.

Primary references: [PTX redux](https://docs.nvidia.com/cuda/parallel-thread-execution/#parallel-synchronization-and-communication-instructions-redux-sync),
[PTX conversions](https://docs.nvidia.com/cuda/parallel-thread-execution/#data-movement-and-conversion-instructions-cvt).
TRT source is pinned published PR2917 prior art, not the newer benchmarked
binary's source identity; see `scripts/trtllm_gen_decode_audit/README.md`.
The old balanced-absmax experiments in `scripts/fc1_arithmetic_experiment` are
closed; neither proposal is a rerun of that arithmetic-only axis.
