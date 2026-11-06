# SF/payload issue interleave: rejected

[Final results](RESULTS.md) preserve all56 cells, all32 negatives and clock/repeat boundaries. The independent [raw replay](../../audits/sf-payload-interleave-data-peer.json) confirms22,400 CUPTI samples,112 native resource pairs unchanged and zero local memory. Overall−0.245686%, T32−0.078375%, T16384−0.412717% does not justify the extra compile-time issue control.

The earlier [native qualification](NATIVE_RESULTS.md) remains a historical gate, not a retention decision. [Source proof](source-proof.json), [exact patch](candidate.patch), [combined22-call/33-pair gate](qualification-summary-combined.json), performance helpers and immutable raw/native evidence remain preserved. No repeated or expanded timing was run.

The rejected review checkout/local branch was removed only after exact source/patch/status checks; [retirement receipt](retirement/receipt.json). Canonical retainedc1ac8ce7 is clean and unchanged. Measurements stay bound to their original2b8 control plusa014 candidate, with no relabeling.
