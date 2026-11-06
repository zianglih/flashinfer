# Partial transform-group scope

Retained control: `49c91adf47d30fc2049c76cbaf34d0ccf3291434`. Candidate changes only the shared W4 kernel's `_transform_tile` implementation, SHA256 `b25dacfac38c3193a4368e87be2ec058f0da71fbc76db6b56490679b42676851`; all callers and interfaces are unchanged.

The static clipping extent is `min(group_k, round_up(consumed_k % group_k, 32))`. A second constexpr view is emitted only when that extent is strictly between zero and the whole group. Current frozen W4 tactics use stage K256 and two transform groups, hence group K128.

| Arm | FC1 K | FC2 K | Changed specialization |
|---|---:|---:|---|
| V3 EP8 / TP8 | 7168 | 2048 / 256 | None |
| V41F EP4 / TP4 | 5120 | 2304 / 576 | TP FC2 only: last live group64 |
| K3 EP8 / TP8 | 3584 | 3072 / 384 | None; TP final group128 remains full |
| N3U EP8 / TP8 | 2048 | 5120 / 640 | None; TP final group128 remains full |

Thus the current 468-cell model table has 13 affected V41F TP W4A16 cells and 455 unaffected cells. The authorized experiment measures only those 13 cells, reusing the original recorded tactics/routes with strict same-GPU C-A-A-C. Tokens1/2 remain raw-only for retention. These dimensions must match the frozen benchmark metadata; the preparation script checks them from the source model configuration.

Unaffected-source inference is supported by reconstructed full-path AST equality and representative actual aligned split and Mega raw PTX/cubin/SASS equality. It does not claim all455 unaffected specializations were recompiled. Mega explicitly supplies its padded consumed extent, so its specialization has no clipping branch; both existing aligned and partial-logical-K Mega cases produce identical native binaries.

Qualification retains two limitations: legacy64 gated-weight preparation cannot represent intermediate352, so the retained-control setup failure remains preserved and the FC2-tail96 pair uses the supported swap layout; direct private M-major K16 is admitted by `can_implement` but the retained kernel fails `_setup_transform_partitions`'s existing whole-scale-block assertion before entering `_transform_tile`. There is no new fallback or shape whitelist and no claim to have fixed that pre-existing capability mismatch.
