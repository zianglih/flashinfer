# K3 W4A16 MegaMoE: prior ledger and tactic review

Read-only review on 2026-10-08. Current source inspected at FlashInfer `a7103ae2a97f38f4dbbf410c32acc7c6fe99cab1`; prior benchmark source is `b730d5f6f5929fe666b24b466144a57f5587ba4b`. No GPU work or correctness run was performed by this review.

## First candidates

1. **Optimize the SiTU epilogue first.** The current W4A16 `_tanh` explicitly expands each tanh to exp2 + reciprocal + arithmetic, twice per output, in addition to the sigmoid. Its FC1 loop holds the gate/up fragments and uses scalar SiTU multiplies where the plain SwiGLU branch uses packed pairs. K3's FC1 reduction is only 14 K256 steps, versus GLM5's 24; there is less MMA work to hide this epilogue. K3 also has 50% more intermediate channels per expert. This is a concrete activation-specific difference, unlike most earlier rejected global pipeline changes. Preserve FP32 expert scaling, activation order, and BF16 final conversion; compare native tanh and/or packed FP32 arithmetic against the W4A4/PR4540 implementation before accepting any numerical change. Source: [epilogue.py:418–480](flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/epilogue.py#L418), [fragment processing:594–707](flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/epilogue.py#L594). PR4540's detailed comparison is being handled separately.
2. **Probe existing input dispatch `flag_batch=8` with N64/G512 and N64/G1024.** The W4A4 catalog actually chooses F8 for several K3 decode sizes; W4A16's eight candidates only contain F4. It is a supported existing knob, so this is a small isolated comparison. Do not conflate this input/transport flag with `epi_flag_batch` readiness publication. F8 is not universally superior: K3 T8/T32 choose F4 on B300, and T128/T256 change between sweeps.
3. **Probe G2048 and G4096 at N64/epi on T32, T64, T128, T512.** K3 has 112 experts/rank, each contributing 24 FC1 cluster tiles per token block, versus GLM5's 32 × 16. The original G512/G1024 choice therefore has very different meaning. The actual saved routing histograms show that G512/G1024 create 6/3 groups on every K3 rank at T512; G2048/G4096 create 2/1. The same GLM5 shape needs one group even at G512. Larger groups may reduce phase-transition costs, but delay FC2 and worsen intermediate reuse; test rather than hardcode. A G256 control tests the opposing earlier-return hypothesis if larger groups do not help.
4. **After the activation change, retune existing N64/N128 and return choices before adding more dimensions.** SiTU cost can change which geometry wins. At K3 T4096/T8192, W4A16 currently chooses epilogue return while GLM chooses dispatch return. The W4A4 K3 T4096 winner instead uses standalone return on both hardware generations. This is a useful signal that return/epilogue contention differs, not permission to label standalone return a ready W4A16 tactic.

Fixed-knob JSONs are in [evidence/tactics/](evidence/tactics/). These are unmeasured probes, not a recommended production catalog. `control_n64_g1024_f4.json` supplies the common control; compare one field at a time. For benchmark JSON ingestion, convert `mma_tiler_mnk`, `cluster_shape_mnk`, and `epi_flag_batch` to tuples before passing to CuTe if the runner does not already normalize all three. No fused FC2/TMA reduction is enabled in any file.

## Actual W4A4 selections versus W4A16

[Complete per-token tables](evidence/tactics/PRIOR_TACTICS.md) preserve both sweeps on both B200 and B300. [The JSON](evidence/tactics/prior-selected-tactics.json) contains 176 selected records and SHA256 bindings for all eight original log files. This is selected-tactic evidence, not the hot score margin between candidates.

| B300 workload | W4A4 | W4A16 | Meaning |
|---|---|---|---|
| GLM and K3 T4–512 | M256/N128/K256, epi; F4/F8 | M256/N64/K256, epi; F4 only | The common decode geometry is unchanged between models. F8 is missing from W4A16 AUTO. |
| GLM T4096/T8192 | N128, dispatch | N128, dispatch | Both use dispatch return. |
| K3 T4096 | N128, standalone | N128, epi | Repeats identically in both sweeps and both GPUs. |
| K3 T8192 | N128, dispatch on B300; N256, standalone on B200 | N128, epi | Return and tile choices are model/hardware dependent. |
| GLM/K3 T16384 | N256, dispatch; GLM F8, K3 F4 | N128, dispatch | W4A4's N256 is unavailable under the present W4A16 TMEM allocation. |

Every selected W4A4 tactic uses G512; every selected W4A16 tactic uses G512/G1024. Both use atomic scheduling and epilogue flags `(2,4)`. No observed winner supports copying a static scheduler or M128 choice from W4A4.

## K3 changes the work distribution

K3's latent core has D3584, E3072, N896, K16; GLM5 uses D6144, E2048, N256, K8. K3 is not simply a smaller version of GLM: it has a shorter FC1 reduction, longer FC2 reduction, wider gate/up output, more experts, more routes, and more expensive activation.

| Property | GLM5 | K3 |
|---|---:|---:|
| Local experts at EP8 | 32 | 112 |
| FC1 K256 steps | 24 | 14 |
| FC2 K256 steps | 8 | 12 |
| FC1 feature tiles per expert/token block (M256/C2) | 16 | 24 |
| FC2 feature tiles per expert/token block | 24 | 14 |
| Expected tokens per expert | T/32 | T/56 |
| FC1 activation elements per unit GEMM work | reference | 1.714× reference |

The last row follows `1/(2D)` and describes arithmetic work, not measured stall time. D3584 and both E values already align with current feature tiles: an M128 trial cannot claim avoided feature padding. Dynamic MMA N handles partial token tiles, while epilogue granularity remains 64 tokens. This leaves a possible short-token epilogue masking/granularity direction, but N32 is not a catalog-only addition.

The route-derived group model exactly follows the greedy complete-expert FC1-tile budget in [fc1_fc2_fuse_sched.py:775–801](flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/fc1_fc2_fuse_sched.py#L775). Its full per-rank results are [prior-routing-group-counts.json](evidence/tactics/prior-routing-group-counts.json).

| K3 global tokens | Active experts/rank | G512 groups/rank | G1024 | G2048 | G4096 |
|---:|---:|---:|---:|---:|---:|
| 4 | 3–15 | 1 | 1 | 1 | 1 |
| 16 | 23–30 | 2 | 1 | 1 | 1 |
| 32 | 43–55 | 2–3 | 1–2 | 1 | 1 |
| 64 | 64–85 | 3–4 | 2 | 1 | 1 |
| 128 | 94–103 | 5 | 3 | 2 | 1 |
| 512 | 112 | 6 | 3 | 2 | 1 |

These use the captured seeded routes, not uniform expected routing. Identical group boundaries do not imply identical machine code, and fewer groups do not guarantee a gain.

## What the previous ledgers retained or rejected

| Direction | Final historical disposition | K3 implication |
|---|---|---|
| Eight-tactic G512/G1024 product | Retained after repeated changed-path EP4 improvements and EP8 guard; initial T8 regression required a matched repeat | Broader K3 expert population is a new, concrete reason to probe larger group budgets. |
| M128/N64/C1 | No selection in the completed EP4 sweep; best hot M128 was 5.83–11.27% slower at T16–512 | Supported but lower priority. K3's shorter FC1 is a new rationale, but D/E alignment provides no padding win. |
| Scheduler depth3 | ~1.0012× decode with mixed rows; not retained | More K3 expert boundaries provide a plausible reason for one narrow probe, after activation/group changes. Do not jump to depth5. |
| Static epilogue scheduling | No retained-shape selections; static hot decode 1.7–8.0% slower | Defer unless K3 profile proves atomic claim overhead. |
| Immediate epilogue publication `(1,1)` with dispatch return | New hot prefill winners, but cold regressions and no new decode winner; not retained | Lower-priority K3 prefill probe, motivated by its changed return winners and more expert boundaries. |
| Multi-WG input copy, earlier metadata/readiness, earlier scheduler, local-ready overlap, fifth combine WG | Implemented and measured, mostly flat or regressing; no later batch promotion | Do not present these as untried ideas or assume useful work is being blocked by initialization. |
| Raw-TMA readiness-probe removal and wider TMEM stores | Eventually restored; trace PR retained no pipeline optimization | Repeating the old variants requires new causal K3 evidence. Keep original probes and x8 storage initially. |
| 256-bit combine payload or scores | Final spill-free variants lost all 12 focused shape comparisons; LDG128 retained | Avoid a generic vector-width retry. K3 K16 can increase live combine state and register pressure. |
| Paired-slab/coalesced16 combine | No useful EP4 decode gain despite structurally fewer strides | Defer without current K3 combine-tail evidence. |

Historical source/evidence (read directly, not inferred from memory):

- [EP4 performance ledger](../hashinfer-w4a16-megamoe/ep4-perf-20260920/README.md), especially **M128/C1 catalog result**, **Group-size product retained and pushed**, **Static epilogue scheduling not retained**, **Immediate publication complete**, and **Coalesced paired-slab combine not retained**.
- [Pipeline resource audit](../hashinfer-w4a16-megamoe/ep4-perf-20260920/PIPELINE_RESOURCE_AUDIT.md): stage budgets and earlier ACC1/K128/B4/raw6 rejections.
- [Final September19 staging/combine state](../hashinfer-w4a16-megamoe/integrated-topk-20260918/CURRENT_EXPERIMENT_STATE.md) and [round summary](../hashinfer-w4a16-megamoe/integrated-topk-20260918/ROUND_SUMMARY_20260919.md).
- [Trace experiment ledger](../hashinfer-w4a16-device-trace/optimization/EXPERIMENTS.md), final tracing-only disposition at lines1003–1023. Historical `d453`/raw-probe-off results are explicitly superseded as retained optimization claims.
- [Alignment256 final decision](../hashinfer-w4a16-device-trace/optimization/alignment256-20260926/FINAL_DECISION.md) and [spill ledger](../hashinfer-w4a16-device-trace/optimization/alignment256-20260926/DIAGNOSTIC_SPILL_LEDGER.md).

## Supported knobs versus kernel work

The current factory emits eight M256/C2 candidates: N64/N128 × G512/G1024 × epi/dispatch, all F4/S2. [autotune.py:16–46](flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/autotune.py#L16). Existing validation admits M128/N64/C1, static scheduling, arbitrary positive group budgets, and dispatch flags such as F8. These can be measured without kernel modifications.

N256 is different: W4A16 allocates two accumulator stages and 128 TMEM columns per decoded K256 stage. N128 leaves two decoded stages; N64 leaves three. N256 would consume all512 columns in accumulators alone. [megamoe_kernel.py:69–108](flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py#L69). Importing W4A4's N256 tactic would require changing accumulator/decoded-weight ownership. Earlier ACC1 and K128 trades were rejected, so this is not the first experiment.

Likewise, standalone return is rejected by both [frontend validation](flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/frontend.py#L94) and the W4A16 kernel. Its existing five-WG division is epilogue/control/dispatch/two decoders; creating another live role would trade with the critical decode pipeline. First investigate existing return modes after reducing activation cost.

For retention, compare fixed-tactic baseline/candidate, then an expanded AUTO catalog that preserves existing choices. Use the same C2 node, native CUPTI cold-L2 graph rank-MAX methodology, PDL on, fused TMA reduction off, and deterministic integrated combine active. Only run correctness after a repeatable performance win, per the user's instruction. No historical numeric checks in these ledgers qualify a new SiTU implementation.
