# W4A16 performance and shared preparation

Control: `1496b557f9b606f3a0bb36bcebf5293d3e11555a` (PR #7290 rebased onto merged #7196 and #7501). Retained and pushed: `0b7fe90151340d4fca6a5ec41a91019dde743819`.

The final four-file change shares preparation, simplifies scheduler metadata publication, specializes static M/K and fixes the compilation-cache SM-budget key. The user removed W4A16 CLC tactic doubling: original 23 tactics, tuple schema, cache extras and FC1 scheduling policy are restored. The unpublished `a2beb1f1` was amended before publication; no 46-tactic W4A16 policy was pushed.

`no-tactic-expansion/` contains the source-bound validation, commit/push/PR receipts and cleanup record. `composed23/` contains the final same-winner CAAC comparison: 1.0002x overall, 0.9993x decode and 1.0027x prefill, excluding tokens 1/2. Retain for shared implementation and instruction efficiency; no broad latency improvement is claimed. All 50 existing tests and 72 targeted checks pass. The four completed review copies were removed; helpers, evidence and persistent GPU compilation caches remain.

Earlier `composed/` and `composed-recheck/` results describe the rejected 46-tactic composition and are historical only.

Environment: existing C3 `fi-moe-nvfp4-port-1026`, 8x B300, `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2. Candidates reuse native compilation artifacts only after full native-source identity verification, with private CuTe DSL namespaces. `deploy.py` records patch/source/cache identities.

Benchmark: public `benchmarks/bench_moe_deepseek.py`, V3 EP8, V4.1-Flash EP4, K3 EP8; W4A16, PDL, no fused finalize. 10 warmups and 100 cold-L2 CUPTI graph samples. Tokens: 1,2,4,8,16,32,64,128,256,512,4096,8192,16384. Tokens 1/2 are reported but excluded from retention. Initial control runs are diagnostic; retention uses same-GPU adjacent source pairs with matched tactics or native AUTO.

Policy: preserve the original 23 tactics. CLC doubling and independent FC1/FC2 K128 choices were evaluated and rejected. No model-specific kernel thresholds. Existing exact coverage gates retained changes; broad sanitizer work remains deferred.

Rejected CLC metadata-depth trial: `clc-stage/` keeps the12-point forced-CLC CAAC evidence,24 exact replays and8 existing tests. Stage2 was mixed and slower for V3; its source review copy was removed after hash verification. The retained policy keeps one CLC metadata stage.
