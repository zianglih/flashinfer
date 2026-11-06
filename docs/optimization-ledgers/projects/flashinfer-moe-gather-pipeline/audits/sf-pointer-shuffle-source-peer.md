# SF pointer-shuffle source peer

No source-level blocker found. The candidate preserves the original payload register-coordinate setup, one signed Int64 SF offset per lane/row block, all shared storage/planner calculations, and the payload task order. The R1 copy ownership, padding/zero-fill predicates and static arrival count remain consistent with the replayed 652,800-copy algebra.

Both full-mask pointer-half shuffles execute before the copy predicate inside the existing side-effecting primitive. The helper call is unconditional across each participating gather warp. Reconstruction and the lane-word addition are both 64-bit; G1 produces the exact original asm string, constraints and options. No new shared cache, synchronization phase, public argument, policy axis or quota is present; the helper gains two compile-time parameters.

Native validation must still establish compiler acceptance and actual SHFL/address placement, resources and spill behavior. The new shuffle-to-address-to-copy dependency is real work; source correctness does not demonstrate a performance benefit or prevent ptxas rehoisting.

Bindings and individual checks are in [the JSON receipt](sf-pointer-shuffle-source-peer.json). Candidate `371510e6a745e8c7845d0918a7d5984386b07ff7eea3eb4749f3f5f8fe6ad6e4`; patch `5b94bb24c4a58b8e462e7d0e573ef992ec5a07a011dd9d693b4522152725f17a`.
