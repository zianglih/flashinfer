# Published refresh

PR #7290 body and the same four benchmark comments were updated on 2026-11-03 and read back byte-for-byte. The source head remains `2b4732791a3ce48bc3ae6c030a283fab73854e0e`; the canonical source checkout is clean. No implementation change was needed for this refresh.

- PR: https://github.com/flashinfer-ai/flashinfer/pull/7290
- Comments: 6519314397, 6519315021, 6519315606, 6519316131. No new comments were created.
- Immutable asset commit: `e12ed6c3e7c619f06c427bc69e05ff7c3fedd955`, new `2b473279` prefix on the fork's `codex/moe-gather-pipeline-assets` branch. Previous prefixes are unchanged.
- Two end-to-end EP/TP heatmaps and 15 native benchmark tables cover 468 fresh candidate cases. Historical external denominators are reused unchanged.
- Full matched check: 187,200 CUPTI samples, -0.0878% overall and -0.3550% prefill versus retained a620. The separate 4,800-sample diagnostic averages +0.4179%; it does not replace the original measurements.
- V41F EP4 at 16,384 tokens remains -2.64% MXFP4x8 / -2.14% MXFP8 in the diagnostic, with 6.53% / 4.48% control-repeat spreads. These are explicit unresolved measurements, not a blanket non-regression pass.
- Five evidence archives, all below 100 MB, are hash-verified. HTTP readback checked 183,796,147 bytes across 12 published files. Credential screen found no matches in 4,474 selected files.
- The GitHub connector could read but returned 403 for comment edits. The authenticated `zianglih` CLI completed the authorized edits; connector readback verified the final body and all four comments.

Final receipts: `publication/publication-readback.json`, `publication/http-verification.json`, `publication/assets-published.json`, `publication/comments-published.json`, and `publication/pr-body-published.json`. Full results and limitations are in `RESULTS.md` and `audit/isolated-campaign-audit.md`. Persistent C3 compilation caches are retained and the GPUs are idle.
