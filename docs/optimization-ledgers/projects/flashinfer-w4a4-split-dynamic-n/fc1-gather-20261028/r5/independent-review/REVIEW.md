# R5 payload cp.async source review

Frozen kernel `80dc6ad6`, patch `a1c3f3f3`, retained base `d35fcfda`. Source reconstructed from the archived patch because the live experimental review had advanced. No source edits or GPU execution.

No source-level blocker found. Independent source-extracted checks cover40 geometry combinations,4,008 live-row states and857,088 swizzled16-byte destinations. All nominal per-CTA payload bytes have unique destinations within their owned stage; runtime dynamic-N ownership consumes each valid logical row once. Narrow dynamic tiles can copy additional rows into unused nominal storage, which is not a duplicate consumed row or an overlap between CTA allocations. Logical K-tail vectors cannot cross the valid row extent under the admitted alignment.

The source caches an Int64 byte offset per distinct source row and uses predicate zero-fill for invalid rows/tail vectors. Four-byte SF transfers still populate the complete required SF layout in each CTA. The explicit SW128 byte transform is applied to absolute addresses. SDK recast_ptr without a swizzle argument builds an unswizzled destination pointer, so the subsequent 16-byte copy does not apply a second iterator swizzle. Actual compiled address lowering remains a GPU qualification boundary.

Every gather thread executes exactly one noinc completion marker after both SF and payload loops, including threads with no live payload task. The local barrier count remains128. Warp1's local wait, proxy fence and elected leader publication are AST-identical to R4 after the storage rename. MMA waits both weight/SFA readiness and payload/SF readiness. Existing operand-empty release is still the sole overwrite authority; it cannot be released until this generation has completed and been consumed. The previous phase/wrap/terminal proof therefore applies without a new synchronization path.

The weight producer announces only weight/SFA TMA bytes for gather FC1; activation payload and SF have moved entirely to the local completion/relay path. Non-gather FC2 kernel and load_weight_stage partially evaluate exactly to the retained AST, including its TMA byte counts. No new public or tactic axis.

`audit.py` and `receipt.json` bind source, patch and checks. Parent-run compiled exact output/resource/performance checks are separate; this review makes no speed or spill claim.
