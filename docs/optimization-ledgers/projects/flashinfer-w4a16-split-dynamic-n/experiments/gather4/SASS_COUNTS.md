# Gather4 v3 versus v4 issuing cost

Read-only disassembly audit on October 25, 2026. Exact file hashes, all opcode counts and loop ranges are in `SASS_COUNTS.json`. No profiler or GPU run was performed.

The v3 file is the original project-root `evidence/gather4/ptx-topk8/fc1.sass`, not the later `codegen-v3` package. The v4 file is `experiments/gather4/codegen-v4/evidence/gather4/codegen-v4/ptx-topk8/fc1.sass`. The examined specialization is M256/N128/K256, cluster2, top-k8; v4's saved synthetic launch uses K256 and PDL off. Counts below describe an activation K-loop for one CTA.

| Instruction | v3 static sites | v3 modeled executions | v4 static/executed body |
| --- | ---: | ---: | ---: |
| Gather4 | 4 | 64 | 64 |
| ELECT | 5 | 65 | 1 |
| R2UR / R2UR.BROADCAST | 20 | 320 | 64 |
| SHFL | 0 | 0 | 64 |
| BRA.U.ANY | 4 | 64 | 0 |
| PLOP3 | 12 | 132 | 0 |
| UMOV | 11 | 56 | 174 |
| UIADD3 | 6 | 6 | 70 |
| Total instructions | 106 | 751 | 454 |

The v3 activation loop spans `0x5420–0x5ab0`, source lines 2699–2909. It contains four scalarization loops: `0x55c0–0x5650`, `0x56f0–0x5790`, `0x5830–0x58d0`, `0x5970–0x5a10`. Each loop repeatedly elects an active lane, broadcasts four row coordinates and a destination to uniform registers, issues one Gather4, removes that lane from the pending predicate, then branches while any lanes remain. Sixteen active row-owner lanes imply sixteen iterations per scalarization loop. The model counts all static instructions once and adds fifteen extra passes through each of these four loops.

This explains why v3's four PTX/SASS Gather4 sites do not represent four hardware requests: the modeled count is the same 64 requests as v4, surrounded by substantially more control and broadcast work. The model includes the single barrier election and excludes out-of-line barrier polling. Divergent branch paths and runtime stalls are not measured, so 751 versus 454 is an instruction model, not a cycle estimate.

The v4 activation loop spans `0x5430–0x7080`, lines 2701–3607. Its 64 requests are explicitly unrolled. PTX repeats row-group elections, but ptxas removes those elections from the Gather4 issue body. The only remaining ELECT belongs to the producer barrier arrival. Further removal of source-level elections alone therefore has no demonstrated SASS benefit.

V4 still repeats 64 SHFL and 64 R2UR operations per K256 iteration even though row IDs do not change across K. It also has 174 UMOV and 70 UIADD3 instructions. Many UMOVs appear to pack repeated descriptor, barrier, channel and row operands into the aligned uniform-register sets required by TMA; that is an interpretation of the operands, not a measured stall diagnosis. Hoisting or directly loading issuer-owned indices must be evaluated against register pressure.

For an equivalent H7168 specialization, 28 K256 iterations imply 1,792 Gather4, 1,792 SHFL and 1,792 R2UR per CTA work tile in v4. This is an extrapolation from emitted code, not an instruction measurement of the full benchmark.
