# Early reducer preparation candidate

Base: `04c51ad94738877e67045ece949ed16cd12c6f82`. Candidate worktree: `early-reduce-prep/hashinfer`, branch `perf/megamoe-early-reduce-prep`. This is a source-validated experiment; compilation, generated-code placement, numerical checks and performance are not established by this document.

## Dependency split

```text
same-stream input stage ──> immutable local FP32 routing scores
                                  │
all five compute roles retire ──> first existing 640-thread rendezvous
                                  │
               ┌──────────────────┴──────────────────────┐
               │ retired four WGs                        │ dispatch WG
               │ compute worker/token/tile coordinates   │ grid + cross-rank
               │ prefetch first live worker's scores     │ FC2 return drain
               └──────────────────┬──────────────────────┘
                         existing 640-thread handoff
                                  │
               ┌──────────────────┴──────────────────────┐
               │ load BF16 FC2 terms + ordered FP32      │ reset counters,
               │ reduction + final BF16 store            │ publication barrier,
               │ prepare/reduce subsequent workers       │ local reset
               └──────────────────┬──────────────────────┘
                              kernel completion
```

The first rendezvous and transport drain remain inside `W4A16TokenComm.kernel_tail_drain`; non-dispatch warps return from that method after the rendezvous while dispatch remains in the drain. No additional transport phase or synchronization is needed. The second handoff remains barrier8 with 640 participants, reached once by every warp through two warp-uniform branches. BF16 combine reads are reachable only after that handoff. Dispatch starts its existing cleanup after the same handoff.

Readiness is established independently in `routing-readiness-audit.md`: the local symmetric score matrix is populated by the ordinary same-stream input stager, not by remote token pulling. Neither staging nor this MegaMoE version enables PDL. Only live local rows were staged; speculative reads of capacity padding are forbidden.

## Source organization

- `topk_reduce.py:42`: `_prepare_bf16_worker(topk_score, score_reg, worker_idx)` computes the token/hidden-tile scalar coordinates and performs the existing compile-time `topk <= 16` score prefetch. The caller supplies stable register storage and guards active workers.
- `topk_reduce.py:55`: `_reduce_bf16_worker` consumes prepared coordinates and score registers. The existing guarded body is AST-identical after removing the moved allocation/prefetch statements. It still constructs tensor views, loads BF16 terms, multiplies the first top-k term, applies ascending packed FP32 FMAs, and casts once to BF16.
- `megamoe_kernel.py:1353`: after drain returns for retired warps, the original four-WG striped map and active-output bound are computed. Only a valid first worker calls preparation. All retired warps then execute the handoff, including those with no output.
- `megamoe_kernel.py:1395`: one consumer loop handles every worker. The next worker is prepared only when valid. Scalar token/tile coordinates are loop-carried; score storage remains the same rmem tensor. No tensor-pointer loop state, first-iteration flag or duplicated unrolled reduction body is introduced.
- Dispatch warps have no reducer mapping, score allocation or score loads. They execute the same handoff and existing cleanup. The compile-time IKR/optional-output fallback still performs only the original drain/cleanup sequence.

Term/destination tensor-view construction remains in the consumer. This deliberately favors a single clean consumer over peeling the first iteration and duplicating its unrolled arithmetic. The initial combine recast is descriptor-only; it performs no memory access. Early setup explicitly covers the worker-bound calculation, striped worker assignment, token division/modulo and score loads.

## Generality and lifetime

- The mapping, worker stride and dynamic output-row bound are unchanged for all four deterministic tactics, both return modes and either CTA-cluster geometry. Every active element keeps its original unique worker and top-k order.
- Zero-row ranks and the zero-row raw thunk perform no preparation loads, combine reads or output stores, but still join both rendezvous and the full communication protocol. Invalid tail lanes likewise join the handoff without reading stale scores.
- For `topk > 16`, the preparer computes coordinates only; the prior per-k score load remains in the consumer. The experiment does not widen the score-prefetch policy.
- The first worker's score registers are live across the drain handoff, after all compute roles have retired. Existing 144/80/64/96/96 register budgets remain unchanged; scores are not carried through live GEMM/dequant work. No TMEM, shared scratch or persistent cache is added. Actual spill effects require generated-code inspection.
- Replays stage fresh live scores on the same stream. Kernel completion still includes both reducer output stores and dispatch cleanup. Existing next-invocation cross-rank gating is unchanged; independent concurrent streams sharing one workspace remain unsupported.

## Evidence and expected effect

`audit_source.py` / `source-audit.json` prove the consumer arithmetic/control body after the named moved statements, unchanged math/alignment/constructor helpers, unchanged kernel prefix through the drain call, all other kernel definitions unchanged, exact mapping/stride/bound, and 72 sampled iteration configurations including empty ranks and 16K rows. Each valid worker is prepared and consumed exactly once. Scoped pre-commit hooks passed. The independent `candidate-source-review.json` agrees. Only the two owned Python files differ from the base.

The qualified base PTX/SASS in the readiness audit places mapping and score loads after the second handoff; they are not already hidden by compiler hoisting. The candidate attempts to cover their latency with the dispatch drain. It helps only to the extent that drain latency remains to hide and the longer score live range does not cause spills or scheduling loss. Large outputs prepare only the first strided worker during drain; later workers retain ordinary serial prepare/consume execution. No speedup is claimed yet.

Before retaining the experiment, inspect actual codegen for score loads before the second handoff, every BF16 combine load after it, correct barrier participation, and resource/spill changes. Run matched numerical/sanitizer checks and the full existing 1–8192 before/after timing sweep. The second valid-worker guard may be folded into loop control by the compiler; inspect it rather than assuming zero control-flow cost.
