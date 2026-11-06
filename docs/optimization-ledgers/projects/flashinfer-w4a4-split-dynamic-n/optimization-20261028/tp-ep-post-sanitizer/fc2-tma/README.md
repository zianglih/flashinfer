# Routed FC2 2D TMA experiment

Base `d1767be1f42fdc371f90db4fb06598299ea32845`. Active source is `../../../flashinfer-fc2-tma-review` (four unstaged files; independent project-local Git metadata). Canonical and frozen control source remain unchanged.

The TP8 K3 MXFP4x8 diagnostic places FC2 at813.7us with19.78% tensor utilization,773.8MB DRAM reads and1.830GB writes;42.24% long-scoreboard and20.76% barrier stalls. Its combine is already predominantly memory-bound. This experiment reduces FC2 output transactions and routing/address instructions without changing GEMM or accumulator ownership.

Only the high-level swap-AB unfused chain selects routed scratch. The private FC2 launcher preserves its expanded/fused default. Each64×128-channel bulk slab is represented as two contiguous64×64 halves with the existing128B TMA swizzle and issued by one elected lane in each of two epilogue warps. It replaces64 individually scattered256-byte stores with two ordinary2D tensor stores. The32-row fallback similarly replaces32 stores with two. The previous routed-FC2 experiment retained individual stores; the rejected scatter4 family needed four destination coordinates per packet and32 half-row packets. Neither removed the per-row transaction structure as this candidate does.

## Invariants

- Routing reserves whole route tiles. A32/64-row bulk slab lies wholly within its owning padded tile, so writing inactive rows cannot overwrite another tile. The existing inverse map makes combine ignore padding; channel and allocation tails are clipped by tensor-map bounds.
- The two halves retain the exact current scratch extent and stage stride `tokens*136` elements. Every stage/half starts at a128B-aligned location. The absolute byte XOR `address ^ ((address >>3)&0x70)` matches the already qualified scatter4 SW128 contract, including nonzero base offsets.
- TMEM loads, packed FP32 multiplication, BF16/FP16 conversion, forward/reverse traversal and early protected64-column accumulator release are unchanged. No new register fragment persists across steps.
- All128 epilogue threads retain the existing shared publication/reuse/final joins. The two elected tensor-store owners still execute the same commit and read-completion waits; their completion is included before scratch reuse/exit. No barrier is removed.
- Default-false, fused finalize, low-level expanded output and W4A16 paths are unchanged. The combine's existing private row-extent policy is explicitly enabled to preserve current swap-AB launch geometry despite routed addressing. No new public parameter, tactic, dtype/model branch or input alignment contract.

Routed capacity may greatly exceed expanded capacity on decode because of expert padding (earlier layout-only trial documented up to16–256×). This cost and descriptor startup must be included in full-chain timing. No gain is claimed from source review.

## Gates

Use private compiler CWD per process, persistent native caches, source hashes before/after and native artifact identity checks. First run a short MXFP4x8 K384 public-chain check, then all four formats including per-token NVFP4, one/twoCTA, N16–256, static/CLC, PDL off/on and balanced/skewed/empty/reactivated routes. Gate compares final output storage bytes to source-matched d1767; it is not a substitute for a new standalone exact oracle.

After codegen and exactness pass, use fixed fresh winners with cold-L2 CUDAgraph CUPTI C–A–A–C on both EP and TP, tokens4/64/4096/16384. Include allocation/launch cost as represented by the existing benchmark closure. Preserve all individual cells and regressions. No broad retune, public update, or retention before both topologies pass.
