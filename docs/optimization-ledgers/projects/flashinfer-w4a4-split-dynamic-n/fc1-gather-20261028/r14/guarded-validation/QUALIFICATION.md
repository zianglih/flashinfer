# R14 qualification

Kernel SHA `6605aeacc09dfe16232312d17bcf00d320f4e5065e8a5ed34514b9542f6cf372`.

All **44 existing tests passed**, without skips: 32 primary cases plus 12 supplemental cases. Primary groups cover NVFP4, MX formats, functional/wrapper interfaces, and partial K/token tails. Supplemental cases exercise PDL on/off, ordinary/CLC scheduling, one/two CTA, all four quantization modes, and existing activation contracts. Source hashes remained frozen; no repository changes were required for qualification.

All **68 compiled kernels** were checked before launch against actual CUBIN SASS/ELF: 43 FC1 kernels used 168 initial registers and the intended control80/gather128/epilogue256 policy with a legal physical register pool; 25 FC2 kernels retained their original policy. Twenty per-process guard receipts include collection-only processes; only compilation-bearing receipts count toward 68.

Evidence: `../evidence/{validation,broader,register-guard}/`, `qualification-summary.json`, and `round-04.json`. The final helper adds CUBIN dumping outside test/benchmark timing. Performance qualification is separate: benchmark CUDA-dialect compilation can return a CUBIN pathname without emitting that file, so the perf guard is being adapted to query the actual loaded CUDA function rather than reusing test-only artifact assumptions.

The performance guard issue is resolved with the stable source-bound CUDA runtime resource query: helper SHA `251f758644533c98556eb8d19765345f114d165736789826ce5f9a124cf91aee`. The actual loaded executable is queried before launch; no compile/cache options are changed. `summarize_runtime_guard.py` summarizes NUM_REGS and per-thread local bytes without GPU work. SASS instruction counts remain available from qualification and dedicated codegen captures; runtime local bytes are not described as a dynamic spill count.
