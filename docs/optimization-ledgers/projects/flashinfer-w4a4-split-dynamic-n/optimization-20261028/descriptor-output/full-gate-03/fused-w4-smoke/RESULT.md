# W4A16 fused-finalize compatibility smoke

**Passed all four source-paired cases** on full-gate-03: original/swap-AB weight layouts × PDL disabled/enabled. Canonicalized valid FC1 rows matched R2 exactly; final fused outputs also matched exactly in this run (maximum absolute difference 0 in every case; required tolerance was rtol=atol=1e-2).

Shape: 17 tokens, hidden256, intermediate512, four experts, top-k2; every token routed to experts0/1 so both have a full16-row tile plus one-row tail, while experts2/3 remain empty. Fixed FC1/FC2 tactic `((128,16,256),(1,1),True)`; two executions per configuration. No autotuning, sanitizer, graph replay, performance measurement, or source edits.

Existing C3 `fi-moe-sanitize-1028`, GPU1 B300, `nvcr.io/nvidia/pytorch:26.05-py3`/CUDA13.2. Paired control/candidate processes reused their existing persistent caches. Full source hashes were verified before and after each process. Wall time37.26s including both processes. `receipt.json` records exact source hashes, commands, GPU UUID, timings, and raw result objects; `control/stdout.log` and `candidate/stdout.log` contain raw output.

This confirms the unchanged fused FC2 path still compiles and operates with descriptor-based FC1 for these boundary inputs; broader activation/tactic/graph coverage remains the separate gate's responsibility.
