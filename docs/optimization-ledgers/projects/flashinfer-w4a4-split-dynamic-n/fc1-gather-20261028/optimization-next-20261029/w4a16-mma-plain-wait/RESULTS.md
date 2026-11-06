# W4 MMA plain A wait

Status: **approved for retention by the parent**, as a source/instruction simplification with near-neutral broad timing. The stable V3 TP16K−0.911% tradeoff is accepted. Preserve K3 EP4K−3.959% and its state/repeat uncertainty; do not claim no regression or a causal end-to-end speedup. Retained and pushed as `9037f6d46fcb45eac04be04c182104336c8b1e7c`. The old review copy was retired after514-file verification:513 match canonical and the only intentional difference is the already-retained swap kernel. Exact proofs are in `retention-source.json` and `retirement.json`. GPUs3/6 are released; no more runs needed.

- Base: `e780f02cc1f8a7e59f22b8bda6f7acd8f8792b24`. One file, **1 addition / 15 deletions**. Kernel SHA256 `1b39c23e1f8cf148ab48d53541ec21639c54c3f36f989b768726c45f1fd3061b`.
- Both remote source arms are independent immutable materializations with actual Git HEAD `1b0f1f69acbb7e20055d5aaf76cc29c840779304`; all514 source hashes bind the logical e780 control and candidate. Exactly one W4 file differs between arms. Persistent C++/CuTe caches and stable whole-data symlink are retained.
- `d9-source-equivalence.json` verifies all514 current d9 files: only the unrelated swap-AB kernel differs from e780. W4 and transitive wrapper/prepare/benchmark/test source is identical. No gate was restarted for that unrelated update.
- The MMA warp now waits directly on A, as it already does for B. Its discarded cached token previously polled at the end of the K iteration immediately before the next wait, without independent MMA/TMA work between them. All synchronization, pipeline transitions, stages, quotas, tactics and math remain. DQ's useful earlier peeks are unchanged.
- Source AST proof changes only `kernel`; `_transform_tile` and `_issue_mma_tile` are identical. Own-file pre-commit passes.

## Codegen

Fresh paired captures use N16/N128/N192 with the existing native choices. All three remove exactly12 non-NOP instructions: two TRYWAIT sites, one branch, two PLOP3, two phase shifts, one last-K compare, one counter increment, two address operations and one initialization. No opcode-count increase, resource-attribute change or local-memory spills.

| N | Control non-NOP | Candidate non-NOP | Delta | Local bytes |
|---:|---:|---:|---:|---:|
|16|1626|1614|−12|0→0|
|128|1955|1943|−12|0→0|
|192|1985|1973|−12|0→0|

Generated code and the CUTLASS/Rubin dependency proof are in `DESIGN.md`, `codegen-analysis.json` and `codegen-qualified.json`. Initial paired-codegen archive SHA256 `375aa105b093e3520639c5d1499e943120f27708ae5893353244f3de9be792e6` (502,628 bytes).

## Existing correctness gate

```text
.................................                                        [100%]
33 passed, 1661 warnings in 42.49s
```

No failures/errors/skips. The existing selection includes FC1/FC2, one/two CTA, static/CLC, route boundaries, weight layouts, SiTU and GeGLU. All33 captured kernels have zero local storage and no LDL/STL (22 gather,11 FC2/regular). No new repo test, oracle change or sanitizer. `exact-codegen-qualified.json` records every capture. Exact/codegen evidence archive SHA256 `6c686e1d3861f3070abac440ee3356835e44391598ee529bda32df8b2b3cdeb7` (2,697,382 bytes).

## Fresh 24-cell performance

Eight model/topology jobs, tokens8/4096/16384: V3 EP8/TP8, V41F EP4/TP4, K3 EP8/TP8 and N3U EP8/TP8. Fresh paired C-A-A-C, unchanged frozen native cache choices (including existing default sentinels), route/tactic/source/runtime guards,10 warmups and100 strict CUPTI cold-L2 CUDA graph samples per cell. No AUTO, retune or clock changes. Read-only2ms NVML telemetry and raw quartiles are retained. W4 uses BF16 input directly, regardless of the family's include-activation-quant CLI flag.

No timings are reused from the rejected W4 batching experiment. Each job remains on one physical GPU for all four phases; lane plan is fixed in `perf24/lane-plan.json`.

Each phase is the median of100 samples; each arm is the median of its two phase medians (the arithmetic mean for two values). Change=control/candidate−1. Same-arm spread=max/min−1. These spreads and rawquartiles matter because samples within a phase are not independent under clock/power-state drift.

| Shape | Tokens | Control ms | Candidate ms | Change | C/A phase spread |
|---|---:|---:|---:|---:|---:|
| V3 EP8 | 8 | 0.06953650 | 0.06897600 | +0.813% | 0.138% / 0.048% |
| V3 EP8 | 4096 | 0.28909725 | 0.28907950 | +0.006% | 0.828% / 0.162% |
| V3 EP8 | 16384 | 1.19362300 | 1.17394275 | +1.676% | 0.314% / 1.993% |
| V3 TP8 | 8 | 0.05685650 | 0.05689550 | -0.069% | 0.028% / 0.002% |
| V3 TP8 | 4096 | 0.47356975 | 0.47552675 | -0.412% | 0.169% / 0.011% |
| V3 TP8 | 16384 | 1.69877475 | 1.71438725 | -0.911% | 0.094% / 0.413% |
| V41F EP4 | 8 | 0.05092825 | 0.05112850 | -0.392% | 0.064% / 0.031% |
| V41F EP4 | 4096 | 0.43934600 | 0.43884950 | +0.113% | 0.044% / 0.182% |
| V41F EP4 | 16384 | 1.47508625 | 1.46712625 | +0.543% | 7.351% / 4.711% |
| V41F TP4 | 8 | 0.06407200 | 0.06372800 | +0.540% | 0.025% / 0.050% |
| V41F TP4 | 4096 | 0.57636350 | 0.56249975 | +2.465% | 5.122% / 0.788% |
| V41F TP4 | 16384 | 1.94438000 | 1.90786000 | +1.914% | 0.738% / 0.088% |
| K3 EP8 | 8 | 0.08450450 | 0.08435300 | +0.180% | 0.133% / 0.152% |
| K3 EP8 | 4096 | 0.56434025 | 0.58760400 | -3.959% | 4.203% / 1.178% |
| K3 EP8 | 16384 | 2.02063650 | 2.03242100 | -0.580% | 0.097% / 2.062% |
| K3 TP8 | 8 | 0.08732075 | 0.08727250 | +0.055% | 0.166% / 0.093% |
| K3 TP8 | 4096 | 0.72545075 | 0.70101900 | +3.485% | 2.282% / 3.264% |
| K3 TP8 | 16384 | 2.41871275 | 2.41727400 | +0.060% | 1.230% / 0.370% |
| N3U EP8 | 8 | 0.05116800 | 0.05108825 | +0.156% | 0.000% / 0.064% |
| N3U EP8 | 4096 | 0.39253775 | 0.39329000 | -0.191% | 0.167% / 0.273% |
| N3U EP8 | 16384 | 1.48931000 | 1.48059850 | +0.588% | 3.421% / 3.202% |
| N3U TP8 | 8 | 0.06621650 | 0.06611250 | +0.157% | 0.121% / 0.048% |
| N3U TP8 | 4096 | 0.54583525 | 0.54649925 | -0.122% | 0.249% / 0.352% |
| N3U TP8 | 16384 | 1.98692400 | 1.96641225 | +1.043% | 0.942% / 0.005% |

Across-cell geometric mean is +0.289% overall, +0.179% decode and +0.344% prefill. These are descriptive aggregates of this bounded screen, not a causal performance claim. Stable tradeoffs include V3 TP16K−0.911% and V41F EP8−0.392%; V3 EP8+0.813% and V41F TP16K+1.914% are positive with lower phase spreads. No row is discarded.

K3 EP4K is −3.959%, with control/candidate spreads4.203/1.178%. Its C-A-A-C medians are0.575956/0.584164/0.591044/0.5527245ms. First quartiles are0.549316/0.546787/0.547716/0.5521ms; last quartiles0.614339/0.61642/0.615876/0.628229ms. Large within-phase transitions strongly affect the median; the first/last quartile similarity does not establish source neutrality and the negative remains unresolved. K3 TP4K's+3.485% also has appreciable spread. Read-only NVML may be stale; no frequency-normalized or external-noise causal claim is made. Source-induced utilization changes can themselves change clock/power behavior.

The simplification removes proven redundant instruction/state work and source lines. Parent approved retention on that basis and the near-neutral broad timing, accepting the stable V3 TP16K−0.911% tradeoff. K3 uncertainty remains explicitly disclosed; no no-regression or causal end-to-end speedup claim is justified. Independent recommendation agrees with retaining the simpler policy under these documented limits. No additional repetitions are needed or launched.

All raw CUPTI100-sample vectors, routes, source manifests, cache/winner receipts, loaded-kernel resource guards, phase quartiles and read-only telemetry are in`perf24/evidence`. `perf24/qualification.json` verifies all8jobs/24cells and zero local storage in every observed kernel. Archive SHA256 `9e45bf00f335af58d62bc007aa5d49280c8a5e697395a02c2ff83d3489e06ee4` (19,933,688 bytes).
