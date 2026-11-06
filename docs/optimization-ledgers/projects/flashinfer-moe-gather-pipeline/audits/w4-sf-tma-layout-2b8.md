# W4 scale shared-memory bank conflicts: producer-side closure

**Decision: close without a prototype.** The current V41F TP4 W4 FC1 conflict is the same canonical scale-word mapping already investigated in the earlier W4 effort. No simple supported TMA/view change was found that preserves global scale bytes and current transform/TMEM ownership while making the loads conflict-free. Main remains clean at `2b8eb9d8`; no source edit, compiler run, GPU work, or performance claim.

## Current mapping and producer constraint

- The peer's source-bound native trace gives byte address `82944 + stage*2048 + group*1024 + warp*4 + lane*16 + word*512`. The two scale instructions read **32 distinct words through eight banks**, four words per bank. The small CPU replay in the sibling receipt checks all four transform warps and both words. These are not duplicate values that can be broadcast.
- `moe_w4a16_kernel.py:479–498` builds canonical transform and TMA views of the same bytes. The consumer is tied to the weight transform copy partition at `:617–634`; the producer uses `make_tiled_tma_atom_A(..., internal_type=Int16)` at `:988–1000`.
- Ordinary 16-byte TMA swizzles preserve byte bits 2/3, which are the two low bank-index bits. Varying the higher bits cannot spread one warp's words beyond eight banks. Larger 32/64-byte atoms do not improve this bound.
- For this ordinary Int16, non-interleaved copy, CUDA 13.2 requires a contiguous inner box in multiples of 16 bytes and outer global strides in multiples of 16 bytes; the descriptor cannot simply promote the canonical 4-byte row submode to a freely reordered outer dimension. These constraints and the supported swizzle granularities are documented in [CUDA 13.2 tensor-map encoding](https://docs.nvidia.com/cuda/archive/13.2.0/cuda-driver-api/group__CUDA__TENSOR__MEMORY.html).
- There is a qualification to the usual “all low four bits are fixed” shorthand: CUDA also documents alternate-row `FLIP_8B`. It can change byte bit 3, but leaves byte bit 2 fixed, so it still cannot produce 32 conflict-free banks here. The bundled CUTLASS TMA converter contains its internal enum but no corresponding conversion case. This audit does not claim it is impossible to build a separate lower-level path; that would be a different, unqualified design, not the simple existing-layout correction sought here.

## Exact prior experiments

The older ledger is `../flashinfer-w4a16/w4a16_optimization_experiments.md`:

| Lines | Trial | Recorded result |
|---|---|---|
| 621–652 | B1/B2 scale allocation swizzles | Same N-way conflict counts; neutral B1, slower B2. |
| 926–937 | Subgroup scale-word broadcast | K-varying cases passed but row-varying cases failed; conflicting words are distinct rows. |
| 1178–1199 | Four-warp transform ownership transpose | Some shapes passed, route8/mixed128 failed; source ownership cannot be changed independently of physical TMEM ownership. |
| 1201–1218 | Consistent TMA/shared atom transpose from `16*m0+4*m1+k1` to `4*m0+128*m1+k1` | Layout-equivalence failure or illegal instruction. This is exactly the 4-byte regrouping needed by the new proposal. |

These are historical ledger findings, not rerun or independently re-audited raw measurements in this task. The new profile confirms the same address mechanism, not a new performance result.

## Existing references and scope

MegaMoE BF16/NVFP4 explicitly reuses the same mixed-input scale layouts and Int16 TMA construction (`megamoe_kernel.py:804–839`), then the same transform partitions. It therefore does not provide an alternate conflict-free producer mapping. Rubin's block-scaled scale-to-TMEM path consumes the canonical block-scale format directly; it does not solve this W4 register-dequantization ownership requirement. The bundled CUTLASS `BlockScaledBasicChunk` likewise uses the same canonical atom.

Changing physical SF format, adding a shared transpose/shuffle, changing transform/TMEM ownership, or adding a separate load mechanism would require fresh design and evidence. None is proposed by this bounded audit. The existing source and staged byte footprint remain unchanged.
