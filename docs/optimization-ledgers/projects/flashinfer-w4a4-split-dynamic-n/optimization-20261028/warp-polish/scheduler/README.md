# Follower MMA bookkeeping removal

Status: isolated unstaged candidate on retained `99f4d0c27`; no GPU validation or performance claim yet. Source is `flashinfer-scheduler-polish-review`. Only `moe_swap_ab_kernel.py` changes. Public API, tactics, legacy path, W4A16 and Rubin are untouched. The canonical checkout is not modified.

The group-two MMA instructions are issued only by the leader CTA, but both CTAs currently run the MMA role's setup, metadata consumption, routed-tile arithmetic and K-loop pipeline-state updates. The follower's local metadata quorum is the only reason it must continue this bookkeeping. This candidate makes that quorum reflect actual owners and skips the follower MMA role completely. It is an ownership invariant for two-CTA MMA, not a model, dtype or problem-size policy.

| CTA | Metadata consumers | Arrival count |
|---|---|---:|
| Leader / one-CTA | Weight, activation, MMA, four epilogue warps | 224 |
| Follower | Weight, activation, four epilogue warps | 192 |

The existing `PipelineAsync` metadata ring is CTA-local: neither producer nor consumer sets a remote mask. Its count is now `32 * (6 + Int32(cta_rank == 0))`. The installed CuTe 4.8 helper explicitly accepts `Union[int, Int32]` cooperative-group sizes, forwards a Thread group's size without conversion, and initializes each local barrier from elected warp0 using that count. The existing init fence and cluster join order initialization before consumption. See the captured `optimization-20261027/warp-specialization/installed-helpers.py:98`, `:139`, `:343`, and `sdk48-pipeline-source.json`. Compilation still needs to verify lowering of the runtime uniform count.

One outer MMA-role leader predicate replaces four inner leader guards (accumulator acquire, K body, accumulator commit, tail). The leader body is AST-identical after these guards and the exit wait are normalized. Both MMA and scheduler roles execute their common delayed PDL wait after dispatch, including the now idle follower MMA warp. Weight's own delayed wait remains before its producer-exit publication. All 256 physical threads still participate in TMEM allocation/retrieval and final CTA joins; two-CTA deallocation handshakes are unchanged. One-CTA work is unchanged apart from guard/count lowering, which must be checked in codegen and the screen.

## Required synchronization retained

- Operand ring: both TMA roles must announce each stage; leader waits for both operands/scales, issues group-two S2T/MMA, then releases the shared slot to both CTAs. Follower activation/weight producers remain active.
- Accumulator ring: leader alone issues full completion; both CTAs' epilogues read their TMEM partition and contribute the existing 256-thread empty quorum.
- CLC response ring: both scheduler warps still consume the multicast response, including terminal response, and contribute 32 arrivals per CTA. The leader tail drains the peer's remote acknowledgement before teardown.
- Metadata ring: all remaining local consumers copy fields into registers before release. Every active consumer still acknowledges the terminal sentinel; the final CTA join drains it. There is no unnecessary new metadata producer tail.
- Static schedule: no metadata ring exists; follower MMA setup/tile/K bookkeeping can be skipped directly. Both TMA and epilogue owners retain the existing persistent work sequence.
- PDL: activation and epilogue retain their payload waits. Weight and scheduler may use already-published routing; the leader MMA sees payload only through operand-full acquire. Deferred-role exit waits and publication ownership remain intact.

## Other audit conclusions

The CLC cancellation currently occurs only after acquiring space for the current metadata item. Moving the query before that acquire can overlap independent work, but it also reserves another work item while all metadata slots are full. This exact direction was already tried and rejected in the local ledger (`perf-general-20261026/clc-request-overlap` and `scripts/clc_elected_owner_20261026/freeze-v1-elect-context/protocol-review.md`). No repeat is justified without current traces showing the dependency has become limiting. Likewise, a single elected scheduler owner was previously tried; it adds reconvergence and did not establish a benefit. The full-warp CLC response contract remains.

FlashMLA uses this same asymmetric ownership principle: `references/flashmla/csrc/cuda_kernels/sm100/prefill/sparse/fused_norm_rope_attn_rope_cast_fwd/core_attn/kernel.cuh:1022` enters its entire MMA role only on CTA0, and `config.h:193` counts only that issuing thread in its working-thread quorum. Its CLC queue is a different protocol, so this is an ownership precedent rather than a reason to copy its barrier counts.

The static path performs per-role routing reads but avoids a new shared queue/barrier. Earlier centralized static-metadata lookahead was slower (`scripts/scheduler_experiment/README.md`), so this candidate does not introduce it. CLC metadata arithmetic, three-field loads, and early register-copy release remain unchanged. Unused return fields can be removed by compile-time dead-code elimination; a source rewrite alone is not an instruction optimization.

`verify_static.py` reproduces the leader-body and non-kernel AST checks and enumerates the per-CTA quorum. `candidate.patch` and `static-proof.json` freeze the candidate. Planned next steps are a frozen-native-tactic CUPTI screen on GPUs2–3, one/two-CTA generated-code inspection, then focused exact changing-route checks if the screen is neutral or better. No sanitizer, extra tactic axis, cache deletion or benchmark-baseline rerun is planned.
