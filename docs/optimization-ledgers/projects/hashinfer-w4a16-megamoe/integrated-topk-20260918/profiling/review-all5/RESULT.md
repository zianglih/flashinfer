# All-five-WG profiling: independent early audit

Source `f5f4de65e575abb9d17571273697b84f8c198e1b`, manifest
`2cb5b1763d12e0b9734c01c5ddac5c8f2ad43f32374eb67257810c6b53b06d5b`.
Both early bundles were rehashed against their collection receipts, including
all eight reports and SQLite exports. This is read-only profiling evidence;
it does not replace numerical tests or unprofiled timing.

**The separate reducer launch is gone.** At both global128/N64/epilogue-return
and global8192/N128/dispatch-return, each of five NVTX replay intervals on each
of eight ranks contains exactly two graph-node kernels: `Bf16InputStage` and
`Sm100W4A16MegaMoEKernel`. All 80 graphs pass; no `TopkReduce` launch occurs
anywhere in either capture. Rank0 compile records contain only those two
families. Graph DOT was unavailable, so this conclusion uses actual nsys nodes.

| Rank0 artifact | Cubin REG | STACK | LOCAL | Static SASS LDL / STL |
|---|---:|---:|---:|---:|
| Baseline68eb1fe core, N64/global128 | 96 | 0 | 0 | 0 / 0 |
| Baseline separate TopkReduce | 36 | 0 | 0 | 0 / 0 |
| Integrated core, N64/global128 | 96 | 0 | 0 | 0 / 0 |
| Integrated core, N128/global8192 | 96 | 0 | 0 | 0 / 0 |

The integrated stage remains REG18/STACK0/LOCAL0 and is byte-identical to the
baseline stage. Both integrated core specializations retain the actual PTX
redistribution instructions: decrease80, increase144, decrease64; the decode
groups retain96. The five roles still total61,440 registers/CTA. No PTX local
declarations, local loads or local stores are present. These are static
codegen/allocation checks, not measured dynamic spill counters.

At N64/global128, core compile options and PTX compiler header match the
baseline: O3, maxrregcount96, NVVM CUDA13.3.27, PTX9.3, `sm_103a`. Input/weight
hashes and the complete fixed tactic also match. Static SASS instruction lines
(including compiler padding) change from 5416 core + 184 separate reducer to 5616
integrated core. This describes code size, **not executed instruction count**
or a speedup. The N128/global8192 core has 6320 such lines and is a different
specialization, so it should not be compared numerically with the N64 baseline.

**Dispatch-return uses a full outgoing-copy wait.** In the actual 8192 PTX:

- Token metadata supplies source rank/token/top-k. The peer mapper plus
  `(src_token*8+src_topk)*14336` builds destination `%rd1010`;14336 is one
  H7168 BF16 token. Local FC2 pool data supplies `%rd1008`.
- An elected lane loads local FC2 data into shared memory and waits for its
  mbarrier, then issues the shared-to-peer bulk copy at line 6314.
- The following join executes `cp.async.bulk.commit_group` at 6319 and full
  `cp.async.bulk.wait_group 0` at 6320, before pacing, the next token's scheduling
  and kernel-tail rendezvous. There is no `.read` bulk wait in this PTX.

This maps directly to the frozen `token_back_by_push` data path in
`token_comm.py:1341–1416`; it is not an unrelated input-pull wait. The retained
excerpt includes address construction, elected-lane branch, commit/full wait,
subsequent scheduling and tail entry.

Exact hashes, all 80 replay checks, launch-resource fields and PTX instruction
locations are in `nsys-codegen-audit.json`; the dispatch excerpt is
`dispatch-token-return-ptx-excerpt.txt`. Early bundles include rank0 codegen
only, so all-rank cubin equality is not yet claimed. Full NCU metric availability,
dynamic local-memory traffic and occupancy diagnostics remain pending.
