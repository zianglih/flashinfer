# Clean W4A16 TMA gather composition

Active unstaged source: `/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/flashinfer-w4a16-tma-clean-review`.

- FC1 gathers original BF16 activations with four TMA Gather4 issuer warps in the fifth, last warpgroup. FC2 retains regular TMA and its established four-warpgroup design.
- Retain register targets144 epilogue /80 control /96 decoder /96 decoder /64 gather with96 initial registers. The112-decoder and176-epilogue redistribution variants were rejected.
- Retain activation evict-last. Cache-default effects were mostly neutral, and the apparent K3 TP4K gain had9.71% control-repeat drift; no cache-policy change is retained.
- Lane-distributed route IDs use one guarded unsigned mapping load/division per lane and four shuffles.
- Four producer arrivals are preserved. Each supplies the compile-time total B-stage byte count divided by the four gather warps. Bytes are shared by the barrier; expected-byte ownership does not need to track each warp's exact instruction subset.
- Remove the unused predicate option from the shared Gather4 primitive. No caller used it and it emitted no PTX in the previous default path.

Final source patch against fb66a27e: `26bce62f6fb27f821a7e17aad04170f304e808201bfb04e10edba08fe91619d6`. It additionally preserves the original BF16 input contract by annotating16-byte activation alignment. The source-only screen used the earlier patch `ba17cae46a33ff19a2278319829bc1134d6295cb08e234c5908f4bed00dfa98a`. The local source checkout is based on7106faf, so compare file hashes/remote measured patch rather than equating local patch hashes.

Validation: all40 selected existing exact tests passed (127.13s); all four full-model codegen captures report zero local bytes/LDL/STL. Local Ruff, AST parsing, and git diff checks pass. No sanitizer run.

The32-cell fixed-winner source comparison against b361 was launched on GPUs1/2/3. The C3 devbox disappeared during this campaign. Persistent data remains under `/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/fc1-gather-20261028/optimization-next-20261029/w4a16-tma-clean`. Completed C-A-A-C cells are valid within their original GPU UUID; any incomplete job must restart all four phases on the replacement GPU. Do not stitch phases across UUIDs.

The full104-cell harness has been configured in the sibling remote `w4a16-full` directory but was not launched. It freshly selects existing native tactics on the candidate, then compares fb66+old winners against the candidate+native winners in paired C-A-A-C order. This is implementation-plus-tactics evidence, distinct from the source-only32-cell screen. The104 tokens/model-topology cells include1/2, which remain excluded from retention summaries.

The32-cell source screen is complete: EP decode−0.02%, EP prefill−0.47%, TP decode+0.05%, TP prefill−0.35% against b361. The largest−2% to−2.8% rows have2.6–5.8% repeat drift. Instruction counts fall4–6% in the four full-model FC1 captures. All40 exact cases pass again on the final alignment16 source; offset-view checks and final104 native-tactic comparison follow. Native C++ caches and `CUTE_DSL_CACHE_DIR` are on persistent storage.
