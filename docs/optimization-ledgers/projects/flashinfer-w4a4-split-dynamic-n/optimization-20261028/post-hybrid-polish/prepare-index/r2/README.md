# Prepare index R2

Isolated retained61c2 candidate: unsigned arithmetic for nonnegative internal route indices, plus explicit `unroll=1` on the persistent row loop. No new public argument, format/model branch, memory-layout change, or synchronization change. R1 files and gates remain one directory above; they are not R2 evidence.

The row loop stays signed for its induction/termination and `source` stays signed at the valid/invalid join. Only division/modulo operands are unsigned. Address promotions to Int64 are unchanged. Invalid `mapping` entries are never read. Every valid expanded route index is `token * top_k + slot >= 0`; routing emits signed Int32 indices so accepted valid values fit Int32.

`unroll=1` is a compile-time loop policy intended to avoid ptxas multiplying the row body after simplifying signed division. It does not select shapes or power-of-two divisors. R1 had static SASS replication for K3, despite unchanged PTX load/store sites and exact byte checks. R2 will be qualified independently.

Source is frozen by the 348-file manifest in `source-local.json`. GPU7 only; persistent C++ cache links preserved. No sanitizer or autotuning. Exact byte/codegen qualification passed; see `QUALIFICATION.md`. The two-cell CUPTI screen is complete and does not support retention; see `RESULTS.md`. This candidate is not retained or included in the composed publication source.
