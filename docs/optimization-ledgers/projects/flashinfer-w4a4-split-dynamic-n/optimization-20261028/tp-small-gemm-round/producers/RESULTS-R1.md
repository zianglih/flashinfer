# Rank bitmask R1: reject

The frozen bitmask candidate passed64 cross-source storage-bit exact replay comparisons,32 paired GEMMs and4 unchanged combine kernels on105474. Scoped pre-commit passed. All321 fetched files were hash verified.

One-CTA kernels remove11–15 static non-NOP instructions; static scheduling removes one activation-limit global load. Total hardware rank-read sites increase2→3 due to compiler/SDK control-flow lowering, so this does not prove every dynamic instruction count decreases. Registers are unchanged except one variant−1. No local or stack spills; recorded uniform spill/fill counts remain unchanged.

Two-CTA kernels gain1–5 non-NOP instructions from the needless mask. This form is rejected without timing. R2 expresses the degenerate one-CTA rank as a compile-time zero and retains the original two-CTA expression. R1 source, patch, logs and codegen remain immutable here.

`evidence-verification.json` binds the6.7MB raw archive; `evidence/analysis.json` gives every paired resource and instruction result. No sanitizer or performance measurement was run.
