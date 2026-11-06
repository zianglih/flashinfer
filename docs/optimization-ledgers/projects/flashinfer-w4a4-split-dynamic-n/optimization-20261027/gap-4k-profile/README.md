# N3U W4A4 4K profile diagnosis

Read-only diagnosis after retained commit `1e69d0a39`. Profiles use the frozen measured sources, native winners and public functional API from the retained campaign; current swap-AB and legacy non-swap both use unfused finalize and include input quantization. No new tuning or timing was launched for this analysis.

The 12-file archive includes both original Nsight Systems reports, SQLite exports, logs, selection receipts and timeline summary. Archive SHA256: `373849c4bc42b6b8a1f80f97539e3540395a23cab17cde9d098f167b5fc2a213`. `analyze.py` checks profile completion, exact native-cache hashes, benchmark/config hashes and all 20 graph repetitions against the SQLite source. `validated-profile.json` records the file hashes and resources.

| Stage | Legacy duration us | Swap-AB duration us | Legacy critical extension us | Swap-AB critical extension us |
|---|---:|---:|---:|---:|
| Input quantization | 5.984 | 6.224 | 5.984 | 6.224 |
| Routing | 19.232 | 19.376 | 18.256 | 18.272 |
| Prepare | — | 7.968 | — | 7.633 |
| FC1 | 88.592 | 115.841 | 88.256 | 114.449 |
| FC2 | 83.296 | 103.536 | 81.216 | 73.185 |
| Combine | 93.857 | 17.632 | 13.840 | 13.264 |
| Full graph | 207.681 | 233.441 | | |

Kernel durations include time waiting on PDL dependencies. In particular, legacy combine begins much earlier and waits longer: its 93.857 us span does not mean 93.857 us of combine work. Critical extension measures additional end time beyond the prior kernels, rather than adding overlapping spans. Per-stage medians need not sum exactly to the median full graph.

## Source-traced selection and resource differences

- Both winners use route tile 256. Legacy FC1/FC2 use `(256,256)` and two CTAs. Swap-AB FC1 uses `(128,256)` and one CTA; FC2 uses `(256,256)` and two CTAs. Swap-AB K steps are `(4,4)` with shared CLC disabled.
- Current `moe_swap_ab_tuner.py:34` already admits one-CTA M128 and two-CTA M256/M512 alternatives, independent FC1/FC2 tiles, K4/K8 and shared CLC. No new tactic axis is needed to compare those choices.
- The swap-AB FC1 ring is four 55,296-byte operand stages at K256, with eight K stages per 2048-channel reduction. Its 221,952-byte launch matches the storage planner. FC2 uses five 38,912-byte stages plus bulk-output scratch, matching its 229,632-byte launch. Both use 288-thread CTAs. Legacy FC1/FC2 use 384/256 threads and 232,448/226,304 bytes. Shared-memory occupancy remains one CTA per SM; the larger current register counts alone do not establish an occupancy regression.
- All 64 local experts have exactly one live N256 route tile: actual counts are 117–252 (median180.5), totaling11,180 tokens in16,384 routed slots. The current reuse-aware weight hint therefore selects evict-first for every expert at this size; the retained large-prefill weight-reuse improvement is intentionally inactive here.
- Current FC1 has40 channel tiles/expert versus20 feature tiles/expert in the legacy M256/N256 interpretation. Two-CTA MMA and the new orientation have different work ownership, so this difference is a scheduling/issue-overhead hypothesis, not proof of twice the work.

## Conclusion and next decision

FC1 contributes the largest additional critical extension (+26.193 us); preparation adds7.633 us. FC2 has a longer total span but overlaps more aggressively, recovering8.031 us of critical extension; combine saves0.576 us. Thus this profile does not support another combine rewrite.

The first useful decision is whether the existing two-CTA FC1 choices outperform the selected one-CTA choice on the actual routing tensor. The source's autotune helper replaces routing with balanced approximate-max-load inputs (`tuner.py:570`, `_inputs_helper.py:175`), whereas the measured distribution is uneven. This is a plausible misranking cause, not a demonstrated explanation of this profile pair. The parallel actual-routing experiment owns that investigation; no duplicate experiment is launched here.

If actual-routing tuning retains the same winner, FC1 issue/epilogue activity is the next profiling target. A new transpose or register-lifetime rewrite is not justified by this timeline alone: the prior large-N transpose, ownership compaction and metadata-preload trials are already recorded/rejected. Preserve the general pipeline and existing tactic set until the selection question is resolved.
