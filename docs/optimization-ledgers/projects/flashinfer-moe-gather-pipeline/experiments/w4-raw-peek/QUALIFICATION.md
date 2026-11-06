# W4 raw readiness TEST qualification

Retained base `2b8eb9d8`; candidate kernel `0871b67f` was qualified unstaged in
`flashinfer-w4-raw-peek-review`. The rejected review is now retired; its exact
source and patch are preserved in `retirement/`. The diff is 8 added / 4 removed lines, solely
because two existing raw `consumer_try_wait(state)` calls become the existing
SDK `sync_object_full.test_wait(state.index, state.phase)` calls. The whole
module returns to the retained AST when those two calls are reversed. Scoped
pre-commit and the independent source/API/lifetime review pass.

The split gate passed 12 existing zero-tolerance calls across six shapes and
18 actual native pairs. Coverage includes full/partial K, a longer K loop,
old/new gated weight layouts, SwiGLU/SiTU/ReLU2, one/two CTA, actual static/CLC,
and PDL on/off. Mega separately passed four existing single-rank calls and two
native pairs. This does not establish distributed correctness; fresh GLM5
was held and canceled after the split performance rejection; no distributed
performance run occurred.

All loaded resources match: split FC1 96 registers, FC2 128; Mega 96, with zero
local storage. Six split finalizer images are byte-identical. In all 20 pairs,
replacing `mbarrier.test_wait` with `mbarrier.try_wait` in candidate PTX recovers
control PTX byte-for-byte. Every blocking fallback and decoded-slot TRY is
therefore unchanged. Successful TEST uses `.parity.acquire.cta.shared::cta`.
Short K folds away the unused next-stage query; nothing adds a new poll.

Native multi-stage split kernels add three non-NOP instructions (two VOTEU.ANY
and one UPLOP3), with a BRA-to-BRA.U change. There is also local scheduling churn;
one FC2 has a MOV-to-HFMA2 substitution. Single-stage split and both Mega pairs
retain their non-NOP totals. This is a query primitive experiment, not an
instruction-count reduction or a performance claim.

The long-K split FC1 capture illustrates the intended dependency distinction.
The control raw TRY at `0x2ea0` shares write barrier 5 with preceding raw LDS and
first waits that group at an F2FP conversion after 40 intervening instructions.
Candidate TEST at `0x2eb0` first waits its group at VOTEU after 78 instructions;
the earlier conversion proceeds under a separate dependency. Actual raw LDS
work remains, and TEST may return false more often. Static placement alone
cannot predict latency or fallback frequency.

Evidence is frozen under `qualification/evidence/1793386426136276000/`, with
`qualification-summary.json` and `query-native-proof.json`. Mega's successful
retry is `mega-qualification-r1/`; its initial preflight path failure happened
before GPU work and remains preserved. The combined independent review is
`audits/w4-raw-test-native-peer.json` (16 calls, 20 pairs). The initial local
native-query parser incorrectly filtered by predicate polarity; its note is
preserved, and the final parser uses unchanged NANOSLEEP/fallback structure
plus exact PTX and native query counts.

The full 104-cell split CAAC plan uses frozen routes/choices, including ten
recorded defaults, strict CUPTI 100 samples, 10 warmups, cold L2 and four phases.
It retains all clocks, variation and negative rows. Tokens 1/2 are recorded but
excluded from retention statistics. No tactic, stage, compiler option, clock,
or source change is permitted during the run.

Final status: the complete 104-cell CAAC screen was rejected after independent
raw replay. See `RESULTS.md`, `decision.json`, and `retirement/receipt.json`.
The main checkout remains clean at `2b8eb9d8`.
