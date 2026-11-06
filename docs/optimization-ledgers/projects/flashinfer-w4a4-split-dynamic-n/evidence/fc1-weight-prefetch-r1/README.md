# FC1 A/SFA startup prefetch, first-tile contract

Experimental source: `../../flashinfer-fc1-weight-prefetch-review`, independent base `24c48b9fd5d7c38fdcea213376602f97635c4ef9`, six unstaged files, full patch `e05fcdc72c6c8e74df4cec6f8b31f94a74955cd29e5eca14103ec83a15649cd0`. Production is not modified. `source.json` binds all 83 source files; scoped pre-commit receipt is `precommit.log`.

Prepare owns the new publication edge: after its all-thread ancestor wait, warp0 executes GPU release before the first dependent launch signal. FC1 primes A/SFA for its initial scheduled tile using `min(actual_operand_stages, ceil_div(K, tile_K))`; B/SFB remain after the dependency wait. The public FC1 direct flag defaults false. The library wrapper opts in only on Blackwell with PDL; explicit Rubin requests fail. Existing FC2 restrictions remain. The temporary MX benchmark opt-in is only part of this frozen causal experiment; the follow-up public API refactor will put all final admission in the library.

CLC initial coordinates use the installed SDK's default unswizzled M-major raster. Logical initial tile is `block_y * total_m_tiles + block_x / cta_group_size`; static fallback uses normalized block_x. Only that initial tile skips already-primed A/SFA acquisitions. A padded initial tile primes nothing, and any later cancelled live tile follows normal acquisition. Scheduler and queue ownership are unchanged.

`gate.json` and `chain-result.json`: 216 exact captured-chain replays across NVFP4, homogeneous MXFP8, MXFP4×MXFP8; H256/H5120, I2304; M128/N16, M128/N128, M256/N128, M512/N128; changing routes/data, zero-local routing, core PDL-off controls. Actual compiled CLC admission is asserted for M128 and false for the two-CTA geometries. This does not claim that a naturally scheduled padded initial block later cancelled live work. That state transition is covered by the source mapping/skip argument, not a measured counter.

`codegen-gate.json`: nine additional exact replays with compile-bound prepare/FC1 PTX and SASS. `codegen-review.json` verifies the expected stage count, exact expected-byte constants, no early B, and prepare release-before-first-trigger. Named resources cover NV short/long K: 0–6 extra registers, no stack/local allocation; shared storage and stage counts unchanged. Two-CTA leaders declare the two-CTA aggregate byte count; each CTA contributes half. M256 long-K uses 114688 total / 57344 per CTA bytes; M512 uses 94208 / 47104.

Generated compile artifacts and their hashes are retained alongside the exact commands and source receipts. No sanitizer or broad suite was run for this experiment. Full-chain fixed C–A–A–C performance is separate under `../fc1-weight-prefetch-r1-fixed` and will decide whether to advance to a combined native campaign.

The optional per-token r1 continuation failed before FC1 execution because the task-local codegen observer replaced `cute.compile` options and dropped the quantizer's existing `--enable-tvm-ffi`. The resulting export/missing-stream diagnostics are an observer error, not evidence of a production runtime or kernel failure. Failed r1 receipts are preserved; The corrected r2 gate appends options and passed36 exact replays with unchanged83source pins: H256/H5120, M128/N16 with CLC and M256/N128 twoCTA, changing routes/data and zero-local cases. See `per-token-r2-gate.json` and `per-token-r2-chain-result.json`.

Recheck saved evidence locally with `python3 scripts/fc1_weight_prefetch_experiment/audit_codegen.py` from the project root.


FC1-only fixed decision: not retained. Both-model C–A–A–C shows all six T4 gains, but repeatable larger-point losses reach approximately0.8% (V41 mixedT512) and0.6% (V3NV T128/512). Aggregate NV/MX8/mixed: V3 0.998208/1.003232/1.001221×; V41 1.001794/1.002745/0.997797×. The separate producer-only wait co-design uses this frozen source as its control.
