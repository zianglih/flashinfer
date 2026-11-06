# Early MMA readiness: bounded qualification

The frozen candidate `e9088366` on retained `49c91adf` passes the eight selected control/candidate pairs (16 exact calls). This is correctness and native-code qualification, not performance or retention evidence. The source remains unstaged and isolated; no production tactic, layout, stage policy, PDL contract, or W4 path changes.

The original strict campaign stopped before wide per-token FC2 launch because its registers grew from 128 to 130 and its driver maximum thread count changed from 512 to 384. That failure, partial FC1 capture, and raw logs remain intact under `qualification/evidence/1793376514158643000`. Root explicitly approved a separate, exact-signature exception. The resumed pair verifies 256 actual launch threads, unchanged 222,208-byte dynamic shared storage, LOCAL0, and one resident CTA per SM from the CUDA occupancy API in both arms. Static shared bytes and binary version also match. No other resource increase is accepted. The resumed control and already captured candidate FC1 are byte-identical to their original binaries.

The resumed four pairs, including long-K and both private `num_stages=1` cases, passed under `qualification-r1/evidence/1793376967654441000`. Full 13,245-file inventories and helper/source guards pass. Across both campaigns there are 18 executed calls: 17 complete exact passes (one duplicate control) plus the preserved partial failed candidate. The selected qualification set contains eight disjoint pairs and 24 native kernel pairs. All 48 selected images have zero driver local memory and no SASS LDL/STL sites. All eight finalizer pairs are byte-identical.

| Case | Role | CTA group / channel tiles | Operand stages | Registers | Non-NOP delta | New PTX TEST sites |
|---|---|---:|---:|---:|---:|---:|
| mxfp8-11-Swiglu | FC1 | 2 / 1 | 6 | 168 → 168 | +12 | 3 |
| mxfp8-11-Swiglu | FC2 | 2 / 1 | 5 | 122 → 122 | +5 | 1 |
| w4a4-13-Relu2 | FC1 | 1 / 1 | 9 | 168 → 168 | +9 | 1 |
| w4a4-13-Relu2 | FC2 | 1 / 1 | 9 | 76 → 76 | +6 | 1 |
| w4a4-15-Swiglu | FC1 | 2 / 1 | 10 | 168 → 168 | +7 | 2 |
| w4a4-15-Swiglu | FC2 | 2 / 1 | 10 | 72 → 72 | +5 | 1 |
| w4a8-0-Relu2 | FC1 | 1 / 1 | 10 | 168 → 168 | +10 | 2 |
| w4a8-0-Relu2 | FC2 | 1 / 1 | 10 | 82 → 82 | +6 | 1 |
| mxfp8-11-Swiglu-stage1 | FC1 | 2 / 1 | 1 | 168 → 168 | +9 | 3 |
| mxfp8-11-Swiglu-stage1 | FC2 | 2 / 1 | 1 | 122 → 122 | +4 | 1 |
| per-token-14-Relu2 | FC1 | 2 / 2 | 4 | 168 → 168 | +10 | 1 |
| per-token-14-Relu2 | FC2 | 2 / 2 | 4 | 128 → 130 | +50 | 3 |
| per-token-6-Swiglu-stage1 | FC1 | 1 / 1 | 1 | 168 → 168 | +10 | 4 |
| per-token-6-Swiglu-stage1 | FC2 | 1 / 1 | 1 | 87 → 87 | +9 | 2 |
| w4a8-7-Swiglu | FC1 | 2 / 1 | 11 | 168 → 168 | +10 | 2 |
| w4a8-7-Swiglu | FC2 | 2 / 1 | 11 | 70 → 68 | +22 | 2 |

The native code preserves a useful query window in the examined narrow/wide bodies. FC1 examples keep the TEST result in a predicate across 43–48 intervening instructions, including 2–3 SF copies and four MMA instructions. FC2 examples carry it across the normal loop backedge with 60–64 intervening instructions, including 2–3 SF copies, four MMA instructions, and the existing asynchronous releases. There is no immediate predicate materialization in these inspected windows. `qualification/early-window-proof.json` records exact PCs and SASS hashes; these instruction counts are not cycles or a latency prediction.

All 16 selected main-kernel pairs retain their original static PTX TRY counts. New queries lower to non-TRY `SYNCS.PHASECHK.TRANS64`; the blocking fallback and releases remain. Both one-stage cases pass exact outputs and actual requested/allocated depth checks; these are private-constructor correctness diagnostics, not native recorded tactics. Native CLC is confirmed for both CTA groups in separate pairs.

The wide per-token FC2 cost is material: +50 static non-NOP instructions and two registers despite unchanged one-CTA occupancy. The long-K FC2 adds 22 instructions while using two fewer registers. These costs rule out an instruction-simplicity claim; any retention requires measured useful gains with the full relevant frozen-choice coverage and preserved regressions. No timing has been run for this candidate.

Replay: `python3 experiments/mma-readiness/audit_qualification.py`. The summary binds both raw receipts, exact source inventories, captured PTX/SASS/ELF hashes, all resources, and the single approved exception. The failed initial receipt is never rewritten.
