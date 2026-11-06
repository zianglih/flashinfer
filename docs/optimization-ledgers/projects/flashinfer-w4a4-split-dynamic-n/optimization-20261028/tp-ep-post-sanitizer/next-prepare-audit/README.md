# Next prepare/FC1 audit: fixed-atom index arithmetic

Read-only review on 2026-10-28. No source variant, GPU launch or benchmark was created. Finish the retained refresh before any new experiment.

## One bounded lead

The fixed 128-row SF atom address in `moe_swap_ab_prepare.py:175–179` currently uses signed `// 128`, `% 32` and `(% 128) // 32`. The saved K3 TP8 MXFP4x8 T16384 SourceCounters/SASS export contains a 34-instruction region at `0x748c759fc1e0..0x748c759fc3f0` between the payload store and SF store. It includes sign checks, correction predicates and four PRMT operations for floor/remainder handling, besides necessary address arithmetic. The full instructions and source hashes are in `evidence.json`.

A small follow-up can express just these fixed-atom operations directly:

```text
sf_row // 128          → sf_row >> 7
sf_row % 32            → sf_row & 31
(sf_row % 128) // 32    → (sf_row >> 5) & 3
```

Keep the existing `Int64` promotion of the atom index before the wide byte/word multiplication. These are mathematical identities for signed floor division by positive powers of two, including negative values, not an assumption that the compiler must infer. A CPU check covers 102,051 signed values, including both int32 extremes. CUDA DSL must still be verified to emit arithmetic right shifts for the signed expression; the CPU proof is not hardware qualification.

This changes only index arithmetic inside the existing scaled SF branch. It keeps one CTA/row, the same 128 payload lanes and LDG/STG256, grid, register SF preload, routing traversal, byte layout, invalid-row zeros, physical-padding canaries, PDL and memory lifetimes. Unscaled W4A16 does not execute the branch. There is no extra storage, barrier, copy pass, tactic axis or model/token policy. The constants describe the established SF atom rather than benchmark dimensions.

The first follow-up gate should be static generated-code comparison, requiring fewer floor/remainder correction instructions with unchanged memory instruction counts, no spill/occupancy regression and identical unscaled W4A16 SASS. Only if that succeeds should the existing byte/canary gate and bounded EP/TP decode/prefill CAAC screen be reused. No expected speedup or exact instruction reduction is claimed before compilation.

## Why this is a narrow cleanup, not the TP gap solution

The same source export attributes 11,111 of 16,178 sampled long-scoreboard stalls (68.68%) to payload `STG256` at `0x748c759fc1c0`, waiting on its earlier `LDG256` result. Mapping and limit-dependent instructions at `0x748c759fc000` and `0x748c759fbfb0` account for another 2,801 and 1,100 samples. Thus the observed dependency chain is mostly payload/routing reads, not a synchronization barrier or SF-store stall. These PC samples are diagnostic and are not additive wall-clock costs.

The earlier traffic attribution remains valid: 29.36M payload store sectors plus 8.87M SF store sectors, with roughly 998 MB DRAM writes. Removing signed correction instructions does not eliminate that traffic. R1 already proved that coalescing SF stores alone trades away input load locality; R2/R3 proved that four lanes per row loses useful decode payload parallelism, even after fixing grid geometry and forced loop unrolling. None of those ownership changes is proposed again.

## FC1 boundary

Saved K3 TP FC1 is about 582 µs critical extension and 76% tensor-elapsed utilization; V3 TP MX4x8 FC1 is about 352 µs extension. Aggregate barrier/long-scoreboard/wait counters do not identify an unnecessary FC1 dependency. The later K96 V3 EP profile shows fewer MMA instructions but unchanged SF-copy and synchronization sites; it is not a TP or MX FC1 profile. Existing ledger audits already ruled out repeated-election cleanup, single-transpose per-token FC1 and duplicate-SFB multicast as useful measured changes.

There is insufficient current per-PC/warp evidence to propose another FC1 synchronization or producer policy change. After compact FC2 is retained, a fresh final-source stage breakdown should establish whether FC1 or prepare is on the new critical path before collecting a focused FC1 source/warp stall trace. The fixed-atom arithmetic cleanup above is the only small source lead supported by the existing generated code.

Evidence read:

- `../profile-evidence/RESULTS.md` and its TP K3/V3 reports.
- `../k96-profile/RESULTS.md` and the retained K96 codegen accounting.
- `../prepare-sf-coalescing/ncu-evidence/source.csv`, `ncu-attribution.json`, and R1/R2/R3 README/retention notes.
- `../../warp-polish/producers/next-audit/CLOSED_LEADS.md` and `SFB_MULTICAST_FOLLOWUP.md`.
