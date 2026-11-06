# Utility review

Baseline: ed67c4857ce4e8d8cc047cf3808e2efa65e874b2.

- Share the FC2 scatter metadata calculation between bulk and direct epilogues. Both retain expanded-row mapping, per-token scale lookup, optional fused route weights, and the same metadata-scale rounding. The bulk path statically excludes fused finalize, so its helper call passes no route-weight tensor. The two device paths still retain their distinct transfer/transpose and accumulator-release sequences.
- Compute activation scale-column geometry once in a host helper reused by workspace allocation and preparation. Generated preparation kernel is AST-identical; 51 valid geometries match the old formula, and four invalid geometries are rejected.
- Audited the combine, standalone quantizer, W4A16 layout adjustment, FC1 adapter and trace/reference additions. Retained their code: their distinct arithmetic, row masking, activation contracts and architecture boundaries remain necessary. Avoided unrelated refactors and preserved original comments.
- The epilogue helper is a source deduplication, not a performance claim. Require source-paired exact output checks plus emitted-code/resource comparison before retention. No new upstream tests are needed.

Static utility receipts: utilities-static.json. GPU validation pending final freeze.
