# Early raw-slot release native admission

PASS on actual direct N64/N128 fixtures, frozen3b42507e. Original82882 and downloads7113/98820 exited0. Both performed one actual compile and zero kernel launches/allocations/collectives.

| Geometry/phase | Final STTM issue | Raw release | TMEM fence | Decoded-full publication |
|---|---|---|---|---|
| N64 FC1 |7020|7040|7050|7060|
| N64 FC2 |8040|8060|8070|8080|
| N128 FC1 |6f40|6f60|6f70|6f80|
| N128 FC2 |7f60|7f80|7f90|7fa0|

All four raw arrivals have waitmask0 (encoded highword0003e200081004ff). The retained TMEM fence writes dependency2 and decoded-full arrivals wait on mask4. Raw release therefore precedes completion without an encoded equivalent completion wait. Final stores consume register fragments; all payload-producing shared loads precede their store issue. Actual PTX lines133/134/135 map raw mbarrier arrival, wait::st.sync.aligned, decoded mbarrier arrival respectively. The last store issue and designated signaling predicate remain warp coherent under the separately reviewed source protocol.

Resource reports remain REG96/640, STACK0, LOCAL0, dynamic shared200064/230784, grid[2,1,74], and two decode WGs. Comparison JSONs and original PTX/SASS/results sit beside the bound execution records. Source review independently passed all original multicast arrivals/stage-state/tail obligations and exact expansion of the split default TMEM/SMEM completion hook. These native fixtures cover direct Mega return only; no split or reuse native result is claimed.

This admission permits the unchanged8/32 numerical cohort under root authorization. It does not claim numerical success or speedup.
