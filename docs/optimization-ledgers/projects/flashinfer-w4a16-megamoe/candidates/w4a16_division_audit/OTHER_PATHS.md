# Division/remainder audit outside the owned scheduler

Read-only source audit at retained commit `083a9fd39e7ddda43a8b912ef50f7a13390287f9` (source `e470f255`). Owned `fc1_fc2_fuse_sched.py` is excluded and reviewed separately. No source edits, imports, compiler invocations, GPU work, or new result validation were performed.

**Finding:** no additional dynamic integer divisor warrants a FastDivmod change in the owned compute, epilogue, frontend, workspace, or staging paths. Their arithmetic is host/trace work or uses fixed powers of two. The reused transport has one real dynamic quotient/remainder pair in active-source remapping. Saved native PTX confirms it remains a division, but the divisor changes with routed counts and setup amortization is unproven. This is a common/upstream transport opportunity, not an owned-scheduler change.

Paths below are relative to the [source repository](../../flashinfer):

- `A/` = `flashinfer/moe_ep/cute_dsl/megamoe/nvfp4_w4a16/`.
- `B/` = `flashinfer/moe_ep/backends/mega/kernel/sm100/bf16_nvfp4_bf16_cutedsl/`.
- `T` = `flashinfer/moe_ep/kernel_src/cutedsl_megamoe/src/src/token_comm.py`.
- `R` = `flashinfer/moe_ep/kernel_src/cutedsl_megamoe/src/moe_nvfp4_swapab/topk_reduce.py`.

## Owned arithmetic inventory

“Host/trace” includes ordinary Python setup and validation, and static integer expressions evaluated while CuTe traces a launcher or kernel. A plain Python constructor can also receive a device SSA index; those expressions are listed separately below. Tensor partition APIs named `logical_divide`, `flat_divide`, or `zipped_divide` are layout operations, not evidence of a scalar hardware division.

| Source | Division/remainder and provenance | Classification |
|---|---|---|
| `A/frontend.py:69–73,101,193` | Expert count/world size divisibility and quotient; H mod 32, I mod 64; SM count/cluster size. Configuration Python integers. | Host construction/compile setup. |
| `A/frontend.py:328–329,362–363` | Packed weight and blocked-scale shape calculations: /2, ceil /128, /8, ceil /4. | Per-call host validation; no device divider. |
| `A/workspace.py:45,49` | Byte-size ceil /8 and alignment roundup. | Host workspace planning. |
| `A/autotune.py:91` | `sample / 1000.0`, CUDA-event milliseconds to seconds. | Python timing unit conversion; preserve metric. |
| `A/megamoe_kernel.py:77,82,177–179,223–227,255–258,296–297,393,658,1383–1385,1399–1401` | Stage/TMEM capacity, geometry guards, I=gateup/2, static K256 tile counts, CTA span, zero-prefix words, aligned storage and pool shapes. All operands derive from Python configuration/layout sizes. | Host/trace. |
| `A/megamoe_kernel.py:851,876,924,930,997` | CTA rank/MMA-slice `%` and work feature `/` with MMA thread-group size 1 or 2. | Device indices, fixed power-of-two divisors. |
| `A/megamoe_kernel.py:1002` | `ceil_div(intermediate_gateup, cta_tile_shape_mnk[0])`. Both are static attributes. | Trace-time completion threshold. |
| `A/megamoe_kernel.py:1222` | `(warp - transform_warp_id[0]) // 4`. Active transform warps give the two decode-group indices. | Device index, constant 4. |
| `A/epilogue.py:72–73,223,348,552` | I, subtile counts, aligned-H/I constexpr predicates. | Trace/configuration. |
| `A/epilogue.py:127,184,402–403,475,563` | Thread `%128`, thread `/32`, lane `%32`, output column `/16`. The output column is `work.tile_m_idx*64 + warp_idx*16`, hence divisible by 16. | Device indices, fixed powers of two; no fast-divisor object needed. |
| `A/tmem_epilogue.py:472,558,567,573,594,600` | Static fragment parity, store-vector width, vector iteration count, tile divisibility and mapping domain. | Trace/layout calculations. |
| `A/tmem_epilogue.py:608–610` | Mapping lambda uses lane `%32`, lane `/32`, iteration `/2` and `%2`. Domain is 128 epilogue threads and 4/8 mapping iterations for N64/N128. | Fixed power-of-two index mapping. |
| `A/dynamic_mainloop.py:41,118,123–124,131` | Static N/2 and K/16 geometry; validation and Python loop emitting fixed instruction fragments. Dynamic aligned-token arithmetic is already a signed shift. | Host/trace constants. |
| `B/backend.py:63`, `B/weights.py:48–54,106–111,150–153` | I divisibility, blocked scales, packed weights and local expert partition. | Host preparation/validation. |
| `B/staging.py:31,43` | Width and pointer alignment eligibility. | Host fallback selection; preserve supported fallback. |
| `B/staging_kernel.py:53–64` | `width: Constexpr = self.hidden`; loop bound `width // 8`. | Constant loop limit. The copy loop is dynamic, but no runtime division is required. |

`A/custom_ext.py` and `B/config.py` contain no executable scalar division/remainder. The saved e470 N64 full-shape Mega PTX has no integer `div`/`rem` instructions outside the transport sites described below. This confirms the constant-path conclusion for that captured specialization, not every possible shape or the separately compiled reducer.

Shared `src/moe_nvfp4_swapab/moe_utils.py:302` converts byte offsets using fixed pointer-dtype width; line 870 divides the configured expert count by a fixed initialization chunk size. Its generic scale-descriptor arithmetic at 990–1006 divides by static scale-vector size/128; owned W4A16 uses its own scale descriptor construction in `A/custom_ext.py:294–311`. No dynamic divisor is introduced. Shared `flag_batch.py`, `grid_sync.py`, and `sym_buffer.py` have no executable scalar division/remainder.

The floating reciprocal at `A/epilogue.py:382–384` is intentionally `rcp_approx(1 + exp(-gate))` in SwiGLU. The saved PTX `rcp.approx.ftz.f32` instructions implement that numerical contract; integer FastDivmod is unrelated.

## Pipeline cursors and implicit layout arithmetic

The active owned kernel constructs `cutlass.pipeline.PipelineState` through `make_pipeline_state` at `A/megamoe_kernel.py:1129,1172,1264–1268,1303–1310`. Raw stage count 5 and activation/transform count 3 are compile-time pipeline sizes, but their circular indices and phase bits change on device. There is no active `RingCursor` symbol imported or instantiated in the maintained Mega source; an alternative cursor representation must not be inferred from its name.

The locally saved dependency source `candidates/cuda132_recovery_0909e/dsl_pipeline_source/cutlass/pipeline/helpers.py:830–949` stores count/index/phase independently. `advance` increments count/index, compares index with the fixed stage count, resets index to zero, and XORs phase on wrap. Index/phase accessors are field reads, not `count % stages` or `count // stages`. That older saved dependency is supporting source context; the actual retained e470 capture is the decisive current code evidence.

In that capture, raw-5 wrap uses `add`, `setp.eq ... 5`, `selp ... 0`, and `xor` (PTX 1898–1903, 2110–2115); stage-3 wrap uses the corresponding compare-to-3 sequence (2350–2355). Shared work publication uses the same compare/reset pattern at 1035–1040 for its two slots. No additional integer divider remains from pipeline stage/phase access or implicit tensor-layout coordinate arithmetic: all captured integer `div` sites map to `T:946/953`. No cursor or layout change is warranted by this evidence.

## Reused split decoder

`A/megamoe_kernel.py:24,69` imports/subclasses `Sm100W4A16GroupedGemmKernel` from `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py`. The relevant reused setup/transform methods are `_setup_attributes`, `_setup_transform_partitions`, and `_transform_tile`; the standalone split scheduler/finalization is not the Mega runtime path.

- `moe_w4a16_kernel.py:200,205,210,347,351,411,418`: static MMA/transform geometry, transform-block distribution across two decode groups, and fragment scale stride 16. These execute during trace/layout construction.
- `_transform_tile:457–568` has no explicit scalar division. Its decode call at line 541 uses `moe_w4a16_utils.decode_nvfp4_fragment_to_bf16`.
- `moe_w4a16_utils.py:178–179,183,194,210,221,236–238`: fragment sizes are exactly 32/64/128, NVFP4 scale stride is 16, and byte/scale register packing divides/modulos by 4. Python loops generate fixed register/shift selections. Both direct CUDA 13.2 conversion and the older conversion fallback avoid dynamic integer division.

## Shared transport: constant arithmetic versus dynamic remapping

The owned constructor supplies Python integers for world size, experts/rank, top-k, H and tile/padding sizes (`A/megamoe_kernel.py:261–286`). W4A16 has BF16 input/output, no activation scale-factor payload, and `token_back_reduce_topk=False`.

| Transport lines | Arithmetic | Range/constant provenance |
|---|---|---|
| `406,485–492,628,855,1021,1211,1224,1231,1703` | Byte/chunk sizes, warp routes, expert lane batches. | Constructor/constexpr values. BF16 input/output size ratio is 1; scale payload calculations are inactive for W4A16. |
| `587` | Work feature index / cluster CTA count. | Fixed C1/C2 helper; no dynamic divisor. |
| `641–644,688–695,754–755` | Lane / top-k and `%topk`; valid expert / experts-per-rank and remainder. | Lane is 0–31; valid expert IDs are within total experts. Top-k and experts/rank are positive configuration constants, including legal nonpowers of two. Constant compiler lowering is appropriate. |
| `886,891,896,977–978,1126,1300,1321` | Padding/tile ceil divisions and packed route decoding. | Fixed padding/tile/top-k; public tile N64/N128, scale padding 1. Packed route is explicitly Uint32. |
| `911,1315,1163,1170,1464–1465` | Shuffle lane `%32`; pacing ceil /4 and byte estimates /4. | Fixed divisors. Preserve signed branch-bounded pacing arithmetic. |

The dynamic pair is [T:946,953](../../flashinfer/flashinfer/moe_ep/kernel_src/cutedsl_megamoe/src/src/token_comm.py:946), inside `dispatch_pull`:

```python
num_active_ranks = Int32(popc(ballot(remaining_lane > 0)))
if num_active_ranks > 0:
    num_round_tokens = length * num_active_ranks
    if slot_idx < num_round_tokens:
        slot_idx_in_round = slot_idx % num_active_ranks
        token_idx_in_rank = offset + slot_idx // num_active_ranks
```

- Rank counts are loaded when the expert changes (916–923). The per-token round search then derives active ranks from those runtime counts (924–964). Divisor `d` is in `1..min(world_size,32)` at the division, not necessarily equal to world size or a power of two.
- For valid existing Int32 count/index inputs, `slot_idx >= 0`, `slot_idx < length*d`, quotient is in `[0,length)`, and remainder in `[0,d)`. The source does not independently prove that arbitrary oversized count products fit Int32; an optimization must preserve the existing range rather than silently assume a wider contract.
- **One pair executes per selected token.** Failed rounds only subtract a segment and update active counts. The constexpr loop produces `world_size+1` source sites, but `decided` prevents later divisions for the same token.
- Saved e470 N64 PTX confirms the origin through `.loc 3 946/953`: nine `div.s32` sites at lines 7011, 7073, 7136, 7198, 7260, 7322, 7384, 7446, 7502. The first takes the `popc` result from line 6987; remainder is reconstructed by multiply/subtract, and the quotient is reused with signed-floor correction. There are not two independent hardware divisions per source pair.
- A FastDivmod divisor created at that same chosen-token site is not an established win: creation has a cost, the quotient is already shared, and `d` can change by segment/expert. Amortization would require a clean common implementation that reuses segment/divisor metadata across token strides, or other measured lowering; its additional state/register cost needs evidence.
- `kernel_src/cutedsl_megamoe/VENDOR.md:24–30` requires a verbatim source drop. This prospective optimization belongs upstream/common or in a real supported hook; no copied transport loop or local vendor-body patch is proposed.

Saved evidence: [e470 N64 codegen directory](../../profiles/cu132-recovery0911c-static-dims-padding-revert-candidate-n64-f4-direct-i2048/codegen). Inspection only; no compile or performance attribution was added.

## Separate ordered BF16 reduction

`R:183–215` fixes `hidden_tiles = H/8` in the reducer object; `R:384–385` computes token/feature coordinates with `worker_idx // hidden_tiles` and `%hidden_tiles`. H is a positive supported multiple of 32, so the divisor is positive and static (896 at H7168, 900 at H7200). The worker index is nonnegative; excess tail workers are guarded before loads at line 387. The pair is outside the top-k loop.

These are constant nonpower divisions, eligible for compiler reciprocal/multiply lowering without a runtime divisor parameter. No captured reducer-native comparison was inspected, so no byte-level claim is made for its lowering. `R:276` grid ceil division is launch-side by fixed 128. Other quantized reducer branches are inactive for BF16 W4A16.

## Repository practice and recommendation

- `flashinfer/cute_dsl/attention/scheduler/mla_persistent.py:49–60,208–218` creates reusable divisor metadata for problem extents and uses `divmod(index, metadata)` in repeated scheduler work.
- `flashinfer/cute_dsl/sparse/sm100_blk64/bsa_fwd_combine.py:283,420–425` creates `FastDivmodDivisor(seqlen)` in the launcher, then reuses it for the fixed-length device mapping; its variable-length branch deliberately keeps direct arithmetic.
- Grouped-GEMM schedulers use the same pattern in `blackwell/blockscaled_contiguous_gather_grouped_gemm_act_fusion.py:272–282` and `blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py:257–267`, both under `flashinfer/fused_moe/cute_dsl/`. The finalize helper retains a swizzle compatibility gate. These are stable per-launch/per-problem divisors, unlike the transport's per-segment active-rank count.
- Carrying metadata through CuTe state is part of the implementation: `attention/fmha/helpers/static_persistent_tile_scheduler.py:243–319` handles extracted-value lengths explicitly. Do not assume every FastDivmod object is one scalar or copy an older reconstruction ABI blindly. Signed/floor behavior and legal dividend ranges must be checked against the actual installed DSL API before substitution.

For this bounded owned change, leave nonscheduler paths unchanged. If the common transport is optimized later, first compare emitted quotient/remainder code and divisor setup lifetime; then reuse existing routing tests with balanced/uneven/skewed counts, empty/refill, and at least three active source ranks (to exercise `d=3` and segment transitions), plus both return modes. EP2 alone only supplies `d=1/2`. Preserve exact numerical tolerances and inspect resource/register effects before any latency claim.
