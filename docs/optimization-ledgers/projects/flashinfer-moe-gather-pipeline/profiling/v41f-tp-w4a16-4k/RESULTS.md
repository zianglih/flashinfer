# Gated V41F TP4 W4A16 FC1 shared-output profile

The retained gated output stores do not show an exposed layout-conflict or publication bottleneck in this case. All 16 native `STS.U16` sites have one wavefront per warp instruction and no excess wavefronts. Their 603,520 dynamic warp instructions account for about 0.34% of the kernel's 178.76 million executed instructions; they have 33 of 18,150 PC observations. The output-slot acquire has no samples, and the two epilogue joins have small sample counts. This does not justify a new output-ownership mapping or another late-acquire experiment.

The whole-kernel hardware counter does report 665,592 shared-store bank conflicts and 1,273,840 shared-store wavefronts. Those totals must not be assigned to the gated store layout: the independently collected instruction-level source counters report no excess at any output store. NVIDIA documents that aggregate counters can include cross-client contention between shared-memory and L1 accesses to the same physical banks. The measured disagreement is retained rather than discarded. [NCU shared-memory guidance](https://docs.nvidia.com/nsight-compute/ComputeTriage/#symptom-shared-memory-bank-conflicts-are-significant), [source metric definitions](https://docs.nvidia.com/nsight-compute/NsightCompute/).

## Source, geometry and execution

- Retained `2b8eb9d8f72ceda3952fbb05054fee97173fc9c7`; W4 kernel `5e61d045...`. The immutable `candidate-w4-paired-situ` inventory is byte-equivalent to this retained revision across all 13,245 files. It was reused as the output-ring experiment's **control**; an inherited `identity_boundary` sentence describes that separate experiment, but no output-ring or clamp candidate is selected here.
- V41F TP4, 4096 tokens, 384 local experts, top-6, H5120, local intermediate576. Frozen FC1/FC2 tactic: logical `(256,128,256)`, cluster `(2,1)`, raster along M. FC1 is actual CLC with PDL; FC2 is static with PDL. Both explicit choices and routing identities match the saved native winner.
- Logical M256 is a two-CTA group, each with physical M128, not two M128 channel tiles per CTA. Gating produces M64 output per CTA. FC1 stages: raw4, transformed2, accumulators2, output4, metadata1. Actual launch640 threads, initial96 registers, zero local bytes, 222,208 dynamic shared bytes; shared-memory occupancy limit is one CTA per SM.
- Recovery node `fi-gather-pipeline-recovery-1030`, C2/ziangli; GPU0 UUID `GPU-b7ed3e57-a8c2-743e-2dda-8ac02a384d8a`, B300, driver595.91.07. Original pinned runtime and persistent C++/CuTe caches remained unchanged. All four release module hashes and Ninja no-op checks passed before/after. Full source pre/postflight passed. GPU0 was released after capture.

## Native timing, not NCU timing

The unchanged cold-L2 CUPTI CUDA-graph harness collected two 100-sample retained-only passes with 10 warmups. Every saved sample span was replayed from the actual activities. There was no fallback, retuning, source instrumentation, sanitizer or external-baseline rerun.

| Native median, µs | Pass 0 | Pass 1 |
|---|---:|---:|
| E2E | 553.7955 | 540.9155 |
| Routing | 9.5840 | 9.3760 |
| FC1 duration | 299.4735 | 291.4905 |
| FC1 critical-path extension | 298.6420 | 290.9460 |
| FC2 duration | 195.2810 | 191.6810 |
| FC2 critical-path extension | 183.1375 | 179.6175 |
| Combine duration | 69.5850 | 68.8490 |
| Combine critical-path extension | 61.7285 | 61.2325 |

E2E phase variation is 2.381%; all 200 samples remain. All eight measured clock quartiles have SM2032MHz and reason0, with no gaps. Normal observed clocks do not erase that variation. These retained-only observations establish component scale; they are not a speedup comparison.

## FC1 diagnostic counters

NCU uses stock-clock, cache-preserving **application replay**, followed by a separate SourceCounters pass. It perturbs execution and overlap. The 291.936µs NCU duration is not substituted for the native durations above.

| FC1 diagnostic | Value |
|---|---:|
| DRAM read / write | 1,365,291,520 / 87,771,392 bytes |
| DRAM throughput | 64.89% of peak |
| L2 throughput / read hit rate | 47.97% / 44.14% |
| Tensor active | 56.65% of peak sustained elapsed |
| Issue active | 59.50% of peak sustained active |
| Long / short scoreboard | 54.09% / 1.42% active-warp observations |
| MIO / barrier stalls | 0.39% / 0.47% active-warp observations |
| Wait / math-pipe stalls | 9.51% / 5.28% active-warp observations |
| Active warps per scheduler cycle | 4.73 |

Twenty returned FC1/FC2 ELF captures across the NCU application replays have unchanged source/compiler options and zero local storage. All FC1 ELF hashes are identical (`b1e3b692...`); all 1,776 NCU PCs match this exact loaded binary after explicit address/printer normalization. FC2 was compiled/captured by the native public call but was not NCU-profiled.

## Output instruction attribution

| Native scope | PC(s) | Dynamic warp instructions | PC samples |
|---|---|---:|---:|
| 16 gated BF16 stores | `0x4b20`–`0x4c80` | 603,520 | 33 |
| Shared publication fences | `0x4c90`, `0x4ca0` | 75,440 | 20 |
| Publication join and dependent branch | `0x4cb0`, `0x4cc0` | 75,440 | 70 |
| TMA store and commit | `0x4d10`, `0x4d20` | 18,860 | 5 |
| Output slot acquire | `0x4d30` | 9,430 | 0 |
| Scratch-reuse join and loop compare/branch | `0x4d50`–`0x4d70` | 113,160 | 32 |

Each `STS.U16` executes37,720 times with all32 lanes active, N-way1,37,720 achieved/ideal wavefronts and0 excess. Source lines2480–2507 fold paired up/gate rows into the existing reduced-M output tile; lines2509–2526 retain the proxy fence,128-thread publication join, one-warp TMA issue/commit/acquire and reuse join. The source-correlated result supplies no case for a bank-remapping change. Shared-store counters, instruction counts, and PC observations describe different quantities; the sample ratios are not runtime fractions.

The much larger sampled dependencies are the epilogue waiting for accumulator publication (3,418 observations, barrier base0xb0), the transform raw-readiness query/result path (1,247, base0x10), gathered activation-slot reuse (1,213, empty base0x90), weight raw-slot reuse (719, base0x30), and scheduler metadata-slot reuse (844, base0xd8). These are mapped from the actual `SharedStorage` offsets, role control flow and out-of-line wait destinations. Necessary producer/consumer waits can accumulate observations because other roles are doing useful work; their counts do not prove removable latency.

## History and stop boundary

The old `w4-output-acquire-iket-b52/RESULTS.md` already includes V41F TP4/4096 and a roughly32ns output-acquire scope; it did not include the preceding writer publication join or bank counters. The prior N3U W4 profile is nongated. This new source-bound gated capture closes that missing diagnostic boundary and agrees that output acquire is not exposed here. Prior late-acquire, raw-readiness, stage-inventory and output-ownership rejections are not reopened. No optimization prototype follows from this result.

Reproducible evidence: `fetch.json` / `evidence.tar.gz` (SHA `f6545952...`), `analysis.json`, `analyze.py`, `store-pcs.csv`, `evidence/fc1-pc/pc-proof.json`, native output logs, raw activity/telemetry records and both NCU reports. All original records are preserved.
