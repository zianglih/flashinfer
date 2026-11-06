The proposed patches remove only four immediate caller load waits in `_run_token_group`. They are based on the two active local reviews at retained77391e28. Both review sources and every measured remote source remain unchanged. `propose.py` executes the AST checks and writes separate serial/paired proposed patches and complete source snapshots.

The fixed helper's postcondition is that every generic TMEM read issued by the calling warp has completed before return. Its final statement before return is `fence_view_async_tmem_load`; all three scratch-store phases have already completed before the subsequent read phases. Returning a register tensor or its static view does not issue another TMEM read.

| Release path | Reads covered by the helper | Work between helper and release |
|---|---|---|
| Gated, per-token | Both accumulator fragments at `scratch` and `scratch+(16<<16)`, plus the complete transpose scratch reads | Static register views in paired R1; the second complete helper in serial R2 |
| Gated, per-tensor | Both original accumulator fragments, activation register inputs and the single-result transpose | None |
| FC2 half output | The original top/bottom accumulator fragments and the single packed transpose inside `_scale_pack_transpose` | BF16/FP16 bitcasts, register permutation and return; all objects are rmem tensors |
| Non-gated/ReLU2 | Both top/bottom accumulator fragments and both transpose results | Static register views in paired R1; the second complete helper in serial R2 |

Each warp's scratch is its original32-row TMEM datapath, derived from `acc_tensor + token_start + warp*(32<<16)`. The proposal changes no address, alignment, protected interval, phase, valid-token predicate, slab order or release condition. The entry wait covers the original accumulator loads before scratch reuse, including the second fragment held in registers during serial transposition. The final helper wait covers all scratch reads before `consumer_release` can transfer ownership. The other epilogue warps perform the same local completion before their existing pipeline arrivals; the pipeline still joins the original participants. No new shared-memory or global-memory ordering assumption is introduced.

The AST proof confirms that every one of the four removed waits directly precedes its existing `consumer_release`, and that the complete module AST is otherwise identical. The helper, `_scale_pack_transpose`, all release calls and all original comments remain intact. `_scale_pack_transpose` performs no new TMEM load after the complete helper; its remaining loads/stores operate on tensors created by `make_rmem_tensor`.

The proposal deliberately retains waits outside these four dominated release paths: native bulk-output loads, the skipped protected-slab release in `run_overlapping_fc1`, other fallback/terminal paths and the kernel's final TMEM lifetime handling. Those paths are not justified merely by the helper return contract. The same proof applies to either serial or paired helper policy.

These are source-local proposals only. No GPU measurement or correctness claim for the composed wait-removal candidate has been made. After choosing the helper, inspect emitted PTX/SASS and run the existing resource/exact gate before measuring the composition.
