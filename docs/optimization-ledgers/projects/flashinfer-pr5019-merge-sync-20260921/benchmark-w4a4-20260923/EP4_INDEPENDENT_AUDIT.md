# EP4 independent evidence audit

Reviewed both completed `evidence/ep4-sweep{1,2}` directories on 2026-09-23. EP8 was still running; this does not declare the campaign complete.

Direct reconstruction from all eight rank JSONL files, without calling the campaign renderer, confirmed:

- 7,800 rank-MAX samples reconstructed exactly from 31,200 individual rank spans; 100 samples per arm/token/sweep and 200 pooled samples per final latency cell.
- All 13 rows' three pooled medians, both speedup ratios, and both per-sweep selected Mega tactic dictionaries exactly match `ep4-paired-preview.json`.
- Input and route hashes agree across the three arms; inputs, routes, and canonical weights agree between sweeps. Source/helper hashes, node, boot, revision, and image agree between sweeps; current helper hashes match the measured copies.
- All 312 untimed logical rank/output checks are finite and repeat-bit equal. Both runs disable IKR, all ranks agree on each selected Mega tactic, and the two sweeps contain 208 per-rank Mega tactic records.
- Compressed archive SHA-256 values match their transfer/validation receipts. Every member of each nine-file EP4 archive matches the extracted evidence bytes.

Decode 4–512 geometric speedup of Mega W4A16 is **1.1259088664126478× over Split W4A16** and **1.0153242187613312× over Mega W4A4**. Mega W4A4 / Mega W4A16 ratios at prefill 4096/8192/16384 are **0.5706× / 0.4009× / 0.3587×**; the tables correctly preserve W4A4's prefill advantage.

## Native tuning boundary

W4A4 `shim/autotune.py:294-317` measures ten synchronized eager launches with `time.perf_counter`, then selects by maximum rank median. `autotune_nvfp4_mega_moe` passes `sync=True` at lines 362-374. W4A16 `cute_dsl/megamoe/bf16_nvfp4/autotune.py:79-89` uses hot CUDA-graph replays and GPU events, then selects by maximum rank median at lines 204-214. Neither native candidate selector flushes L2 per sample. Final reported latencies use the same cold-L2 CUPTI graph method for all arms. This measures each delivered native AUTO path, not a common-tuner best-case comparison.

## Draft fill review

`fill_review_draft.py` remains unexecuted until all four sweeps validate. It now includes 52 per-sweep rows (100-sample medians), distinct from final 200-sample pooled medians, plus verified local archive links/hashes and the complete results artifact. Each archive member is checked against validated extracted evidence. The filler also verifies the measured patch/base identity and checks that rendered Markdown exactly matches the validated JSON before embedding it. Historical nonperformance evidence and runtime-alpha evidence remain outside this replacement scope.

No benchmark source, GPU state, Git state, or GitHub resource was changed by this audit. Only the authorized local draft-fill helper and this note were edited.
