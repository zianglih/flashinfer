# SF copy address rematerialization: memory and correctness boundary

Read-only assessment against retained `c1ac8ce7`, whose swap kernel is `482b636a`; no kernel edit, compilation, or GPU operation was performed for this note. This is distinct from R2's pure source-expression relocation, which emitted the same failed native image as R1. It does not reopen either result as successful.

**Conclusion:** forming the exact row address inside the existing private copy primitive is compatible with the proven mapping. Its memory benefit remains fewer source-sector requests per instruction, not fewer unique bytes. Compact state could reduce the failed G2 specialization's SF register footprint to the original footprint, but cannot establish that spills disappear or that repeated address work is profitable.

## Address and completion contract

The smallest proposed form keeps the source pointer adjusted by the existing `channel // sf_vec_size`, and adds an Int32 row and constexpr row stride to `_copy_gather_sf`. This is two private parameters and one additional runtime asm operand. Inside that same side-effecting asm, signed widening followed by 64-bit multiplication/addition must reproduce:

`adjusted_source + Int64(source_row) * row_stride`

`cvt.s64.s32` plus `mad.lo.s64` preserves the current width semantics without imposing a new signed-32 stride bound. Multiplying in Int32 before widening, or narrowing the stride to use `mad.wide.s32`, is not an equivalent general contract. The existing channel expression, 4-byte alignment, destination, `issue`, and `ignore_source` must remain unchanged. Arithmetic for an unused lane creates no new memory access.

The [current private copy](../../flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py:95) uses a predicated 4-byte `.ca` copy. [PTX 9.2](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#data-movement-and-conversion-instructions-cp-async) specifies that `ignore-src` writes zeros to the destination. Preserve `issue = row < mma_n` and `load = row < valid && channel < logical_K`: unused rows issue nothing; MMA padding and K padding still receive defined zeros. Preserve each thread's completion arrival after all its copies, the static participant count `min(128, route_tile * G)`, and the existing local-to-leader relay and waits.

I replayed the existing [mapping proof](proof.py), without its artifact-writing footer: **20 geometries and 19,038 live/zero/unused word-class checks passed**, including both CTA group sizes. The minimum-owned-row arrival predicate matches the set of threads owning any route row. Address rematerialization does not change that ownership argument.

## Actual traffic opportunity and limits

Let `W = tile_k / (4 * sf_vec_size)`, `G = min(W, 4)`, `V` be live rows, and `R <= W` be valid 4-byte words in this K stage. If routed rows occupy distinct source sectors and every G-word group fits a 32-byte sector, the request model is:

| Full-stage words / lane group | Original requests | Coalesced requests | Reduction factor |
|---|---:|---:|---:|
| 1 / 1 | V | V | 1 |
| 2 / 2 | 2V | V | 2 |
| 4 / 4 | 4V | V | 4 |
| 8 / 4 | 8V | 2V | 4 |

For partial K, the formula is `V * R` versus `V * ceil(R/G)`: one live word gives no reduction; G4 with seven live words gives 3.5x. Current gathered SF16 uses G4 for K256/512 stages; SF32 uses G1/G2 for K128/256. Native MMA K96 does not change these gathered-stage dimensions. Group2 keeps full-N SFB in **each** CTA, so it duplicates the SF work while retaining the same per-CTA factor.

The current models' FC1 SF row strides fit these lane groups without sector crossing (SF16: 448/320/224/128 bytes; SF32: 224/160/112/64). The public wrapper, however, guarantees only a multiple of four bytes. Arbitrary row strides/base alignment can make a group cross sectors; adjacent or duplicate routed source rows can already coalesce. Therefore the table is an aligned, distinct-row request model, not a universal G-fold hardware result.

The live global address set, unique sectors, and byte volume are unchanged. Repeated original `.ca` reads may already hit cache, and the two CTAs may share cached data. No reduction in DRAM bytes or latency follows from this model alone. The canonical shared layout also remains unchanged: its 512-byte word stride maps G distinct word destinations to the same bank per fully active warp instruction. This is a G-way bank-address model, not a measured cp.async wavefront or serialization claim. Zero-filled K-tail words still write shared memory.

## Liveness and native acceptance boundary

With `B = max(1, allocated_n/128)`, the original SF cache holds `B` Int64 offsets (2B register words); R1 holds `B*G` Int64 offsets (2BG words); compact rows hold `B*G` Int32 values (BG words). G2 returns the SF state to the original word count. G4 still doubles it. In the failed N256/G2 case, the ideal saving is **four register words**, not the full 64-byte spill allocation. Separate Gather4 row IDs remain live (up to 64 Int32 values for N256/group1, or 32 for group2), as do the extra row predicates. Native register allocation can uniformize or spill these values differently.

R1/R2 [native results](../../experiments/sf-lane-coalescing/RESULTS.md) remain decisive historical failures: wide MXFP8 had 43 LDL and 15 STL sites, 3,691→4,112 non-NOP instructions and driver LOCAL64 at 168 registers. Narrow NVFP4 was exact/LOCAL0 but added 31 instructions. R2's PTX and cubin were byte-identical to R1. Full-K channel predicates and lane-group modulo were already optimized; those are not available savings.

The new asm boundary could prevent the LLVM-level hoisting seen in R2, but ptxas may still combine, schedule, or hoist address operations. Rematerialization also exchanges once-per-work products for per-copy address work throughout K. Only actual native placement, remaining local accesses, and total instruction/resource deltas can establish whether this is a useful change. This note supplies no performance or retention conclusion and does not justify quota changes, alignment restrictions, or shape exceptions.

Source bindings: retained kernel `482b636a1714486e2ffb34c8ae005da3cef26f25f0ce034ba1eb59c6198d6276`; existing proof `461405b451cc0489f575d48aeaefc4547281cee5575b68293feea33ee241dff2`; R1 `868363559094068c95c1c5c85257ac1a351e4a59d8efb594b029e7530347faab`; R2 `377f040445b488541d6e5b594f4e532875ccaa5af76f227e53942b5a98e61a76`.
