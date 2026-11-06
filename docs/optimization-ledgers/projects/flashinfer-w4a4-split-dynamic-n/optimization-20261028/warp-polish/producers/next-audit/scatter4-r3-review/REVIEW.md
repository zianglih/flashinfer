# Independent scatter4 r3 review

Source: `3e59f19e433bf9d311f9653d523c8a2fdd0194b23549aabaee0ae190f5428ccc` in `flashinfer-scatter4-review/flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py`. The active source and frozen gate snapshot match. No source edits or GPU runs were made for this review.

**Result: no source/lifetime blocker.** All 192 compiled-artifact hashes and 96 storage-byte replay hashes independently match their receipts and reused control; all 24 FC2 variants remove `R2UR.OR` and the backward `BRA.U.ANY` issue-arbitration loops. This is not a performance-retention decision.

## Ownership and lifetime

- For a 64-token slab, each of four epilogue warps owns 16 rows, partitioned into four consecutive four-row groups; for a 32-token slab each owns eight rows in two groups. All row groups are disjoint and cover the slab exactly.
- The source pointer, channel offset, descriptor and shuffle source-lane index are warp-uniform. `row_source` initially differs by lane, but the same shuffle source index broadcasts each coordinate to every lane. All four shuffles run before the elected-issuer region, preserving the full-warp shuffle contract.
- Both channel halves issue from the elected thread. The compiler may pick different elected threads across source groups; safety does not rely on a fixed elected lane. Every thread still executes one bulk commit after all groups for a slab and the existing read waits before shared-stage reuse. Every issuing thread is therefore covered by its own bulk groups.
- There remains exactly one commit per issued slab, not one per four-row group. Static `UTMACMDFLUSH` counts match control and r2 in all 24 variants. The stage-index sequence, 128-thread publication/reuse barriers and final read-drain are unchanged. Skipped slabs issue no groups and cannot increase the number of outstanding reads to a reused stage.
- `_scatter_metadata` now gives bulk stores the first out-of-bounds row (`output_tensor.shape[0]`) once per metadata slot. The other callers retain the default zero initialization. Invalid routes are clipped by TMA; no per-command tail compare/select is required. Valid-route scale arithmetic is unchanged.
- CTA2 behavior remains local shared-source/read ownership; there is no new cross-CTA producer or barrier. TMEM early-release fences and their conditions are unchanged.

## Generated-code tradeoff

The promised arbitration removal is present in all 24 variants. However, compiler scheduling eagerly materializes uniform command operands and introduces **uniform-register-to-GPR spill/fill**, not local-memory spill. Eighteen variants have 15–94 `MOV.SPILL` sites and the same number of `R2UR.FILL` sites. `LOCAL=0` and `STACK=0` in all variants. Do not summarize this as simply “no spills.”

| Representative FC2 static PDL-off | Control REG | r2 REG | r3 REG | r3 uniform spill/fill pairs |
| --- | ---: | ---: | ---: | ---: |
| config4 W4A4 N128 M256 | 99 | 124 | 167 | 32 |
| config5 per-token N256 M128 | 150 | 180 | 193 | 88 |
| config6 MXFP8 N256 M256 | 112 | 144 | 183 | 37 |
| config7 MXFP4x8 N128 M128 | 94 | 116 | 164 | 15 |
| config11 narrow control | 116 | 127 | 130 | 0 |
| config12 narrow control | 107 | 117 | 120 | 0 |

Across the 24 variants, r3 adds 1–50 registers and 73–536 static non-NOP instructions versus r2. Static counts alone are not executed counts: r2 repeatedly executes its lane-arbitration loop, while r3 explicitly emits the commands. Config4's first issue sequence at `0x3d70`–`0x4040` shows the uniform spill/fill clearly. Pending matched timing must decide whether the tradeoff helps; no shape/dtype workaround is proposed.

Reproduce the read-only audit with `python3 optimization-20261028/warp-polish/producers/next-audit/scatter4-r3-review/audit.py`. `audit.json` includes the 24 three-way resource/opcode comparisons; it verifies the source SHA, all compiled artifact hashes, exact replay hashes and input/control receipt equality.
