# W4 scale-byte duplication: one local PRMT

Candidate `d5105227` is an unstaged, 8+/6− change only in `moe_w4a16_utils.py`, based on b52. It preserves the independent 16-value decode helper and its public signature, every `.rn` conversion/multiply, compact scale-word shifts, all fragment ownership, and all kernel roles/waits/stages/quotas.

Retained native SASS exposes a concrete two-instruction sequence for each block scale: `PRMT … 0x7770` zero-extends the low byte, then `PRMT … 0x6540` duplicates it into the low halfword. All ten current source-equivalent native FC1/FC2 captures contain eight E4M3 conversions and eight duplication permutations. FC1 has exactly eight corresponding zero-extension permutations; some FC2 captures have two additional unrelated ones. The candidate requests the same byte pattern in a single `prmt.b32 packed, scale, 0, 0x4400`, then aliases its low halfword for the original conversion.

The selector means `{zero, zero, scale.byte0, scale.byte0}` from high to low. [PTX 13.2.2 PRMT semantics](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#data-movement-and-conversion-instructions-prmt) define source0 as low `a` byte and source4 as low `b` byte; `b=0`. The exact bit-origin proof plus196,608 upper-byte/low-byte cases is in `bit-proof.json`. Both direct BF16 and FP16 compatibility conversions receive the identical16 input bits, including signed zero and NaN encodings. No conversion or floating-point operation changes.

Expected lowering is one fewer integer instruction per independent scale block (eight per captured transform loop), without coupling adjacent blocks. This is a codegen hypothesis, not a speedup claim. Added `.b32` spelling replaces the former packed temporary; actual register allocation must be checked rather than inferred from source.

## History exclusion

- July22 compact-scale handling (`w4a16_optimization_experiments.md:1586–1624`) retained packed words plus external shifts and removed extraction of broadcast scale vectors. The candidate keeps that logic verbatim and changes only duplication *inside* the existing independent block helper.
- Two/four-scale monolithic helpers (`:1133–1154`, `:2022–2068`) combined E4M3 conversions and increased cross-block dependencies. Rejected; this proposal preserves one conversion per scale and one block-local assembly region.
- Conversion/multiply interleaving (`:1221–1242`) was neutral; this candidate preserves that source order.
- Bit decoders, scale preload, scale ownership changes, immediate TMEM fragment stores, stage shrinking and register redistribution remain closed. None is changed here.

Targeted current patch/Markdown and original-ledger searches found no identical single-block scale-duplication PRMT trial. This is a bounded history statement. The first gate is paired compile-only native FC1/FC2 captures under the original compiler options; no exact or performance launch until resources and generated instructions are reviewed. Preserve the compatibility path for later focused validation if codegen qualifies.
