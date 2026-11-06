# Cumulative W4 prefill: bounded source attribution

Read-only assessment of the completed `82254e20 → c1ac8ce7` 24-cell comparison. No new compilation, profile, timing, source edit, commit or publication. The actual recorded configurations narrow which changes can affect the two adverse cells; they do not establish a causal instruction-level regression.

| Actual measured stage | Logical K / stage K | Transform fragment cap | Tail | Source changes that can alter this active path |
|---|---:|---:|---:|---|
| V41F EP4 T8192 FC1: M256/N192, 2CTA, CLC, PDL | 5120 / 256 | 128 | 0 | `02de` packed-scale byte selector |
| V41F EP4 T8192 FC2: M256/N192, 2CTA, static, PDL | 2304 / 256 | 32 | 0 | No active arithmetic/tail/SiTU operation change identified |
| N3U TP8 T16384 FC1: M256/N128, 2CTA, CLC, PDL | 2048 / 256 | 128 | 0 | `02de` packed-scale byte selector |
| N3U TP8 T16384 FC2: M256/N128, 2CTA, static, PDL | 640 / 256 | 32 | 128 | `bf072d26` unused-tail-group skip and `c1ac8ce7` cutoff calculation |

The shapes and actual CLC/PDL values come from every phase's `w4_resolved_configs`, joined by `compiled_library` to its resource receipt. The public tactic's trailing `True` means raster-M, not CLC. V41F uses its explicit N192 tactic; N3U uses recorded default `-1`, which resolves to N128. All four phases have the same resolved geometry and resources.

`moe_w4a16.py:131` chooses fragment cap128 when activation is present, otherwise32 unless logical K equals stage K. Both FC2s have no activation and K greater than256. Their actual decoder fragment must therefore be32: `_setup_transform_partitions` caps it at32, while `decode_nvfp4_fragment_to_bf16` only accepts32/64/128. `scale_count` is2. The `02de` implementation deliberately retains that two-scale extraction branch and passes `byte_index=0`, so its PRMT immediate and conversion operations are unchanged. FC1 selects cap128 and is eligible for the packed4/8-scale selector path; no exact current winner opcode count is inferred from that source eligibility. See [wrapper](../flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16.py#L131), [partition](../flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py#L639), [decoder](../flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_utils.py#L171).

The two transform warpgroups each own128 K elements. The tail guard is `0 < K%256 <= 128`. It is false for both V41F stages and N3U FC1. N3U FC2 has three stages and a128-element tail: `bf` omits the second group's unused final-stage transform while preserving pipeline participation; `c1ac` computes its live-stage cutoff once instead of rebuilding the K coordinate per stage. `2b8eb9d8` changes only SiTU; V41F is parameterized SwiGLU with no SiTU beta, N3U is Relu2, and FC2 has no activation. `49c91adf` only changes the separate swap kernel. Neither commit has an active W4 path here. This classification is source-level: compiler layout/scheduling changes from otherwise inactive source refactoring are not excluded without paired native images.

There are **no PTX/cubin/SASS images in these performance artifacts**. The unchanged observer records actual loaded handles, names, driver resources and geometry, not native bytes. A read-only inventory of both new private cache roots found only their JIT log, with no `.o`, PTX or cubin. Thus neither raw binary identity nor an exact endpoint opcode delta is available for these timed functions. [Cache inventory](../experiments/w4-cumulative-prefill/cache-artifact-inventory.json).

Closest preserved evidence:

- [N3U TP16K profile](../profiling/n3u-tp-w4a16-16k/RESULTS.md): exact production shape/tactic under **02de**, with actual loaded FC1/FC2 images, e.g. `evidence/fc1-metrics/loaded-codegen/60651/{fc1,fc2}.{ptx,cubin,sass}`. It is neither the822 control nor currentc1ac endpoint and was captured in another runtime cohort. No paired current endpoint comparison is made.
- [V41F TP4K profile](../profiling/v41f-tp-w4a16-4k/RESULTS.md): **2b8** at N128/TP4K, not the requested EP/N192 case. Do not relabel it as the measured winner.
- [Selector qualification](../validation/w4-scale-selector-r2/RESULTS.md) and [tail-cutoff qualification](../experiments/w4-tail-cutoff/qualification-summary.json) supply source-qualified small direct cases, including unchanged two-scale FC2 images and affected K640 tails. They do not capture these two cumulative performance handles.

V41F EP8K's first candidate phase has normal clocks and is slower than both controls; FC1/FC2/combine extension deltas are +26.368/+8.576/+0.680µs. The source-active change is in FC1; the FC2 extension increase is not proof of an FC2 code change or a causal cache/overlap mechanism. N3U TP16K has +14.728/+21.464/+1.712µs extensions, with clock exceptions in every phase; its FC2 does activate both tail commits. These results preserve the adverse observations but cannot assign the whole-chain difference to a particular instruction or commit. The separate historical per-commit experiments retain their own source/runtime and repeat boundaries.

All timing is complete and GPUs were released. Optimizations are paused by the user. No follow-up experiment is proposed here.
