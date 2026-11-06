# FC1 store granularity: held setup and measured scope

Control is retained `49c91adf47d30fc2049c76cbaf34d0ccf3291434`.
Candidate is the same source inventory with only the swap kernel at
`faae883465b0c648a4923ca3ecc241bf49e650da7b0ebe56a0a555e6f4dfcba8`.
The final qualification gate is copied unchanged as `final-gate.json`.
No production source was edited by the performance harness.

The screen covers all 26 N3U per-token cells: EP8 and TP8, tokens
1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 4096, 8192 and 16384.
The 22-cell retention aggregate excludes only tokens 1/2. Both input and
intermediate activation quantizers are included by the existing benchmark arm.
Use four serialized C/A/A/C phases per GPU, 10 warmups and 100 untrimmed strict
CUPTI cold-L2 CUDA-graph samples per phase. GPU0 runs EP8 and GPU1 runs TP8.
The 12 original timing/source/cache/resource helpers and all explicit recorded
choices/routes are unchanged. No autotuning, policy axis, compiler override or
sanitizer is introduced. Persistent native build and driver/DSL caches remain.

Before launch, the harness verifies the 16-call numerical/native gate, all
source/capture hashes, all four release Ninja descriptions and native libraries,
`ninja -n` no-work status, and GPU idleness. Full source inventories are checked
at campaign entry/exit; each process verifies the existing bounded source map.
All runtime resource guards remain fatal. Same-GPU phase results are retained
with clocks and repeat spread; no selective sample or cell removal.

The candidate groups converted output fragments using a compile-time count
based on output width and the 256-bit copy maximum. Quantized 4/8-bit captured
kernels are byte-identical to retained49. Per-token BF16 restores the prejoin
FC1 binary: representative non-NOP count increases 3309→3355 at unchanged168
registers/LOCAL0. Wider stores alone cannot justify this follow-up, because its
BF16 width is already256 bits; it must show a performance benefit. The unrelated
FP32 fused two-CTA signature reduces125→122 registers, outside this unfused
benchmark scope. Those analytic fused checks are not a general bit-exact claim.

Any later full-table reuse would comprise 442 cells:104 unchanged W4,260 gated
swap and78 quantized N3U cells. This is supported by source specialization and
representative native equality, not individual recapture of all442 images.
Only the26 per-token nongated cells are measured here. No retention, commit or
publication decision is made by the setup.
