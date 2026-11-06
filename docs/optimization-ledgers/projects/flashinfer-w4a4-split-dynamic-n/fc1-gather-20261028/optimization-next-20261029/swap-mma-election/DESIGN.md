# One election per MMA batch

Retained374ed4c0 control. Candidate moves the existing elected-lane scope around the static width loop in _blockscaled_dynamic_mma, rather than electing for every MMA instruction. All descriptors, K96 tail widths, accumulator flags, operands, stage waits/commits, warp roles and tactics remain unchanged. This is an instruction-efficiency probe across dtypes and CTA groups, not a new tactic. Compile/SASS and existing exact tests before timing; reject if code generation becomes less efficient. FC1 and FC2 share this helper.
