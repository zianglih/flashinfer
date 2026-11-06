# Unified MX integration probe

Clean source `eb141478505103f4bc65d10fb655f3deb3cd71dc`; GPU 1 only on `fi-moe-rebase-audit-1026` (C2 B300). **24/24 exact comparisons pass**, with empty stderr and unchanged source pins before/after.

The local-only probe exercises public `MoELayer` with `CuteDslConfig.prepare_weights`, prepared activation packs, and unfused finalize. MXFP4×MXFP8 activation preparation uses the shared public `TrtllmFp4Config.prepare_activations` contract; homogeneous MXFP8 uses `CuteDslConfig.prepare_activations`. The comparison is direct `CuteDslMoEWrapper` with the same prepared tensors and independently specified activation kwargs.

Coverage: both MX pairs × nondefault SwiGLU / SiTU(4,25) × PDL off/on × mixed-local / changed / empty-local routes. Geometry is T32/H512/I256, 8 global / 4 local experts, offset4, top-k2. The ordinary public selection path returns default tactic `-1` under `autotune(False)`; the helper does not override dispatch or perform an AUTO search. Outputs are finite and exactly equal to the direct wrapper (`torch.equal`); PDL on/off output hashes also match, and empty-local results are zero.

The source receipt binds the parent's complete source map plus unified API/layer/runner/prepare modules. Raw code, source, launch command, runtime imports, all output hashes and logs are under `raw/`; `fetch.json` and `summary.json` bind their bytes. The compiler runs with the parent's source-private workspace and a unique configured CuTe cache directory; no global environment is changed.

This verifies unified runner/pack integration. Both paths share production kernels, so it is not an independent numerical kernel oracle, performance measurement, graph replay test, or sanitizer result. No repository files or upstream tests were changed.
