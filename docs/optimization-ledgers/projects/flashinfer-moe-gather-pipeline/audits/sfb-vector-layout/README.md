# Wider gathered SF copies through a different shared layout

**Decision: no source or GPU experiment.** A shared-layout-only change cannot turn the current 4-byte gathered SF copies into 8/16-byte copies while preserving the existing `Cp4x32x128bOp` source-to-TMEM image. It needs a sub-16-byte permutation that this descriptor cannot express. This revalidates a closed mechanism rather than discovering a new variant.

Bound source: retained `49c91adf47d30fc2049c76cbaf34d0ccf3291434`; project CUTLASS `b46b16d003484063bca4ed365e44095c4c6ed633`. The checkout remained clean. `proof.json` binds exact source hashes, including the helper. Validation is source inspection and CPU arithmetic only, not a CuTe descriptor compilation or a hardware trial.

## Exact obstruction

The current FC1 input is byte-valued, linear per token. Four consecutive scale bytes correspond to one `sf_block_k = 4 * sf_vec_size` group. For a 128-row shared atom, with logical row `r` and scale-byte index `s`, the current address is:

```text
D(r,s) = 16*(r % 32) + 4*(r // 32) + (s % 4) + 512*(s // 4)
```

Outer row blocks and pipeline stages add multiples of the full stage extent. Thus one token's next four-byte word is 512 bytes away. Conversely, one contiguous shared 16-byte unit contains four-byte fragments from four independent token rows `r, r+32, r+64, r+96`.

The current CUTLASS source closes the alternative-descriptor route:

- `cute/nvgpu/tcgen05/copy.py:850–872`: DSL `Cp4x32x128bOp` is PTX `.32x128b.warpx4`, not a general four-word transpose.
- `include/cute/atom/copy_traits_sm100.hpp:3661–3688`: the copy's core image has 32 data-path rows and 128 leading bits, broadcast across four TMEM lane groups. Broadcast duplicates that image without rearranging its four 32-bit words.
- `include/cute/atom/mma_traits_sm100.hpp:398–421`: the S2T source view is specifically converted to `UMMA::Major::K` and recast in 128-bit units.
- The same file's descriptor construction at `:135–307` requires canonical K-major layout and 16-byte-address units. Its supported swizzles retain the low four address bits; the 32-byte-atomic variant is additionally disallowed for K-major.

For a fixed logical token, the required byte slot inside every core 16-byte unit is `4*(r//32) + (s%4)`. Changing the atom's base, stride, or swizzle cannot change that slot. Therefore the next four-byte word has the **same address modulo 16**. A contiguous 8/16-byte cp.async would instead place it at `+4`, which has a different residue. The contradiction holds independently of stage size, row count, descriptor stride, CTA count, and static source alignment.

This agrees with the matching-toolkit [PTX 9.2 descriptor alignment](https://docs.nvidia.com/cuda/archive/13.2.1/parallel-thread-execution/index.html#tcgen05-shared-memory-descriptor) and [tcgen05.cp definition](https://docs.nvidia.com/cuda/archive/13.2.1/parallel-thread-execution/index.html#tcgen05-instructions-tcgen05-cp). The copy accepts a source descriptor and broadcasts the specified core image; it supplies no arbitrary word-permutation operand.

A different target layout/SF-ID interpretation, redundant overlapping copies, or a register/shared transpose would be a different algorithm. They are not a free shared-descriptor change. In particular, using unused banks of an N16/N32 specialization would introduce a narrow-N layout policy and change the MMA scale contract; this audit does not propose that exception.

## Alignment, tails, padding, and stages

`moe_swap_ab.py:340–383` accepts `K % (4*sf_vec_size) == 0`, checks a four-byte-aligned SF pointer, and does not promise stronger alignment. `_run_blockscaled_gemm:147` passes that exact four-byte alignment to the compiler. Even if the descriptor obstacle disappeared, the existing public contract would not universally support a wider copy. With a genuinely stronger base guarantee, a static width dividing `gcd(16, K/sf_vec_size, tile_k/sf_vec_size)` could avoid mixed-validity tail vectors; that does not fix the descriptor obstruction. Shape-derived alignment alone cannot strengthen a pointer that the API accepts at `4 mod 8`.

Current publication must remain intact:

- Every stage waits for operand reuse before overwriting SFB. All four gather warps participate; SFB remains full-N in each CTA, including two-CTA mode.
- A row below `valid` loads its current SF word. Rows in `[valid, round_up(valid, 8*cta_group_size))` are zero-filled on every stage reuse. Rows beyond rounded MMA N issue no SF copy.
- K is four-scale aligned, so every copied word is wholly valid or wholly padded. A final partial K stage zero-fills each wholly invalid word. K96 changes MMA instruction consumption, not this shared atom or the copy granularity.
- The local gather barrier counts one payload announcer plus `min(route_tile,128)` SF participants, with every participant's cp.async completion attached. The relay acquires this combined completion, crosses the async/shared proxy, and publishes to the MMA leader. A wider-copy proposal must preserve the completion domain, even if it reduces instruction count.

Current SFB bytes **per operand stage, per CTA**:

| SF group | Stage K | SF bytes/token/stage | N16–N128 | N256 |
|---|---:|---:|---:|---:|
| 16 | 256 | 16 | 2,048 | 4,096 |
| 16 | 512 | 32 | 4,096 | 8,192 |
| 32 | 128 | 4 | 512 | 1,024 |
| 32 | 256 | 8 | 1,024 | 2,048 |

These are `max(1, allocated_n/128) * 128 * tile_k/sf_vec_size`. A pure permutation need not increase footprint, but no legal descriptor-only permutation was found. Adding a second full-N linear stage before the canonical stage would add these bytes again, plus transform work and its lifetime coordination; a smaller scratch layout would itself require a new layout/ownership design. SF32/K128 already has only one four-byte word per token per stage, so there is no within-stage K-word vector to combine.

## Earlier experiments are different, but already expose this boundary

The following files are in the read-only older project `flashinfer-w4a4-split-dynamic-n`:

1. `scripts/compact_sfb_audit/README.md` and `LOOP_BOOKKEEPING.md`: physical N16 and a specialized compact SFB image in the earlier nine-warp design. Layout validation covered a particular FP4 gated FC1 path, not all current SF16/SF32/full-N cases. It did not establish a new legal sub-16-byte descriptor permutation.
2. `scripts/sf_warp_pairedrow_experiment/README.md`: all 32 lanes issued four 4-byte copies instead of eight sites with half the lanes active. It changed lane ownership, not copy width. Full-chain T32/T128 ratios were `0.987438x/0.992111x`; the candidate was unretained. Native LDGSTS sites halved, but startup stores and total static instructions increased. It predates the dedicated gather warpgroup.
3. `fc1-gather-20261028/optimization-next-20261029/sf-transport-audit/AUDIT.md`: already explicitly considered changing shared layout while keeping the fixed TMEM image and reached the same 16-byte descriptor obstruction. Current source still has that contract.
4. Current `audits/swap-gather-publication-followup.md`: Rubin split's wider linear SF loads are followed by a separate SF-transform warpgroup and pipeline. Mega's TMA-SFB path consumes scales already transformed by its communication/refine pipeline. Neither is a descriptor-only replacement.

This audit does not rerun paired-row, compact-SFB, ownership splitting, direct-TMA, or scale-cache candidates.

## CPU receipt and scope

Run:

```sh
python3 audits/sfb-vector-layout/proof.py
```

The source-bound receipt checks:

- 20 current public shared-stage geometries, both one/two-CTA groups; 46,080 uniquely covered canonical bytes.
- 7,680 attempted contiguous 8/16-byte images fail the fixed target mapping.
- 1,310,720 low-four-bit checks over the five CUTLASS swizzles and 4,096 descriptor-residue contradictions.
- 3,093,405 route/K padding word-class checks, including every valid-token count in each supported route tile.

These exhaustive arithmetic checks support the source-derived constraint; they do not claim compiler acceptance of every alternative layout or rule out a broader redesigned scale-storage algorithm. No performance claim, source change, or additional GPU run is warranted by this bounded lead.
