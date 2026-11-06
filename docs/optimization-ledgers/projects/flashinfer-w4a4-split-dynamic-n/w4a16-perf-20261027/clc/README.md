# W4A16 shared CLC candidate

Base: `1496b557f9b606f3a0bb36bcebf5293d3e11555a`. Source: `flashinfer-w4a16-clc-review`; changes stay unstaged. The v1 patch and SHA receipt are `v1-shared-clc.patch` and `v1-freeze.json`.

The original 23 geometry pairs each get one shared FC1/FC2 CLC boolean, giving 46 tactics. The launcher no longer infers scheduling from activation presence and problem-cluster count. Internal grouped-GEMM dispatch receives the selected boolean directly. The W4A16 tuner cache has a new explicit signature to prevent stale two-field tactics from entering the new contract.

The scheduler metadata ring has one producer arrival per stage. The elected lane writes the four generic shared-memory values and commits the stage itself. Consumers acquire that stage, copy the metadata to registers, and release it. This removes three scheduler warp barriers and thirteen generic-to-async proxy fences: the metadata never enters an async copy or MMA data proxy. The independent synchronization audit checked the installed CuTe PipelineAsync/MbarrierArray implementation and confirmed that its release/acquire arrivals order these generic accesses. Terminal metadata drains remain because W4A16 does not have the blockscaled implementation's final all-role CTA join.

The existing route-boundary exact test now covers both boolean values across one-CTA, cluster-two one-CTA MMA, two-CTA MMA, mixed FC topologies, route sizes 8 through 192, and two boundary patterns. The private weight-scale mapping test explicitly chooses static scheduling. Local AST parsing, isolated tactic enumeration (unique 46 entries, paired booleans), and `git diff --check` pass. The shared scheduler passed24 exact boundary replays across both scheduler choices, both PDL settings and full/one-cluster static grids. A later metadata-depth candidate also passed8 existing tests, including the final padding test whose explicit W4A16 tuple was updated after this source freeze.

## Follow-up experiments

- Keep the first candidate's geometry and K=256 policy fixed to isolate scheduling and metadata synchronization.
- Test K=128 independently per phase at measured winning geometries before expanding production tactics. Smaller K uses less TMEM per transformed stage, potentially allowing more overlap, but adds TMA/MMA loop overhead. K=512 generally cannot retain the required two transformed stages with current TMEM partitioning.
- The existing tactic space already permits mixed FC1/FC2 M topologies in five pairs. It does not allow independent routed-row N tiles because both phases share tile-index metadata. Separate N is not a free tactic-axis change; it needs an explicit metadata mapping contract.
- Do not repeat rejected old experiments blindly. The historical ledger found early packed-input release, later transformed-stage acquire, striped transform groups, and dual readiness peeks neutral or regressive.

## Completed shared-flag comparison

All three models completed a fresh46-tactic native AUTO search followed by same-GPU control/candidate/candidate/control cache-only runs. Controls reuse the prior1496 native winners; candidate runs reuse their own new winners. All39 token/model points retain100 raw samples per arm, with identical routing identities verified across the four arms. Tokens1/2 are excluded from retention.

| Model | Overall | Decode 4–512 | Prefill 4096–16384 |
| --- | ---: | ---: | ---: |
| V3 EP8 |0.992809x |0.993622x |0.990644x |
| V4.1-Flash EP4 |0.996241x |0.999079x |0.988711x |
| K3 EP8 |1.014004x |1.006835x |1.033371x |

The33-point aggregate is 1.000975x. Treat the change as a scheduler-policy and instruction cleanup with mixed small end-to-end effects, not as a universal latency win. Full token speedups, absolute medians, selected tactics, source hashes and raw samples are in `speedups.md`, `summary.json` and `evidence/`.

The scheduler metadata-depth follow-up was rejected; see `../clc-stage/`. The final root-owned composition adds shared preparation and compile-time weight dimensions, which need their own final measurements.

Analysis clarification: decode/prefill groups were aligned with the retained project methodology (4–512 / 4096–16384). AUTO wall-time fields in `summary.json` now end in `_seconds` after nanosecond conversion. These are analysis-only corrections; measurements were not rerun or changed.
