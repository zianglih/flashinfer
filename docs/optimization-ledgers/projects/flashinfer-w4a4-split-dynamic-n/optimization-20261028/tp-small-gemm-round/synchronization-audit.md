# Synchronization audit at105474378

Source: `flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py`. Scope is the new swap-AB blockscaled pipeline; existing W4 barriers are not changed by this round. No sanitizer was requested for these iterations.

- Operand stages already share one empty/full lifecycle across weights,SFA,activations,SFB. Weight producer announces the sum of both producers' transaction bytes; each producer independently waits for reuse and issues TMA. MMA waits for the shared completion and releases only after all channel tiles consume their shared B/SFB. Removing either producer's empty wait would allow overwrite of in-flight MMA inputs. Splitting barriers would increase state without independent operand lifetimes.
- Accumulator stages have a different lifetime: MMA acquires a TMEM window; the full epilogue warpgroup releases it after loads. TMA-store scratch and TMEM-transpose scratch have their own overwrite/read completion; their waits cannot be inferred from operand readiness.
- CLC response and published tile metadata are distinct. Hardware response storage becomes reusable once the scheduler consumed it; metadata remains live until all consuming roles have read it. Existing terminal CTA join drains metadata consumers. Reusing the fourth already allocated metadata word changes payload only, not these lifetimes.
- PDL metadata/weight startup runs ahead of payload dependency waits. Activation and epilogue payload readers wait; deferred MMA/scheduler dependency waits occur before terminal join. This is separate from per-stage operand completion and cannot be dropped merely because a stage barrier was satisfied.
- Pipeline initialization fence is followed by the existing cluster/TMEM setup synchronization. No extra role-specific initialization barrier is introduced.

No synchronization change was made without a distinct lifetime proof and a generated-code/performance hypothesis. Current candidates instead remove redundant route decoding, affine output mapping, and degenerate cluster-rank work. Static and CLC schedules, PDL, both CTA group sizes and format combinations are included in source-paired qualification.
