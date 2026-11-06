# Independent review: fixed SF-atom indexing

**Pass for source correctness and the completed focused qualification.** Performance retention remains conditional on the separate 56-cell CAAC screen; this review does not invent a speedup claim or relabel earlier tests.

- Base: `83dfef8a656384f5cd10db847602593bb6f9b2c6`. Candidate prepare SHA256: `83e046ef20a750eeca9d9d90d93a0c52877d2d14b32ae19def8fe6dac917d8f4`.
- The entire repository delta is exactly three substitutions inside the existing SF destination offset. All348 source hashes are present in each frozen source manifest; only this file differs. The independent checker reconstructs the candidate from the base using these three substitutions and requires byte equality.

## Arithmetic and lifetime

For any signed integer `x`, write `x = 128q + r`, with `0 <= r < 128`. Arithmetic `x >> 7` equals `q`; `x & 31` equals `x % 32`; and `(x >> 5) & 3` extracts `floor(r/32)`, equal to `(x % 128)//32`. This includes negative values. An independent CPU check covered272,146 inputs, including both Int32 extremes, every value from−131072 through131072, and seeded random signed Int32 values.

The reachable `sf_row` is a destination-row index derived from the nonnegative row loop and route-tile geometry. Invalid input mappings are guarded before source loads; their negative sentinel is not the SF destination row. The signed proof therefore covers more than the reachable destination domain.

`cutlass.Int64(sf_row >> 7)` retains widening before the SF-atom product. Representative compiled PTX uses `shr.s32 ..., 7` followed by `mul.wide.s32` for the atom offset. The masked bits5–6 extraction may use `shr.u32 ..., 5; and ..., 3`; that is also exact because the sign-fill bits are discarded. No pointer representation, row ownership, route padding, PDL release/wait, compact-prefix metadata, or memory-lifetime rule is changed.

## Raw qualification independently verified

| Evidence | Compiled control/candidate pairs | Exact graph replays per source | Unscaled/W4A16 instruction streams identical |
|---|---:|---:|---:|
| Production codegen, PDL off/on, compact offsets off/on for scaled inputs | 18 | Not a live-row accuracy gate | 2 |
| Byte/canary gate | 92 | 552 | 30 |

All904 raw files in the two manifests were hash-verified. The gate checks the entire payload and scale allocations, including invalid-row zero scales, untouched payload/padding canaries, and unchanged input mappings/limits. It covers route tiles16/32/64/128/256, SF16/SF32 and unscaled activations, aligned256-bit and fallback128-bit copies, PDL off/on, six zero/partial/full/empty/reactivated count states, and an80,016-row capacity that exercises multiple grid-stride iterations.

**Coverage boundary:** the552 comparisons are live **CUDA-graph** replays. The initial eager warmup has zero active tiles, so this is not552 eager-plus-graph comparisons. The live byte gate does not enable compact offsets; the separate18-pair codegen matrix includes compact offsets on/off. The unchanged compact-prefix algorithm and new SF address arithmetic share no data dependency. The public CAAC run exercises the live compact path, but does not replace a numerical test of that path.

## Generated code

- Every scaled pair removes23–24 **static SASS instruction sites**, including the signed correction/PRMT work. This is not a blanket dynamic-instruction or end-to-end speedup claim; the count includes emitted NOP sites.
- Register count decreases by0–2; no increase. Shared allocation is unchanged.
- All artifacts have zero local-memory load/store sites, zero stack/local allocation, and **zero `MOV.SPILL` / `R2UR.FILL` uniform-register spill/fill sites** in both control and candidate.
- The complete control/synchronization opcode sequence is unchanged in every pair, including PDL instructions. Source branches and loop bounds are byte-identical.
- Memory opcode **counts** and widths match in every pair. Memory issue **order** is not universally identical:8/18 codegen and30/92 byte-gate pairs schedule the independent SF load before the payload LDG. This is normal compiler scheduling of independent operations, with the source ownership/dependencies unchanged. Do not describe the machine instruction stream as unchanged for scaled inputs.
- All30 unscaled/W4A16 byte-gate instruction streams are exactly identical, as are the two representative unscaled codegen streams.

Machine evidence: `independent-review.json`; reproducible CPU checker: `independent-review.py`. No repository writes, GPU launches, or sanitizer changes were made during this review.

## Minimal PR validation wording

> The full EP/TP benchmark and focused sanitizer results above were collected at `83dfef8a6563`. The subsequent three-expression SF-index simplification was checked against that source with552 byte/canary CUDA-graph replays per source across92 prepare specializations; all30 unscaled/W4A16 instruction streams were unchanged. The focused codegen checks found no local or uniform-register spills.

If the CAAC screen is retained, append its exact final result and commit binding separately or link its immutable receipt. Do not silently change the tested source attached to the83df full matrix/sanitizer evidence, and do not claim the full sanitizer suite was rerun for this expression-only follow-up.
