# Shared NVFP4 layout: completed contract audit

PASS:129 public host-contract tests and4 exact GPU tests, with zero failures,
errors or skips. Original19133/fetch26163 closed0. Sourceaf938d808556e72925933208f0844cd92f44dff5cc7f407b050897c5660b2e9e is identical
before/after; completione7281fff0c51be8b0161c6050f9d67753f5e44d1f5c9aaa1fbedaa20236333f8; audit SHA0070f5ef6f79227dec29e57150cc52e732dcc57ee02303860391c9358a9a60ea.

GPU coverage uses both FP4/E4M3-first and uint8-first prepared representations
with changed backing pointers on the same compiled frontend. The unchanged
canonical term-band oracle passes with separate non-unit FP32 alphas; stable
and changed-input graph replay matches eager output exactly. Real BF16 and FP32
preparation for3 experts,H288/I448 produces byte-identical packed weights and
native padded SF versus W4A4. These are actual CUDA results, beyond the earlier
selected CPU loader's mocked quantizer/swizzler boundary.

Twelve actual CuTe descriptors retain leading axis1. FP4-x2 Torch packed K
becomes logical doubled K in CuTe; uint8 aliases keep packed K until explicit
kernel recasting. Static/dynamic descriptors cover H288 andH7168 weights and
native per-expert SF planes. Descriptor inspection itself launched no kernel.

Host pytest4.61s (subprocess11.070096747s); GPU pytest26.88s
(subprocess33.553500216s); descriptor subprocess6.177780046s. Original records
pin unchanged nativec6da before/after; no independent native validator rerun.
The separate18/48 reference jobs, native captures and full13AUTO will have their
own receipts. No test, original validator or GPU execution was repeated here.
