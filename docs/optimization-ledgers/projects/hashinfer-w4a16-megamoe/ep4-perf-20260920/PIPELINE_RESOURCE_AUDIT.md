# EP4 pipeline and resource candidates

Source-only audit of HashInfer PR8 at `7e6e977f4788f91eaf5988fd4ffea93fc4f1eed5`.
No GPU launch, profiler capture, or performance claim. Source locations below
are relative to `integrated-topk-20260918/hashinfer/` unless specified.

## Priority and prepared candidate

1. **Existing `group_hint` 512 versus 1024**: root owns this trial. It changes
   real phase grouping for EP4 decode, with no new pipeline code.
2. **Existing scheduler depth 2 versus 3**: prepared in
   `sched3/hashinfer`, commit `aec91ab6dca7683485acd6e0d31a2b8b11eada37`.
   Only the candidate factory's constant and its docstring change. The same four
   deterministic choices remain; opt-in IKR still has six. No new public knob
   or runtime branch. `sched3/source-audit.json` records the CPU audit; all scoped
   pre-commit hooks passed. `source.tar.gz` contains 104 exact Git blobs, SHA256
   `45679ad6c31716256d8a8b2bece9bbbbd9f7b59da4d80f8089a71dea48289f03`.

If S3 improves EP4, compare the clean eight-candidate Cartesian product of the
current four dictionaries and S2/S3. Keep the underlying existing knob interface.
Evaluate the complete decode/prefill sweep, record selected tactics, and check
EP8 before retention. S3-only measures the direction more narrowly and avoids
doubling tuning cost before evidence supports it.

## Existing pipeline and S3 mechanism

- `hashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/autotune.py:16-42` fixes
  M256/C2, N64/N128, return-by-epilogue/dispatch, F4, S2, group512.
- `megamoe_kernel.py:57-100` partitions 512 TMEM columns into ACC2 plus decoded
  K256 stages: N64 uses 128+384 columns (D3), N128 uses 256+256 (D2).
- `megamoe_kernel.py:375-397` fits raw packed-weight/SF shared stages, preferring
  activation B3 then B2 and raw5 down to raw2. H7168 uses N64 raw5/B3 and
  N128 raw4/B3 in the historical actual resource captures.
- `megamoe_kernel.py:1183-1285` separates scheduler, weight TMA and activation
  TMA. Only the activation loader waits for FC1 remote pulls or FC1 completion;
  weights/decode already run independently of those payload dependencies.
- `fc1_fc2_fuse_sched.py:283-315` allocates a compile-time scheduler ring.
  `custom_ext.py:37` makes each work record eight Int32 words. The shared
  consumer in `kernel_src/cutedsl_megamoe/src/moe_nvfp4_swapab/`
  `moe_persistent_scheduler.py:169-191` copies and immediately releases each
  record, before the compute role processes that work.

S3 gives the scheduler one additional buffered work descriptor. It could hide
longer expert/group traversal before consumers request their next work. EP4 has
64 experts/rank instead of 32, so more expert-boundary transitions occur per
rank. This is a plausible scheduling hypothesis, not evidence of exposed stalls.
It **does not** add decoded-weight storage, allow arbitrary K reordering, or
let useful dequantization begin before the initial routing publication.

One additional stage adds 32 bytes of work records plus 16 bytes of barriers.
The current shared allocator rounds that 48-byte delta to **128 bytes** before
the raw tensor. Source-derived H7168/E256 predictions:

| Geometry | S2 shared bytes | S3 shared bytes | Raw / activation / decoded / accumulator |
| --- | ---: | ---: | --- |
| M256/N64/C2 | 200064 | 200192 | 5 / 3 / 3 / 2 |
| M256/N128/C2 | 230784 | 230912 | 4 / 3 / 2 / 2 |

Both fit the 232448-byte per-block capacity. EP4 does not enlarge communication
scratch: `token_comm.py:511-543` in the shared source sizes the count array by
total E256 and pull buffers by H and dispatch warps, all unchanged. These are
allocation predictions; record actual fitted stages and driver/cubin resources
when compiling on the GPU. Larger H fallback layouts can still change fit.

Costs include another barrier initialization/drain, longer work lookahead and
potentially earlier atomic claims of not-yet-ready FC2 work. More descriptors do
not necessarily increase useful execution overlap. Existing BF16 and MXFP8
backends expose this same scheduler-stage override and normally default to S2:
public FlashInfer `kernel_bf16_glu_fc12.py:362-363`,
`kernel_mxfp8_glu_fc12.py:396-397`, and
`kernel_mxfp8_bf16_glu_fc12.py:260` under the vendored MegaMoE source.

## Independent group1024 review

Reviewed root candidate `62c3ba1c5d0a20d69ab1ed96cb0379f31269defb` against
7e6e977. Exactly one factory literal changes: `group_hint=512` to `1024`.
AST execution confirms every other value, candidate ordering and four/six
candidate count remain equal. No correctness issue found in this delta.

`fc1_fc2_fuse_sched.py:778-804` measures this budget in **FC1 cluster tiles**.
With I2048 and M256/C2, each nonempty expert with one token block contributes
16 FC1 tiles. All 32 EP8 experts fit group512; 64 EP4 experts need two groups.
Group1024 can put the EP4 expert set into one FC1 segment followed by one FC2
segment. Sparse/empty experts and experts with multiple token blocks alter the
exact boundary; this is not a tokens threshold.

In particular, ordinary EP8 decode with at most one token block per expert
already fits one group. Changing512 to1024 cannot change its phase grouping;
do not credit latency noise there to this mechanism. Sparse EP4 small-token
rows may likewise contain at most32 active experts and keep the same grouping.

Larger groups reduce phase transitions and repeated group setup, but delay FC2
and revisit older FC1 activations later. Smaller groups can return completed
experts earlier but add more phase transitions. No GEMM arithmetic or deterministic
combine order changes. Timing must decide the cache/readiness tradeoff.

## Register and deeper-stage directions to defer

`frontend.py:303-307` reserves 640×96 = 61440 registers/CTA. The roles at
`megamoe_kernel.py:1181,1338,1359,1403-1407` redistribute exactly
128×(80+144+64+96+96). Keep the five roles, both dequantization WGs and full-SM
CTA. Raising the initial nominal count above96 is not a free use of remaining
physical registers: warp allocation granularity previously rounded97-104 to
66560 registers, which cannot fit. No current EP4 spill evidence supports a
new redistribution.

Earlier EP8 experiments in public project's `w4a16_optimization_experiments.md`
are historical, not current-head measurements:

- Entry050: S2 pruning was a simplicity/tuning-cost tradeoff. The matched S3
  subset advantage was at most0.715% outside T1; S2/S3 product cost much more
  setup. EP4 was not established by that evidence.
- Entry041: S5 was4.25% slower geometrically; do not jump directly to deep
  scheduler rings.
- Entry044: B4 was0.42% slower geometrically with4K+9.42% and2K+4.43%.
- Entry081: raw6/B3 was2.17% slower; N128 code was unchanged and also drifted,
  so the whole loss cannot be attributed causally to raw depth.
- Entry059/060/061/063: ACC1 and K128 capacity trades were rejected. They
  change accumulator overlap or K-loop granularity, far beyond S3's metadata
  ring. The owned decoder already has early raw-slot release.
- The recent fused-staging audit records six additional publication/startup
  overlap trials without retention. Do not repeat them without locating an
  exposed current-source dependency window.

## Next optional geometry extension

Rank **M128/N64/K256, C1, F4, S2, both existing return modes** above M128/C2.
Adding those two supported dictionaries would make six deterministic candidates,
not a broad product of every knob. No core tiling change is needed.

The current kernel accepts M128/N64 with C1 or C2 at
`megamoe_kernel.py:160-175`; M128 requires `use_2cta_instrs=False`.
C1 has independent CTAs (grid1×1×148 on B300) instead of74 two-CTA clusters.
It still occupies each SM and uses exactly two dequant WGs. Compared with
M256/C2 it halves the feature extent per work claim, increases claims, loses
activation multicast, and changes group512's expert boundary. It is a catalog
comparison, not an isolated cluster experiment. H/I are already aligned, so
there is no avoided feature-padding argument.

Historical Entry017a's same-M128 C2/C1/C2 trial regressed16/64/256 and modestly
improved4K; later Entry019 retained C1 for small hot-score wins at4/8/32/64,
with0-3.6us margins. M128/C2 had no winners in that sweep. By Entry046-050,
M128's advantage appeared only atT1 and was pruned. The current user explicitly
permits useful extensions, but T1/T2 are excluded from retention: require a
selected M128 improvement at4-512 or prefill and full numerical qualification
if it survives. Current all-tactic accuracy coverage is the four-M256 catalog,
not new evidence for M128.

After the root authorized preparation, the six-candidate extension was frozen
at `9bc743e2d670f2eb200afd24498a8701c527c132` in `m128c1/hashinfer`, based directly
on7e6e977 (not the S3 trial). Only `autotune.py` changes, using three explicit
geometry/cluster pairs crossed with the existing return choices; the 2CTA flag
is derived from M. Every original dictionary remains unchanged and in the same
relative order. The existing validator accepts all six deterministic choices
and all nine choices when IKR is permitted. Scoped pre-commit and the CPU AST
catalog audit pass. Archive104 blobs SHA256
`57ecc670b88b9ddcaeceddcf82ef2732121da02e1eb3c4ad9bdb4bfb7330ef83`.
This is not GPU numerical or performance qualification.
