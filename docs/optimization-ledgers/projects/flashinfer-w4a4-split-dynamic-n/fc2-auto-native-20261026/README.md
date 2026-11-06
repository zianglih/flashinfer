# Independent FC2 scheduler native AUTO screen

The candidate adds an independent sixth internal tactic field for FC2 CLC scheduling. Legacy three/four/five-field tactics still use static FC2. The existing FC1 choice stays independent. No problem, shape, or dtype dispatch thresholds are added.

- A: frozen retained implementation, patch `8828ab24d607c27905ab6b53e19ad278869fd84655f1d96b289e43eb0bdcd03b` over `0def601d`; subsequently published as `dd266b91`.
- B: A plus scheduler choice, patch `2d1a8e5dc7e548a023d15fa58f80f586f5e2c561519ed5a6cbd4bd6ab1eaa0d0` over `0def601d`.
- Remote `c3/infra`, devbox `fi-moe-nvfp4-port-1026`; B300, CUDA13.2, `nvcr.io/nvidia/pytorch:26.05-py3`.
- GPUs6/1/3: K3 EP8, V41-flash EP4, V3 EP8, respectively.
- K3 tokens64/128/512/4096; V41 tokens64/128/4096; V3 tokens32/128/4096.
- Standard NVFP4, MXFP8, and MXFP4x8. The normal NV selector also includes unchanged W4A16. Per-token is omitted here and remains in the eventual full-table campaign.

Each family is measured in A–B–B–A order on the same GPU. A uses the exact frozen native choices from the completed retained full sweep; B starts with a fresh absent timing cache and performs unrestricted native AUTO, then replays its own selections. This is intentionally an expanded-native-choice screen, not fixed-tactic isolation of one kernel change. The observer records chosen tactics per measurement. Sources and replay cache files are verified unchanged; routing identities match the retained full sweep.

Timing uses the public benchmark:10 warmups,100 cold-L2 CUPTI CUDA graph samples, deterministic two-stage CuTe finalization; NVFP4 includes input quantization. The observer captures raw samples only inside the public measurement function, leaving native AUTO profiling unchanged. TRT is not rerun in this internal screen. Fresh full final tables remain required for retained public results.

The first observer launch rejected the saved cache's additional profiling-metadata field before measurements. Only the observer comparison was corrected to compare runner and tactic while preserving metadata; all jobs restarted in a fresh `fc2-auto-native-20261026-r2` output folder. Sources were unchanged.

The source-paired exactness gate is separately archived at `../fc2-clc-20261026/scheduler-gate`:64 control+128 candidate replays, PDL off/on, independent scheduler choices, one/two CTA and narrow/wide N configurations, and changing/empty/reactivated routing. No new upstream tests or sanitizer claim.

Helpers: `../scripts/fc2_auto_native_20261026/`. Completed: all 6 family screens / 24 processes / 40 measured cells (30 affected cells and 10 incidental W4A16 controls). `validation.json` verifies 16,000 raw timing samples, unchanged sources/replay caches, exact routing identities, and stable repeated native choices. `evidence/collection.json` hashes all 150 collected files. `results.md` contains every paired ratio; `summary.json` preserves full precision and complete A/B tactics.

Affected-format geometric means (A/B, larger is better):

| Model | Decode | Prefill4096 | All screened cells |
|---|---:|---:|---:|
| V3 | 0.999737x | 1.000411x | 0.999962x |
| V41-flash | 1.010939x | 0.997939x | 1.006587x |
| K3 | 1.006985x | 0.999626x | 1.005140x |
| All | 1.006034x | 0.999325x | 1.004017x |

Native B selects FC2 CLC for 20 of 21 decode cells and 1 of 9 prefill cells. K3 mixed T512 correctly retains static FC2, avoiding the earlier unconditional-CLC regression. K3 NV decode improves 0.7–1.4%; V41 MX decode improves 1.0–1.5%, with both comparisons in each pair positive. K3 mixed decode gains are small (0.19–0.21%).

Tradeoffs: V3 MXFP8 T32/T128 regresses 1.09%/0.77%; its native choices also change route N and FC1 scheduling, so these are broader selection effects. V41 NVFP4 prefill regresses 0.47% while keeping FC2 static and changing FC1 K8 to K4. Do not attribute the noisy unchanged W4A16 controls to this change; they are excluded from these aggregates.

Recommendation: advance the independent scheduler choice to the final combined full-table campaign. It produces consistent gains at the target V41/K3 decode gaps while avoiding the large forced-CLC prefill regressions, without model/dtype dispatch. The aggregate gain is modest, and the V3 MXFP8 native-selection tradeoff should remain visible. This screen does not itself replace final full public measurements or decide publication.
