# Tiny epilogue release experiment

Frozen source `a9efdc81` at retained `f175faea`; parent retention decision remains pending independent review. The larger register/buffer experiments remain rejected.

The source only publishes the existing gated per-token accumulator release after the last TMEM transpose and before independent token-scale/activation work. No planner, tactic, register policy, math or allocation change.

Exact gate: 32 replays per source, 16 GEMM pairs and 6 prepare pairs; no spills or setmax instructions. The four affected synthetic FC1 pairs have real earlier release scheduling; all other cores and prepare encodings are identical.

| Model | Backend | Tokens | Actual compiled condition | CAAC speedup |
|---|---|---:|---|---:|
| v3 | CuteDSL W4A4 | 4096 | unchanged | 1.000464x |
| v3 | CuteDSL W4A4 | 16384 | unchanged | 0.998581x |
| v3 | CuteDSL PER-TOKEN | 4096 | affected | 1.002201x |
| v3 | CuteDSL PER-TOKEN | 16384 | unchanged | 0.998778x |
| kimi-k3 | CuteDSL PER-TOKEN | 8192 | affected | 1.004389x |
| v41-flash | CuteDSL PER-TOKEN | 8192 | affected | 1.005240x |

Three affected-cell geometric mean: 1.003942x. The six-cell aggregate is 1.001605x. These are bounded diagnostics, not a full-model-grid performance claim. The exact raw samples, source/tactic/route checks and compiler artifacts are in `bounded-screen-evidence/` and `extra-model-screen-evidence/`; `completion.json` binds all summaries.

Actual model resources: V3 affected FC1 has unchanged REG122; K3 FC1 uses REG102→112 with9048 instructions unchanged; V41 FC1 uses REG120 unchanged with5720→5712 instructions. All are spill-free. Actual FC2 and unaffected model core encodings are unchanged.

Final `final-inventory.json` verifies unchanged frozen source hashes, retained native C++/private DSL cache roots, and all eight B300 GPUs idle with no compute process. No further experiments or autotuning are scheduled.
