# Combined alpha/norm hoist: frozen, unretained

Current source: b85eff41 + patch247e09b609ec0eb7c2e92a70a727b9ae9262c249599a3d26be9417e3378b3a5f. Both arms use the same six-field all-CLC enumeration.

The existing bounded source-paired gate passes64 exact graph replays (32 per source) with four formats, one/two CTA, N16/N128, inline/dedicated epilogues, PDL on/off, changing balanced/skewed/empty/reactivated routing. All16 kernel pairs have identical shared/TMEM resource policy and zero local loads/stores, local memory or stack. Register increases occur in inline NVFP4 FC1 (+2/+3) and mixed FP4x8 FC1 (+6/+9), FC2 (+2).

Actual SASS proves the invariant norm load moves outside the scheduled-tile backedge (norm-sass-proof.md). Alpha also acquires a longer live range. The combined change is not timed or retained: under the current simplicity criterion, first isolate the invariant norm-only load removal in a separate source, flashinfer-epilogue-norm-20261027. Register increases are not by themselves a correctness or occupancy failure; this is a deliberate experiment-scoping decision.

Frozen source, raw PTX/SASS/cubins, source-paired hashes and complete receipts remain under this folder. No source mutation occurred during the gate. No new upstream tests were added.
