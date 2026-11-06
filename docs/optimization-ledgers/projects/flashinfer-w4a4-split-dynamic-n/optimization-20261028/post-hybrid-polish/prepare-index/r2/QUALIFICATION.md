# R2 qualification

R2 passed **120 exact graph replays per source and 20 compiled pairs** on GPU7. The paired control is source-identical retained61c2 (348 checked files); R2 changes only `moe_swap_ab_prepare.py`. R1 evidence remains separate. No sanitizer, fresh tuning, or full qualification expansion was run.

Every pair reduced non-NOP static SASS instruction sites with unchanged LDG/STG/ULDG/USTG site counts, zero local-memory instructions, and zero stack bytes. Raw register counts can rise by2, but all tested prepare variants remain at or below32 registers/thread; no register-allocation occupancy threshold is crossed. Counts below omit PDL-on duplicates; both PDL settings passed and have the same deltas.

| Gate | Payload uint32 words | SF uint32 blocks | Route tile | top_k | Threads / grid | SASS sites control → R2 | Registers |
|---|---:|---:|---:|---:|---:|---:|---:|
| persistent | 896 | 28 | 128 | 16 | 128 / 2368 | 85 → 61 | 30 → 32 |
| persistent | 1792 | 56 | 128 | 8 | 128 / 2368 | 91 → 67 | 32 → 32 |
| persistent | 1792 | 0 | 128 | 16 | 256 / 1184 | 49 → 35 | 24 → 26 |
| persistent | 3584 | 0 | 128 | 8 | 256 / 1184 | 52 → 38 | 28 → 30 |
| quick | 896 | 28 | 128 | 16 | 128 / 1024 | 85 → 61 | 30 → 32 |
| quick | 1792 | 56 | 128 | 8 | 128 / 1024 | 91 → 67 | 32 → 32 |
| quick | 1792 | 0 | 128 | 16 | 256 / 1024 | 49 → 35 | 24 → 26 |
| quick | 3584 | 0 | 128 | 8 | 256 / 1024 | 52 → 38 | 28 → 30 |
| quick | 32 | 4 | 96 | 6 | 128 / 1056 | 78 → 66 | 28 → 28 |
| quick | 132 | 0 | 96 | 22 | 256 / 1056 | 51 → 39 | 20 → 22 |

The persistent gate covers the hardware-sized2368-CTA scaled and1184-CTA BF16 grids, with4096 routed rows to execute repeated grid-stride iterations. Both width/top_k combinations use route_tile128 in this focused gate; the frozen end-to-end V3 winner actually uses route_tile256, while K3 uses128. This is an index-domain/hardware-grid qualification, not a complete winner-by-winner numerical matrix. The quick gate additionally exercises route_tile96 with top_k6/22, including a128-bit payload-copy case. Both change mapping/limits during graph replay, test0/1/near-full/full active tile counts then empty/reactivated, poison invalid mappings with INT32_MIN, and compare all payload/SF bytes and padding canaries. Six replays/configuration; both PDL modes.

## Instruction evidence

In `evidence/gate-persistent/candidate/compile-0.ptx:51`, explicit `unroll=1` becomes `.pragma "nounroll"`. The K3 scaled SASS now has61 non-NOP sites versus85 in control (and301 in the separate R1 attempt). Its limit index becomes the one `SHF.R.U32.HI ... 0x7` at0x160, and valid mapping quotient becomes one `SHF.R.U32.HI ... 0x4` at0x230. Control begins a signed quotient/remainder correction chain at0x160 and another after mapping load at0x2c0. The divisor is still compile-time and generic; route_tile96/top_k6/22 also improve without a power-of-two branch.

The signed loop induction/termination and valid/invalid `source` join are preserved. Only known-nonnegative internal index division operands become Uint32. Existing Int64 address promotion and payload/SF vectorization are unchanged. No barriers, waits, public parameters, shape rules, or staging allocations changed.

## Boundary

This establishes exact bytes and compiler simplification, not an end-to-end speedup. The two authorized V3/K3 TP8 MXFP4x8 T16384 public-API CUPTI C-A-A-C comparisons are recorded separately under `screen/`. All source, route and frozen-winner identities must match; no external baseline or autotune rerun.
