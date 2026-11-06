# Independent TMA warp specialization

Status: retained and pushed as `99f4d0c277746fb706d10a4bb303c98c5f31e0a9` after the final r2 gate and 80-cell matched pilot. The full refresh completed all 16 current-head passes on eight GPUs: 520 CuTe medians / 52,000 CUPTI samples. Per the user's follow-up, remaining baseline-only runs were stopped and the full tables consistently reuse saved `retained-rerun` baseline measurements. Completed incidental fresh baseline data remain diagnostic only. The full 44×9 end-to-end table and red/white/green heatmap are published in PR7290; see `full-rerun/publication-receipt.json`. This comparison uses saved baselines, not fresh matched C-A-A-C controls. See `retained-commit.json`, `performance/RESULTS.md`, `performance/DIAGNOSTICS.md`, and `performance/drift-repeat/`. The local review checkout was bumped clean to retained head and removed; all retained source is in the canonical checkout. The 1080-file runtime/codegen evidence archive and all 42 manifest pins were independently verified.

- Fixed 256 threads: weights+weight scales warp0, activations+activation scales warp1, MMA warp2, scheduler warp3, epilogue warps4–7.
- Every route tile owns `ceil(N/128)*128` physical SF rows. Payload remains compact. Prepare, fused quantization epilogue and existing per-token quantizer publish this private layout directly; public weight/layout APIs remain unchanged.
- One shared operand full/empty ring. Two elected leader-CTA arrivals announce disjoint role byte counts; both CTAs contribute TMA completions. MMA waits once and releases once. This removes cp.async SFB and its proxy/cluster join.
- Weight warp follows its normal producer loop before the payload dependency wait; ring ownership naturally bounds prefetch. The activation warp publishes startup dependencies after its ancestor wait. Weight/scheduler roles wait before completing or republishing ancestors.
- Weight, scheduler, and MMA roles defer their dependency wait to exit; MMA only consumes payload after the activation warp's wait and the shared operand-full completion.
- Keep S2T scale copies on MMA initially because the single TMEM scale slot is owned by ordered MMA issuance. Moving them requires a distinct overwrite protocol and is not part of this initial rewrite.
- Preserve TMEM allocation/retrieval and final CTA joins. Do not add register redistribution until the fixed-role version passes and generated-code ownership is understood.

Validation: exact/reference and public-graph checks across all formats, N16/32/64/128/256, static/CLC, PDL off/on, and one/two CTA. Sanitizers remain deferred per user. Benchmark using matched CUPTI graph timing and current public benchmark, with persistent native compilation caches. Retain only after representative and broad matched performance gates.

The prior actual-routing and seeded-uniform tuning policies were rejected. The graph/eager diagnostic did not establish a general measurement-policy gain. Their evidence remains in adjacent directories; none is part of this candidate.

Final candidate removes iteration/zeroing over unused physical SF padding. Both prepare and optional routed-pitch quantization iterate logical rows, retaining defined zero SF for invalid logical rows. The NaN-padding gate demonstrates unused SF rows do not affect live outputs. The final source-bound gate passed before launching the matched performance pilot.

Snapshot boundary: r1 exact/codegen evidence uses kernel `85f12b60`; it still had the original MMA startup wait plus the newly added exit wait because the first textual replacement missed formatted lines. Final r2 explicitly exempts MMA from startup wait (only activation and epilogue wait there), removes two unused internal arguments, renames the shared operand ring, and skips unused physical-padding iterations. R2 has its own source-bound runtime gate and is the only candidate intended for timing.

Static checks: Ruff lint and Python compilation pass. A matched five-file mypy invocation reports the same six existing `fused_moe.py` option-dictionary typing errors on retained1e69 and the candidate; see `static/mypy-comparison.json`. No new mypy diagnostics were introduced.

Read-only SF/API review found no blocking issue: public MoE signatures, tactics, weight-layout helpers and default quantizer behavior are unchanged; W4A16 retains its SF=None preparation path. See `SF_API_AUDIT_R2.md`.

Commit checks: all applicable pre-commit hooks now pass, including mypy and Ruff. The two local option-dictionary annotations and required formatting are behavior-equivalent to the gated r2 wrapper; see `commit-bytecode-equivalence.json` and its reproducible helper. The four changed kernel/helper files remain byte-identical to the runtime/performance gate.
