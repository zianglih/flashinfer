# Universal SF ordering

The per-stage sequence is acquired weight/SFA → SFA0 → optional SFA1 → optional gathered-B wait → SFB → MMA0/1. There is one SFB copy site and no new GEMM-specific behavior knob.

- SFA0 occupies TMEM `[acc_reserved_cols, acc_reserved_cols + sf_cols)`. SFA1 starts at `acc_reserved_cols + sf_cols`, when present. SFB starts at `acc_reserved_cols + sf_cols * channel_tiles`. The destinations do not overlap; changing SFA1/SFB issue order introduces no dependency.
- The weight/SFA consumer wait still protects both SFA source tiles. The gather barrier still protects SFB and gathered activation data before their reads. Existing operand-empty release and same-warp tcgen05 ordering remain unchanged.
- All scale copies remain before their first MMA use. The stage's prior MMA/empty lifetime is unchanged, including both channel tiles and two-CTA ownership.
- The complete module AST after specializing `gather_input=True` matches the measured `04c92...` SFA-overlap predecessor. Nongather one-channel work also has the same operations/order. Nongather two-channel work changes SFA0→SFB→SFA1 into SFA0→SFA1→SFB.

This is a distinct candidate (`f377110b...`). Its exact-test and paired-performance receipts must be used for retention; do not label the predecessor's measurements as this version's results.
