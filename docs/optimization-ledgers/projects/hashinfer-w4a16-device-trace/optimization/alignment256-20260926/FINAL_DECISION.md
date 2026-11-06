# Alignment and register experiment decision — 2026-09-26

**Retain none of the alignment256 or standalone LDG128 register-restoration candidates.** HashInfer PR13 stays at `cd7cc07c02300553ef9b8e6af0a4044f0b5dc8a7`, with the existing 128-bit payload/alignment contract. The source checkout is clean; all experimental commits and artifacts remain available locally. No upstream FlashInfer sync and no new trace capture are required for an unchanged kernel.

## Decision evidence

Zero spills remains mandatory for any future 256-bit contract. The refined wide-payload and score-only variants achieved STACK0/LOCAL0 with no native LDL/STL in every selected winner of the completed focused comparison. However, all 12 candidate/shape pooled speedups are below 1. Instruction reduction alone does not justify this stronger contract when the fresh paired timings show no repeatable gain. The earlier compound also had unpromising broader EP4/EP8 screening, including a sizeable nativeEP4 one-token deficit.

These are retention decisions for the measured implementations, not proof that every256-bit approach is slower or that any small observed slowdown is wholly caused by source changes. AUTO tactic changes and repeated-run drift are explicitly reported.

## Completed fresh256 comparison

B300 on C2/infra node `hu-pdx-43`, EP4, uniform routing, H6144/I2048/E256/top8, global T128/4096/8192/16384. Eight fresh AUTO candidates per sweep; 3 warmups; 100 cold-L2 CUDA-graph CUPTI samples per sweep; reduce ranks with per-iteration MAX, then pool 200 raw untrimmed samples per source/shape. Order A1/B1/C1/D1/D2/C2/B2/A2. Timed public forward includes staging and MegaMoE; setup/JIT/tuning remain outside timing.

A original 128 `cd7cc07`; B wide payload + late state + scalar scores `679aa752`; C wide payload + late state + participant96 tail `f8c97bb`; D native 256 score loads + original 128 payload `adadbd6`. Exact package/source/fixture/helper hashes are in the linked audit. No earlier-node samples enter this comparison.

| Global tokens | Before µs | B µs | C µs | D µs | Before/B | Before/C | Before/D |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 128 | 282.514000 | 283.938000 | 283.234500 | 284.307500 | 0.994985 | 0.997456 | 0.993692 |
| 4096 | 594.007000 | 596.388000 | 595.269000 | 597.189500 | 0.996008 | 0.997880 | 0.994671 |
| 8192 | 1141.351000 | 1146.776000 | 1148.570500 | 1143.385500 | 0.995269 | 0.993714 | 0.998221 |
| 16384 | 2346.006500 | 2352.493500 | 2364.445000 | 2368.071000 | 0.997243 | 0.992202 | 0.990683 |

The apparent C T128 first-pass gain (1.021020x) reverses to0.986194x. Its repeat latency rises 3.321% while AUTO changes G1024→G512; baseline changes −0.204% with the same G512 tactic. At 8192 every phase uses N128/G1024/reuse-dispatch and all three pooled candidate results are slower. See the full per-pass medians/tactics/first/reverse ratios in [the independent review](tail-variants-focused-r2-review-v1.md).

Audit PASS:3,200 cold rank-MAX samples,10,240 hot tuner rank samples,128 winner exports,32 independent T128 reference records,128 finite/repeat rank records, and exact cross-arm input/weight/route/output hash parity. All 128 winner exports (32 baseline,96 candidate) are spill-free. [Full audit](tail-variants-focused-r2-audit-v1.md), [raw JSON](tail-variants-focused-r2-audit-v1.json), [completed evidence](tail-variants-focused-r2-progress-v1/).

## LDG128 controls completed first

The separate completed six-pass study on `hu-pdx-38` used the same four uniform EP4 shapes and 200 raw samples/source/shape, in A1/C1/D1/D2/C2/A2 order. It is not pooled with the replacement-node256 comparison. No detailed correctness sweep was inserted before these timings.

| Global tokens | Original128 µs | Restore96 tail µs | Late + restore96 µs | Original/restore96 | Original/late+96 |
|---:|---:|---:|---:|---:|---:|
| 128 | 282.738000 | 286.690500 | 291.026500 | 0.986213 | 0.971520 |
| 4096 | 594.918000 | 597.301000 | 597.734000 | 0.996010 | 0.995289 |
| 8192 | 1139.673000 | 1151.675000 | 1155.994000 | 0.989579 | 0.985881 |
| 16384 | 2357.044000 | 2380.516000 | 2374.242000 | 0.990140 | 0.992756 |

Both controls preserve the original compute-phase role budgets and change retired-tail registers only. Neither gives a repeatable gain or native instruction reduction. All 96 selected exports are spill-free. [LDG128 audit](original128-focused-audit-v1.md).

## Spill findings and qualification boundary

Initial payload widening produced40 B stack with10 LDL and17 STL native sites in the fixed uniform128 fixture. The inspected spills belong to combine-tail state/payload; no local-memory sites occur inside the repeated MMA/scheduler/TMA/transform per-K loops. WG3 already has 96 registers and performs the payload in this fixture, so restoring WG1 alone did not remove the spills. Late state preparation plus tail restoration eliminates them; late preparation plus scalar score loading also eliminates them without changing register budgets. Detailed PC/WG maps and native instruction counts are in [the spill ledger](DIAGNOSTIC_SPILL_LEDGER.md) and [tail refinement audit](tail-refinement-independent-audit-v1.md).

The user’s zero-spill requirement is not relaxed. Winner coverage is not full native AUTO catalog coverage. Because the completed focused timing rejects all candidates, the planned 1,376-export broad catalog, final trace-enabled winner, SM100a compile smoke, and further detailed correctness qualification were not run. No unqualified candidate is promoted. Earlier memcheck/reducer and compound integration results remain source-specific evidence in EXPERIMENTS.md; they are not claims about every new candidate.

The broader implementation audit is [IMPLEMENTATION_AUDIT.md](IMPLEMENTATION_AUDIT.md): score loads are the other natural256 candidate; TMA/token transport is already bulk, FC1/direct-FC2 stores already use256, transform TMEM accesses are separate, and input staging would require an additional caller-input contract. No TMEM widening is retained.

## Preservation and environment

The original box disappeared during C2 of the first focused campaign. Its five complete phases and partial sixth remain in [the pod-loss recovery ledger](TAIL_FOCUSED_POD_LOSS_RECOVERY.md), excluded from final performance. The replacement completed all 8 phases2026-09-26T06:59:58Z; wrapper exit 0, GPUs idle. Complete immediate-evidence archive SHA256 `df79d8599d3da411e629793eb7810eafcb3529d56b4ba30904b4bbc440f4dde6`. Compiler/cache trees remain in durable storage.

Keep C2/infra devbox **fi-w4a16-align256-r2-0926**, pod `devbox-fi-w4a16-align256-r2-0926-0`, node `hu-pdx-43`. It has 8 B300SXM6AC GPUs; EP4 used GPUs0–3. Image `nvcr.io/nvidia/pytorch:26.05-py3`, digest `sha256:222d8b18e671be5c3ef91cb41727a2572a0b23f59ded6c39f373a96946f6f2ba`; driver 590.48.01, Torch 2.12.0a0+5aff3928d8.nv26.05, CUDA 13.2, CuTe 4.8.0. Runtime freeze matches the prior node. The live [NGC catalog](https://catalog.ngc.nvidia.com/orgs/nvidia/-/containers/pytorch/-) and [NVIDIA release table](https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel-26-08.html) were checked before requesting the replacement.

Remote task: `/workspace/hashinfer-alignment256-20260926`; results: `/data/ziangli/hashinfer-w4a16-device-trace/alignment256-20260926`. Frozen runner/manifest and exact commands are in [the experiment plan](TAIL_VARIANTS_FOCUSED_PLAN.md), with the final output directory `tail-variants-focused-r2-v1`; full command receipts are preserved. No automatic continuation is queued. All helpers/results/traces stay outside the PR.
