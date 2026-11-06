# General pipeline performance round

Frozen measurement control: `2995bfda8338ca6ae623fbc2657d44e35e665627`, clean/pushed. This round targets V3 EP8, V4.1-Flash EP4 and Kimi K3 EP8 across per-tensor NVFP4, per-token NVFP4, MXFP4x8 and MXFP8. No new tuning axis or model/dtype profitability threshold is allowed. Instruction reductions and simpler policy are useful retention signals even when timing-neutral; regressions still require review.

## Active candidates

| Source copy | Mechanism | Frozen evidence | Status |
|---|---|---|---|
| Removed: `flashinfer-epilogue-overlap-20261027` | Finish protected TMEM slabs before output work, then release overlap earlier | `epilogue-overlap/` | V2 exact pass but spills; rejected, register policy audit underway |
| Removed: `flashinfer-mainloop-20261027` | One wide SFB TMA multicast replaces duplicated two-CTA requests | `mainloop/`, `mainloop-gate/` | Rejected:0.998345× overall,0.996460× prefill; more instructions |
| Removed: `flashinfer-mma-alignment-20261027` | Derive dynamic N alignment from CTA group, avoiding unnecessary masked-column MMA | `mma-alignment-source/`, `mma-alignment/` | Retained f7182d5c:96 exact replays/source, neutral48-point screen1.001360× |
| Removed: `flashinfer-epilogue-release-20261027` | Release per-token accumulators immediately after the last protected TMEM transpose | `epilogue-release/` | Retained/pushed ee88cf2a: 32 exact replays/source, six fixed-tactic CAAC points. Three affected points +0.22%/+0.44%/+0.52%, no spills; K3 FC1 +10 registers. Review copy removed. Larger register/overlap revisions 651b and 3fa remain rejected |
| Removed: `flashinfer-sf-source-address-20261027` | Remove an inactive SF source-row selector already made redundant by zero-byte predicated copies | `sf-source-address/`, `sf-source-address-gate/` | Retained/pushed f175faea: 64 exact replays/source; 48-point screen 1.001574x and targeted repeats. +1/−4 source lines; no E2E speedup claim |
| Removed: `flashinfer-sf32-scratch-20261027` | Two-slot SF32 exchange scratch with publication joins and one final drain per helper | `sf32-scratch/`, `sf32-scratch-gate/` | Rejected c6a8b50e: 64 exact replays/source pass, but 18-cell CAAC is 0.995903x overall and 0.993811x prefill. Copy removed; cleanup receipt and full table retained |

Packed combine is retained/pushed as `94a89e2c`. The scalar-metadata variant passes98 B300 exact cases and74 compiled source pairs, removes all1,960 PRMT instructions, halves arithmetic instruction count, and has no candidate spills. Summed static instructions fall18,384→15,528; registers vary−15…+24. The48-point CAAC screen is neutral:1.001934× overall,1.001416× decode,1.002452× prefill. Retention follows the requested instruction-efficiency criterion. Worst point is K3 per-token16384 at0.99238×. Full raw evidence stays in `packed-combine-scalar/screen-evidence`; the completed source copy is removed. The first packed-metadata variant is superseded, not timed. The final composed source now has six fresh public AUTO tables; see the final sweep below.

Historical source bindings: alignment/multicast/early epilogue experiments are 2995-based; register-only was 94a-based. Final composition f7182d5c passed its fresh exact gate and six-table public AUTO campaign. Current active copies are f175faea-based and listed above.

## Environment and protocol

Existing C3 `fi-moe-nvfp4-port-1026`, eight idle B300 GPUs verified at round start, image `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2, CuTe4.7.1 and Torch2.12.0a0 nv26.05. Immutable control and candidates live on persistent `/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/perf-round-20261027`. All4,389 native source hashes match the persistent C++ cache; each changed DSL source has a private, identity-bound namespace. No moving container tag or new devbox.

Bounded exact-output/resource gates precede timing. Screens use the completed shared-FC1/FC2-CLC native winner cache without retuning or new axes, identical source-bound routing hashes, and control/candidate/candidate/control on the same GPU. Forty-eight diagnostic cells are3models×4formats×tokens32,128,4096,16384. Each arm uses10warmups/100cold-L2 CUDA-graph CUPTI samples; NV includes initial input quantization, MX is prequantized, fused finalize disabled. Ratio is `sqrt(C0*C3/(A1*A2))`. These are fixed-tactic diagnostics, not a fresh public AUTO sweep. Historical baselines are not retimed merely to recreate existing data. Final public tables remain source-attributed until the final retained composition is measured.

GPU allocation: public AUTO, K3 diagnostics, V3 AUTO diagnostic, scale-address and larger register screens are complete. SF32 timing is complete and rejected; the tiny release change is retained as ee88cf2a. No GPU work remains active; all eight GPUs are idle and persistent caches are preserved. Failed public preflight attempts measured no rows; the corrected launcher preserves the venv Python path. Source edits remain unstaged in active review copies; after retained pushes, those copies are bumped so remaining diffs show only pending work.

## Final public sweep at f7182d5c

All six model/family tables are published in PR #7290 and verified by exact readback (`pr-publication.json`). This fresh native AUTO sweep contains 377 measurements / 37,700 samples; independent source, recipe, routing, winner and raw-output validation passed. The current [gap summary](public-refresh/final-public-f7182d5c/remaining-gaps.md) excludes tokens 1/2. Worst matching point is V3 MXFP8 T8192 at 0.9586x; K3 NVFP4 T64 is 0.9900x. Unsupported K3 TRT per-token and MXFP8 comparisons remain N/A. These are native backend comparisons, not paired evidence for either neutral instruction cleanup.

Nested AUTO observations across six concurrent workers: 1,260.88 s in `cute.compile` API calls (30.79%), 2,779.09 s in profiling outside those calls (67.86%), and 55.13 s other work. The slowest worker took 889.5 s. Compile API time includes cache lookup/compiler work; profile spans include setup, warmups and waits. Summed worker times are not elapsed campaign time or pure GPU work. Persistent C++ and source-bound DSL caches remain intact.

Current K3 [NSYS evidence](nsys-k3-t64/README.md) identifies an exposed FC2 extension, while current V3 MXFP8 diagnostics investigate the native geometry transition at T8192. The larger register/epilogue candidates are rejected: universal redistribution introduces hot producer spills, and the resource-scoped revision is timing-neutral overall. The remaining tiny release experiment has no register redistribution or fragment buffering.

## Current gap diagnostics

The current-source K3 T64 N16/N32 CAAC comparison is negative for N16 (0.99591x); do not expand N8 tactics on the strength of the overfetch counters alone. Existing K3 FC2 prefetch already fills all resident A/SFA stages before its payload wait. No safe blanket barrier removal is established.

For V3 MXFP8 T8192, the existing N256 tactic beats the selected N128 tactic by 1.08610x on actual routes, but only 1.01780x on the existing synthetic tuning routes. The synthetic routes weaken the advantage without reversing the ranking. This does not establish why native AUTO selected N128. A bounded, fresh native AUTO diagnostic uses the public `cuda_graph_profile_replays=10` option, an isolated selection cache, the same 320 tactics and inputs, and warmed source-bound compilation caches. It records every tactic median/order and clock/temperature snapshots. Existing final public tables and native caches remain unchanged; forced-tactic diagnostics are not substituted into published AUTO rows.

The scale-address cleanup is committed as `f175faea` and the PR readback is verified in `pr-publication-f175faea.json`. Its completed clone is removed. Universal register redistribution (`651b`) was rejected before candidate timing: an unselected but supported FC2 N256/M128 tactic generated 144B stack storage and 18 64-bit producer reloads per persistent tile versus no control spills. Stopped control-only screen artifacts are separate; no candidate result is claimed. Revised policy must follow actual buffered fragment need, not exclude a shape. The SF32 scratch lifetime audit is feasible and a separate active experiment is preparing two slots plus a bounded-call drain.

The resource-scoped register revision `3fa61657` repairs all unaffected kernels (10 preflight +6 later FC2 cores are instruction/resource-identical) and passes48 exact replays/source, but is also rejected: four-cell CAAC is1.000960x overall, with only1.005055x at V3 per-token4096. Its implementation cost is not justified; no48-cell or nativeAUTO expansion. Independent reviews bind177 artifacts and1,600 samples. A separate tiny release-order cleanup may reuse the active review clone after the rejected diff is removed.

## Round complete at ee88cf2a

Retained packed combine arithmetic, hardware-derived MMA N alignment, redundant scale-address selector removal, and the five-line accumulator release change. The larger register/epilogue and SF32 scratch changes are rejected. Canonical source is clean and pushed; no active review copies remain. The PR body uses current diff counts (+5,986/−8,028) and final follow-up validation while retaining the six full AUTO tables at their measured f7182d5c source. See `pr-publication-ee88cf2a.json`. Remaining TRTLLM gaps are still listed in `public-refresh/final-public-f7182d5c/remaining-gaps.md`; none is hidden by a new shape policy or tuning axis.
