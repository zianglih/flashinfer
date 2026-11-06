# Retained SF epilogue simplification

Retained as `d7e5ea1c67e6d5f011377e340811ffc377a41763` on `2d60c885`. The committed patch exactly matches the measured candidate; kernel SHA256 is `924be38531be1e8ad18b95acc2827d5a496255de0a24b2048d6d01ca58c137d0` and patch SHA256 is `ee5b3006df450774956259731791adf859b8a7746ce25708a535b66bf45fc44a`.

- The SF-row formula and shared quantization-parameter extraction simplify repeated work. Original half-loop predicates, arithmetic, synchronization and scale ownership remain unchanged; no new policy or tactic.
- All 96 byte-exact replays pass. The 48 GEMM/10 combine pairs include eight per-token FC1 encoded-identical streams and 24 unchanged FC2 streams. Quantized ReLU2 removes 201–365 static non-NOP sites with no extra branches or local/stack/uniform spill growth.
- The 72-cell CAAC screen contains 28,800 CUPTI samples: scaled geometric change +0.133%, decode −0.056%, prefill +0.323%. Retention is for instruction simplicity with near-neutral aggregate timing. The stable V3 EP W4A4 T4 cost of −0.458% remains explicit.
- N3U EP MXFP4x8 T16384 remains −4.604% in the original screen. Its independently audited same-GPU/source/winner/routing confirmation is +2.364%, but last-50 diagnostics are −4.756% and pass spreads are large. Preserve both results; do not infer a stable large gain or loss, or substitute the repeat for the original row.
- No sanitizer, external baseline rerun, or autotuning. These are bounded qualification and diagnostic results, not the forthcoming full-table refresh.

[RETENTION.json](RETENTION.json) binds every source, gate, independent audit, performance and confirmation receipt. [Integration receipt](integration-receipt.json) verifies every tracked review file and gitlink against the retained commit. [Full results](RESULTS.md) preserve all original rows and limitations. Cleanup is separately recorded after dependency and process checks.
