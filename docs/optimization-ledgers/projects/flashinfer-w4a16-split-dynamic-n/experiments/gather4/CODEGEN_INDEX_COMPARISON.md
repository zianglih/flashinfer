# Gather4 index-caching code generation comparison

**Cache48 reduces the fixed-cluster N192 K-loop substantially, but does not reduce N128 or mixed-cluster loop size. Mixed row-count guards remain inside the K loop. Full96 introduces local-memory spill traffic in mixed N192.** These are disassembly findings, not benchmark or cycle measurements.

## Scope and counting

All 24 specializations are M256/K256 with H7168, N128 or N192, requested cluster 2 or preferred cluster 4/fallback 2, and top-k 3 or 8. Evidence is under project-root `evidence/gather4/codegen-{v6,cache48,full96}-k7168/`. The supplied `codegen-index-manifest.json` records source hashes and CuTe bundled ptxas 13.3.27/PTX 9.3/sm103a. Every ptxas log reports 128 registers.

Counts cover the **activation Gather4 K-loop only**: the smallest backward branch enclosing all Gather4 sites, including its barrier-arrival path and loop control. They exclude index-cache setup outside K, unrelated weight/MMA/epilogue code and out-of-line barrier polling. There are 28 K256 iterations at H7168. No full-function instruction count is substituted for this loop. Exact address/line ranges, opcode counts, branch blocks, compiler reports and file hashes are in `CODEGEN_INDEX_COMPARISON.json`; `analyze_index_codegen.py` reproduces them.

`R2UR` and `R2UR.FILL` are counted separately. The observed `MOV.SPILL Rn, URm` and matching `R2UR.FILL URm, Rn` move between uniform and ordinary registers; they are not local-memory stores/loads. `LDL`/`STL` below identify actual local-memory instructions.

## Emitted K-loop sites

These are static instruction sites in the loop, including predicated instructions and both mixed-cluster branches. `Creq=4` therefore is not an executed-path total. All branch opcodes, including the loop backedge and barrier branch, count in BRA.

| Variant | N | Creq | Top-k | Sites | Gather4 | SHFL | R2UR | R2UR.FILL | UMOV | BRA | LDL/STL |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| v6 | 128 | 2 | 3 | 454 | 64 | 64 | 64 | 0 | 174 | 3 | 0/0 |
| cache48 | 128 | 2 | 3 | 482 | 64 | 16 | 56 | 10 | 226 | 4 | 0/0 |
| full96 | 128 | 2 | 3 | 488 | 64 | 0 | 46 | 8 | 270 | 4 | 0/0 |
| v6 | 128 | 2 | 8 | 454 | 64 | 64 | 64 | 0 | 174 | 3 | 0/0 |
| cache48 | 128 | 2 | 8 | 480 | 64 | 16 | 56 | 9 | 226 | 4 | 0/0 |
| full96 | 128 | 2 | 8 | 492 | 64 | 0 | 46 | 8 | 274 | 4 | 0/0 |
| v6 | 128 | 4 | 3 | 534 | 64 | 32 | 62 | 4 | 232 | 8 | 0/0 |
| cache48 | 128 | 4 | 3 | 575 | 64 | 16 | 64 | 9 | 257 | 9 | 0/0 |
| full96 | 128 | 4 | 3 | 587 | 64 | 0 | 61 | 35 | 255 | 8 | 0/0 |
| v6 | 128 | 4 | 8 | 534 | 64 | 32 | 62 | 4 | 232 | 8 | 0/0 |
| cache48 | 128 | 4 | 8 | 575 | 64 | 16 | 64 | 9 | 257 | 9 | 0/0 |
| full96 | 128 | 4 | 8 | 587 | 64 | 0 | 61 | 35 | 255 | 8 | 0/0 |
| v6 | 192 | 2 | 3 | 1012 | 96 | 96 | 140 | 67 | 380 | 3 | 0/0 |
| cache48 | 192 | 2 | 3 | 690 | 96 | 48 | 76 | 13 | 323 | 3 | 0/0 |
| full96 | 192 | 2 | 3 | 654 | 96 | 0 | 166 | 8 | 256 | 3 | 0/0 |
| v6 | 192 | 2 | 8 | 966 | 96 | 96 | 140 | 46 | 373 | 3 | 0/0 |
| cache48 | 192 | 2 | 8 | 682 | 96 | 48 | 76 | 13 | 315 | 3 | 0/0 |
| full96 | 192 | 2 | 8 | 654 | 96 | 0 | 166 | 8 | 256 | 3 | 0/0 |
| v6 | 192 | 4 | 3 | 725 | 96 | 64 | 109 | 5 | 65 | 19 | 0/0 |
| cache48 | 192 | 4 | 3 | 823 | 96 | 48 | 88 | 10 | 85 | 15 | 0/0 |
| full96 | 192 | 4 | 3 | 1016 | 96 | 0 | 267 | 10 | 138 | 3 | 50/1 |
| v6 | 192 | 4 | 8 | 725 | 96 | 64 | 109 | 5 | 65 | 19 | 0/0 |
| cache48 | 192 | 4 | 8 | 823 | 96 | 48 | 88 | 10 | 85 | 15 | 0/0 |
| full96 | 192 | 4 | 8 | 1016 | 96 | 0 | 267 | 10 | 138 | 3 | 50/1 |

## Preferred and fallback paths in the mixed kernel

The following **modeled visited-site counts** follow the disassembled row-guard branches for physical cluster 4 versus 2, keeping the producer-barrier path. Counts include remaining predicated-off instructions; they are not active-thread instruction or cycle counts. Actual runtime placement proportions were not collected. Top-k 3 and 8 have identical counts in this table.

| Variant | N | Physical cluster | Visited sites | Effective Gather4 requests | SHFL | R2UR | R2UR.FILL | UMOV | BRA |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| v6 | 128 | 4 | 303 | 32 | 0 | 30 | 4 | 136 | 8 |
| v6 | 128 | 2 | 534 | 64 | 32 | 62 | 4 | 232 | 8 |
| cache48 | 128 | 4 | 312 | 32 | 0 | 32 | 7 | 128 | 9 |
| cache48 | 128 | 2 | 575 | 64 | 16 | 64 | 9 | 257 | 9 |
| full96 | 128 | 4 | 345 | 32 | 0 | 38 | 25 | 127 | 8 |
| full96 | 128 | 2 | 587 | 64 | 0 | 61 | 35 | 255 | 8 |
| v6 | 192 | 4 | 372 | 48 | 16 | 41 | 5 | 29 | 19 |
| v6 | 192 | 2 | 725 | 96 | 64 | 109 | 5 | 65 | 19 |
| cache48 | 192 | 4 | 446 | 48 | 0 | 20 | 10 | 49 | 15 |
| cache48 | 192 | 2 | 823 | 96 | 48 | 88 | 10 | 85 | 15 |
| full96 | 192 | 4 | 1016 | 48 | 0 | 267 | 10 | 138 | 3 |
| full96 | 192 | 2 | 1016 | 96 | 0 | 267 | 10 | 138 | 3 |

Full96 mixed N192 visits 96 predicated Gather4 sites on either path; only 48 requests are active for physical cluster 4. This is why its preferred-path site count remains 1016 instead of halving. The other preferred-path Gather4 site counts equal their effective requests. Multicast destinations per request are 2 for physical cluster 4 and 1 for fallback 2, so halved per-CTA requests do not mean halved delivered activation bytes.

## What changes and what remains hot

- **Fixed cluster 2, N128:** cache48 removes 48 SHFL sites but increases total sites from 454 to 480 (top-k 8) or 482 (top-k 3). UMOV rises 174→226; ordinary R2UR falls 64→56, while 9/10 register spill/fill pairs appear. Full96 removes all 64 shuffles but grows the loop to 492/488 sites. There is no instruction-count reduction to claim for N128.

- **Fixed cluster 2, N192:** cache48 removes 48 SHFL, lowers R2UR 140→76 and sharply reduces register spill/fill pairs: 46→13 (top-k 8) or 67→13 (top-k 3). Total sites fall 966→682 (-29.4%) and 1012→690 (-31.8%). Full96 reaches 654 sites without local-memory spills, but shifts work into 166 R2UR and 99 VIADD sites. Cache setup cost outside K is excluded and timing must decide retention.

- **Mixed N128:** cache48 removes 16 fallback shuffles, but preferred-path visited sites grow 303→312 and fallback 534→575. Cache48 increases UMOV and register moves; full96 grows further to 345/587. Preferred N128 already had zero hot-loop shuffles in v6.

- **Mixed N192:** cache48 removes the preferred path's 16 shuffles, yet visited sites grow 372→446; fallback grows 725→823. One visible cause is more repeated address calculation: UIMAD 1→24 and ULEA 2→25 in the emitted body, plus additional predicate/register work. Reducing shuffles alone is not a reliable proxy for this loop's total cost.

- **Full96 mixed N192:** both top-k variants have 216-byte stack frames and 220 bytes each of compiler-reported spill stores and loads. The hot loop contains 50 local loads and 1 local store, in addition to 1016 sites and 267 R2UR. Other 22 specializations report zero stack/spill bytes. This is a distinct resource regression, despite eliminating SHFL.

## Mixed guards are inside every K iteration

For v6 N128/c4/top-k8, the K loop is `0x5f20–0x8070` (SASS lines 3051–4117). Four prefix guard branches remain at `0x5ff0`, `0x61e0`, `0x63b0`, `0x68b0`, followed by `0x7180: BRA.U UP1, 0x8000` around the fallback-only row suffix. Some prefix predicate comparisons are set before K, but their branches still recur inside K; ptxas has not split the kernel into separate fixed-width K loops.

For v6 N192/c4/top-k8, the K loop is `0x6480–0x91c0` (lines 3223–4671). Sixteen forward guard branches begin at `0x70b0` and continue through `0x8f90`; cached-prefix TMA/address operations also remain predicated. Cache48 N192 keeps 12 guarded suffix blocks inside `0x62d0–0x9630`, beginning at `0x78f0`, with predicate extraction/reconstruction in the loop. Full96 replaces these branch blocks with predication rather than eliminating the guards.

A once-per-routed-tile dispatch to constexpr cluster 4/cluster 2 row counts therefore targets real emitted guard and address work. It remains an experiment: code size, uniform-register packing, register pressure and cache setup can offset the savings. Preserve the existing before data and use measured candidate timing to decide.

## Reproduce this read-only analysis

```bash
python3 experiments/gather4/analyze_index_codegen.py
```

No GPU work, production edits, baseline reruns or historical-result rewriting occurred in this analysis.
