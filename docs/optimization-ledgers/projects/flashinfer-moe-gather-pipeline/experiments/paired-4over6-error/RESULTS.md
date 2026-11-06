# Paired 4over6 error recurrence: rejected

Candidate `5f232629` is rejected after the complete 42-cell same-source CAAC screen against retained `c1ac8ce7`. Exactness and native instruction/resource improvements passed, but whole-chain performance regressed: **CuTe PER-TOKEN −0.3062% across 24 cells; TRTLLM PER-TOKEN −0.1183% across 18 cells**. No repeat, expansion, retuning, recipe exception or rescue branch. Canonical source and published PR evidence are unchanged.

The decisive N3U TP CuTe losses are −2.8275% at T4096 and −3.6937% at T16384, with both-arm repeat spreads below 0.1% and normal clocks. Intermediate quantizer exposed intervals increase 14.768/63.961µs. FC2 starts earlier, but its exposed tail is nearly unchanged; native resource redistribution and PDL interference remain hypotheses, not isolated causes. The K640 cached images match the lower-register pilot bytes, so its instruction/resource success does not override runtime losses. Total grid size is unchanged; its average CTAs/SM is not a residency cap or trace.

All 16,800 samples, 168 phase medians, 23 negative cells, 22 clock-exception quartiles and three missing quartiles remain intact. K3's two complete CuTe-only jobs and the six remaining complete dual-backend jobs are kept as separate source/cache-qualified acquisitions, without phase splicing. See [full performance verdict and raw tables](performance/RESULTS.md), [independent raw replay](../../audits/paired-4over6-error-full-data-peer.json), [N3U cached-image audit](n3u-prefill-native-cache/RESULTS.md), and [K3 cached-image audit](k3-prefill-native-cache/RESULTS.md).

The one-file +15/−18 source and exact patch are preserved in this experiment. The rejected review worktree/branch is retired; [retirement receipt](retirement/receipt.json) binds ownership, saved bytes and clean canonical source. All helpers, raw/native evidence and immutable remote validation snapshots/caches remain available. A separately authorized no-successor N3U quantizer diagnostic may use those remote snapshots; it does not replace the primary 42 cells or reopen retention.

## Passed exact/native gate

| Existing direct case | Non-NOP instructions | Registers | Driver local bytes | Driver capacity, CTAs/SM |
|---|---:|---:|---:|---:|
| BF16 K640 MSE256/error-fast, precise base, grouped256 |743→695|61→48|0→0|16→20|
| FP16 K1536 MAE448/error-fast, fast base |407→375|64→55|0→0|10→12|
| FP16 K80 strict-error/fold control |1430→1430|64→64|16→16|32→32|

All six calls passed output/scale-byte comparison and four changing-live-row graph replays. Both affected PTX images contain sixteen linked RN packed additions, one per original input position; MSE has sixteen packed RN subtract/multiply operations, MAE has sixteen packed RN subtract operations and retains 32 scalar absolute values. No packed FTZ or FMA appears in the recurrence. The strict control's PTX, cubin and SASS are byte-identical. MSE also redistributes some integer/address instructions; native schedule identity is not claimed.

The authorized error-fast CuTe subset of the existing `test_nvfp4_quantize_te_reference` passes26 regular pairwise tests: 6 non-per-token and 20 per-token. Actual selected IDs and parameter coverage are in `reference-tests/evidence/{non-per-token,per-token}/selected.json`, with unmodified test/oracle outputs and JUnit. Both FP16/BF16 and both base math settings appear. This is not full Cartesian recipe/shape coverage; no new test or oracle was added.

Full source/cache pre/post checks passed. Quantizer families used separate real per-arm cached_ops directories, while four unchanged release C++ modules were shared by verified links. The replacement-node cohort is explicit; the unavailable prior launch was preserved and ran no remote command. GPUs 2/3 are idle/released.

Proofs: `source-proof.json`, `native-summary.json`, `qualification-summary.json`; independent peer `../../audits/paired-4over6-error-native-peer.json`. The public quantizer also serves the timed TRTLLM PER-TOKEN input stage, so retained performance publication would require refreshing those affected denominator rows rather than relabeling historical measurements.
