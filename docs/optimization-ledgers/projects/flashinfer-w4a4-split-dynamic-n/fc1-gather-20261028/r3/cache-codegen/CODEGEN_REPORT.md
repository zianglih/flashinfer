# R3 codegen diagnostic

**No register/spill catastrophe was found.** All8 captured FC1/FC2 cubins report zero local and stack storage, with no LDL/STL instructions. FC1 uses70–88 registers. The capture covers V3 EP8 at8/16384 tokens for MXFP8 and MXFP4x8, with the same frozen winners and routes as the R3 screen.

| Tokens | Mode | Phase | N / CTA | CLC | K steps / stages | Regs | Stack / local | wait_group0 sites |
|---:|---|---|---|---|---|---:|---|---:|
| 8 | MXFP8 | FC1 | 32 / 1 | True | 8 / 5 | 78 | 0 / 0 | 2 |
| 8 | MXFP8 | FC2 | 32 / 1 | True | 8 / 5 | 74 | 0 / 0 | 0 |
| 8 | MXFP4x8 | FC1 | 32 / 2 | True | 4 / 11 | 74 | 0 / 0 | 4 |
| 8 | MXFP4x8 | FC2 | 32 / 1 | True | 4 / 10 | 72 | 0 / 0 | 0 |
| 16384 | MXFP8 | FC1 | 256 / 2 | False | 4 / 6 | 88 | 0 / 0 | 2 |
| 16384 | MXFP8 | FC2 | 256 / 2 | False | 4 / 5 | 106 | 0 / 0 | 0 |
| 16384 | MXFP4x8 | FC1 | 128 / 2 | False | 4 / 9 | 70 | 0 / 0 | 2 |
| 16384 | MXFP4x8 | FC2 | 128 / 2 | False | 4 / 7 | 112 | 0 / 0 | 0 |

The relevant FC1 sequence is visible in `evidence/candidate-01/capture/002-fc1.ptx:848–872`: scale cp.async → commit_group → elected Gather4 payload → reconverged wait_group0 → async.shared fence → release.cluster arrival. The final wait/fence/arrival is outside the Gather4 elected-thread branch. Thus all128 gather threads perCTA execute the local wait and publication for eachstage; in two-CTA mode the leader barrier receives256 arrivals. SASS confirms `LDGSTS`, `LDGDEPBAR`, `DEPBAR.LE SB0,0`, `FENCE.VIEW.ASYNC.S`, and `SYNCS.ARRIVE` in that order. This supports testing the R4 nonblocking local-completion/relay design; it does not independently establish the fraction of slowdown caused by the sequence.

The printed wait-site counts include static loop unrolling. They are not executed counts. `cuobjdump` static SHARED=1024 excludes dynamic shared memory. Uniform-register fill instructions are not local-memory spills.

Source kernel `c259b6cb4b01037def6f1b8d4be09221f7abc36dd76e910660ced0179daebf75`, all513 files and full patch verified before/after. The42-file archive SHA256 is `bb7b3aecf3dd7401dcda1afc7bf01cda636aae0bca797eaf2ea833740ff0607e`. `source-winner-route-bindings.json` asserts equality against `r3/perf/ep-v3-mxfp/1-candidate/results.json` for all4 cells. Private winner-cache copies were unchanged; no autotune was run.

CUPTI diagnostic samples are retained in raw observer output but must not be published as retention measurements. No control compilation was needed because the requested catastrophic-spill condition was absent. GPU7 was released immediately after capture.
