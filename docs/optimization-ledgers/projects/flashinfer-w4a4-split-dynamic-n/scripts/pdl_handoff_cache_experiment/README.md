# Paired FC2 output-handoff L2 priority

Unretained experiment in `flashinfer-pdl-handoff-cache-review`, independent base aab93f854. Four unstaged files are pinned in `manifest.json`. Adjacent control is frozen `flashinfer-pdl-allthread-review` (core adcc6506, prepare a3b0042), with its exact two dirty files truthfully verified. Production and previous experiments are unchanged.

Only two files differ from adcc: ordinary nonfused FC2 stores use CuTe CopyR2GOp at the original vector width with L2 evict-last; the existing FC2 bulk TMA store receives the same policy. Combine's guarded expert-payload reads use coherent CopyG2ROp at 128 bits with L2 evict-first. Final output stores, routing loads, A weights, B inputs, SF, math, synchronization, allocation, and geometry are unchanged. No token threshold or new API flag. The shared combine hint also applies to W4A16. FIRST is an advisory eviction priority, not invalidation/discard.

Installed CuTe 4.7.1 CopyG2R/R2G defaults are ordinary weak coherent .ca/.wb with normal L1; the traits support a cache_policy descriptor. Universal lacks that operand. The bulk operation stays TMA. Compile-only PTX/SASS verifies actual widths, no .nc loads, policy operands, register/local-memory resources, and unchanged model-output policy before native timing.

Performance hypothesis: retain FC2 handoff until consumption, then reduce dead output's cache priority. Risk: the live output working set can exceed L2, displacing FC2 inputs; FC2 phase and full-chain both matter. Live CUDA L2 capacity is recorded, not assumed.

Method: the same actual native NVFP4 input/routing and fixed tactics, input quantization outside timing, full preparation included. T4/N16 and T16384/N256 adjacent ABA/BAB, 10 warmups and 100 cold-L2 CUDA-graph CUPTI samples per arm; exact phase/full output bytes before and after. Original observer/timing function ASTs are unchanged. Control/candidate actual preparation, core, utils, and finalizer source identities plus independent caches are verified. No primary or TRTLLM sweep and no original baseline rerun.

Commands on the existing devbox:

```sh
bash scripts/pdl_handoff_cache_experiment/run_codegen.sh
bash scripts/pdl_handoff_cache_experiment/run_pairs.sh
```

The compiler export is a fresh compile-only source/geometry check, not a claim that the exported cubins are the later timing-process objects. Broader dtype/per-token/W4A16 coverage is deferred until the bounded performance gate is useful.

## Result

Closed unretained. All exact gates passed; fullchain control/candidate T4=0.992260× and T16384=0.995215×; wide FC2=0.956949×. Complete raw medians, samples, resources and source receipts: `evidence/pdl-handoff-cache-adcc/README.md`. No additional GPU work or primary rerun.
