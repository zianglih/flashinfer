# Independent numerical-model audit

Audit target: `research/tcgen05-model`, upstream `sf-tensor/tcgen05` at `d96b82180ac9041c09295f3a6a3c2c4e592ddce6`.

## License and provenance

- Repository `LICENSE` is MIT, copyright 2026 San Francisco Tensor Company.
- A translated or adapted source implementation may be shipped without an installed package dependency. Preserve the full copyright and permission notice with the adapted source (a link or an SPDX label alone is not the full required notice).
- This is an independent empirical Blackwell B200 model, not an NVIDIA-specified arithmetic guarantee. Its frozen validation and hardware-harness claims do not by themselves establish equivalence for our accumulated multi-instruction GEMM or for B300/SM103.
- Local `PYTHONPATH=research/tcgen05-model python3 -m tcgen05_model.validation` passed all 79 included frozen checks. I have not independently rerun the project's claimed 46-million-case hardware corpus.

## Why an ordinary BF16 warp MMA is insufficient

The production split FC2 was invoked directly with exact prepared random operands, alpha 1, unfused finalize, output FP32 where supported, K1024/4096. No activation or quantization is involved in these checks.

- NVFP4 E2M1×E4M3 values decode exactly into BF16 (at most eight significand bits). Nevertheless, SF bytes spanning 1..125 produce thousands of FP32 result mismatches versus progressive BF16 warp MMA. Resetting a partial accumulator every K16 and adding it to the total does not resolve this.
- Homogeneous MXFP8 with ordinary scale exponents 124..130 also produces FP32 mismatches at both K sizes. Resetting every K32 does not resolve this.
- MXFP8×MXFP4 wider scales produce mismatches even after the required BF16 output conversion.
- Complementary E8M0 scale bytes 254/0 produce finite native results, but dequantizing individual operands into BF16 overflows/underflows and yields NaN reference results. The product is representable even when separate dequantized operands are not.

Raw evidence is in `artifacts/quant-reference-validation/mma-extended-block-results.json`, `mma-block-r2.log`, and `mma-qualification-tensors.pt`. The first block-reset experiment (`mma-block.log`) had a harness substitution bug and is **invalid**; use `mma-block-r2.log` or the identical follow-up `mma-block-with-tensors.log`. All exploratory logs are preserved.

## Model semantics that a port must preserve

- Decode signed integer significands, value exponents, and **encoded raw exponents** separately. Replacing raw exponents with normalized product exponents changes the window selection for subnormal payloads.
- MXF8F6F4 scales use E8M0 code zero as `2**-127`, not zero. Quantizers deliberately emit payload zero when their SF code is zero, but the MMA format itself does not mean scale zero.
- MXF8F6F4 uses a shared 25-bit raw-exponent window per hardware instruction, includes prior accumulator C in that window, truncates each scaled product toward zero into it, sums integer units, then packs FP32 toward zero.
- NVFP4 uses the larger 39-bit product/35-bit scale windows; the product-dominant path sums aligned K4 groups before truncation, while C-dominant updates expose K16 groups and the C-relative 35-bit window. A universal per-element or per-SF-block RN dot is not equivalent.
- Run the scalar model sequentially with the actual hardware instruction K (NVFP4 K64; MXF8F6F4 K32), carrying the previous FP32 bit pattern into the next update. A single model call over the entire GEMM K changes the truncation boundaries.
- Truncate negative values by shifting absolute magnitude and restoring sign; arithmetic right shift of a negative integer rounds down instead.
- Guard shift counts explicitly. PTX integer shifts outside the word width cannot replace the arbitrary-precision Python model's shifts. The NVFP4 bounded significands and group shifts can fit signed 64-bit integers, but the E8M0 exponent range requires skipping terms whose truncation removes all bits before shifting.
- Final FP32 packing must explicitly preserve sign, exponent/subnormal handling, RZ significand truncation, zero canonicalization, and the observed overflow/special-value policy. Converting a large integer to FP32 with default RN and multiplying by a power of two is not an equivalent packing operation.

## Qualification boundary

The 16 saved cases contain CPU tensors with raw payload/SF bytes and native output, so the new integer port can be tested without rereading a live kernel result. This corpus is useful differential evidence, not a complete architecture proof. Extend numerical qualification to random small-format exponent boundaries, zeros, nonzero carried C, multiple tile shapes, and the actual MoE cases before replacing the narrowed integration oracle.
