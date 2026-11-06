# Bounded queued-K AUTO screen

This is a sequential same-GPU V3 EP8 control/candidate screen at 4, 128, and 4096 tokens. Control is frozen planner `a9ef37a8`; candidate `b51752b2` changes only automatic K ranking. Both use the original public benchmark with fresh native AUTO, all five CuTe arms, 10 warmups / 100 iterations, cold L2, CUDA graphs and CUPTI, with fused finalize disabled. No TRT or historical-GPU comparison is part of this screen.

CuTe compiled artifacts are source-private; unchanged native artifacts and the regular-file lock directory are shared. The cache helper verifies each source identity before launch. Earlier `auto-r1` failed before all timing rows because FileLock rejects final-component symlinks. The separate repaired-helper receipt preserves that failure and demonstrates contention/reacquisition. No data from that attempt is used here.

A single C1 then A1 sweep is an optimization screen, not a paired retention decision. Both source receipts, helper hashes, actual runtime imports, GPU UUIDs, route identities, full-precision medians and selected native tactics are preserved in each fetched run.
