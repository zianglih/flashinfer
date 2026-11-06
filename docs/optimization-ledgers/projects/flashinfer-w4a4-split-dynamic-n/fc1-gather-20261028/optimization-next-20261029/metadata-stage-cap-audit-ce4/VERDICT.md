# Metadata publication does not prove a physical B-stage cap

**Keep stage allocation unchanged.** Finite W4 metadata publication bounds logical producer lookahead, but it does not establish that B slots beyond that bound are physically reusable. Adding waits to manufacture the missing ordering would change the asynchronous overlap being optimized. This was a read-only audit; no source/GPU change or timing claim.

## What is provable

In retained ce4 `moe_w4a16_kernel.py`, metadata has S=1 slot for CLC or S=3 for ordinary scheduling (line2925). Scheduler publication acquires each slot before reuse (1539/1605/1678); all active work roles consume metadata. Each consumer copies the current tile into registers, releases its info slot immediately, then executes that tile. Therefore the consumer may hold one private current tile outside the S shared slots.

Let P be published valid tiles, Rr the metadata tiles consumed/released by role r, and K the static number of stage-K tiles per valid work tile. Publication satisfies `P <= min(Rr)+S`. A B producer cannot reserve more than `RB*K` operand slots in sequence. The leader MMA consumes its next metadata only after issuing all K stages of the preceding tile, so `RM <= floor(I/K)+1`, where I is issued MMA stages. Thus B reservations minus MMA issuance are bounded by `(S+1)*K - (I % K)`. This is an **issuance/lookahead** bound, not a bound on occupied storage.

Both B paths obey that metadata dependency: regular TMA reads/releases info at1719–1727 and1809–1817; Gather4 at2775–2780 and2865–2871. Regular-TMA PDL waits after reading initial metadata, while Gather4 waits on the dependency before role dispatch (1497–1503). Neither bypasses metadata. CLC cancellation may skip publication of invalid capacity tiles, but does not supply unannounced B work. Pipeline `reset_count()` preserves index and phase across work tiles.

## Missing physical-retirement ordering

MMA issues B `consumer_release` at2039, advances its stage state, commits accumulator-full at2047 and reads/releases next metadata at2051–2056. The B release and accumulator commit lower to separate `tcgen05.commit` operations on different barriers. CUTLASS `pipeline/sm100.py:329–341,750–762` delegates them to `MbarrierArray.arrive_tcgen05mma` (`pipeline/helpers.py:433–455`). Neither call waits for the target B-empty arrival to become visible.

The epilogue waits for accumulator-full at2334, releases the accumulator after protected reads, and consumes the next metadata only after finishing the tile body (2739–2744). That proves prior tile MMA completion. It does not explicitly observe all prior **B-empty barrier arrivals**. PTX defines each commit in terms of the prior MMA/copy/shift operations it tracks and signals its chosen barrier; the documented dependency does not give us a cross-barrier signal-delivery bound for this cap. See [PTX tcgen05 completion and memory ordering](https://docs.nvidia.com/cuda/parallel-thread-execution/#tensorcore-5th-generation-instructions-tcgen05-commit).

If E is physically retired B stages, ring occupancy is `Breserved-E = (Breserved-I)+(I-E)`. Metadata bounds the first term. The second includes asynchronous pending retirements and is not bounded by S alone. An accumulator-full observation cannot simply be substituted for observing those empty barriers. A conditional `(S+1)K` physical bound would require exactly that extra ordering premise; this audit does not establish it. This is not a claim that hardware delays arrivals indefinitely, only that the existing contract cannot prove the proposed slots unreachable.

## Separate scheduler cases

W4 ordinary scheduling still uses the three-slot metadata pipeline, so the logical reasoning applies. Swap-AB ordinary scheduling does **not**: `moe_swap_ab_kernel.py:2502–2517` computes work independently and allocates/uses info barriers only for CLC (2684–2697). There is no finite S publication window for its ordinary mode. Swap CLC would also need the physical-retirement proof; neither backend should inherit a blanket cap.

This is distinct from the previously rejected one-work-tile clamp in [pipeline-tail design](../pipeline-tail-f63/DESIGN.md). Both preserve the conclusion that small K alone does not identify dead ring capacity.
