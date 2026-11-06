# Prior W4A16 MegaMoE optimization audit

Read-only audit on 2026-09-25; current source is `002ef1454cbacde09972ed5e2ec7dcfe37e55749`. Historical efforts were not modified. Paths below are absolute so the older evidence can be opened independently. Historical latency is context, not a current control.

## Current authorized benchmark plan, 2026-09-25

The user explicitly selected **before versus after like HashInfer PR #11** and authorized reusing current PR head `002ef145` as the control. Collect its complete native EP4 and EP8 baseline once, then reuse those same-node, same-stack, source-bound rows for candidate sweeps. Do not require a new ABBA pair per candidate. Already completed target-workload ABBA trials remain separate, useful evidence; they do not impose a new repeat requirement. Preserve all trials and decisions in the local ledger. See [PR11 contract audit](/Users/ziangli/playground/projects/hashinfer-w4a16-device-trace/optimization/pr11-contract-audit.md).

## Current mechanism versus historical conclusions

Current `_MegaMixedInput._compute_stages_and_tmem_cols` reserves two accumulator slots, leaving **three decoded K256 slots for N64 and two for N128**, filling 512 TMEM columns. The shared decoder waits for raw TMA, acquires an empty decoded slot, loads/decodes/scales the complete register fragment, writes TMEM, then publishes ready. The owned `_finish_transform_stage` already releases packed-weight/scale SMEM after the final register-fed TMEM store issue and before its completion fence. It must keep decoded-full publication after that fence.

Consequently, transform waiting for an empty decoded slot and MMA waiting for a full decoded slot are not contradictory. They may happen at different ring positions/times; compare matched K payloads and the two decoder groups before concluding that TMEM capacity alone is the cause. Moving independent decode work ahead of acquisition is a coherent hypothesis. Fresh generated code and uninstrumented timings must establish an actual overlap window and benefit.

Current pointers:

- [TMEM capacity and retained early raw release](/Users/ziangli/playground/projects/hashinfer-w4a16-device-trace/hashinfer/hashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py:55).
- [Current raw/acquire/decode/store loop](/Users/ziangli/playground/projects/hashinfer-w4a16-device-trace/hashinfer/hashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py:373).

The historical [pipeline resource audit](/Users/ziangli/playground/projects/hashinfer-w4a16-megamoe/ep4-perf-20260920/PIPELINE_RESOURCE_AUDIT.md) explains TMEM, register and SMEM constraints. Its H7168 stage fit and CuTe DSL 4.7.1 resources are predictions/context for the current H6144/DSL4.8 run, not measurements. The older [early-weight audit](/Users/ziangli/playground/projects/flashinfer-w4a16-megamoe/candidates/w4a16_pipeline_orchestration_review/EARLY_WEIGHT_DECODE_AUDIT.md) correctly notes that weight loads/decode already run independently of activation readiness, but does not prove the current decode schedule is optimal.

## Relevant earlier trials

Canonical detailed ledger: [w4a16_optimization_experiments.md](/Users/ziangli/playground/projects/flashinfer-w4a16-megamoe/w4a16_optimization_experiments.md). These are different revisions, mostly EP8/H7168 and earlier compiler stacks. Negative results do not forbid a narrowly motivated current retest.

| Entry / source link | What ran and result | Implication now |
|---|---|---|
| [020/024, FC2 first32](/Users/ziangli/playground/projects/flashinfer-w4a16-megamoe/w4a16_optimization_experiments.md:1209) | Fully scaled first 32 BF16 values moved before decoded-slot acquire; native proof, no spill, +8 instructions. Old 512-thread/REG128 layout. Numerics passed; fixed 4/13 wins, AUTO 6/13; mixed and unpromoted. | Shows overlap can be emitted, but old layout and unbracketed EP8 run limit applicability. |
| [027/030, FC2 first16](/Users/ziangli/playground/projects/flashinfer-w4a16-megamoe/w4a16_optimization_experiments.md:1517) | Modern 640-thread/REG96 path. Full numerics and complete fixed/AUTO sweep. Fixed latency GM +0.294%, AUTO +0.208%; no broad gain or promotion. | Closest prior partial-predecode trial. Preserve arithmetic and check instruction motion instead of assuming source motion suffices. |
| [032, FC1 first16](/Users/ziangli/playground/projects/flashinfer-w4a16-megamoe/w4a16_optimization_experiments.md:1756) | Native +11 FC1/+8 kernel instructions, payload preserved across wait, zero spills. Fixed CONTROL +0.470% GM against retained source, 6/13 wins; AUTO skipped, unpromoted. | FC1 partial predecode has also been tried. |
| [057, MMA decoded-readiness probe](/Users/ziangli/playground/projects/flashinfer-w4a16-megamoe/w4a16_optimization_experiments.md:4520) | Wait sequence change, same resources. Numerics passed; 8–4096 GM +0.659% latency, 4/10 wins; rejected. | A different polling/probe spelling alone lacked evidence. |
| [059, ACC1/decoded3](/Users/ziangli/playground/projects/flashinfer-w4a16-megamoe/w4a16_optimization_experiments.md:4681) | N128 traded ACC2/D2 for ACC1/D3; N64 unchanged ACC2/D3. Passed numerics; +2.515% latency GM, 1/10 wins; rejected. | Deeper decoded rings consume accumulator overlap. Current N64 already fills all TMEM; there is no free fourth K256 slot. |
| [060/061, K128 + B6](/Users/ziangli/playground/projects/flashinfer-w4a16-megamoe/w4a16_optimization_experiments.md:4760) | K128 doubled decoded depth to D6/D4; B6 later helped hot scores but every matched K128 score remained worse, all AUTO winners stayed K256. Added tuning cost, no retention. | More stages also mean finer K-loop overhead; do not infer capacity gain equals performance gain. |
| [063, full K128 predecode](/Users/ziangli/playground/projects/flashinfer-w4a16-megamoe/w4a16_optimization_experiments.md:5016) | Decode before acquire for K128 only. Native +57 non-NOP instructions including payload copies; FC1 scales partly sank after wait. All AUTO winners remained unchanged K256; same-tactic K128 hot scores +6.60% GM, unpromoted. | Not a test of full K256 predecode under DSL4.8. Check scaled payload location in SASS, especially FC1. |
| [064, shared operand completion ring](/Users/ziangli/playground/projects/flashinfer-w4a16-megamoe/w4a16_optimization_experiments.md:5046) | Shared decoded/activation empty barriers when depths/ownership match; fewer instructions, no end-to-end gain. Briefly pushed then explicitly reverted because user found design too tedious. | Do not resurrect this coupled ring merely as cleanup. |
| [078, early raw release](/Users/ziangli/playground/projects/flashinfer-w4a16-megamoe/w4a16_optimization_experiments.md:6132) | Native proves raw release before TMEM fence, decoded publication after fence, no resource/instruction cost. Mixed marginal −0.424% latency GM; retained. | Already present at current head; not a new experiment. |
| [081, raw6/B3](/Users/ziangli/playground/projects/flashinfer-w4a16-megamoe/w4a16_optimization_experiments.md:6433) | N64 raw5→6, added SMEM/ring overhead; +2.170% latency GM, rejected. Unchanged N128 also drifted. | Do not attribute whole historical loss causally to depth; current trace should show raw-ring starvation before revisiting. |

Reusable candidate/native references:

- [FC2 first32 implementation](/Users/ziangli/playground/projects/flashinfer-w4a16-megamoe/candidates/w4a16_fc2_first_fragment_predecode/README.md) and [native review](/Users/ziangli/playground/projects/flashinfer-w4a16-megamoe/candidates/w4a16_fc2_first_fragment_predecode_native_review_0d795/README.md).
- [FC2 first16 implementation](/Users/ziangli/playground/projects/flashinfer-w4a16-megamoe/candidates/w4a16_fc2_first16_modern5wg/README.md) and [native review](/Users/ziangli/playground/projects/flashinfer-w4a16-megamoe/candidates/w4a16_fc2_first16_modern5wg_native_review_ec94/README.md).
- [FC1 first16 native review](/Users/ziangli/playground/projects/flashinfer-w4a16-megamoe/candidates/w4a16_fc1_first16_native_review_e359/README.md).

## Earlier HashInfer benchmark contract

Canonical [methodology](/Users/ziangli/playground/projects/hashinfer-w4a16-megamoe/integrated-topk-20260918/BENCHMARK_METHODOLOGY.md), [EP4 runbook](/Users/ziangli/playground/projects/hashinfer-w4a16-megamoe/ep4-perf-20260920/RUNBOOK.md), and [final whole-PR table](/Users/ziangli/playground/projects/hashinfer-w4a16-megamoe/ep4-perf-20260920/whole-pr-final.md):

- Full public forward, precomputed routing, BF16 input/output, W4A16 weights, deterministic ordered FP32 combine over BF16 FC2 outputs; default FC2 top-k weighting. Preparation/JIT/autotune outside samples.
- Historical performance shape **H7168/I2048/E256/top8**, primary EP4 and EP8 guard, C2 B300, CUDA13.2 `nvcr.io/nvidia/pytorch:26.05-py3`. Numerical GLM5 shape was H6144. Preserve that distinction.
- Global tokens **1,2,4,8,16,32,64,128,256,512,4096,8192,16384**. Report all rows; retention focuses 4–512 decode geometric speedup and every prefill row separately. No invented threshold, no hiding 16K loss in an aggregate.
- **3 warmups, 100 cold-L2 CUDA-graph CUPTI samples**, median of **per-iteration rank maximum**. This is not maximum of rank medians. Keep every sample, MAD and 25-sample quarter medians; no trimming/minima/drift subtraction.
- Same-node baseline/candidate, fresh per-arm knob cache, complete actual AUTO catalog, all winners and hot native selection scores recorded. Hot graph-event tuner scores are secondary, distinct from cold CUPTI latency. Fixed-tactic runs isolate mechanisms; AUTO compares complete selection policy.
- Routine exploratory candidate: one complete sweep against same-node source-bound control. Promising final confirmation can use **A1/B1/B2/A2** and pool all **200 samples per arm/row**, not median of the two run medians. This pattern was explicitly predefined for a prior PR confirmation; the latest whole-PR table itself used serial single sweeps. Do not imply every old PR used ABBA.
- No concurrent profiling or another GPU workload during performance collection. Record exact source/harness/timer, image, package versions, host/boot/GPU identities, complete results and process closure.

The requested current trace is **H6144, 256 tokens/rank, EP4, exact uniform routing**, i.e. **1024 global tokens and 32 tokens/expert**. It differs from both the native benchmark H7168 and its global token matrix. Add a labeled target-workload row and use the same CUPTI/cold-graph methodology; do not silently relabel historical global T256 as 256/rank or compare the trace's hot 50-event score with cold CUPTI.

Latest local ledger supersedes memory: [BENCHMARK_STATE.md](/Users/ziangli/playground/projects/hashinfer-w4a16-megamoe/ep4-perf-20260920/BENCHMARK_STATE.md) records G512/G1024 catalog `ec42ba07` retained after an independent same-node repeat, all-tactic qualification and T8 codegen audit. Older memory saying it remained blocked is stale. S3 and M128/C1 were not retained; new M128 choices never won in that EP4 sweep. Static scheduling, coalesced reducer and initial-idle pull override were also unpromoted.

## Reusable execution and correctness tools

Reuse ideas/code in the current effort; do not run old resource identities blindly:

- [run_arm.py](/Users/ziangli/playground/projects/hashinfer-w4a16-megamoe/ep4-perf-20260920/run_arm.py): sealed source, fresh knob directory, native benchmark CLI, environment cleanup, PID/PGID and final process/source closure.
- [worker.py](/Users/ziangli/playground/projects/hashinfer-w4a16-megamoe/ep4-perf-20260920/worker.py): unchanged native timer, untimed finite/repeat-bit-equal output signatures, optional strict independent oracle using actual benchmark fixture.
- [compare.py](/Users/ziangli/playground/projects/hashinfer-w4a16-megamoe/ep4-perf-20260920/compare.py): source/fixture/output/timer parity, all100 samples, rank-MAX medians, MAD, quarters, actual winner dictionaries and decode geometric mean. Hardcoded H7168/global13 must be deliberately adapted for a separately labeled trace fixture.
- [cupti_lifecycle.py](/Users/ziangli/playground/projects/hashinfer-w4a16-megamoe/ep4-perf-20260920/cupti_lifecycle.py): historical host `cupti.finalize()` SIGSEGV workaround retains callbacks and detaches once after process-group drain. It does not alter timing. If reused, both arms must match this lifecycle; current stack may no longer need it.
- [NUMERICAL_PLAN.md](/Users/ziangli/playground/projects/hashinfer-w4a16-megamoe/ep4-perf-20260920/NUMERICAL_PLAN.md): focused promotion qualification, not a command to rerun every trial. EP4/8 × random T128/skewed T1 × FC1/FC2 weighting; scan all deterministic tactics × O2/O3 × eager/graph, every output finite and BF16-bit exact against independent reference. Eight tactics give256 combinations,768 references,3968 pair checks across8 logical cases. Current test entrypoints/catalog must be checked before reuse.

Benchmark paired output hashes alone are not independent numerical proof and do not validate every timed replay. A transform scheduling change should additionally qualify long-K/ring wrap, partial-K/tails, both widths/returns and the shared split path if the base decoder changes. Full expensive numerical/sanitizer work follows a useful performance candidate; historical “no sanitizer during this iteration” was scoped to that old task, not a permanent exemption.
