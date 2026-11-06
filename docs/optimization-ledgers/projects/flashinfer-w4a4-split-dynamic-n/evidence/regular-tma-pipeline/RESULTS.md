# Separate FC1 TMA pipelines: rejected

Moving B/SFB TMA to idle warp1 and giving it a separate ring does not justify retention. N128 regresses at 8K in both orders and its 16K result changes sign. N256 regresses in both orders at both token counts. This conclusion concerns the separate-pipeline delta; the regular-TMA preparation and core are the control.

No production source was edited. The independent clone and all three source files remain unstaged. No additional dtype timing, sanitizer, or profiling was launched after this gate.

## Validation and method

20/20 low-level paired cases pass using actual-source host preparation and kernel versus the frozen442 numerical reference. The cases cover NVFP4 K tails, per-token modes, NB2, N256, and N16/32/64 controls. All 24 native rows match complete inputs, routing, and final output across both orders for each geometry/token count. All 2,400 individual timing samples are retained, and final outputs remain exact after timing.

B200 GPU6, CUDA13.2, nvcr.io/nvidia/pytorch:26.05-py3, CuTeDSL4.7.1. Fixed-tactic native DeepSeek routing: hidden7168, intermediate2048, top-k8, 32 local experts. Preparation is included in each full-chain invocation. Every row uses a new process, 10 warmups and 100 cold-L2 CUDA-graph CUPTI samples. Native candidate cache paths stay unchanged; each arm has a private CuTe cache.

Forward order is control/pipeline/control, tokens8K then16K. Reverse is pipeline/control/pipeline, tokens16K then8K. The comparison below averages the two bracket-arm medians where applicable; speedup is control/pipeline.

| N | Order | Tokens | Control us | Pipeline us | Speedup | Latency change |
|---:|---|---:|---:|---:|---:|---:|
| 128 | forward | 8192 | 302.9600 | 304.6080 | 0.994590 | +0.544% |
| 128 | forward | 16384 | 510.2965 | 512.4645 | 0.995769 | +0.425% |
| 128 | reverse | 8192 | 303.5845 | 304.7765 | 0.996089 | +0.393% |
| 128 | reverse | 16384 | 513.1525 | 507.6970 | 1.010746 | -1.063% |
| 256 | forward | 8192 | 290.3600 | 290.9760 | 0.997883 | +0.212% |
| 256 | forward | 16384 | 479.6805 | 481.3605 | 0.996510 | +0.350% |
| 256 | reverse | 8192 | 290.5605 | 291.0085 | 0.998461 | +0.154% |
| 256 | reverse | 16384 | 479.2970 | 483.0810 | 0.992167 | +0.789% |

## All raw medians

| N | Order | Arm | 8192 us | 16384 us |
|---:|---|---|---:|---:|
| 128 | forward | control0 | 302.8000 | 510.0645 |
| 128 | forward | pipeline1 | 304.6080 | 512.4645 |
| 128 | forward | control2 | 303.1200 | 510.5285 |
| 128 | reverse | pipeline0 | 304.2250 | 507.9370 |
| 128 | reverse | control1 | 303.5845 | 513.1525 |
| 128 | reverse | pipeline2 | 305.3280 | 507.4570 |
| 256 | forward | control0 | 290.5600 | 479.8085 |
| 256 | forward | pipeline1 | 290.9760 | 481.3605 |
| 256 | forward | control2 | 290.1600 | 479.5525 |
| 256 | reverse | pipeline0 | 291.2485 | 485.7130 |
| 256 | reverse | control1 | 290.5605 | 479.2970 |
| 256 | reverse | pipeline2 | 290.7685 | 480.4490 |

## Source and evidence

Base `442d2aa53f68b4640c3ab5118a76f1599ff60d34`. Pipeline core `5faf74ca89b38ef3277013d69dd358ee21590053f99d8a1252a69c2107906fb0`.

[Experiment notes and replay commands](../../scripts/regular_tma_pipeline_experiment/README.md), [machine-readable validation receipt](validation-receipt.json). The directory contains every per-arm JSON with raw samples, exact receipt, command and log. The script directory contains failed and repaired source snapshots, manifests and the pinned harness.

The first smoke failed CuTe IR dominance verification before execution. Cloning the A producer tail state repaired a Python-state alias across producer branches; the failed source and compiler log remain preserved. The corrected variant compiled and passed all subsequent checks.

Validation boundaries: this rejected variant has no six-format matrix or sanitizer run. Fused-finalize is excluded. These fixed-tactic diagnostics are not primary AUTO benchmark evidence.
