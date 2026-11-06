# Split Blackwell block-scaled MoE TMEM layout audit

This records the validated TRT-LLM MajorK 32-row shuffled block-scaled epilogue. Historical up64/gate64 and plain up16/gate16 diagnostic probes remain in `transfer/epilogue-debug/`; their evidence is not substituted for the final-layout checks below.

## Snapshot and evidence

- Baseline: `a65d5b09e7e4c4c5c160b0161c48becd100b3970`; candidate is the current uncommitted implementation.
- Epilogue source: `flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/utils.py`, SHA256 `fa2b10cd5dc124dbb9a29118a810b0b415ba7c11916df51ba10b3f0dbe421a3e`.
- Shared core source: `flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py`, SHA256 `54e3bb3b9c71fa187fe7348496ea6cf1eb87a5c535a243fd7263b987e8120b7c`.
- Task-local probe: `scripts/probe_epilogue.py`; complete final-layout output: `logs/probe-epilogue-07.log` (per-tensor) and `logs/probe-epilogue-08.log` (`--per-token`). The previous successful plain up16/gate16 probe is preserved at `transfer/epilogue-debug/probe_epilogue_up16_final.py` with logs05/06.
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

TMEM uses channel rows and token columns, with address `base + (row << 16) + column`. The four epilogue warps own physical row groups `[0,32)`, `[32,64)`, `[64,96)`, and `[96,128)`. A pointer to another warp's row group does not transfer ownership to the issuing warp. The original gated implementation incorrectly tried that and aliased up/gate values. The final TRT32 preparation keeps both activation operands inside the issuing warp's own row group, eliminating that access and the temporary activation-payload exchange.

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

Prepared Blackwell weights use the existing TRT-LLM MajorK row permutation. For each 32-row block, the ordinary shuffle maps logical row `j` to physical row `8*(j%4)+j//4`. Gated FC1 first interleaves canonical up/gate rows, then applies that shuffle. Its physical rows are `[up-even8, gate-even8, up-odd8, gate-odd8]`.

The epilogue loads both 16-row halves before reusing TMEM, transposes each half, and uses compile-time register selections to recover logical order. No activation values are exchanged through SMEM.

```text
ordinary logical j (0..31): physical = 8*(j%4)+j//4

gated logical i (0..15), operand h (0=up, 1=gate):
  physical within warp = 16*(i%2)+8*h+i//2
  logical output channel = channel_tile_start/2+16*w+i
output token = route_start+t+L (after transpose)
```

Both per-tensor and per-token gated modes now activate the restored register fragments after the two transposes. Per-token mode multiplies both fragments by `alpha[expert] * per_token_scale[token_mapping[row] // top_k]`; per-tensor mode uses `alpha[expert]`. Packed FP32 arithmetic remains elementwise; the transpose and static row permutation introduce no arithmetic reduction.

Ordinary FC1/FC2 already required two half-transposes; the TRT permutation adds only static register selections. Compared with the preceding plain up16/gate16 experiment, gated per-tensor mode now uses two transposes instead of one, while per-token mode still uses two. The native-load mapping experiment is tracked separately; no performance claim is made from the shuffle alone.

Source contract: `prepare_trtllm_fp4_weights` and the MXFP8 branch of `prepare_trtllm_fp8_block_weights` apply `_maybe_get_cached_w3_w1_permute_indices(...,128)` for gated FC1 and `get_w2_permute_indices_with_cache(...,128)` for ordinary FC2. `get_shuffle_matrix_sf_a_row_indices` delegates to the same row permutation for both SF16 and SF32. Shuffling canonical weights before quantization therefore gives the same weight/SF row relationship without a separate SF permutation step.

Only gated SF32 output needs a cross-warp exchange: four warps × 32 token lanes × one FP32 maximum = 512 bytes. The core passes a Float32 alias of existing `storage.a` after `acc_pipe.consumer_wait` (`core:769–788`). All K-stage operand consumption has completed; these same 128 loader/epilogue threads cannot load the next tile until epilogue returns, and the MMA warp waits for accumulator release. The max-exchange helper finishes its reads with a 128-thread barrier before returning. There is no additional SMEM allocation, no 16 KiB payload stage, and no SMEM exchange on SF16 output.

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
- `transfer/kernel-debug/probe_fc1_up64.py`, `logs/phase-probe-03.log`: 20 corrected up64/gate64 FC1 cases, all BF16 outputs bit-exact for these inputs. Covers all N tactics, partial/repeated tiles, reverse activation gather, independent SF powers, and both per-tensor and per-token alpha. This evidence is historical once the external weight layout switches to TRT32; the probe must use the final arrangement before revalidation.
- `logs/smoke-22.log` / `.exit`: full end-to-end smoke was intentionally stopped during native JIT with exit143 when the user changed the weight-layout design. It provides no end-to-end correctness verdict. No production source was changed during that run.

The phase probes establish the exercised operand/SF address mapping, dynamic widths, and output scatter. Homogeneous MXFP4/MXFP8 have the static layout evidence above but are not covered by these two numerical mainloop scripts. Full existing backend tests and sanitizer checks remain separate validation boundaries.


## Shared W4A16 weight-layout adaptation

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
