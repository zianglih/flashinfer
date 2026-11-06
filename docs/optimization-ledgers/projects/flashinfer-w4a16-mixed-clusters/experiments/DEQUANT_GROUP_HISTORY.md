# Decoder warp-group history

Durable source/history context for the mixed4+2 effort. **Keep exactly two decoder warpgroups. No group-count AUTO axis or new implementation is proposed.** This note records a read-only review; it does not add GPU, compiler or profiling results. Further source work waits for the current PC evidence.

## Current supported design

- [Mega W4A16 constructor:288–292](../flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py#L288) fixes two transform warpgroups, eight transform warps at12–19, and640 CTA threads. The maintained [local W4A16 constructor:158–160](../flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py#L158) also fixes two groups. Group count is not exposed by their existing autotuners.
- The inherited [transform partition:348–389](../flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py#L348) divides complete NVFP4 blocks between groups and requires exact divisibility. A field used in layout arithmetic does not make arbitrary group counts supported configurations.
- The inspected historical local CUTLASS checkout is commit`b46b16d003484063bca4ed365e44095c4c6ed633`. Its [grouped mixed-input example:228–233](/Users/ziangli/playground/projects/flashinfer-w4a16/flashinfer/3rdparty/cutlass/examples/python/CuTeDSL/blackwell/mixed_input_gemm/grouped_mixed_input_gemm.py:228) and [ordinary mixed-input example:214–220](/Users/ziangli/playground/projects/flashinfer-w4a16/flashinfer/3rdparty/cutlass/examples/python/CuTeDSL/blackwell/mixed_input_gemm/mixed_input_gemm.py:214) fix four transform warps, or one group; neither is a ready-made group-count tuner. This is the inspected checkout's behavior, not a claim about every CUTLASS version or kernel.

## Mega history: two groups were retained

The historical [performance ledger:44–52](/Users/ziangli/playground/projects/flashinfer-w4a16-megamoe/PERFORMANCE_LEDGER.md:44) explicitly records the user's preference to retain two groups and keep one-group configurations as historical controls. The later [K3 ledger:419–423](/Users/ziangli/playground/projects/flashinfer-k3-w4a16-megamoe-opt/OPTIMIZATION_LEDGER.md:419) preserves the same two groups while expanding M/N geometry.

The [adjacent fitted comparison:3–14](/Users/ziangli/playground/projects/flashinfer-w4a16-megamoe/FITTED_TRANSFORM_GROUP_COMPARISON_001.md:3) tested one versus two groups on older DSV3 H7168/I2048/E256/top8, EP8/B300/CUDA13.2 source. The apparent T64 regression did not reproduce in the [two/one/two repeat:3–41](/Users/ziangli/playground/projects/flashinfer-w4a16-megamoe/FITTED_TRANSFORM_GROUP_REPEAT_001.md:3): both two-group arms were faster at T64 and T4096. This supported retaining two groups; it is neither current GLM5 evidence nor a general performance guarantee.

The initial two-group hang was a resolved register-budget defect. The [failed-capture audit:5–13](/Users/ziangli/playground/projects/flashinfer-w4a16-megamoe/TRANSFORM2_CODEGEN_LIVENESS_001.md:5) records a640×96=61,440-register CTA allocation while requested role targets totaled65,536. It also identified nonuniform control-warpgroup register-donation sites. The [corrected review:25–31](/Users/ziangli/playground/projects/flashinfer-w4a16-megamoe/TRANSFORM2_CODEGEN_REVIEW_002.md:25) records uniform donation and role targets176/80/64/80/80 totaling61,440, followed by successful warmup. Do not repeat the invalid assumption that unused SM registers automatically enlarge the CTA's initial register pool, or describe this resolved failure as a rejection of two decoder groups.

## Earlier split-W4A16 rejection was superseded

The older split ledger [2100–2138](/Users/ziangli/playground/projects/flashinfer-w4a16/w4a16_optimization_experiments.md:2100) rejected a particular half-block/two-group specialization. Later [dedicated two-group work:2877–2907](/Users/ziangli/playground/projects/flashinfer-w4a16/w4a16_optimization_experiments.md:2877), [complete-block ownership:2922–2931](/Users/ziangli/playground/projects/flashinfer-w4a16/w4a16_optimization_experiments.md:2922), and [contiguous block ranges:2985–3012](/Users/ziangli/playground/projects/flashinfer-w4a16/w4a16_optimization_experiments.md:2985) superseded that design and retained the current two-group structure. Preserve the implementation/workload boundary when citing the earlier rejection.

## Stage depth is a different quantity

The historical `w4a16_n64_transform3` artifact means **three decoded-weight TMEM stages**, while retaining two decoder warpgroups. Its [README:1–7,15–37](/Users/ziangli/playground/projects/flashinfer-w4a16-megamoe/candidates/w4a16_n64_transform3/README.md:1) states that N64 uses three stages and N128 keeps two. Current Mega's [TMEM rule:99–113](../flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py#L99) likewise derives three decoded stages for N32/N64 and two for N128. Do not interpret `transform3` filenames as a three-group trial.

No executed three/four-decoder-group trial was found in the bounded historical ledger and candidate-note search. Such counts are not existing supported knobs: changing them would require role/thread, register-pool, barrier-participant and layout admission work.

If PC evidence shows transform-related waiting, first distinguish [raw-TMA readiness:503–507](../flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py#L503) from [decoded-TMEM capacity:519–523](../flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py#L519) and MMA consumption. A decoder waiting for raw input or for a free output stage is not evidence that additional decoder groups would help. No new tuning axis follows from this note.
