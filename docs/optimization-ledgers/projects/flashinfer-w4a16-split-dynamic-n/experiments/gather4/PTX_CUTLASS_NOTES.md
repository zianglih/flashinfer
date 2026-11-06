# Gather4 instruction and memory-system follow-ups

## Primary-source constraints

- [PTX Gather4 mode](https://docs.nvidia.com/cuda/parallel-thread-execution/#tensor-tiled-scatter4-gather4-modes): exactly four source rows, a 2D tensor, bounding-box dimension 1 equal to one, and no interleaved layout. [CUTLASS's copy traits](https://github.com/NVIDIA/cutlass/blob/b46b16d003484063bca4ed365e44095c4c6ed633/include/cute/atom/copy_traits_sm100_tma.hpp#L248-L267) enforce rank 2 and four indices.
- [CUDA tensor-map encoding](https://docs.nvidia.com/cuda/cuda-driver-api/cuda_driver_api/group__CUDA__TENSOR__MEMORY.html): for a noninterleaved SW128 descriptor, `boxDim[0] * element_size <= 128` bytes. The current 64-BF16 row chunk is therefore already the largest chunk compatible with the existing SW128 MMA layout. A 3D descriptor or a larger second dimension cannot collapse four K chunks into one Gather4.
- [PTX tensor-copy semantics](https://docs.nvidia.com/cuda/parallel-thread-execution/#data-movement-and-conversion-instructions-cp-async-bulk-tensor): a remote completion barrier requires `shared::cluster`; CTA-group 2 completion targets the matching leader parity. [CUTLASS SM100 2SM copy](https://github.com/NVIDIA/cutlass/blob/b46b16d003484063bca4ed365e44095c4c6ed633/include/cute/arch/copy_sm100_tma.hpp#L78-L97) clears the peer bit and uses `shared::cluster`.
- [CUTLASS Gather4 multicast](https://github.com/NVIDIA/cutlass/blob/b46b16d003484063bca4ed365e44095c4c6ed633/include/cute/arch/copy_sm100_tma.hpp#L713-L739) supplies four row coordinates plus a destination CTA mask. Multicast preserves the destination SMEM offset across recipients.

## Measured code-generation distinction

- V3 M256/N128/K256: four static Gather4 sites, each issued by 16 lanes. Root's SASS inspection found `R2UR.BROADCAST`, `UTMALDG.2D.GATHER4.2CTA`, and predicate-driven `BRA.U.ANY` serialization after each site.
- V4: 64 static elected-issuer Gather4 sites and no immediate serialization backedges. Both versions still execute **64 Gather4 transactions per CTA per K256 stage**. Unrolling removes control overhead; it does not reduce transaction count.
- Runtime `top_k` is absent from the compiled launch and kernel signature. Captures for `top_k=3` and `8` show constant multiply/shift division. Other scheduler divisions remain unrelated.

## Bounded V5 experiment

- Use `shared::cluster` for nonmulticast CTA-group 2 copies; keep `shared::cta` for CTA-group 1.
- Elect the FC1 TMA issuer once per routed tile and reuse the predicate throughout K. Later SASS inspection found V4 already had only one election after compiler hoisting, so the explicit source change is not itself an instruction-count win.
- When a CTA owns at most 32 source rows, broadcast and retain those coordinates before K. Wider partitions retain four indices per lane and perform the V4 shuffles inside K. This avoids storing all 96 row IDs for N192 under the existing 80-register producer target.
- Keep the same warp roles, MMA arithmetic, stage sizes, transaction counts, and constexpr `top_k`. Check exactness and generated register/spill behavior before interpreting timing.
- Root's V4 N128 SASS hot loop contained 454 instructions: 64 Gather4, 64 SHFL, 64 R2UR, 174 UMOV, 70 UIADD3, and one ELECT. This makes row-coordinate broadcasts and uniform-register moves more relevant than source-level election count.

## Next actual transaction reduction

- A cluster of four CTAs with two M256 MMA pairs can multicast gathered B activations across pairs. Each CTA then gathers half as many rows as in a two-CTA cluster. For N192/K256, this changes 96 Gather4 transactions per CTA to 48, while each destination still receives its full B tile.
- Compare equal channel work: two separate two-CTA clusters issue 384 transactions; one four-CTA cluster issues 192. Weight work and arithmetic remain unchanged. Runtime fallback to two CTAs must restore the full row ownership and correct barrier arrival counts and masks.
- Scheduler coordinates must remain logical for the preferred cluster geometry while multicast, barrier masks, and peer addresses use the actual physical cluster geometry. This separation is required before enabling mixed four/two-CTA scheduling.

## V6 integration

- Keep the static scheduler's four-CTA grid and obtain its channel offset from logical `bidx % 4`. Read physical cluster width with `cute.arch.block_in_cluster_dim()[0]`; use physical rank for peer addresses and B row ownership.
- The physical four-CTA cluster gives B completion masks 0b0101/0b1010; fallback pairs use 0b0001/0b0010. The B empty barrier has two or one MMA-pair arrivals respectively; byte counts stay unchanged. Existing weight transformation and accumulator pipelines retain physical pair masks.
- Cache the first 32 uniform source-row coordinates before K. Preferred N128 clusters need only these; fallback pairs use the remaining distributed coordinates. N192 caches a prefix without exceeding the 80-register role target by construction; actual compiled registers/spills remain to be checked.
- A distinct-OOB-sentinel screen did not improve the measured large case, so V6 keeps the original zero-fill sentinel. No arithmetic or FC2 change is included.
- Local V6 checks: Python syntax, Ruff, and whitespace checks passed. A host-only exhaustive mapping check covered N=32/64/128/192/256, every valid-row count, both physical widths, and both CTA parities (2,688 cases); each B destination row is supplied once, the dynamic-N source offset is preserved, and masks include exactly the physical same-parity recipients. GPU compilation, exactness, and timing are separate pending checks.
