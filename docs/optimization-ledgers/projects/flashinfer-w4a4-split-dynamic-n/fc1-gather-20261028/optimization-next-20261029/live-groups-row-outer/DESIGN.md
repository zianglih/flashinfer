# Live-group loop interchange

This follow-up changes only the order of the row-group loop and compile-time K-chunk loop in the rejected live-group experiment. It reuses four broadcast route coordinates across all K chunks. It remains a separate experiment; retained475 is unchanged.

- Base: `475cae6b28a536e24aa8da2ed488d0f00fb5305b`; local `flashinfer-fc1-gather-row-outer-review`, unstaged.
- Previous live-group patch SHA: `8e245181072ee512db8da95df1a2eb46c8828d93bb7841c169ecdcee7f731104`.
- New full patch SHA: `92af4b26bbe4957359ae16bb9bc86d9d3c91838648e085a25dfb58216d0d6090`; kernel SHA `821b22521d662d8b1df770b6d40698fbf70a23fdb38ae0af402c9d0570f8a09b`.
- `loop-interchange.patch` isolates the sole follow-up. The old complete source remains in its immutable remote clone, plus local patch/source manifests and all gates/raw screen evidence.

The Cartesian product of live row groups and valid K chunks is unchanged. Distinct `(row-group, K-chunk)` pairs write disjoint shared-memory regions. All TMA transfers still announce the same byte total to the same stage barrier; SF cp.async arrivals, producer phase advance, and stage reuse are unchanged. The four SHFL broadcasts remain outside `elect_one`, with full-warp participation and warp-uniform selected row IDs. No descriptor, pointer, data-dependent work, or barrier is moved across a K-stage boundary.

At N16/two-CTA/K4, half the issuing warps have no K chunk. The new row-outer order makes them execute coordinates/shuffles before the unchanged K predicate. That work is safe but could regress decode; the existing minimal-tile cases are part of the exact/codegen gate and the small timing filter if the generated code is worthwhile. No extra tactic or branch policy is added to hide this cost.

The preceding screen is rejected: all six prefill actual-chain cases regressed, with two decode cases neutral. Some windows show software power-cap flags. Power caps may reflect changed utilization as well as external variation; those measurements are not normalized to a common clock. See `../live-groups/RESULTS.md`. This follow-up tests one concrete redundant-coordinate cost rather than assuming less payload traffic is sufficient.
