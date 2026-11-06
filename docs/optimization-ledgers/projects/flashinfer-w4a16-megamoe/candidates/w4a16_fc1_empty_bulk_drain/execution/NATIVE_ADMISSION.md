# Empty FC1 bulk-drain native admission

PASS on the actual two direct epi_warps N64/N128 fixtures compiled from3efa. Original41864 and downloads47098/45670 exited0; one compilation per fixture, zero launches/allocations/collectives.

- Both actual PTX files remove exactly the owned epilogue commit_group / wait_group.read0 pair (two bulk groups become one). The remaining token_comm.py1113/1114 commit_group/full wait_group0 is retained.
- SASS preserves BAR1 before completion publication at N64b8c0 and N128dac0. Immediately prior LDS record reads, CTA fence and scheduler-stage arrive remain; following phase branch and release flag work remain.
- Every original20 bar.sync instruction and the exact6 atom.release plus7 red.release instructions/operands remain in each PTX fixture. Actual dispatch drain SASS remains at11b70/11b80 (N64),13d70/13d80 (N128).
- Actual resources unchanged:96 registers,640 threads,STACK0,LOCAL0, grid[2,1,74], dynamic shared memory200064/230784, two decode groups. Source3efa has only the five-line epilogue deletion; kernel remains5d6d.

This bounded source/native admission permits the unchanged8/32 numerical cohort under root authorization. Both return modes are covered by that numerical cohort; these native captures are direct return only. No numerical outcome or speedup is claimed here.
