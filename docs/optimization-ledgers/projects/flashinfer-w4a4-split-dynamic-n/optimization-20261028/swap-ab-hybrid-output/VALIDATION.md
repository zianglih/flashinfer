# Swap-AB hybrid output validation

Validation is local experiment evidence, not a new repository test or sanitizer run. Sources are immutable snapshots and are verified before and after each paired gate. The R2 padded-output candidate is the control. Existing verified control results are reused when source hashes, inputs, shape, and selected configurations match.

## Contract

The helper uses the public benchmark wrapper with fixed tactics and captures intermediate buffers through observation hooks. Each configuration runs 64 graph replays: static/CLC × PDL off/on × 16 routing patterns. Patterns include balanced/skewed routing, no local tokens, reactivation, full and partial route tiles, and below/at/above the 16/32/64-row store boundaries. Valid intermediate rows are canonicalized by expanded route ID before hashing. Valid FC1 payload, FC1 scales, FC2 payload, per-token quantized FC2 input/scales where applicable, and final outputs must exactly match R2. Final outputs must remain finite. Captured compile metadata verifies actual CLC and PDL mode.

Owned output padding is diagnostic, not a public output contract. Initial probes required poisoned padding to remain untouched and stopped on that stricter assertion in some FC2 cases. Subsequent probes record the observation while retaining all valid-output equality checks. These stops are preserved separately and are not CUDA errors or valid-output mismatches. No sanitizer was run.

## Completed results

| Immutable snapshot | Paired exact graph replays | Captured GEMM compilations | Spill sites |
| --- | ---: | ---: | ---: |
| Original FC2 hybrid `fc2-01` | 128 | 16 | 0 |
| Native FC2 hybrid `fc2-native-03` | 512 | 64 | 0 |
| FC1 payload hybrid `fc1-02` | 384 | 48 | 0 |

Native FC2 covers NVFP4, per-token NVFP4, MXFP8, and MXFP4x8; route tiles16/32/64/128/256; one/two CTA; SwiGLU, SiTU, and ReLU². FC1 covers all four formats, route tiles16/128/256, one/two CTA, SwiGLU/SiTU, and an additional intermediate192 two-CTA channel tail. Every selected configuration includes CLC/static and PDL off/on. These are bounded representative gates, not the complete activation/output-dtype matrix; direct FP16/FP32 FC1 intermediates and GeGLU were not separately exercised in this round.

All valid-output hashes match R2 exactly. No tensor-map replacements and no local-load/store spill sites were found in any captured candidate compilation. Full summary: `validation-summary.json`. The timing owner was notified of initial passes promptly and all correctness GPU reservations were released after completion.

## Initial development failures

- `fc2-native-01`: CuTe DSL TYPE_UNSTABLE_JOIN from reusing `token` across dynamic branches. Root renamed tail locals in `fc2-native-03`.
- `fc1-01`: IR dominance failure from reassigning `channel` inside an elected TMA issue region. A line-info retry identified `channel //= 2` at line941. The owner moved the independent `payload_channel` calculation outside the dynamic/elected regions in `fc1-02`.
- The first line-info helper retry selected a subset of a multi-config control and failed the helper's strict selection check before compilation. The corrected retry preserved the full selection and localized the source issue.

## Evidence

- Source/deployment manifests live under each snapshot directory.
- `fc2-01/evidence-metadata`: original hybrid path, exact NVFP4 N128 and per-token N256 representative replays, plus initial stricter padding observations.
- `fc2-native-03/evidence-metadata`: native packed-fragment FC2 gates and PTX/CUBIN resource metadata.
- `fc1-02/evidence-metadata`: FC1 payload TMA gates when fetched.
- Full PTX, SASS, and CUBIN artifacts remain in persistent remote gate directories; local metadata retains exact artifact paths.
- `native03-instruction-summary.json`: fixed NVFP4 N128/2CTA FC2 static instruction/resource comparison. No spills; the unrolled scalar tail path increases code size and registers. Static instruction-site counts are not runtime instruction counts.

The performance owner controls timing runs and acceptance. Correctness results alone do not establish a performance improvement.
