# Targeted final-composition repeat

Root requested one additional same-GPU CAAC repeat to qualify the largest prefill change and selected repeat-stable decode gaps. The final source remains patch `e0234935df4e703d30cfdd82c50d6366a66493782c2f24e5368936c7969ea91c` on `1496b557f9b606f3a0bb36bcebf5293d3e11555a`. No source, tactic cache, autotune selection or primary full-table value changed.

V4.1-Flash EP4 ran tokens 512 and 16384 on GPU5; Kimi K3 EP8 ran tokens 8,16,4096 on GPU6. Each source used its original native AUTO winners with `--no-autotune`,10 warmups,100 cold-L2 CUPTI CUDA-graph samples, fused finalize disabled, and the same public W4A16 benchmark observer. `create_inputs` resets its seed per token case, and the captured routing hashes match the primary run exactly.

`analyze.py` validates complete receipts, current source hashes/HEAD/patch identity, benchmark/observer hashes, unchanged cache hashes before/after, all20 routing identities and per-token cache snapshot hashes,100 cache hits against the exact primary selected tactics, and all2,000 raw sample medians. All checks pass.

| Model | Tokens | Primary | Repeat |
| --- | ---: | ---: | ---: |
| V4.1-Flash |512 |0.9786x |0.9793x |
| V4.1-Flash |16384 |0.9475x |0.9699x |
| Kimi K3 |8 |0.9702x |0.9808x |
| Kimi K3 |16 |0.9736x |0.9835x |
| Kimi K3 |4096 |1.0629x |1.0456x |

These repeats support a modest regression at the four slower points and a gain at K3 T4096. The magnitude varies, especially for large prefill; V4.1-Flash T16384 is approximately3.0% slower in the repeat. The primary39-cell aggregate remains essentially neutral and the full table in `../composed/` is unchanged. The composition is defensible as shared implementation and instruction simplification, with these modest regressions disclosed, rather than as a universal speedup.

`speedups.md` includes both speedups and all four absolute medians. `raw-median-speedups.csv` and `raw-samples.csv` preserve the complete targeted measurements. `summary.json` includes the per-arm distributions. Raw source receipts, launch evidence, logs, snapshots and results are in `evidence/`; the source benchmark outputs are never replaced by combined or selectively chosen values.
