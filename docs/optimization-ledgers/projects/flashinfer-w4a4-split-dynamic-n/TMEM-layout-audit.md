# Split Blackwell block-scaled MoE TMEM layout audit

This records the validated warp-local up16/gate16 block-scaled epilogue. The up64/gate64 diagnostic and superseded TRT32 experiments remain in `transfer/epilogue-debug/`; their evidence is not substituted for the final-layout checks below.

## Snapshot and evidence

- Baseline: `a65d5b09e7e4c4c5c160b0161c48becd100b3970`; the original audit snapshot is identified by the source hashes below. Later checkpoints are recorded separately in `CORE_PERFORMANCE_ITERATIONS.md` and the project README.
- Epilogue source: `flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/utils.py`, SHA256 `1e4a5e1603b0cc7d24e88b815432069b5cc269e2c347f506f56b007255a56f0e`. The source was restored byte-for-byte after the superseded TRT32 experiment, so the existing logs05/06 directly validate this snapshot.
- Shared core source: `flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py`, SHA256 `54e3bb3b9c71fa187fe7348496ea6cf1eb87a5c535a243fd7263b987e8120b7c`.
- Task-local probe: `scripts/probe_epilogue.py`; complete final-layout output: `logs/probe-epilogue-05.log` (per-tensor) and `logs/probe-epilogue-06.log` (`--per-token`). The exact probe snapshot is also preserved at `transfer/epilogue-debug/probe_epilogue_up16_final.py`. TRT32 source/probe and successful logs07/08 remain archived, but do not describe the retained implementation.
- Device/runtime: C1 B200 GPU1, image `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2, CuTe DSL4.7.1. No performance measurement or sanitizer claim.
- Production files stayed frozen during the final probe. The synthetic probe bypasses routing, GEMM, and expert SF loads; the kernel owner's phase probes independently cover those paths.

Reproduction inside the devbox:

```bash
cd /workspace/flashinfer-w4a4-split-dynamic-n/candidate
CUDA_VISIBLE_DEVICES=1 PYTHONPATH=. \
  /workspace/flashinfer-w4a4-split-dynamic-n/.venv/bin/python -u \
  /workspace/flashinfer-w4a4-split-dynamic-n/scripts/probe_epilogue.py
# Repeat the same command with --per-token for the focused per-token audit.
```

## Epilogue atoms and register coordinates

TMEM uses channel rows and token columns, with address `base + (row << 16) + column`. The four epilogue warps own physical row groups `[0,32)`, `[32,64)`, `[64,96)`, and `[96,128)`. A pointer to another warp's row group does not transfer ownership to the issuing warp. The original gated implementation incorrectly tried that and aliased up/gate values. The final prepared up16/gate16 layout places both activation operands inside the issuing warp's own row group, eliminating that access and the temporary activation-payload exchange.

The transpose remains the MegaMoE-derived four-round sequence in `utils.py:186–250`; it operates entirely inside one warp's 32-row group. For warp `w`, half `h` (0 or 1), lane `L`, register `i`, and token-slab origin `t`:

```text
raw Ld16x64.x16:
  channel = 32*w + 16*h + (L % 2)*8 + L//4
  token   = t + 2*i + (L//2)%2

after transpose:
  channel = 32*w + 16*h + i
  token   = t + L
```

The final probe encoded every physical coordinate as `1024*channel + token` and verified all 4096 raw-load coordinates plus all 4096 post-transpose coordinates exactly, including both halves of all four warps. The formulas also match MegaMoE's `TmemTranspose16x32.InputContract` and `OutputContract`; no MegaMoE production source is changed or imported by this implementation.

| Stage | Copy atom | Physical rectangle | Per-lane FP32 registers |
| --- | --- | --- | ---: |
| Initial load and round2 reload | `Ld16x64bOp(x16)` | 16 rows ×32 columns | 16 |
| Round1 store after `perm1` | `St16x128bOp(x8)` | 16×32 | 16 |
| Round2 store | `St32x32bOp(x16)` | 32×16 | 16 |
| Round3 loads | two `Ld16x256bOp(x2)` | top 16×16 and bottom 16×16 | 8+8 |
| Round3 store after `perm3` | `St32x32bOp(x16)` | 32×16 | 16 |
| Round4 loads | two `Ld16x128bOp(x4)` | top 16×16 and bottom 16×16 | 8+8 |
| Round4 register permutation | `perm1` | no TMEM store | 16 |

`perm1 = (0,8,2,10,4,12,6,14,1,9,3,11,5,13,7,15)` and `perm3 = (0,1,4,5,2,3,6,7,8,9,12,13,10,11,14,15)`.

Both original 16×32 halves are loaded into independent registers before either transpose reuses TMEM. Top transpose source is rows 0–15; destination is all 32 rows/columns0–15. Bottom transpose source is rows 16–31; destination is all 32 rows/columns 16–31. The bottom source registers survive any overlap with the top transpose. Each new token slab advances by 32 columns, so later slabs remain untouched.

## Warp-local gated activation and scratch lifetime

`utils.py:533` loads up from local rows 0–15 and gate from local rows 16–31 of each warp's 32-row TMEM group. Both fragments are loaded before TMEM is reused. No activation values are exchanged through SMEM. Non-gated FC1 and FC2 retain ordinary consecutive channel rows.

```text
physical up channel   = 32*w+i
physical gate channel = 32*w+16+i
logical output channel = channel_tile_start/2+16*w+i
output token           = route_start+t+L (after transpose)
```

Per-tensor scaling activates the two raw register fragments first and transposes the resulting 16-channel fragment once. Per-token scaling transposes the local up/gate fragments first, so each lane multiplies both with `alpha[expert] * per_token_scale[token_mapping[row] // top_k]`, then applies activation. Packed FP32 arithmetic remains elementwise; the transpose introduces no arithmetic reduction.

This shares NVFP4 MegaMoE's 16-row pairing geometry, but preserves CuTe's existing up-first semantic order. Mega's `nvfp4_nvfp4_bf16_cutedsl/weights.py:76–100` prepares gate16/up16 from canonical [gate,up]; its prequantized branch applies the same permutation to SF rows at181–184 and leaves FC2 rows ordinary at187–193. `moe_nvfp4_swapab/runner_common.py:429–460` reads gate first, up second. Therefore these are the same warp-local fusion design, not byte-identical prepared weight conventions. No MegaMoE source is changed.

The superseded TRT32 implementation passed its diagnostic matrix, but changed ordinary row order and required two gated per-tensor transposes in the straightforward implementation. It is preserved under `transfer/epilogue-debug/utils_trt32.py` and `probe_epilogue_trt32.py`; no direct-load performance claim was established before reverting to the narrower existing CuTe structure.

Only gated SF32 output needs a cross-warp exchange: four warps × 32 token lanes × one FP32 maximum = 512 bytes. The core passes a Float32 alias of existing `storage.a` after `acc_pipe.consumer_wait` (`core:769–788`). All K-stage operand consumption has completed; these same 128 loader/epilogue threads cannot load the next tile until epilogue returns, and the MMA warp waits for accumulator release. The max-exchange helper finishes its reads with a 128-thread barrier before returning. There is no additional SMEM allocation, no 16 KiB payload stage, and no SMEM exchange on SF16 output.


## MegaMoE layout precedent and coverage boundary

The retained split layout follows the swap-AB 16-row pairing design while preserving CuTe's existing up-first semantics. Mega's canonical API uses gate-first semantics. Pairing is a row permutation independent of data encoding, so the split kernel can retain its existing dtype validation without adopting a Mega frontend.

| Source path | FC1 pairing / MMA orientation | Actual coverage boundary |
| --- | --- | --- |
| SM100 legacy NVFP4 | gate16/up16; activations on B | NVFP4 SF16/E4M3; `moe_nvfp4_swapab/kernel_fc12.py:101–104` rejects other SF vector sizes |
| SM100 legacy homogeneous MXFP8 | gate32/up32; activations on A | E4M3 or E5M2 with SF32/E8M0; `moe_mxfp8_glu/kernel_mxfp8_glu_fc12.py:53–55,834–861` |
| New shared GenPhase source and preparation | gate16/up16; activations on B | Preparation branches cover NVFP4, E4M3, E5M2, and W4A8 FP4×E4M3; this is broader than the public SM100 frontend |
| Public SM100 GenPhase frontend | same gate16/up16 source | `next_cutedsl_megamoe/shim/genphase.py:53–73` restricts to MXFP8 E4M3, SwiGLU, grouped scheduling, separate BF16 reduction, and three specific tile/cluster geometries; `107–110` requires that config type |

Exact source anchors (all beneath `flashinfer/moe_ep/`):

- Legacy NVFP4 preparation: `backends/mega/kernel/sm100/nvfp4_nvfp4_bf16_cutedsl/weights.py:76–100,181–193`; gate16/up16 and identical SF row permutation, ordinary FC2. Its device epilogue sets `Fc1GateUpInterleave=16` at `kernel_src/sm100/cutedsl_megamoe/src/moe_nvfp4_swapab/epilogue.py:40` and loads gate/up from local row halves at3015–3029 with `Ld16x64.x16`.
- Legacy homogeneous MXFP8 preparation: `backends/mega/kernel/sm100/mxfp8_mxfp8_bf16_cutedsl/weights.py:41–55` uses32-row groups. Actual epilogue loads32 values per token with `Ld32x32.x32` at `kernel_src/sm100/cutedsl_megamoe/src/moe_mxfp8_glu/epilogue_mxfp8.py:715–727`, then calls thread-local `quant_sfd_row` at765. The stale "cross-warp E8M0 exchange" docstring at547 does not describe that live path.
- Shared GenPhase preparation: `kernel_src/sm100/next_cutedsl_megamoe/shim/kernel_helpers.py:242–262,280–292,319–351,366–432` applies the same gate16/up16 row permutation to weights and scales for its admitted kinds and leaves FC2 row order ordinary.
- Shared GenPhase SF32 exchange: `kernel_src/sm100/next_cutedsl_megamoe/src/blackwell_genphase_sources/kernel_src/blackwell/inference/mega/block_scaled_swap_ab_fc12_epilogue.py:65–69,215–255,1768–1829,1867–1872` explicitly joins16-channel local maxima between `(warp,lane)` and `(warp^1,lane)`, with publish and retire barriers. It batches two32-token slabs in output-stage scratch; split batches one slab in512 bytes of dead A-stage scratch. The same mathematical block maximum and token-preserving pairing are used.

The shared GenPhase `quant_def.py` includes homogeneous MXFP4 in its underlying enum, but the block-scaled shim's `_KIND_TABLE` and preparation branches do not expose it. The enum's SF policy at43–48 explicitly excludes SF16/E8M0 despite hardware support. Its type pairs at117–123 also omit additional mixed FP4/E5M2 or E4M3/E5M2 combinations. Therefore source-level layout precedent is not evidence that a complete Mega frontend supersedes the existing generic split API. No MegaMoE source is changed.

## SF16/SF32 reductions and output stores

- SF16: each lane reduces only its own 16 adjacent output channels; no token-lane reduction occurs.
- Gated SF32: `utils.py:438–448` writes one local 16-channel max per `(warp,lane)` to SMEM and reads `(warp^1,lane)` after a barrier. Adjacent channel fragments join while token lane remains unchanged. A second barrier prevents the next slab from overwriting a peer max before it is read.
- Non-gated SF32: the same lane combines its top/bottom 16-channel fragments directly. No inter-warp exchange is needed.
- Only the first channel fragment of each scale block writes the output scale. The normal output and SF stores are guarded by `token_start + lane < valid_tokens`.
- NVFP4 FP4/E4M3/SF16, FP4/E8M0/SF32, and MXFP8 E4M3/E8M0/SF32 had zero scale-code and output-code mismatches against the task-local arithmetic checks. E8M0 reference conversion explicitly uses round-up; `torch.to(E8M0)` uses a different rounding convention and was not retained as the reference for that conversion.

## Runtime-N and poisoned-tail results

All capacities 16/32/64/128 were tested. For each capacity the probe tested every applicable value from `0,1,15,16,17,31,32,33,63,64,65,127,128`.

Before each partial-N launch, every inactive TMEM input column was set to NaN, including columns 16–31 of an allocated 32-column N16 tile. Every output byte and SF byte was initialized to a sentinel. Checks required live rows and live scale codes to be bitwise identical to the full-N launch and all invalid row stores to remain untouched.

- 36 full-capacity variants: identity FC2 FP32; Relu2/SwiGLU FC1 FP32; Relu2/SwiGLU NVFP4 SF16; Relu2/SwiGLU FP4/E8M0 SF32; Relu2/SwiGLU MXFP8 SF32, over all four N capacities.
- 306 runtime-N poison/masking checks passed for those 36 variants.
- A separate per-token run covered Relu2 and SwiGLU FP32 at all four capacities with nonuniform scales and reverse token mapping: eight full-capacity variants and 68 additional poison/masking checks passed.
- Identity and Relu2 FP32 results were exact versus the arithmetic reference. SwiGLU max absolute error versus PyTorch SiLU was at most `1.9073486328125e-06`; this is an approximate-transcendental comparison, not a general bit-exact activation claim.
- Every tested quantized output reported `sf_mismatch 0`, `sf_maxerr 0.0`, and `code_mismatch 0`.

The poison checks establish that unwritten columns cannot contaminate valid token lanes through the transpose, warp-local activation, or SF16/SF32 max reductions in these exercised paths. They are focused diagnostic evidence, not a substitute for the existing end-to-end numerical tests or deferred sanitizer coverage.

## Mainloop allocation and descriptor audit

The shared core uses physical M=128 channels and N=routed tokens. `allocated_n=max(32,tactic_n)` reserves a complete32-column transpose slab even when the tactic or runtime MMA width is16. The actual MMA descriptor uses `16*ceil(valid_tokens/16)` columns; it does not change the allocated stride or SF base addresses.

All intervals below are half-open TMEM column ranges relative to the allocation base; every column has128 physical 32-bit rows.

| Tactic N | Allocated N | Accumulator columns | Reserved SFA columns | Reserved SFB columns | Allocated columns |
| ---: | ---: | --- | --- | --- | ---: |
| 16 | 32 | [0,32) | [32,48) | [48,64) | 64 |
| 32 | 32 | [0,32) | [32,48) | [48,64) | 64 |
| 64 | 64 | [0,64) | [64,80) | [80,96) | 128 |
| 128 | 128 | [0,128) | [128,144) | [144,160) | 256 |

The power-of-two allocation is `next_power_of_two(allocated_n+32)`. Both SF bases are derived from the Float32 TMEM pointer before recasting to the SF byte type. Therefore datatype recasting cannot accidentally shrink those base offsets. Epilogue transpose scratch stays inside the accumulator interval; even N16 cannot reach SFA at column32. The four epilogue warps cover rows 0–127 and never need a row beyond127.

A host-only CuTe compilation instantiated the actual installed layout helpers for NVFP4, homogeneous MXFP4, mixed W4A8, and homogeneous MXFP8 at allocatedN32/64/128. It launches no GPU kernel. Reproduction:

```bash
cd /workspace/flashinfer-w4a4-split-dynamic-n/candidate
CUDA_VISIBLE_DEVICES=0 PYTHONPATH=. \
  /workspace/flashinfer-w4a4-split-dynamic-n/.venv/bin/python \
  /workspace/flashinfer-w4a4-split-dynamic-n/scripts/audit_tmem_layouts.py
```

The complete layouts are in `logs/tmem-layouts.log`. Accumulator layout is `((128,N),1,1):((65536,1),0,0)`. SFA and SFB layouts are identical for these M128/N<=128 cases; the helper deliberately retains a full128-row SF slab for SFB even when N is smaller. The byte-addressed SF layouts give:

| Native type | K per stage / instruction | Actual SF columns per operand | Inner-K column offsets | Inner-K byte selectors |
| --- | --- | ---: | --- | --- |
| FP4/FP4, SF16 | 256 /64 | 16 | 0,4,8,12 | 0,0,0,0 |
| FP4/FP4, SF32 | 256 /64 | 8 | 0,0,4,4 | 0,2,0,2 |
| Mixed FP4/FP8 or FP8/FP8, SF32 | 128 /32 | 4 | 0,0,0,0 | 0,1,2,3 |

Each native step also uses the four-column scale layout atom. The SF layouts' physical row contribution is `(row_within32 + 32*replica)` for replica0–3, hence rows 0–127. The maximum used SF column is15,7,or3 respectively. Reserving16 columns for each operand covers every supported case without overlapping the accumulator or the other SF operand.

The runtime descriptor places `(round_up(valid_tokens,16)/8)` in bits17–22. Scale-byte selectors come from the top two bits of CuTe's encoded SF pointer and are inserted into bits29–30 for A and4–5 for B. Extraction is `(pointer >>30)&3` before placement, so signed Int32 right shifts cannot propagate sign bits into unrelated descriptor fields. This matters for mixed/FP8 inner steps2 and3 and MXFP4 steps1 and3. Descriptor format bits are constant for a compiled dtype combination; changing live N does not replace them.

The native instruction receives weights as operand A and activations as B. A's channels stay on M; B's live routed-token count supplies runtime N. There is no two-CTA B offset or cluster multicast in this implementation. Partial-token activation data and SFB copies are zero-filled by predicated cp.async, while output stores use the exact valid count rather than the rounded MMA count. K-tail scale copies also zero-fill whole four-scale atoms; supported K alignment is64 for SF16 and128 for SF32.

## Independent mainloop phase evidence

Task-local probes manually construct route metadata and decode FP4 values with a small value table. They bypass native routing JIT and compare the actual common kernel output with PyTorch matrix multiplication using exactly representable FP4 values and power-of-two scales.

- `scripts/probe_phases.py`, `logs/phase-probe-01.log`: 30 NVFP4 FC2 cases, all FP32 outputs bit-exact. Covers M256, N tactics16/32/64/128, live counts1/17/35/67/129, K64/256/384, unit or independently varying SF powers, reverse expanded-row scatter, and repeated tiles on one persistent CTA.
- `scripts/probe_mixed.py`, `logs/phase-probe-mixed-01.log`: 30 native mixed W4A8 FC2 cases, all FP32 outputs bit-exact. Covers the same N/tail/scatter structure, K128/256/384, independent E8M0 SF powers, and148 persistent CTAs. This exercises weight-TMA unpacking and all four SF byte selectors.
- `transfer/kernel-debug/probe_fc1_up64.py`, `logs/phase-probe-03.log`: 20 corrected up64/gate64 FC1 cases, all BF16 outputs bit-exact for these inputs. Covers all N tactics, partial/repeated tiles, reverse activation gather, independent SF powers, and both per-tensor and per-token alpha. This evidence is historical once the external weight layout switches to up16/gate16; the probe must use that new arrangement before revalidation.
- `logs/smoke-22.log` / `.exit`: full end-to-end smoke was intentionally stopped during native JIT with exit143 when the user changed the weight-layout design. It provides no end-to-end correctness verdict. No production source was changed during that run.

The phase probes establish the exercised operand/SF address mapping, dynamic widths, and output scatter. Homogeneous MXFP4/MXFP8 have the static layout evidence above but are not covered by these two numerical mainloop scripts. Full existing backend tests and sanitizer checks remain separate validation boundaries.


## Superseded TRT-layout W4A16 experiment (historical)

This section describes the archived TRT row-shuffle experiment only. It is not the current layout. Production uses up16/gate16 for gated weights and ordinary FC2/non-gated rows; the W4A16 change only removes its old up64-to-up16 decode permutation. Current six-case compatibility evidence is `logs/phase-w4a16-layout-01.log`. Preserve the following experimental details for provenance.

The split W4A16 epilogue retains its internal logical row order: gated up16/gate16 within each warp, ordinary consecutive channels for Relu2/FC2. Only the decode view over packed weights and scales changes to consume the common TRT MajorK row shuffle. The same CuTe composition is applied to both input payload and scale-factor rows.

For each128-row CTA tile:

- Gated desired coordinates are `(i, gate, group)` with `i=0..15`, `gate=0..1`, and `group=0..3`. The source TRT row is `i//2 +16*(i%2)+8*gate+32*group`. CuTe shape/stride is `(((2,8),2),4):(((16,1),8),32)`.
- Non-gated desired row `i=0..127` reads TRT row `(i%32)//4+8*(i%4)+32*(i//32)`. CuTe shape/stride is `((4,8),4):((8,1),32)`.

These mappings leave W4A16 MMA, accumulation, activation, epilogue arithmetic, and output coordinates unchanged. No MegaMoE production or reference source changed.

Task-local `scripts/probe_w4a16_layout.py` loads the preserved old kernel from `transfer/w4a16-layout-old/moe_w4a16_kernel.py`. The control uses old up64/gate64 preparation for gated FC1 and unshuffled ordinary rows. The candidate uses public `shuffle_moe_weights(weights,is_gated)` for both packed weights and linear scales before SF packing. Both receive identical canonical random packed weights/scales and BF16 activations; the probe bypasses routing and quantizer JIT.

All12 BF16-bit comparisons passed with zero mismatches and max absolute error0:

| Tactic | Live tokens | Activations/phases checked | Bitwise identical |
| --- | ---: | --- | --- |
| M128/N32/K256, cluster1,1 | 17 | SwiGLU; SiTU beta1 /linear beta1.5; Relu2; FC2 | all4 |
| M256/N64/K256, cluster2,1 | 33 | SwiGLU; SiTU beta1 /linear beta1.5; Relu2; FC2 | all4 |
| M128/N128/K256, cluster2,1 | 65 | SwiGLU; SiTU beta1 /linear beta1.5; Relu2; FC2 | all4 |

Complete output: `logs/phase-w4a16-trt-layout-01.log`. The earlier six-case plain up16/gate16 experiment remains archived as `transfer/w4a16-layout-old/probe_w4a16_up16.py` and `logs/phase-w4a16-layout-01.log`; it is not the final preparation contract.

The canonical Mega W4A16 reference file in this upstream base consumes canonical weights, so it does not need a prepared-layout selector. Existing `test_weight_scale_mapping` now shuffles weight and scale rows together and retains its canonical expected values and zero tolerance. The direct comparisons above cover the gated and ordinary decode mappings changed here; performance and broad end-to-end tests remain separately tracked.


## N256 feasibility probe (task-local, 2026-10-24)

This originally verified a possible larger tactic before production integration. N256 is enabled at `de4f1aa4`, with mainloop validation and performance evidence recorded in `CORE_PERFORMANCE_ITERATIONS.md`; the probe results below remain the original epilogue/layout evidence. `scripts/audit_tmem_layouts_n256.py` compiles the native CuTe layouts; `scripts/probe_epilogue_n256.py` invokes the unchanged common epilogue against synthetic TMEM values. Both ran on C1 B200 GPU2 in the recorded CUDA13.2 environment, without native routing or quantizer JIT. Complete output is retained in `logs/tmem-layouts-n256.log`, `logs/probe-epilogue-n256.log`, and `logs/probe-epilogue-n256-per-token.log`.

The native accumulator layout is `((128,256),1,1):((65536,1),0,0)`. SFA remains a128-row tile. SFB expands its TMEM row grouping from `(32,4)` to `(32,8)`, and its SMEM layout gains a second128-row block:

| Operand configuration | SFA TMEM columns | SFB TMEM columns | SFB second128-row SMEM offset | SFB stage bytes |
| --- | ---: | ---: | ---: | ---: |
| NVFP4 SF16, K256 |16|32|2048|4096|
| MXFP4 SF32, K256 |8|16|1024|2048|
| MXFP8 / W4A8 SF32, K128 |4|8|512|1024|

For local row `r` in0..127 and128-row block `b`, SFB's byte offset is `stage*SFB_stage_bytes + b*(128*Ktile/SFvec) + sf_block*512 + (r%32)*16 + (r//32)*4`. SFA retains its own smaller stage stride. A conservative TMEM reservation is accumulator `[0,256)`, SFA `[256,272)`, SFB `[272,304)`, rounded to512columns. NVFP4 shared payload is54KiB per stage, so four stages use216KiB before small barrier/state allocations.

The existing epilogue's32-token slab loop handles all eight slabs without enlarging per-thread fragments. Nine per-tensor configurations and two per-token configurations passed. Each exercised22 live-token counts: `0,1,15,16,17,31,32,33,63,64,65,127,128,129,159,160,191,192,223,224,255,256`. All242 partial-column NaN-poison/sentinel checks preserved live output bytes and SF bytes and left invalid output/SF stores untouched. FP4/E4M3, FP4/E8M0 and FP8/E8M0 output scale/code mismatches were zero; identity/Relu2 FP32 results were exact and SiLU differed from the Torch mathematical reference by at most1.91e-6.

This probe alone does not verify the production N256 mainloop. The generalized SFB copy, independent stage strides and tactic validation were subsequently implemented and checked at `de4f1aa4`; see the separate kernel-owner phase evidence. The full-grid performance screen at that checkpoint still regresses and is not retained.

For a separate loader/epilogue overlap experiment, the current512-byte SF32 maximum exchange must use dedicated shared storage: borrowing the A-stage buffer is unsafe once loaders may prefetch the next tile. The TMEM accumulator is also transpose scratch, so concurrent MMA requires disjoint accumulator stages. Two stages fit forN<=128; twoN256 stages plus scale-factor storage exceed the512-column limit.

## Large unfused FC2 bulk row-scatter checkpoint (2026-10-25)

The later selected FC2 epilogue uses a natural TMEM load for N128/N256 BF16/FP16 unfused output when scratch fits. Its warp/lane/register map is `channel=channel_start+32*warp+lane`, `token=route_start+slab_start+register`. `Ld32x32b.x32`/`.x64` covers32channels×32/64tokens within that warp's owned rows. It does not write or transpose TMEM. FP32 accumulation is scaled with the existing rounded metadata contract, converted, and staged at `[token,32*warp+lane]` in dedicated SMEM. All four warps issue contiguous128-channel bulk copies to the original expanded output rows.

The metadata prefetch masks invalid routes, and bulk stores separately mask live token rows and inactive channel CTAs. Whole32/64-token loads may read inactive tail columns; those values never contribute to another row and are never stored. Stage reuse requires per-issuer `wait_group(...,read=True)` and the128-thread epilogue barrier. Scratch is independent of live operand buffers, so loader/epilogue overlap remains valid. Two64-token stages are selected only when actual dtype/layout memory fits without reducing operand pipeline depth; otherwise one32-token stage is used if it fits. Small-N, fused atomic, FP32/FP8/generated-scale paths retain the previous direct epilogue.

`logs/native-fc2-selected-contract02.log` records50 output/metadata cases; `logs/native-fc2-selected-formats01.log` records24 input-format cases. After the inactive-channel guard was added, `logs/native-fc2-selected-tail-formats.log` records24 M384 cases with all six input-format configurations, per-token on/off, top-k8 scatter, repeated partial route tiles and untouched row/trailing sentinels. Native NVFP4, MXFP8 and mixed W4A8 captured inputs also compare byte-exactly to the frozen d907 control. Exact source hashes, commands, all measured phase medians and the remaining performance boundary are in `scripts/native_fc2_experiment/{README.md,manifest.json,results.json}`. This is a locally integrated checkpoint awaiting the final combined full-MoE screen, not a retention claim.
