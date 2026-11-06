# Swap-AB W4A16 MegaMoE independent source review

Scope: CPU/source review of the initial candidate `candidates/w4a16_swap/`
(892-line kernel snapshot), while root owns all GPUs. No candidate files were
edited and no CUDA workload was launched. Findings were sent directly to the
kernel and epilogue authors. Line numbers refer to that initial snapshot and may
move during fixes.

## Required fixes or explicit candidate guards

1. **TMEM allocation barrier participant mismatch.** Kernel lines592–594 set
   the retrieval barrier to288 threads, but636–637 call `wait_for_alloc()` from
   all512 threads. Installed DSL4.7.1's method unconditionally calls the named
   barrier's `arrive_and_wait()`. Either limit waits to exactly the nine TMEM
   warps or use the512-thread barrier matching the existing local W4A16 path.
   Existing BF16 Mega instead limits waits to its five MMA/epilogue warps at
   `src/moe_bf16_glu/kernel_bf16_glu_fc12.py:1625,1735–1736`.

2. **The candidate inherits the old swapped epilogue, not the current kernel's
   epilogue.** Candidate epilogue lines27–34 import `moe_nvfp4_swapab.epilogue`;
   current `src/moe_nvfp4_swapab/kernel_fc12.py:26–29` imports
   `epilogue_refactor`. Old epilogue line2024 accepts only scalar
   `int(epi_flag_batch)`, whereas kernel candidate269 forwards the current
   tuple/list field (default(1,1)). Initial validation should either explicitly
   select scalar1 only at the old epilogue constructor or use the current
   refactored loop/config contract. Do not forward the existing(2,4) reference
   profile unchanged. Old loop2449–2485 also does not visibly flush a partial
   FC1 batch before entering FC2 under direct epilogue return; scalar>1 needs
   a separate phase-boundary correctness audit. Current refactored code uses
   `src.flag_batch.GpuReleaseFlagBatchTracker`.

3. **Finite gate/up clamp is silently omitted.** Candidate superclass accepts
   `gate_up_clamp`, but candidate epilogue224–227 scales and activates without
   applying it. Existing active W4A16 epilogue118–122 clamps gate above and up
   on both sides after FP32 alpha. Reject non-None for the first candidate, or
   implement that exact placement. The requested unclamped path is unaffected.

## Resource concern requiring generated-code evidence

The local W4A16 kernel uses two transform warpgroups/eight warps at
`moe_w4a16_kernel.py:156–158`; candidate184–187 reduces that to one/four. Each
CTA still converts128×256 BF16 outputs per A stage. That is nominally256 BF16
values/thread, or128 32-bit data registers just for the decoded tile. The
inherited helper retains `tArA_transform` across fragment decode until its final
TMEM store (`moe_w4a16_kernel.py:379–382,502–535`), in addition to packed inputs,
scales and address temporaries. Inspect LOCAL/LDL/STL and actual register use
before drawing performance conclusions.

Current four-warpgroup register targets are epi176/control80/dispatch64/
transform128, totaling57,344 registers. An entire transform warpgroup target up
to192 fits65,536 arithmetically, but this is a candidate experiment, not a gain
claim. The prior ledger's3055–3060 mixed-target deadlock history still applies:
never mix setmaxregister targets inside one warpgroup.

## Invariants that match existing source

- **Scheduler and communication participation:**11 consumer warps = four epi,
  one MMA, two TMA, four transform; candidate605 counts352 threads. Dispatch
  remains warps8–11, scheduler7. Twelve non-dispatch warps plus four dispatch
  warps gives512 kernel-tail participants; `token_comm.py:458–466,1791–1795`
  agrees. Dispatch-to-scheduler remains160 threads.
- **Raw A/SF pipeline:** candidate549–561 mirrors local W4A16 raw pipeline
  (`moe_w4a16_kernel.py:896–913`): one TMA producer and one signaling lane per
  transform warp/multicast CTA. Relative transform tidx subtracts384; four
  transform warps supply the matching consumer count.
- **Transform/MMA pipeline:**256 producer arrivals =128 transform threads ×
  two CTAs, one UMMA consumer; matches local W4A16's formula at917–930. Decode
  retains the existing TMEM-store fence before producer commit and raw-stage
  release at local helper535–548.
- **Accumulator pipeline:**256 consumer arrivals are appropriate because the
  candidate epilogue calls release from all128 threads on both CTAs. The old
  local standalone path's eight-arrival count uses warp election and must not
  be copied here without changing release semantics.
- **Stage state persists across tasks:** candidate raw/activation loops reset
  only `count`; installed DSL `PipelineState.reset_count()` does not reset
  index or phase. The inherited transform helper has the same behavior. FC1
  and FC2 therefore continue their common two-stage rings. UMMA producer tail
  internally limits its drain to leader CTA; both-CTA call placement matches
  the existing BF16 path.
- **TMEM partition:** two128-column accumulator stages occupy columns0–255;
  two BF16 K256 transform stages occupy256–511. Helper transform offset and
  MMA A offset both use256. Epilogue has overlapping accumulators disabled.
- **Packed weights:** expert-major uint8[E,N,K/2] becomes logical FP4[N,K,E]
  without copying, with strides(K,1,N*K). Scheduler expert offset and
  tile_m_idx//2 match the existing local 2-CTA weight TMA partition.
- **Scales:** `prepare_scale_buffers()` preserves bytes, uses the public
  batched `block_scale_interleave`, and requires N%128/K%256. That public
  function returns expert-major flat native SF storage
  (`fp4_quantization.py:389–399,1155–1192`). Candidate231–237 uses the matching
  `tile_atom_to_shape_SF(...,16)` view. Weight rows and SF rows already have
  interleave32 before this storage permutation.
- **Interleave and numerical order:** no standalone gated-row transform is
  applied because candidate mixed activation_type isNone. Candidate FC1
  epilogue188–189 pairs gate32/up32, folds four warps into64 output features
  per CTA, and applies FP32 alpha before the inherited W4A16 SwiGLU association
  and BF16 handoff. FC2 alpha is FP32 before BF16, and routing stays in the
  existing external reduction.
- **Activation descriptors:** fixed-N128 B TMA uses the actual 2-CTA MMA B
  partition, preserving the two halves of the route dimension. The current
  candidate does not use dynamic-N. If dynamic-N is enabled later, it must
  also apply the existing non-leader TMA-B shift; changing only the instruction
  descriptor is insufficient.

These are source-derived checks, not compilation, sanitizer, numerical, or
performance validation. Finite-clamp support, smaller K geometries, dynamic-N,
more transform stages/warps, and scheduling profiles beyond scalar flag1 need
separate evidence before promotion.

## Optional BF16 runtime-N helper review

`candidates/w4a16_swap/dynamic_mainloop.py` is source-consistent for the stated
M256/2-CTA, allocated-N128, BF16 K256/TMEM-A case. It remains unintegrated and
unvalidated numerically.

- `bf16_static_idesc()` lines25–31 matches the repository's non-block-scaled
  builder `flashinfer/cute_dsl/sparse/sm100_blk64/mma_sm100_desc.py:149–164`:
  FP32 C=1 at bit4, BF16 A/B=1 at bits7/10, K-major bits15/16 zero, N/8 at17,
  and M/16 at24. M256 base is0x10000490. It correctly does not copy the NVFP4
  block-scaled scale-ID fields into the BF16 descriptor.
- `_issue_bf16_atom()` lines49–57 uses 32-bit TMEM addresses for D and A, a
  64-bit shared descriptor for B, 32-bit idesc, and a predicate for accumulation.
  This matches the documented non-block-scaled
  [tcgen05.mma TMEM-A form](https://docs.nvidia.com/cuda/parallel-thread-execution/#tcgen05-mma-instructions-mma).
  Literal inline PTX needs its own elected issuer; the helper's `elect_one()`
  is appropriate, while its caller must additionally remain leader-CTA-only.
- CPU-only `ptxas`13.2.78 accepts the helper's form without an explicit
  disable-output-lane vector for both CTA groups. It also accepts explicit
  zero-valued register vectors. The group2 omitted-mask and explicit-mask SASS
  dumps are identical and contain UTCHMMA.2CTA. This resolves an apparent
  difference from the explicit-mask CUTLASS reference. No module was loaded or
  kernel executed. Source harness is `candidates/dynamic_bf16_ptx_syntax_probe.py`,
  results `logs/dynamic-bf16-ptx-syntax-probe.log` and remote artifacts under
  `logs/dynamic-bf16-ptx-syntax/`.
- K16 is correct for BF16×BF16→FP32 according to the
  [CUTLASS4.7 operation definition](https://docs.nvidia.com/cutlass/4.7.0/media/docs/pythonDSL/cute_dsl_api/cute_nvgpu_tcgen05.html#cutlass.cute.nvgpu.tcgen05.MmaF16BF16Op).
  Thus K256 requires16 atom issues, unlike the NVFP4 helper's four K64 issues.
  The helper's `(None,0,inner_k)` A/B indexing mirrors the existing dynamic
  helper and preserves fragment-provided K addresses. At integration, assert
  both fragment K extents are16 and M/N inner extents are1; pass stage-sliced
  fragments and the current outer K count, not a stage index. `accumulate`
  correctly becomes false only for outer-K0/inner-K0.
- Dynamic N is align16(valid), which is legal for2-CTA BF16. Positive work
  tiles must satisfy1<=valid<=allocated_N. The helper's M128→CTA-group1
  inference is only valid under its stated per-CTA-M128 convention; it is not
  a general replacement for a2-CTA M128 tactic. No new tactic is proposed.

Required coupled changes for runtime-N:

1. Apply `compute_non_leader_cta_load_shift()` to **both FC1 and FC2 BF16 B
   views**, only on CTA1, before local tiling/partitioning. This is the current
   NVFP4 kernel's pattern at `kernel_fc12.py:1927–1935,2049–2057`. For allocated
   N128 and valid1..16, shift=-56, so CTA1's static+64 begins at token8. For
   valid17..32 shift=-48; valid65..80 shift=-24; valid113..128 shift=0.
2. Preserve allocated-N128 as the global token-tile stride, scheduler capacity,
   accumulator stage pitch, and return-metadata stride. Runtime N changes the
   instruction and B split, not those storage contracts. A conversion/layout
   and stage counts remain unchanged; there is no activation-SF companion.
3. Both CTA epilogues still own their feature halves and the full logical
   token range. Guard stores with `valid_tokens_in_cta_tile`, never with half
   the dynamic N. No padded/stale TMEM columns may reach BF16 FC1 or combine
   outputs. Current per-token activation and transpose operations do not
   intentionally reduce across token columns, but variable-N numerical tests
   must confirm this assumption after the chosen epilogue refactor.
4. Keep transform/activation waits, per-K release, accumulator commit, and
   FC1-completion publication unchanged. Dynamic-N must be one coordinated
   variant after fixed-N passes. Boundary tests should exercise valid counts
   1,16,17,32,33,64,65,96,97,127,128,129,257, skewed experts, and repeated
   launches so changing runtime N cannot mask a ring-state or stale-TMEM bug.
