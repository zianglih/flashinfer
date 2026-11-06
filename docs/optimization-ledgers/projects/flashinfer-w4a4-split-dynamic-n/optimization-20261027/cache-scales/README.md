# Shared weight and scale cache-policy screen

C is e2728, W is route reuse-aware payload policy with explicit warp0 ownership, S applies the same policy to payload and weight scales. C0/W1/S2/S3/W4/C5, four token counts, matched frozen native winners/routes; 10 warmups and 100 cold-L2 CUPTI samples. All 12 phases and 48 medians passed source/cache/result hash and raw-sample verification.

| Model | Tokens | W vs C | S vs C | S vs W | S vs W forward / reverse |
|---|---:|---:|---:|---:|---:|
| nemo3-ultra | 4 | -0.21% | -0.23% | -0.02% | -0.04% / +0.00% |
| nemo3-ultra | 128 | -0.28% | -0.15% | +0.13% | +0.12% / +0.14% |
| nemo3-ultra | 4096 | -0.63% | -0.69% | -0.06% | -0.10% / -0.02% |
| nemo3-ultra | 16384 | +8.16% | +9.14% | +0.90% | +0.79% / +1.02% |
| v3 | 4 | -0.67% | -0.62% | +0.05% | +0.17% / -0.07% |
| v3 | 128 | -0.05% | -0.05% | -0.00% | -0.02% / +0.02% |
| v3 | 4096 | -0.30% | -0.50% | -0.20% | -0.30% / -0.11% |
| v3 | 16384 | +5.30% | +7.79% | +2.37% | +5.10% / -0.30% |

Eight existing exact smoke cases passed (four per snapshot). Generated PTX confirms narrow-SFB steady-state neighbor loads are skipped by warps 1–3; startup remains warp0-only. S uses the same runtime register for weight payload and SFA TMA. Runtime policy is initialized on all paths; no added barrier or tactic axis.

Nemo 16K confirms the SFA change improves both directions. V3 16K S-versus-W varies across repeats; treat its extra gain as provisional. Both S and W preserve decode within 0.7% in this bounded screen. Full four-model/all-dtype candidate selection remains pending.

Raw six-pass medians, 100samples each, source snapshots, native winner cache, receipts and gates are preserved under evidence/. Source hashes and exact ratios are in summary.json.
