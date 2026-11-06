# PR7290 transfer audit

Source snapshots: PR7290 retained `98fd3566b5f945c100f48cddacf25deb2432cbc2`; its frozen Gather4 control `442d2aa53f68b4640c3ab5118a76f1599ff60d34`; W4A16 baseline `36740c36a32a6c6d1c7d8162823fe823912de741`. The neighboring project is read-only for this effort.

The transferable preparation changes are 128-thread persistent row copying, compile-time dimensions/top-k/grid, and aligned 256-bit payload copies. Native W4A16 already skips invalid rows, hoists each row's metadata/division before its payload loop, uses 64-bit offsets, and sizes its 256-thread grid from occupancy. Those are preserved behavior rather than new gains. The new helper explicitly keeps a 128-bit branch for 16-byte-aligned views.

W4A16 already has separate weight/activation pipelines, descriptor prefetch, cache policies, and selective PDL waiting. PR7290's separate-producer-pipeline follow-up was rejected. No wholesale pipeline transplant is justified. The early-PDL experiment here is an independent hypothesis documented in EARLY_PDL_AUDIT.md.

The frozen `442d2aa53` Gather4 control did not run a separate routed activation/SF preparation. Its FC1 core computes SF sources through routing at lines 1147–1162, gathers 4-byte SF groups with `cp.async` at lines 1260–1296, then issues payload Gather4 at lines 1301–1329. Its copy atom is defined at line 1062. The retained `98fd3566b` regular path adds payload permutation plus SF canonicalization. SFB uses TMA at N ≥ 128; decode N16/32 still uses `cp.async` from canonical SF. W4A16 has no activation SF, while BF16 uses 2 bytes/value versus NVFP4's packed 0.5 bytes/value. W4A16 Gather4 removes the entire BF16 permutation launch. These differences limit performance transfer; they are not a causal explanation of any measured W4A16 result.

PR7290's headline final decode gains compare complete AUTO implementations, often with original N128 versus candidate N16/32. They do not isolate regular TMA. This effort therefore compares each new candidate with both immutable W4A16 HEAD and final Gather4 sweeps under the original native benchmark protocol.

A second retained #7290 change makes already-keyed GEMM dimensions compile-time. W4A16 instead needs M/K added to its compilation key; the isolated static-M/K variant does that and omits those values only from the compiled runtime call. Routed N and token count remain dynamic.

The read-only source project is `/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n`. Its `scripts/prep_ldg256_experiment/README.md`, `scripts/regular_tma_pipeline_experiment/README.md`, and `scripts/static_shapes_experiment/README.md` preserve the individual experiments behind [PR #7290](https://github.com/flashinfer-ai/flashinfer/pull/7290). The fetched PR metadata is preserved in `PR7290_SNAPSHOT.json`.
