# Whole-path paired slabs with 16 elements per worker

Source-only candidate based on L1 `d9d510f7a9e1764c96778c36b3f1bae3c6d2278e`, whose parent is retained PR8 `534a623`. No GPU execution, timing, sanitizer, promotion or public API change is performed here. Only the owned `bf16_nvfp4/topk_reduce.py` changes.

Unlike rejected I1, this uses one16-element body for every worker, including decode and the first stripe. It has no8-element head, bulk transition, shape dispatch or second arithmetic body. Like L1 it halves the logical worker count relative to retained width8. Unlike L1's adjacent16 elements, it maps two8-element slabs so each issued128-bit copy is contiguous within a complete lane group. This targets the complementary half-sector issue confirmed in L1's T4 SASS; benefit remains unmeasured and compiler scheduling can change outside reduction.

## Mapping and coverage proof

For a supported hidden size H divisible by32, set Q=H/16 and G=min(32,Q&-Q). Q is even, so G is a power of two in[2,32] and divides Q. These are constructor constants, not runtime dispatch. For logical tile q in[0,Q), decompose q=bG+l,0<=l<G. Its two eight-element source/output tiles are `2bG+l` and `2bG+G+l`.

Each complete logical group b maps bijectively to the complete2G original tiles in[2bG,2(b+1)G). Groups are disjoint and cover[0,2Q), so every element in the row appears exactly once, neither slab crosses the row, and no predicate or tail special case is needed. Logical token mapping remains `worker//Q`; only the intra-row tile is remapped. The inherited caller already guards `worker < rows*Q`, including zero rows. Its striped role/CTA mapping is unchanged and remains a permutation of the first512*SM workers. Grid stride selects each nonnegative worker exactly once by quotient/remainder; the same row proof applies to every iteration. The existing signed32 index domain remains the boundary; this does not add an unbounded-size claim.

For H6144 and H7168, G=32. Lane l's first slab begins16l bytes after its group's base, and the second does likewise at a fixed16G-byte offset. Each128-bit instruction is warp-contiguous. For other supported H, smaller complete power-of-two groups remain contiguous. The pointer contract is only16-byte alignment; group starts may be16bytes into a32-byte sector. No stronger pointer alignment is required: legal16-byte-offset pointers remain legal and may incur the normal boundary-sector request. Do not claim fewer measured transactions from this source geometry.

The remapping lives in the existing `_prepare_bf16_worker`, so first-worker metadata can still be prepared before the tail handoff. The map is implemented as `q + (q & -G)`: for nonnegative q and power-of-two G, `q & -G = G*floor(q/G)`, so it equals `2G*floor(q/G) + q%G` without signed division/remainder correction. No data access or reduction crosses the existing FC2 readiness barriers. Two constexpr slab copies reuse the established I1 `cute.local_tile` pattern, each with128-bit atoms. Outputs continue to be marked16-byte aligned.

## Arithmetic and scope

The route loop remains outermost. Each route score is loaded once per16-element worker, including the existing K>16 nonprefetch case. The existing first-route packed FP32 multiply, ordered packed FP32 FMA sequence, BF16-to-FP32 conversion and final BF16 conversion are unchanged for every element. The two slabs occupy distinct halves of a compact16-element register tensor. No reassociation or tolerance change is introduced.

Caller, input staging, transport, epilogue, barriers, role register budgets, CTA/grid geometry, frontend, autotune candidates and public contracts are byte-unchanged from L1. This candidate does not include M1's cache hint or PR9's alternate FC1 routing-weight semantics.

`source-audit.json` records the exact reducer SHA and unchanged packed-arithmetic loop/helper AST. Ruff check/format and git diff-check pass. `ownership-check.json` records1200 CPU cases spanning H32–1056 in32-element increments plus2048/3072/4096/6144/7168/8192/14336, rows0/1/2/3/8/31/64/127/512/2048, and SM1/2/148. Checks cover full-row bijection, same-row bounds, complete groups,0/16-byte offsets, zero/partial stripes and the inherited worker permutation. These finite checks supplement the proof; no native compile, exact-output or performance claim is made.

Next permitted evaluation is the established full13 public-forward/AUTO4/O3 workload if root authorizes it after current trials. Preserve all100 CUPTI cold-L2 graph samples, decode4–512 retention and three prefill guards. Native lowering should retain two128-bit atoms per route/output and no new spill/ordering issue. Do not run sanitizer during performance iteration.

Frozen experimental commit: `519133d7797f6dd6137c88357eea793612f57d52` (local branch `experiment/coalesced16-wholepath`, parent L1d9). Exact104-file manifest SHA256 `b8f4123cb73a05eb3ab42e6099d8688522468a2e0572b99ee87cb1dc5675a34b`; archive `ea567e4abda7fb4140ca51bb90db6e588c4be98105da7736d78e0f0a6ff2522a`. Source and CPU receipts were refreshed after the final comment clarification. This source remains untested on GPU and unpushed.


The519 snapshot above is preserved and superseded for execution by follow-up `21f598d8db88df87302e96e233599eab2f6db048`, using the equivalent constant-mask map. New104-file manifest SHA256 `1e40a5e3f306928f4e6f39b153cebb71f76fdbfb72e6c32456e35c5cf664dadb`; archive `b9e8c6ecf3cfc70fcd29358b6aac8ef65e3747ac5cdbcf1eb6891cb482ed398a`, under `frozen-v2`. All1200 CPU cases additionally assert bitwise/algebraic mapping equality. No GPU execution or push.

If full13 timing supports retention, use existing native graph/stride cases
(H1600 gives G4) and the existing tail reference case(H2880 gives G4),
as well as a GLM5 bit-exact accuracy case, to cover the smaller compile-time
lane group before promotion. No new bespoke test or pre-benchmark GPU gate
is needed. The final sanitizer scan remains deferred until optimization ends.

## Subsequent bounded native validation

After N1 performance measurement, exact candidate `21f598d` passed the requested existing native11 scope on hu59. See [native-validation/RESULT.md](native-validation/RESULT.md) for the exact 8 graph + 2 tail + 1 GLM5 cases, 16 bit-exact combinations, 48 reference checks, 120 pair checks, immutable archive and clean closure. Earlier source-only status above records preparation history; candidate21 now has bounded GPU validation. No sanitizer, full60, publication or promotion was performed by this validation.
