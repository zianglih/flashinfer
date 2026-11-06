# Retain W4 tail-group skipping after independent data audit

The complete affected matrix supports retaining this change: all24 cells at tokens4–512 improve, with gains from+0.44% to+3.75% and repeat spreads below0.5%. The33 retention cells average+1.47% (decode+1.70%, middle+2.11%). Six of nine prefill cells regress, worst−0.75%, within the user's accepted slight-prefill-regression boundary. The noisy+0.46% prefill aggregate is **not a dependable benefit**; N3U prefill averages−0.48%. All negatives, clock anomalies and15,600 raw CUPTI samples remain in the evidence. Tokens1/2 are measured but excluded from retention.

The implementation removes wholly unused final-stage scale loads, FP4 decode and TMEM stores. It preserves every pipeline arrival/release/state advance; partially live groups keep padded decode. The runtime predicate exists only when the compile-time geometry leaves an entire transform group unused. No model branch, tactic axis, register quota or public interface is added. The private handoff conveys consumed K extent and transform-group coordinate.

Qualification passed12 split exact calls across both layouts,1/2CTA, static/CLC, PDL off/on, short/aligned/all-live/tail K shapes. Registers and LOCAL0 remain unchanged in all78 measured stage configurations. Aligned split paths and an all-live partial path produce identical native images. Actual CuTe ownership probes and independent state/AST review establish the skipped region and phase preservation.

MegaMoE continues passing its **padded consumed-K extent** because its MMA loop consumes complete stages. Its padded arithmetic contract is untouched. Four existing single-rank exact calls cover aligned and partial logical K; both native PTX/cubin/SASS pairs are byte-identical, including a multistage case. No shared Mega arithmetic optimization or distributed timing claim is introduced.

The39 affected full-table cells are the13 tokens for V41F TP4, K3 TP8 and N3U TP8 W4A16 FC2. All FC1 paths,65 aligned W4 cells and364 swap cells are unchanged and reusable under the documented source/native-equivalence boundary. The two disjoint campaigns preserve the original12 rows exactly and add27 rows.

Source and patch are frozen in `retention-source-freeze.json`, `source.json` and `candidate.patch`, based on retained `02de7785c10847b3528340840bed40bd405d85b4`. The parent may apply and commit only after the combined independent audit passes. This review checkout remains unstaged; no commit or push was performed here.
