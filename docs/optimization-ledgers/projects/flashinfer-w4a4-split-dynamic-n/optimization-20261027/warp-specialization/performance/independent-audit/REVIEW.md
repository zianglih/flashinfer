# Independent pilot review

The final 80-cell pilot passes the independent audit. `independent_audit.py` reads the raw phase samples and cache records directly; it does not import the campaign analyzer. The result is `final.json`.

- Verified 60 completed phases, 40,000 CUPTI samples, and 32,000 frozen samples used in ratios. AUTO public samples are diagnostics only.
- Verified 342 source hashes per arm, both patch identities, all 78 pinned inputs, the final runtime gate, launch identity, archive file hashes, immutable saved winner identities, native admitted tactic geometry/count/hash, and matched routing.
- Recomputed every ratio as `100 * (exp(mean(log(C0),log(C3)) - mean(log(A1),log(A2))) - 1)`. All 80 assembled cells match. All cells remain in the aggregates.
- Overall +0.759%, decode T4/T64 +1.189%, prefill T512/T4096/T16384 +0.473%. These compare the frozen candidate with retained swap-AB `1e69d0a39` using each arm's selected native winner. They are not comparisons against TRTLLM or non-swap implementations.

The two material, stable small decode negatives are V3 per-token T4 −1.201% and K3 per-token T4 −1.444%. Their within-arm movement is at most 0.20%, and both candidate passes are slower than both controls. Both selected a different winner, so these do not by themselves isolate a kernel-source regression. N3U per-token T16384 is also consistently −0.499% with at most 0.22% within-arm movement; it remains visible rather than being rounded away.

Eleven T16384 cells exceed 1% absolute control drift or candidate spread. The largest apparent negatives—V41F MXFP4x8 −3.229%, K3 MXFP8 −2.165%, and K3 MXFP4x8 −1.387%—are inconclusive under their larger endpoint shifts. All eleven uncertainty labels, three stable-negative labels, and four format aggregates agree with `assembled/retention-summary.json`. The 1% rule is a transparent screening threshold, not a statistical confidence interval.

The strongest stable same-winner results are N3U T4: W4A4 +4.463%, MXFP8 +4.248%, MXFP4x8 +9.899%. N3U W4A4 T4096 +7.318% also has a stable bracket, but changed its selected winner. Prior tuning diagnostics already showed retained source can select a roughly 218 µs winner; therefore this cell should not be claimed as a pure source-level gain.

All twelve candidate native cache files contain the expected full 13-token public keys: 208/208 same-format keys verified against the established full benchmark. Native AUTO admitted 22 profile buckets through 16384, despite measuring five public rows in the pilot. W4A4 and per-token caches have identical `_metadata`, disjoint tactic keys, and differing content-derived `_generation` values; a merged cache must recompute that digest. Reuse is selection-only and must preserve source/environment provenance. The pilot contains no TRTLLM or W4A16 execution or new selections for those arms.

No GPU work or implementation changes were made by this audit. Bounded repeats and winner crosschecks, if retained, remain separate evidence and must not overwrite the original pilot samples.
