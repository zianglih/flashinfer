# T128 bulk-drain inactivity proof

CPU proof passed: 15 of 16 saved native winners have every changed path constexpr inactive. Nemo NVFP4 is the one active exception.

Both saved repetitions, exact cache keys/values, actual phase dispatches, routing, quantization contracts, source maps and all input file hashes are checked in `receipt.json`. No GPU work was performed.

FC1 has `scatter_output=False`. For the 15 inactive winners FC2 N is below 128, so the unchanged constructor sets `bulk_output_bytes=0`; the unchanged `_epilogue_storage` returns `(0,0,512)` for any capacity. The moved bulk drain is unreachable, and both new final drains have false constexpr guards. Exact source motion and the full remaining executable AST after this specialization are checked against the frozen baseline.

| Model | Precision | FC1 M/N/K-steps | FC2 M/N/K-steps | CLC FC1/FC2 | Bulk tokens FC2 | Guard |
|---|---|---|---|---|---:|---|
| v3 | NVFP4 | 128/64/8 | 128/64/8 | True/True | 0 |  |
| v3 | NVFP4 per-token | 128/16/8 | 128/16/8 | True/True | 0 | selected |
| v3 | MXFP8 | 128/64/8 | 128/64/8 | True/True | 0 |  |
| v3 | MXFP8 x MXFP4 | 128/16/8 | 128/16/8 | True/True | 0 |  |
| v41-flash | NVFP4 | 128/32/8 | 128/32/8 | True/True | 0 |  |
| v41-flash | NVFP4 per-token | 128/32/8 | 128/32/8 | True/True | 0 |  |
| v41-flash | MXFP8 | 128/16/8 | 128/16/8 | True/True | 0 |  |
| v41-flash | MXFP8 x MXFP4 | 128/16/8 | 128/16/8 | True/True | 0 | selected |
| kimi-k3 | NVFP4 | 128/32/8 | 128/32/8 | True/True | 0 |  |
| kimi-k3 | NVFP4 per-token | 128/16/8 | 128/16/8 | True/True | 0 |  |
| kimi-k3 | MXFP8 | 128/16/8 | 128/16/8 | True/True | 0 | selected |
| kimi-k3 | MXFP8 x MXFP4 | 128/16/8 | 128/16/8 | True/True | 0 |  |
| nemo3-ultra | NVFP4 | 256/128/8 | 256/128/4 | True/True | 64 | selected |
| nemo3-ultra | NVFP4 per-token | 128/32/8 | 128/32/8 | True/True | 0 |  |
| nemo3-ultra | MXFP8 | 128/32/8 | 128/32/8 | True/True | 0 |  |
| nemo3-ultra | MXFP8 x MXFP4 | 128/32/8 | 128/32/4 | True/True | 0 |  |

Nemo NVFP4's source-derived resource supplement uses explicit 232448-byte SMEM / 512-column TMEM bounds: K-steps 4, six 28672-byte operand stages, 384 metadata bytes, 60032 bytes available, and 64-token/two-stage bulk slabs (34816 bytes). This is analytical arithmetic, not new CUDA compilation evidence.

Proof covers the saved T128 tactics and their actual saved dispatches only. It establishes identical reachable executable AST when bulk_tokens=0; it does not claim byte-identical compiler output, runtime numerical validation, or any performance result. Nemo NVFP4 is active and requires a GPU guard.

Reproduce: `python3 old-cute-comparison-20261027/bulk-drain/decode-inactive-proof/prove.py` from the project root.
