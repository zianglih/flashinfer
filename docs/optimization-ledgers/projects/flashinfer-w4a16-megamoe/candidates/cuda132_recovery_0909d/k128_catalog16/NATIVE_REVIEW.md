# K128 native review

Saved actual CuTe/PTXAS captures for M256/N64 and M256/N128 at EP8, H7168/I2048. Both are compile-only: no kernel launch or latency measurement.

- Both use 640 threads, REG96, STACK0, LOCAL0, and no LDL/STL instructions. Redistribution remains 144/80/64/96/96 registers across the five roles.
- Both retain ACC2, B3, raw5 and scheduler depth2. N64 has six decoded stages (384 TMEM columns); N128 has four (256). Physical decoded capacity plus accumulators is 512 columns.
- K128 has eight K16 MMA instructions and 64 direct E2M1-to-BF16 instructions in the static kernel body, versus 16 and128 at K256. Its runtime K-loop count doubles to56/16; lower static instruction count alone is not a speedup claim.
- Listed SASS instructions: N64 5504→5312, N1286032→5864; non-NOP5396→5208 and5926→5754.
- Source hashes in result.json match the active K128 kernel/frontend/epilogue; dynamic_mainloop is unchanged. The additional public pipeline-wrap parameter cases do not alter the compiled kernel bytes, so the capture remains applicable without another compilation.

Machine-readable details are in native-review.json. Numerical correctness and full catalog16 AUTO are separate subsequent checks.
