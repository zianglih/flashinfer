# V9 cluster-width dispatch code generation

V9 produces separate activation K loops for physical cluster4 and cluster2. The four captured specializations cover N128/N192 and top-k3/8; all use 128 registers with zero stack or local-memory spills. Top-k3 and top-k8 have identical loop opcode counts. The [JSON report](CODEGEN_BRANCH_HOIST.json) preserves complete counts, branch instructions, line/address ranges, resource reports, and artifact hashes. Regenerate it with `python3 experiments/gather4/analyze_branch_hoist_codegen.py` from the project root.

Counts below isolate each emitted K loop. Earlier v6/cache48 counts are the modeled instruction sites visited by each physical cluster width after skipping the width-guarded suffix blocks. V9 counts its separate loops directly. These include issuer-condition branches and predicated instructions; they are neither measured executed instructions nor cycle counts. Index setup outside K and out-of-line barrier polling are excluded. H7168/K256 executes 28 K iterations per routed tile.

| Route N | Physical cluster | V6 visited sites | Cache48 visited sites | V9 loop sites | Reduction vs cache48 | Gather4 per K tile |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 128 | preferred4 | 303 | 312 | 262 | 16.03% | 32 |
| 128 | fallback2 | 534 | 575 | 485 | 15.65% | 64 |
| 192 | preferred4 | 372 | 446 | 358 | 19.73% | 48 |
| 192 | fallback2 | 725 | 823 | 714 | 13.24% | 96 |

| Route N | Physical cluster | Variant | SHFL | R2UR | R2UR.FILL | UMOV | Branch sites | LDL/STL |
| ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 128 | preferred4 | cache48 | 0 | 32 | 7 | 128 | 9 | 0/0 |
| 128 | preferred4 | v9 | 0 | 29 | 9 | 120 | 5 | 0/0 |
| 128 | fallback2 | cache48 | 16 | 64 | 9 | 257 | 9 | 0/0 |
| 128 | fallback2 | v9 | 16 | 51 | 6 | 197 | 8 | 0/0 |
| 192 | preferred4 | cache48 | 0 | 20 | 10 | 49 | 15 | 0/0 |
| 192 | preferred4 | v9 | 0 | 40 | 0 | 196 | 3 | 0/0 |
| 192 | fallback2 | cache48 | 48 | 88 | 10 | 85 | 15 | 0/0 |
| 192 | fallback2 | v9 | 48 | 88 | 14 | 330 | 3 | 0/0 |

For N192, loop separation removes the repeated width guards and reduces total sites, while instruction selection shifts toward UMOV. Counting only SHFL or R2UR would miss this tradeoff. `R2UR.FILL` and matching `MOV.SPILL` transfer between uniform and general registers; neither denotes local-memory traffic here. All V9 Gather4 sites are unpredicated. N128 still has issuer-condition branches, so branch counts do not fall to zero when cluster-width guards disappear.

Exact top-k8 loop ranges in `evidence/gather4/codegen-v9-k7168`:

| Specialization | Physical cluster | Address range | SASS lines |
| --- | ---: | --- | --- |
| `ptx-n128-c4-k7168-topk8/fc1.sass` | preferred4 | `0x6230`–`0x7280` | 3149–3671 |
| `ptx-n128-c4-k7168-topk8/fc1.sass` | fallback2 | `0x76a0`–`0x94e0` | 3803–4771 |
| `ptx-n192-c4-k7168-topk8/fc1.sass` | preferred4 | `0x8d40`–`0xa390` | 4527–5241 |
| `ptx-n192-c4-k7168-topk8/fc1.sass` | fallback2 | `0x6070`–`0x8d00` | 3093–4519 |

The two loops have 96 static Gather4 sites in total for N128 and 144 for N192. Only one physical-width loop executes for a routed tile, so those totals do not represent additional data transfers. Dynamic requests remain 32/64 and 48/96 per CTA per K tile for preferred4/fallback2.

The [V9 probe](probes/v9-branch-hoist/PROBE_RESULTS.md) selects ordinary cluster2 at every measured token count, with complete active-token records identical to V7. T16384 improves from V7's 1233.5945 µs to 1183.9775 µs; T4096 remains 328.2270 µs versus the reused baseline's 301.1061 µs geometric mean. These single-sweep differences do not demonstrate a benefit from selecting mixed clusters. Uniform cluster2 V9 SASS is not captured in this report, and temporal drift is not bracketed by a fresh baseline. A bounded runtime-N skip variant is the next experiment.

The codegen geometry reports do not record source hashes. This report preserves their artifact hashes and separately records the V9 benchmark's source manifest; it does not claim a cryptographic source-to-cubin binding. Raw codegen files and the earlier `CODEGEN_INDEX_COMPARISON.md/json` remain unchanged.
