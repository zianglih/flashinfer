# Raw-stage lifetime audit

Read-only audit of retained `6be4971b2dc3720f168510d09190e6519da38e2c`; source SHA256 `de042712ac4fcab0f14eb5f870824416f65dce15e2243198b28ffb4226ac0d58`.

`_transform_tile` first copies all scale values from `tSsS_slice_filtered` into the register tensor `tSrS_copy`. Its complete constexpr decode loop copies each packed raw-weight fragment into `tArA_load`, consumes the corresponding register scale fragment, and writes decoded BF16 values into the register tensor `tArA_transform_store`. At the end of that loop, every raw-weight and raw-scale SMEM read is complete. The following `store_transformed_a` reads those decoded registers only.

The decoded destination cannot alias the raw stage: TMEM mode points after the reserved accumulator columns; SMEM mode uses a distinct `smem.allocate_tensor` allocation for `sA_transform` (retained source lines1351–1360), separate from both `sA_input` and `sS_input` (1317–1329). The old gated64 layout changes only raw-input views and does not alias the destination.

It is valid to move the existing `a_load2trans_pipeline.consumer_release(cur_a_load2trans_consumer_state)` immediately after the complete decode loop and before the decoded store. All transform threads still make the same single release using the cloned original stage state; multicast participant counts and phase progression are unchanged. The raw producer may refill that stage while decoded output is stored. The TMEM-store / async-shared fence and `trans2mma_pipeline.producer_commit` must remain after decoded stores; they publish a different resource. Keep both useful raw/destination lookahead peeks unchanged.

The optimization ledger search found no previous experiment making this same release move. Earlier producer-lookahead and narrowed-TMEM-wait experiments changed different dependencies. This is a source/protocol proof, not a fresh correctness or performance result. Gate/codegen/paired timing are owned by the parent.
