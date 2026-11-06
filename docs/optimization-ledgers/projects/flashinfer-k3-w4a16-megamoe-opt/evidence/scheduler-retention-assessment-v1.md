# Completed scheduler retention evidence

The completed K3 comparison shows a concrete small-decode benefit from the scheduler change, with intermediate-decode counterexamples. This is the requested independent AUTO24 comparison; it does not isolate one fixed tactic. No source decision is made here.

| Model | ON/OFF all 11 | Decode 4–512 | Prefill |
|---|---:|---:|---:|
| deepseek-v41-flash | 0.984286× | 0.978551× | 0.999746× |
| kimi-k3 | 1.012860× | 1.018488× | 0.998005× |

Above 1 favors ON. T1/T2 remain in the full report but are excluded from these aggregates.

- **K3 visible ON wins:** T4/T8/T16/T32 have 5.47%/5.47%/5.59%/1.96% lower ON latency, with nonoverlapping p25–p75 bands. T8 and T16 select exactly the same full tactic on both arms; T4 and T32 change tactics.
- **K3 visible OFF wins:** T128/T256 have 2.77%/2.19% lower OFF latency and nonoverlapping bands, with identical full tactics. They must remain visible beside the small-decode gains.
- **K3 prefill:** ON is 1.31% lower at T4096; OFF is 1.67% lower at T8192 and 0.24% lower at T16384. Every prefill pair has overlapping p25–p75 bands; the prefill geometric mean is effectively flat.
- **DeepSeek V4.1 Flash:** the full11 result mildly favors OFF; do not call every shape flat. T4 and T32 favor OFF with separated bands, while T512 and T8192 favor ON with separated bands. T4 changes group tactics, so it is not a fixed-tactic result. Only T32 of those four has the same full selected tactic.
- **Catalog:** all13×8 rank winners on both sides of both models belong to the retained16 catalog. No removed M128/N64 or M128/N128 tactic wins. No omitted point, source/runtime/model mismatch, or sample-count failure was found.

The user criterion asks for a concrete K3 benefit while V4 Flash is roughly flat. K3's small-decode benefit is visible in the completed evidence; it is selective, not uniform. The owner should weigh the preserved K3 T128/T256 losses and DSV per-point differences when applying that criterion.

Each arm is one fresh process group with 100 untrimmed cold-cache CUPTI samples. IQR separation is descriptive within-run evidence, not a repeated-run confidence statement. No models or samples are pooled, and no additional retention threshold is invented. Hot selection scoreboards are separate from these final medians.

Full medians, p25–p75 ranges, both selected tactics, original BEFORE context, complete raw samples, and source/runtime validation are in [scheduler-auto-complete-v1.md](scheduler-auto-complete-v1.md) and its JSON. The JSON SHA256 is `409c8e3dc568f2b078f8b55440bc9c1d7b5257e36d9255a8785fc9c0d6c73f02`.
