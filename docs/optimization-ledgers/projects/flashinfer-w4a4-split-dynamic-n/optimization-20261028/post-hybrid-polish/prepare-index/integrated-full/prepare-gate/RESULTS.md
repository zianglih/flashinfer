# Integrated prepare R1 gate

Passed48 exact graph replays/source and8 compiled pairs onGPU7, then released GPU7 for the producer's full refresh. Source identity is33b7+b668b273 GEMM with prepare603dcdf, compared with source-identical33b7 control. Both348-file manifests are verified before and after the gate; only the prepare file differs.

| Geometry | Route tile | Static SASS sites control → R1 | Registers |
|---|---:|---:|---:|
| V3 FP8/SF32 | 256 | 91 → 68 | 32 → 32 |
| K3 FP8/SF32 | 128 | 85 → 301 | 30 → 32 |
| V3 BF16 | 256 | 52 → 38 | 28 → 30 |
| K3 BF16 | 128 | 49 → 35 | 24 → 26 |

PDL-on cases also pass with the same deltas. No spills/local-memory sites or stack bytes; all variants remain≤32 registers/thread. K3's larger static code is compiler loop unrolling, not evidence of more equivalent per-row executed work; default loop policy is intentionally preserved.

Payload/SF byte checks cover V3 route256/H7168/top8 and K3 route128/H3584/top16 plus shared BF16 representatives,4096 routed rows and hardware-sized persistent grids. Six graph replays per configuration change mappings/limits and empty/reactivate the work; invalid mappings are poisoned, and payload/SF padding is checked.

This is a prepare-only qualification. It does not independently revalidate the retained GEMM's numerical contract or claim a benchmark speedup. Full-model EP/TP timing is owned by the producer under the parent campaign. No sanitizer or autotuning in this gate.

The74-file evidence archive SHA256 is2e1a91a03e60a54ab77026cff51bdd7cecd24f79457c31bdd85180c512baa3af. See `../qualification.json` for source binding and links/hashes to original R1 and integration receipts.
