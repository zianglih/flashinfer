# First-hint reuse assessment

The frozen-tactic screen is complete: 32 main cells covering four models and four block-scaled formats, plus a reversed N3U W4A4 4K repeat. All 52 phases and 13,200 CUPTI samples passed the source, config, observer, saved-tactic, routing, and raw-median checks. The final archive contains 244 files and has SHA256 `400d73b5ae224db4bb171d7c075de542a97ed66a1ebea91c674408c5e74b890a`.

The candidate demonstrably skips two neighbor-expert loads and their address/select work on the first producer-loop tile. The paired gate passed 96 exact replays; PDL-off SASS is unchanged, PDL-on register counts are unchanged or lower, and there are no spills. Static instruction count grows because the later-tile path remains present; dynamic first-tile execution is the relevant saving.

Performance does not establish a broad win:

- The geometric mean over all 32 cells is **−0.129%**. The 16 decode cells average **+0.070%** geometrically.
- V3 and N3U MXFP8/MXFP4x8 at 16K have arm drift of 2.5–10.4%, larger than the measured effects. Their speedups range from −3.280% to +2.113%; these four cells are inconclusive. They remain in the full result table and aggregate.
- The remaining 28 cells range from −0.225% to +0.266%. Their geometric mean is +0.050%, a descriptive subset only, not a replacement retention score.
- The reversed N3U W4A4 4K repeat is −0.228% with candidate drift +0.608%; the original screen was −0.173%. Neither demonstrates a stable improvement.
- GPU snapshots at phase boundaries show normal clocks and temperatures but do not establish the cause of within-run or between-run drift. No clocks were changed.

This is a valid instruction-redundancy reduction, but broad performance neutrality has not been established for the four unstable MX prefill cells. The parent rejected the follow-up: avoiding two startup loads does not justify the additional per-tile control/state and 11 added / 3 removed lines for this marginal result. The simpler pushed implementation remains retained. No additional experiment or policy axis was added.

The owned local and remote candidate checkouts are removed after verifying their independent Git metadata, base commit, sole source delta, and exact frozen patch/source hashes. The measured clean `1e69d0a39` control, canonical source, persistent native/CuTe caches, scripts, patch, complete results, and generated code evidence remain intact. Closure receipts are `local-closure-receipt.json` and `remote-closure-receipt.json`.

See `BROAD_RESULTS.md` for every raw median and drift value, `validated-broad.json` for full precision and input hashes, and `broad-evidence/` for original measurements and receipts. All timings are fresh; only native winner selections were reused.
