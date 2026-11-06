# Native-TMEM FC1 compile-only gate

Candidate kernel SHA `6a48e87c41f2635f44e42d2c4afeaccc3b87d37be7d6b1be33ea8b685c0a073b` on9037. Both arms compile13 representative kernels without launching them. All resource guards pass: FC1 REG168, STACK/LOCAL0, unchanged120/128/256 role budgets and dynamic shared allocation. Both FC2 cubins are byte-identical.

| Case | Whole-kernel non-NOP | Delta | Epilogue reachable non-NOP | Delta |
|---|---:|---:|---:|---:|
|nv-n16|1252 → 1304|+52|387 → 436|+49|
|nv-n128|1500 → 1606|+106|426 → 532|+106|
|nv-n256-relu|1785 → 1915|+130|487 → 617|+130|
|nv-m512-situ|5393 → 6021|+628|4160 → 4788|+628|
|pt-n16-geglu|1352 → 1198|-154|486 → 333|-153|
|pt-n256-relu|1676 → 1797|+121|378 → 499|+121|
|pt-n128-situ|1733 → 1764|+31|660 → 691|+31|
|mx4-n128|1729 → 1835|+106|439 → 545|+106|
|mx8-n256-relu|4092 → 4954|+862|2552 → 3417|+865|
|mx8-n16-situ|1743 → 1793|+50|632 → 682|+50|
|mx8-m512-geglu|4829 → 5514|+685|3239 → 3925|+686|
|fc2-nv|2521 → 2521|+0|0 → 0|+0|
|fc2-mx|1833 → 1833|+0|0 → 0|+0|

Static instruction growth is a real cost, especially wide unrolled MX/relu cases. The candidate replaces epilogue TMEM stores/reloads with shuffle/select/store issue. These static counts do not establish performance. The epilogue CFG includes direct helper calls; no unresolved indirect transfers remain. All per-op deltas and binary hashes are in `codegen-analysis.json`.

Scale ownership matches the planned cost:7 reduction SHFL+14 FSEL per32-token fragment, then8 indexed scale broadcasts. Existing SF32 shared read/write/barrier counts do not increase. Packed transpose shuffles scale with output width. N16 constant geometry prunes unused token-half output work without added dispatch.

The r1 candidate failed before compiling its first kernel due a Uint64/Uint32 conditional mismatch in mask arithmetic. r2 explicitly casts both packed-word branches to Uint32; the bit-level CPU proof still applies. Frozen r1 control codegen was reused for r2. Both arms and the r1 error are in the hash-verified local archive.

The original39-case gate was interrupted by devbox reclamation at19 progress markers/38captured kernels. Its archive is preserved unchanged. The replacement strict-zero gate completed25 exact cases, then blocked a pre-existing M512/N128/K8 MXFP4x8 spill before launch. Matched control proved the same168B stack/21LDL+21STL sites. A fresh full paired gate then passed39/39cases in both arms,76compiled kernels perarm, with each candidate kernel bounded by the matching retained test/geometry resources. M512/K8 MXFP4x8 andMXFP8 are the only two pre-existing local cases; neither grows. Both additional MXFP4x8/MXFP8 ReLU2SF32 cases passed with four zero-local kernels.

All37FC2PTX pairs are identical.35FC2CUBIN pairs are byte-identical; two differ only by a proven UR16/17↔UR18/19 permutation across12MMA descriptor instructions, with identical remaining instructions and resources. Do not claim all FC2 binaries are byte-identical. See paired-exact-analysis.json.

The source remains frozen6a48. The separately predeclared14-cell fixed-winner CAAC screen follows these gates; no performance inference is made from compile or exact-test timings.
