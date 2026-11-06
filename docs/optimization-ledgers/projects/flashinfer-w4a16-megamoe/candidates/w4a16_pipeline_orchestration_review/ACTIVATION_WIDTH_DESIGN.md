# N256 activation-width feasibility

Held source design only. A half-width activation copy is a distinct N256 opportunity, but no inspected sibling supplies a ready adaptive-width loader. No implementation, compilation, runtime validation, or performance claim is made here. The B-loader bytes reviewed are those in the saved N256 source 59bbe native capture; the later catalog expansion does not change them.

Paths below are relative to the project root. `owned/` abbreviates `flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/nvfp4_w4a16/`.

## Fixed destination layout and global coordinates

Current `owned/megamoe_kernel.py:760,795–807` constructs one static B atom per FC phase from the full `mix.smem_layout_b` stage. `_activation_task:932–974` applies the expert's physical row offset, the two-CTA nonleader correction, and `work.tile_n_idx` before copying each K tile. `owned/dynamic_mainloop.py:19–42,99–148` narrows MMA to `align16(valid_tokens)` without narrowing the copy.

For N256/C2 and `0 < valid_tokens <= 128`, MMA consumes at most 64 local B rows per CTA. A possible immutable full/half descriptor choice must load those rows into the **existing N256 ring**, with the address identity `small_dst(r,k,stage) = current_dst(r,k,stage)` for every copied `0 <= r < 64` and `0 <= k < 256`. The MMA B descriptor, swizzle, allocation, and stage stride remain unchanged; this is a restricted view, not a compact replacement B layout.

The saved direct PTX at `profiles/cu132-recovery0911b-n256-acc1-default-candidate-n256-f4-direct/codegen/dsl/*.ptx:2244–2295` makes this concrete: four K64 copies target shared offsets 95616/112000/128384/144768, separated by 16384 bytes, plus `stage <<16`. A half copy would transfer 8192 bytes at each corresponding destination while retaining those 16384-byte K-plane offsets and the 65536-byte stage stride. Constructing an ordinary compact N128 layout would instead pack K planes 8192 bytes apart and is incorrect. Whether CuTe's existing atom/partition construction accepts the exact restricted swizzled view remains an implementation feasibility question; equal element counts alone do not prove it.

Global coordinates must also keep N256 work ownership. Let `base = cumulative_data_physical_row + work.tile_n_idx*256` and `split = align16(valid_tokens)/2`. The required first rows are `base` on the leader and `base+split` on the nonleader. Current full partition 128 plus correction `split-128` produces this mapping. A half descriptor partition 64 would require correction `split-64`, or an explicitly equivalent global view. Reusing `work.tile_n_idx` with ordinary N128 tiling would advance by 128 rather than 256; retain the explicit N256 task base and use tile 0 within the restricted view. Expert offset handling is in `owned/custom_ext.py:302–329`. Untouched rows require no zero fill only because the dynamic MMA never reads them; full jobs must still refill all 128 local rows before consumption.

## Transactions, lifetime, and costs

The existing saved CuTe 4.7.1 API already supports `PipelineTmaUmma.producer_acquire(expected_tx=...)`: `candidates/cuda132_recovery_0909e/dsl_pipeline_source/cutlass/pipeline/sm100.py:343–386`. It retains the empty-slot wait and leader `arrive_and_expect_tx`; commit is a no-op. Current pipeline creation is `owned/megamoe_kernel.py:1053–1064`.

Full/half copies require respectively 131072/65536 expected bytes across the two CTAs per K tile. Both CTAs must select the same width from the uniform work record. Copying fewer bytes while retaining the full expectation hangs; permanently changing the expectation to half is also wrong for full jobs. The normal B-stage acquire, phase advancement, MMA completion/release, and both readiness waits remain. No additional mutable per-stage state is implied by the API.

The narrowest design is N256-only immutable full/half atoms for each FC phase, with one uniform per-work width decision and constexpr-specialized copy paths. It adds two descriptors and argument/control pressure; descriptor construction can be static, but the routed-count decision is runtime. It likely retains four TMA issues per K tile and does not recover SMEM capacity, raw/B stages, or ACC overlap. Descriptor mutation has no demonstrated advantage here and would introduce descriptor-update visibility and lifetime obligations. Reduced transferred bytes are a hypothesis for benefit, not evidence that activation traffic currently limits latency.

## Existing patterns and excluded repetitions

- W4A4 Mega's `flashinfer/flashinfer/moe_ep/kernel_src/cutedsl_megamoe/src/moe_nvfp4_swapab/kernel_fc12.py:1910–1995,2040–2128` uses the dynamic nonleader shift with fixed atoms. Its descriptor-pointer argument is not an adaptive box-width implementation. Split W4A16 likewise builds a fixed B atom/count at `flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py:734–753` and copies it at 1395–1455. No matching adaptive-width path was found in the bounded BF16/MXFP8 sibling search.
- Ledger Entry 014 (`w4a16_optimization_experiments.md:532–548`) rejected descriptor prefetch, which does not reduce tensor payload. Entries 019b–019g concern FC1 TMEM loads/SwiGLU/scratch/output half guards, not activation TMA width. Their code-size/scheduling costs remain relevant cautions, not an equivalent prior trial.
- `candidates/w4a16_fixed8_remaining_overlap_audit/README.md:80–99` closed activation address-hoisting because native code already moved meaningful setup before the readiness spin. Narrowing transferred bytes is different. No equivalent fixed-ring half-B copy trial was found in this bounded history audit.
