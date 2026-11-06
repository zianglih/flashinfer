# K3 deterministic combine: source and historical audit

Read-only review on 2026-10-08. No GPU calls, correctness tests, repository modifications, or claims of current K3 spills. The deterministic fused combine stays active, with no fused TMA/FC2 reduction. This audit concerns the existing FP32-weighted combine (`apply_topk_in_fc1=False`); moving score placement is a different numerical contract and is not proposed.

## Most useful narrow probe

The prepared [K16 scalar-score patch](evidence/candidates/k16-scalar-scores.patch) changes only `self.prefetch = self.num_topk <= 16` to `< 16`. **Exactly K16** moves from whole-row early score prefetch to the existing per-route score-load path already used at K>16. K1–15 and K17–32 retain their previous paths. The [source hash and qualification boundary](evidence/candidates/k16-scalar-scores-source-audit.json) are recorded. This is a perf-first probe, not a recommendation to retain the change.

Why it is a reasonable isolated K3 question: current K16 carries sixteen FP32 scores per active worker across the retirement/drain barriers and into a fully unrolled16-route reduction. The K8 workload carried only eight. Loading each score near its use can shorten that live state without widening payloads, changing worker ownership, altering register targets, changing an output value's reduction order, or adding synchronization. The tradeoff is losing early load overlap and potentially replacing four vector score loads with more scalar instructions. The compiler can still hoist/combine loads, so source liveness alone does not establish register or instruction savings.

The source-level numerical argument is narrow: the same immutable score element is read, the same BF16 term is expanded, the first route still uses FP32 multiplication, routes1–15 still use ordered packed FP32 FMA, and the same final BF16 conversion/store is used. Every existing drain and barrier remains. The score buffer is prepared by dispatch before these consumers; deferring a read to the reduction does not make it earlier than publication. The fallback code already performs `score_reg[k] = topk_score[token_idx,k]` for every constexpr route. This is source reasoning, not native compilation or numerical qualification. [Reducer](flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/topk_reduce.py:22); [retirement and barriers](flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py:1506).

If this isolated path is slower, do not stack further score-lifetime changes blindly. A more involved eight-score-at-a-time vector prefetch could preserve128-bit score loads while limiting early live values, but it needs a fresh native code comparison to show that ptxas has not simply recreated the original schedule. A runtime route loop is lower priority: dynamic indexing can turn the register array into local storage, introduce mux/control work, or lose the useful unrolled load overlap.

## What K16 changes

`hidden_per_thread=8` gives four independent packed FP32 accumulation chains per worker. The route loop is entirely constexpr-unrolled; there is no tree reduction. K3 D3584/K16 has448 workers per local token, versus GLM5 D6144/K8's768. Source operation counts are:

| Per eight-output worker | K8 | K16 |
|---|---:|---:|
| BF16 route payload copies | 8×128 bits | 16×128 bits |
| FP32 score values prefetched | 8 | 16 |
| First packed FP32 multiplies | 4 | 4 |
| Subsequent packed FP32 FMAs | 28 | 60 |
| BF16→FP32 element expansions | 64 | 128 |
| Final output copy | 128 bits | 128 bits |

These are source counts, not a current SASS census. At whole-token scale, K3 combine payload is112 KiB versus GLM5's96 KiB: K doubles, while D is smaller. There is16.7% more route payload per token, not twice as much. Score loads are heavily shared by neighboring hidden workers; their logical byte count must not be presented as DRAM traffic.

Each lane owns sixteen scores, eight FP32 accumulators, route temporaries, and addresses in the K16 weighted path. Compiler scheduling may make multiple route vectors live simultaneously. The prior K8 disassembly already issued seven of eight LDG128 operations before the first multiply, so additional prefetch is not an established missing opportunity. K16 doubles the available independent load work but also the possible live payload. Without a current compiled K16 reducer, neither spilling nor a lack of ILP is demonstrated.

## Which retired warps actually execute K3 decode combine?

The first two grid-wide strips belong to decoder WG3/WG4, then epilogue WG0 and control WG1. Dispatch WG2 drains/cleans up and does not reduce. With148 SMs and128 threads per strip, each strip contains18,944 workers; all four strips contain75,776. Runtime register targets remain decoder96/96, epilogue144, control80, dispatch64. No tail-register restoration is performed.

For balanced EP8 K3 decode:

| Global tokens | Local tokens per active rank | K3 workers/rank | Participating reducer roles |
|---:|---:|---:|---|
| 4 | 0 or1 | 0 or448 | First decoder WG only |
| 8 | 1 | 448 | First decoder WG only |
| 32 | 4 | 1,792 | First decoder WG only |
| 128 | 16 | 7,168 | First decoder WG only |
| 256 | 32 | 14,336 | First decoder WG only |
| 512 | 64 | 28,672 | Both decoder WGs only |

All these workers execute exactly one reducer iteration. Therefore the80-register control role and64-register dispatch role do not explain a K3 decode payload spill. Any such spill would have to be established in the96-register decoder participants and their cross-role live state. Prefill reaches the other reducer roles and continuation iterations; do not generalize the decode role result to those rows. [Worker assignment](flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py:1036); [role preparation/reduction](flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py:1620).

## Prior experiments and what not to repeat

- **Keep LDG128.** Widening the payload originally produced40-byte stack and10 LDL/17 STL sites. Those spills were in the combine tail, including the96-register decoder role; restoring the control role alone did not solve them. Later spill-free wide-payload and score-only variants still lost all12 focused pooled comparisons. This is stronger negative evidence than “LDG256 spilled once.” [Final decision](../hashinfer-w4a16-device-trace/optimization/alignment256-20260926/FINAL_DECISION.md), [PC/role spill audit](../hashinfer-w4a16-device-trace/optimization/alignment256-20260926/DIAGNOSTIC_SPILL_LEDGER.md).
- **Do not restore all tail roles to96 without evidence.** Both original-LDG128 register-restoration controls were spill-free but slower in all four focused rows. K3 decode does not use the80-register role anyway. Same sources above.
- **Packed BF16 expansion was already tested.** The old candidate reduced observed K8 expansion work from96 to64 integer instructions without a retained latency win. K16 could double the nominal saving, but current K16 expansion SASS has not been inspected. This is a conditional secondary direction only if generated conversion work is still excessive, not an untried general optimization. [Source and exact conversion proof](../hashinfer-w4a16-megamoe/integrated-topk-20260918/combine-packed-bf16-expand/SOURCE_REVIEW.md), [batch outcomes](../hashinfer-w4a16-megamoe/integrated-topk-20260918/ROUND_SUMMARY_20260919.md).
- **Width4 was rejected on the older weighted K8 path.** K3's smaller D gives fewer active worker CTAs and its K16 chains are longer, so width4 has a distinct utilization rationale, but it also doubles worker/score preparation and loses LDG128. No patch is proposed before current tail evidence. [Width4 source rationale](../hashinfer-w4a16-megamoe/integrated-topk-20260918/vectorization-research/WIDTH8_ADDRESS_LIFETIME_REVIEW.md), [final width4 result](../hashinfer-w4a16-megamoe/integrated-topk-20260918/EXPERIMENTS.md:2050).
- **Linear address rewrites, unsigned divmod, paired slabs, and continuation recurrence were already explored.** K3's first decode pass cannot benefit from a continuation-only optimization. Preserve the current topology and recurrence until a K16-specific generated issue is established. [Prior round summary](../hashinfer-w4a16-megamoe/integrated-topk-20260918/ROUND_SUMMARY_20260919.md).

The historical scalar-score variant also changed payload width and preparation timing; it was not an isolated K16/LDG128 comparison. The prepared one-line probe deliberately asks that narrower question. No historical bit-exact checks qualify this new source, and correctness remains deferred until a repeatable performance gain, as requested.
