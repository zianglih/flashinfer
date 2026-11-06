# Batched swap Gather4 route metadata

Control is retained e780f02c. Candidate changes only the route-ID preload in the dedicated last gather warpgroup; SF loads, register budgets, stage count, four Gather4 issuers, expected bytes, arrivals, PDL, CLC and every inner-K operation are unchanged. FC2 remains regular TMA.

Each lane loads one coordinate from a batch of up to eight four-row groups. Static shuffle indices reconstruct the identical per-warp coordinate cache. The batch width is the next power of two covering the groups per warp, capped at the warp capacity; small tiles retain the original lane mapping. This moves independent route loads into one warp instruction and reduces repeated divide/address work without extending route-ID lifetime.

The CPU proof covers42,084 cases across every supported token tile, CTA1/2, valid0..N, all four gather warps and seven top-K values. It compares source addresses, decoded IDs and OOB sentinels exactly. GPU gates must also verify bit-exact output, actual register/spill resources and instruction changes before a paired timing campaign. No performance claim yet.
