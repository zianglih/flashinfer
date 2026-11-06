# Retained integration and performance refresh complete

Fork PR9 is merged into upstream PR7290's branch as
`a620ce7790b32f7f0ae524a811417d2c6cee1152`; upstream PR7290 remains open.
The merged tree equals retained `8bc69ee4`, including the selected W4 helper
revert. No new optimization was introduced during this refresh.

- Seven existing exact smoke calls passed; 21 captured kernels report zero local memory.
- All 468 supported model/topology/dtype/token cases were freshly measured in two
  candidate passes, with 93,600 strict CUPTI samples. Original external baselines
  and the historical GLM5 helper comparison were preserved.
- All 936 historical comparison slots retain their original denominator fields.
  The two displayed heatmaps contain 660 measured comparisons and preserve all
  76 negative results. Tokens 1/2 remain in raw outputs, excluded from plots.
- Clock observations retain 98 exceptions and one missing quartile out of 3,744;
  maximum two-pass spread is 8.620823%. These are historical cross-instance
  comparisons, not new causal control measurements.
- Source, native-cache, raw-data, native-table, numerical, visual and archive
  audits passed. All eight GPUs and the benchmark registry are idle.

PR7290 body and four existing table comments were updated and read back exactly:
6519314397,6519315021,6519315606,6519316131. The body and raw tables bind a620;
the benchmark's unchanged printer generated 15 tables using 468 fresh CuTe DSL
records and 390 original TRTLLM records, with 62 original native logs retained.

Immutable assets: `8cfecaf8964ffe61dfa6864c9b5250dfe298dac2/a620ce77` in the
fork's `codex/moe-gather-pipeline-assets` branch. The new archive contains 1,617
members and 79,003,504 bytes, SHA256
`79e271fa11751dda023251a287bdce54dd4a7a77acf3ac613a7c2bb759f7c8cf`.
Seven published resources, including both PNGs and the full archive, passed HTTP
byte/hash verification. All earlier asset prefixes are unchanged.

Receipts:

- [Merge](merge-receipt.json)
- [Performance closure](../integration/pr7290-refresh-20261030/performance-closure.json)
- [Raw data peer](../audits/pr7290-a620-data-peer.json)
- [Publication peer](../audits/pr7290-a620-publication-peer.json)
- [Archive peer](../audits/pr7290-a620-xz-peer.json)
- [Assets](../publication-pr7290-a620/assets-published.json)
- [HTTP verification](../publication-pr7290-a620/http-verification.json)
- [PR/comment readback](../publication-pr7290-a620/github-update/receipt.json)

Optimization remains paused. No sanitizer or additional full test-suite run was
performed for this integration; the current seven smoke calls and historical
validation are distinguished in the PR body.
