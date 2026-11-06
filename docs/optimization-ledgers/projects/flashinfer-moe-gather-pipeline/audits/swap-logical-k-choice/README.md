# Logical-K-aware automatic swap K selection: close without prototype

Source: retained `c1ac8ce7`, swap kernel SHA `482b636a`. This is a source/history audit, not a new performance experiment. No source, cache, or GPU operation was performed.

The decisive scope result is that **all 364 published swap cells explicitly select K steps 4 or 8 for both FCs**: 728 explicit choices, no automatic choices or recorded defaults. Changing only `_select_k_steps` would change none of these cells. [Replay and full choices](choices.json) are reproducible with [replay.py](replay.py).

| TP model | FC1 logical K | FC2 logical K | Supported selected tile K |
|---|---:|---:|---|
| V3 | 7168 | 256 | FP4: 256/512; MX: 128/256 |
| V41F | 5120 | 576 | FP4: 256/512; TP MX unsupported |
| K3 | 3584 | 384 | FP4: 256/512; MXFP4x8: 128/256 |
| N3U | 2048 | 640 | FP4: 256/512; MX: 128/256 |

`K=320` is not in this frozen model matrix. EP FC2 K is respectively 2048, 2304, 3072, and 5120. Every selected FC1 tile divides its logical K exactly.

Current constructor selection is conditional on `k_steps is None` (`moe_swap_ab_kernel.py:1541`). `_select_k_steps` at line 1829 maximizes stage count × tile K over 8/4, subject to existing capacity and overlap constraints. The tuner enumerates explicit 4/8 choices (`moe_swap_ab_tuner.py:41`); its fallback default alone uses `None`. The launcher already knows logical K and includes it in its compile-cache key (`moe_swap_ab.py:119,173`), but does not pass it to the constructor. An automatic-only change would need a private constructor/selector handoff or relocate selection; no new public knob is necessary, but it would not address the observed matrix.

Nominal full-stage padding is not extra logical MMA work or a measurement of DRAM traffic. Current full-stage TMA/SF transactions remain, with OOB zero fill, while the final-stage MMA and SFA/SFB copies use the peeled logical tail (`moe_swap_ab_kernel.py:2499,2544,3189–3286`). Examples for FP4:

| Logical K | K256: stages / nominal padded K | K512: stages / nominal padded K |
|---:|---:|---:|
| 256 | 1 / 0 | 1 / 256 |
| 384 | 2 / 128 | 1 / 128 |
| 576 | 3 / 192 | 2 / 448 |
| 640 | 3 / 128 | 2 / 384 |

Smaller tiles can reduce requested zero-filled extent, but also add issue/acquire/release work. In particular, K384 has identical nominal padding with an extra stage at K256. The persistent stage ring also spans work tiles; logical K shorter than ring capacity is not by itself evidence of unused buffering.

History already tests the proposed motivation. The [logical-K divisibility trial](../../../flashinfer-w4a4-split-dynamic-n/evidence/stage-ktail-r1/NOTES.md) selected K256 instead of K512 for nine narrow V41F FC2 policies at K2304. Its fixed-route paired speedups were **0.9891×, 0.9909×, and 0.9826×** at T8/T16/T512; the unchanged N128 control was 1.0009×. Reduced padding did not offset shorter-tile pipeline cost. This predates the current gather kernel, so it is supporting history rather than a measurement of the present source.

The separate [FC2 K/depth diagnostic](../../../flashinfer-w4a4-split-dynamic-n/scripts/fc2_kstage_experiment/README.md) removed the maximum-buffering confound. Minimum-depth homogeneous gains were small (+0.257% NVFP4, +0.676% MXFP8), while MXFP4x8 lost 3.604%; it rejected a universal K/depth policy. Physical ring caps and W4 stage balancing are separate closed mechanisms and are not proposed here.

**Decision:** close without prototype. There is no affected frozen automatic choice or new native signal that justifies another K-selection policy. Do not override explicit winners, add an axis, shrink the ring, or infer speedup from padded extent alone.
