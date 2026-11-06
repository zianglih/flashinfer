# Per-token quantizer CTA width, retained 475 control

Retained commit `f63e948564582a487f95900c71ef581b90c3f177` computes the useful SF-block count, rounds it to a physical warp, and caps the initial CTA width at the existing 128-thread default. Existing wide-row growth remains unchanged. No precision, PDL, routing, MMA, or autotune policy changes.

- Base `475cae6b28a536e24aa8da2ed488d0f00fb5305b`; one modified quantizer file, +9/−5 lines. The review clone was retired after empty diff against retained `f63e9485` and no-untracked proof; `retained-source-equivalence.json` verifies all514 measured source files match the retained commit.
- Final quantizer SHA256: `2bb9ed15d2ba33520c6c8b015e43fe2d9d8a01fa08541dc7384c9163842ad0dc`.
- Full local patch and source pins: `candidate.patch`, `local-source.json`.
- The whole native data directory links to the stable seed after a csrc/include byte-identity proof (`full-evidence/native-path-audit.json`). Existing C++ compilation caches are preserved. An earlier differing include path caused a native rebuild; that finished before these timings.

## Completed qualification

- 80 existing exact tests passed, zero failures/errors/skips (`full-evidence/gate-r3`).
- 44 direct boundary cases, 176 CUDA-graph replays, and two routed-hole cases passed against the retained 128-thread configuration (`full-evidence/direct-r2`). This covers BF16/FP16, 1/2/3/4-warp widths, small/large K, all SF layouts, PDL on/off, initial and intermediate contracts.
- The final min-one-physical-warp cleanup preserves 40,960 positive-K policies and emits byte-identical K640 CUBIN. Existing K0/M0 calls still fail with their original natural errors; no new empty-input contract is introduced (`full-evidence/edge-verification.json`).
- The benchmark MSE256/error-fast-math recipe has zero local memory in the fresh boundary CUBIN captures. The existing strict-error MSE K1024 recipe has the same 24-byte stack and 10 LDL/6 STL in both 128-thread control and 64-thread candidate; this pre-existing issue is recorded, not changed (`full-evidence/exact-recipe-codegen`).

## Source-paired N3U TP8, 16,384 tokens

Public functional API, per-token mode, initial quantizer included, unfused finalize; frozen retained native tactic without AUTO. One B300 GPU, C-A-A-C, 10 warmups and 100 strict CUPTI samples per phase, cold-L2 CUDA graphs. Both source trees, route, tactic, cache, and runtime register policies checked before/after. No clock settings changed; all timed quartiles observed 2032 MHz and clock reason 0.

| Phase | Control 1 | Candidate 1 | Candidate 2 | Control 2 |
|---|---:|---:|---:|---:|
| E2E µs | 1956.458 | 1762.650 | 1762.474 | 1956.955 |

Geometric-mean latency: **1956.707 → 1762.562 µs (+11.015%)**. Repeat spread: control 0.025%, candidate 0.010%.

| CUPTI timeline component | Control µs | Candidate µs |
|---|---:|---:|
| Initial quantizer | 36.529 | 36.496 |
| FC1 | 536.987 | 536.907 |
| Intermediate quantizer (includes PDL wait) | 661.404 | 467.522 |
| Intermediate quantizer tail after FC1 | 640.547 | 446.771 |
| FC2 tail after intermediate quantizer | 450.098 | 450.179 |
| Combine | 282.346 | 282.402 |

The gain comes from the intended intermediate quantizer; other stages are stable. Kernel durations overlap and must not be summed. Complete measurements, CUPTI activities, telemetry, and source/runtime proofs are in `full-evidence/perf`; `analysis.json` and `component-samples.json` preserve all 400 iterations.

Evidence archive SHA256: `657ac8900e3b103dd01706c129c7cbd3168d3a9b2a089ad68b4b52b67bfef015` (626 files).

## Broader retention screen: passed

24 fixed-winner per-token E2E cells: four models × EP/TP × tokens32/4096/16384; C-A-A-C with the same timing/source/telemetry guards. Positive means candidate faster.

| Model/topology | 32 | 4096 | 16384 |
|---|---:|---:|---:|
| v3 EP | -0.08% | -0.05% | -0.05% |
| v41-flash EP | +0.00% | +0.07% | +0.94% |
| kimi-k3 EP | +0.07% | +0.14% | +1.95% |
| nemo3-ultra EP | -0.03% | +0.00% | +0.01% |
| v3 TP | -0.75% | +6.70% | +6.42% |
| v41-flash TP | -0.25% | +2.90% | +4.32% |
| kimi-k3 TP | +0.53% | +7.82% | +8.93% |
| nemo3-ultra TP | +1.87% | +8.95% | +10.95% |

TP prefill gains generalize across all four models; the largest decode regression is 0.87 µs (V3 TP32). EP widths are unchanged: regard these variations as neutral. In particular, do not credit K3 EP16k's apparent gain: its control repeat spread is 1.68%, candidate 0.87%, and measured SM clocks range1927–2032MHz. All TP cells measured2032MHz/reason0.

Raw results, source/cache/runtime guards, all CUPTI activities and clock telemetry: `broad-evidence/`. Per-phase timeline reductions: `broad-evidence/analysis.json` and each job's `analysis.json`/`component-samples.json`. Full104 candidate-AA refresh completed on GPUs0/2/3/4: all104 cells,16 phases,20,800 strict CUPTI samples passed source/runtime/cache/route guards. Raw data is in `full104-evidence`, and `full104-publication-receipt.json` audits the fetched files. Final source is byte-identical to pushed f63e9485. All GPUs are released. Saved historical baselines are reused for publication; this is not a new same-GPU baseline comparison. K3 EP16k has3.82% AA spread and observed1867–2032MHz/reason4; all other token≥4 cells have≤0.77% spread.
