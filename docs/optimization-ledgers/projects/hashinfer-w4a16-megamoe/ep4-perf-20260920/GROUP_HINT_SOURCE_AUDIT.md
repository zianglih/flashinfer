# Group-hint source trace

Source: clean HashInfer `ec42ba07e2ebc164d1ba2796152f54e0ac821935`. This is a source-only trace; it does not claim generated PTX/SASS identity and required no additional GPU work.

The only direct device arithmetic use of `group_hint` is `fc1_fc2_fuse_sched.py:779`: `threshold = base_fc1 + Int32(params.group_hint)`. The following greedy expert walk (lines 784–800) consumes runtime expert counts until the cumulative FC1 tile count reaches the threshold or the local expert range is exhausted. It then sets the group's FC1/FC2 interval boundaries. Increasing the hint can delay the FC1→FC2 transition and reduce the number of groups. A single expert is never split to meet the hint.

Propagation and other uses:

- `autotune.py:30,41` generates the compile-time G512/G1024 choices. `shim/tuner.py:12` retains the fixed G512 default outside AUTO; its dataclass `with_knobs` propagation carries the candidate field.
- `frontend.py:39,222` stores the field and passes its positive value into the kernel constructor (`None`/zero instead use max-active-clusters). `apply_knobs` compares the frozen config and releases the compiled frontend when it changes, so a changed group hint does compile a distinct specialization.
- `megamoe_kernel.py:201,292,712` stores the constant, includes it in the kernel name, and passes it to scheduler parameters. It is not otherwise read by workspace sizing, transport, epilogue, or MMA/transform pipeline code.
- `fc1_fc2_fuse_sched.py:161,175` validates/stores it. `_mlir_fields` (lines190–201) omits `group_hint`; reconstruction copies it as a Python codegen-time constant, not a runtime launch scalar.
- The scheduler's `make_storage_struct` (line283) depends on scheduler stage count, tile-record size, and static/atomic mode; it does not use the group hint. The kernel stage-fit helper (line375) consumes that storage type. Thus the source does not alter SMEM allocation, raw/activation stage depths, register role budgets, or CTA grid as a direct function of this hint.

Equal computed group boundaries for a fixture establish equal high-level work ordering, not identical generated instructions. G512 and G1024 still insert different compile-time constants into the threshold expression and use different specialization names. Compiler simplification, instruction placement, or register assignment can consequently differ even when every runtime loop takes the same branches. An instruction/codegen-identity claim would require generated-code comparison; none was done here.

For retention analysis, rows selecting G512 with otherwise identical tactics use the original specialization. Rows selecting G1024 must remain labeled changed specialization even when the source-derived phase groups coincide. In the current EP4 combined-eight sweep, T8 hot AUTO scores for G512/G1024 are both 136.5 us, supporting a noise interpretation of their differing cross-sweep cold medians, but not proving zero implementation impact.
