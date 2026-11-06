# FC1 fragment64 source candidate

Worktree `optimization/fc1frag64` starts at detached `002ef1454cbacde09972ed5e2ec7dcfe37e55749`. It changes only the first `_make_mixed` argument inside `_fit_raw_stages`,128→64. The FC2 construction remains32. The worktree common Git directory is the effort-owned `hashinfer/.git`; no shared repository metadata is touched.

Whole-module AST equality was checked after applying exactly this literal change to the base AST. `git diff --check` passes. Raw patch and SHA256 audit are `fc1frag64.patch` and `fc1frag64-source-audit.json`. No GPU work, correctness result, or performance claim is attached to this candidate.

The requested fragment is clamped by the existing coalesced layout size and splits the per-thread decode into smaller static chunks. It changes no packed-weight or scale layout, element ownership, TMEM storage layout, buffer count, accumulator depth, warp roles, register allocation limits, or synchronization placement. The actual instruction schedule and register liveness may change, so native SASS/resource inspection is required. The input tensors and output arithmetic remain source-equivalent, but bitwise numerical validation is still necessary after compilation.

This is deliberately separate from full K256 predecode, no-peek and store16. The old CUDA130 resource audit proposed a cap64 trial conditionally but supplied no measured result; prior FC2 fragment16 and lookahead/store experiments were rejected. See `trace-follow-on-hypotheses.md` for the historical pointers and exact limits.
