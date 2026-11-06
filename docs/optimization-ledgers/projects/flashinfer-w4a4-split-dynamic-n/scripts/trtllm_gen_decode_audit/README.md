# TRTLLM Gen decode audit against retained 98fd

Read-only audit, 2026-10-25. No production edits, AUTO retuning, or primary benchmark reruns. GPU0 is released after three one-replay diagnostic traces. Parent owns the separate descriptor-only N8 prototype.

## Published source and measured binary boundary

The requested unmerged source is [FlashInfer PR2917: trtllmgen moe oss kernels](https://github.com/flashinfer-ai/flashinfer/pull/2917), open and unmerged when checked, head `64ed071e23bf8d5d2d5af5c91577e5b8e036a1cf` (`aleozlx/flashinfer`, `trtllm_oss_staging`), base `15f11e95c882c891fbd1236b0d463b56e6d655c9`. Public GitHub identity was verified as `zianglih`. The source export is Apache-2.0. `pr2917-tree.json` pins the full tree; `source-manifest.json` pins selected raw files to both Git blob IDs and SHA256.

Measured native cubins come from the newer artifact revision `8ee504560a86b6c72b8c941d3003e8fb1804b1b6/batched_gemm-fdba669-16ba8ed`. The PR source is architectural prior art, **not a claim of binary/source identity**. All six selected cubin hashes match the prior completed benchmark archive's `native-build-hashes.json` exactly. Disassembly, resources, profile databases, and immutable cache copies are in `profiles/`, with hashes in `profile-receipt.json` and `profiles/selected-cubins.json`.

Selected published FC1 sources:

- **N8-TMA-P:** `sources/src/Bmm_E2m1_E2m1E2m1_Fp32_bA16_bB16_bC16_t128x8x512_s5_et128x8_m128x8x64_cga1x1x1_16dp256b_rM_TN_transOut_schPd2x1x2x3_biasM_bN_tma_tmaSf_rgTma_clmp_swiGlu_dynB_sm100f.cu`
- **N16-LDGSTS-P:** `sources/src/Bmm_E2m1_E2m1E2m1_Fp32_bA16_bB16_bC16_t128x16x512u2_s5_et128x16_m128x16x64_cga1x1x1_16dp256b_rM_TN_transOut_schPd2x1x2x3_biasM_bN_ldgsts_ldgstsSf_rgTma_clmp_swiGlu_dynB_sm100f.cu`

The earlier downloaded `schedS` files are reference-only; the actual selected decode kernels use `schPd2x1x2x3` persistent scheduling.

## Actual saved decode winners

Single process / single GPU0, simulated EP8 (32 local experts), H7168/I2048/top-k8, original native logits routing. GPU UUID `GPU-7d34f345-ddcf-6ad5-4791-84a6f16c1281`, image `nvcr.io/nvidia/pytorch:26.05-py3`, clean reference checkout98fd. Native finalize remains enabled. T1 caches were copied; all three copies are byte-identical to the archived originals after profiling. Logs prove config-file cache hits and no autotuning.

| Tokens | T1 native tactic | Phase | Physical tile / pipeline | Actual grid | Threads | Registers/thread | Dynamic SMEM bytes |
|---:|---|---|---|---|---:|---:|---:|
| 4 | `[8,310]` | FC1 | `128x8x512_s5`, Gather4/SF Gather4 | 32×32 | 640 | 96 | 202640 |
| 4 | `[8,310]` | FC2 | `128x8x256u2_s9`, regular TMA | 56×32 | 512 | 128 | 184464 |
| 32 | `[16,84]` | FC1 | `128x16x512u2_s5`, routed LDGSTS/SF LDGSTS | 32×46 | 512 | 128 | 213904 |
| 32 | `[16,84]` | FC2 | `128x16x512_s5`, regular TMA | 56×46 | 512 | 128 | 216976 |
| 128 | `[8,98]` | FC1 | `128x8x512_s5`, routed LDGSTS/SF LDGSTS | 32×156 | 512 | 128 | 202640 |
| 128 | `[8,98]` | FC2 | `128x8x256u2_s6`, regular TMA | 56×156 | 512 | 128 | 124816 |

Every captured GEMM has zero reported local memory per thread. Nsight kernel durations are deliberately not used as replacement benchmark medians: these are one-replay identity/launch traces, with PDL overlap and the cold-L2 fill visible. The unchanged reference campaign remains the performance evidence.

The T4 FC1 actual SASS has `LDTM.16dp256bit` at PC0x5160 and0x5170, then packed `FMUL2`/`FFMA2`/quantization. There is no epilogue TMEM transpose between those reads and output. Earlier `STTM` instructions in that cubin are in scale publication; counting all STTM as epilogue work would be incorrect. `profiles/sass-opcode-counts.json` gives **static instruction counts**, not executed counts. Actual full names are retained in the receipt, not inferred from tactic integers.

## Prioritized transferable candidates

1. **One-CTA runtime N rounded to8 instead of16, keeping all current allocations/tactics.** Current98fd `_blockscaled_dynamic_mma` line137 rounds every width to16. The captured N8 native cubins and published N8-TMA-P MMA descriptor show actual M128/N8/K64 instructions. Official [PTX shape table](https://docs.nvidia.com/cuda/parallel-thread-execution/#tcgen05-mma-shapes) and [CuTe4.7 operation docs](https://docs.nvidia.com/cutlass/4.7.0/media/docs/pythonDSL/cute_dsl_api/cute_nvgpu_tcgen05.html) permit step8 for group1 across all three blockscaled instruction kinds used here; group2 must retain step16. Root is testing this separately. It reduces math for valid widths1–8,17–24,etc., but does **not** reduce A/B TMA bytes or the current32-token epilogue, so no proportional speedup is assumed.
2. **A narrow8/16-token epilogue with the existing up16/gate16 weight contract.** Current `blackwell/utils.py` lines203–279 always loads/transposes32 tokens, and `run` lines1085 onward advances in32-token slabs. N8/N16 routes therefore perform substantial inactive-token work. Published N8-TMA-P lines2279–2299 use two native16×256b TMEM loads; lines2470–2501 reduce per-token channel maxima with warp shuffles, then quantize and stage output without a TMEM transpose. Our layout differs, so reuse the load/reduction mechanism rather than copying TRT's row-shuffle or arithmetic. The concrete coordinate design below preserves our current values and leaves TMA/mainloop untouched. This is distinct from the closed large-N transpose/store experiments, which were judged mainly on N128/N256.

These are the useful new directions from this audit. I do **not** recommend porting the whole640-thread Gen topology or re-running closed CLC/cache/register experiments solely because Gen uses them. Actual Gen uses more threads and more independent rings than98fd, not a universally smaller launch. Current98fd already has wideK8 for narrow tiles, dedicated epilogue warps, two accumulator stages, packed FP32 arithmetic, and weight cache hints. CLC was tested on current pipeline and failed consistent full-chain retention (`scripts/clc_current_experiment/README.md`). Routed LDGSTS/Gather4 would undo the retained regular-TMA preparation contract and prior direct-loader experiments were negative; this audit is not authorization to restore them.

## Narrow epilogue CPU design

Keep physical rows `[up16,gate16]` within each warp's32-channel accumulator region and preserve the existing per-token/global-scale ordering, BF16/FP16 metadata rounding, activation formula, scale encoding, and exact FC1/FC2 ownership fences.

A conservative register-only adaptation of the current `Ld16x64b` load is fully coordinate-checked by `prove_narrow_layout.py`/`.json`:

- With warp lane L and register i, raw16×N mapping is `token=2*i+((L>>1)&1)`, `channel=8*(L&1)+(L>>2)`. N8/N16 requires4/8 registers per up or gate half, rather than16.
- After activation, swap register bit0 with lane bit2, then register bit1 with lane bit3. Each swap is a butterfly SHFL plus explicit register selection; there is no TMEM scratch or payload SMEM exchange.
- Result mapping is `token=((L>>1)&7)+8*(i>>2)`, `channel=8*(L&1)+4*(L>>4)+(i&3)`. Each lane has four contiguous output channels for one/two tokens. Two swap stages cost8/16 SHFL operations for N8/N16 per activated fragment.
- Reduce each local quartet, then XOR1 and XOR16 across lanes. The proof checks these peers cover exactly all16 channels of **one token**, so inactive-token NaNs cannot enter a live scale. SF32 adds the existing neighboring-warp max exchange for the same token. Stores can use packed four-channel output fragments.

A lower-instruction alternative uses `Ld16x256b` directly, as the actual cubin does. For8 columns its four registers per half map `token=2*(L&3)+(i&1)`, `channel=(L>>2)+8*(i>>1)`. Up and gate are read at row offsets0 and16; the two channels per lane share two adjacent tokens. Local two-channel maxima followed by XOR4/XOR8/XOR16 give the16-channel maximum for each token. Our output channels are not TRT-shuffled: adjacent-channel nibble packing needs explicit peer exchange (e.g. XOR4 before byte stores), or a small register transpose. Do not copy TRT's final direct packed stores assuming their row order matches ours. This alternative's mapping follows `TmemTile.h` lines51–89 and the generated bias-load coordinates; it is source-derived, not yet compiler/GPU-validated.

Before any retention claim, both designs need exact paired all-format/per-token tests, live-token counts1/7/8/9/15/16, poisoned inactive TMEM columns, SF32 token isolation, channel tails, repeated persistent tiles, and short/nonaligned K fallback. Changing a width does not permit changing allocation/descriptor bounds or assuming private invalid payload is initialized. No dedicated repository test file is proposed.

## Reproduction and evidence

The diagnostic command used a copied saved cache and the unmodified benchmark profile mode; the original timing campaign was never rerun:

```bash
cd /workspace/flashinfer-w4a4-split-dynamic-n
source scripts/recovery442/env_candidate.sh
export CUDA_VISIBLE_DEVICES=0 FLASHINFER_DIST_AWARE_AUTOTUNE=0
export FLASHINFER_AUTOTUNER_LOAD_FROM_FILE=0
export CUTE_DSL_CACHE_DIR=$PWD/cache/trtllm-reference-98fd/cute_dsl
for N in 4 32 128; do
  # Cache copies already exist; never overwrite the archived originals.
  PYTHONPATH=trtllm-reference-98fd nsys profile --trace=cuda \
    --capture-range=cudaProfilerApi --capture-range-end=stop \
    --sample=none --cpuctxsw=none --cuda-graph-trace=node \
    -o scripts/trtllm_gen_decode_audit/profiles/trt-t${N} \
    .venv/bin/python trtllm-reference-98fd/benchmarks/bench_moe_deepseek.py \
    --num-tokens "$N" --ep 8 --backends trtllm-nvfp4 --no-autotune \
    --cache scripts/trtllm_gen_decode_audit/profiles/T1-t${N}.cache.json \
    --profile-cuda --profile-backend trtllm-nvfp4 --profile-iters 1 \
    --warmup 10 --iters 100
done
```

`extract_sass_remote.py` reads the exact traced cubin paths and invokes `cuobjdump`; `archive_profiles.py` only fetches and verifies existing diagnostics. `profiles.tar.gz` and `profile-receipt.json` preserve the trace/SASS inputs. No initcheck or performance retention claim is made for the CPU design.
