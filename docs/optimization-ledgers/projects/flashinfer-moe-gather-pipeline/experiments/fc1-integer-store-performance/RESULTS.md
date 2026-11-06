# FC1 integer-carried stores:32-cell screen

Control is production-equivalent retained`bf072d26b163e71458e7e4dfb12e615b19bd2c9a`. Candidate differs only by the final swap kernel`482b636a1714486e2ffb34c8ae005da3cef26f25f0ce034ba1eb59c6198d6276`. Historical`d2aaa`qualification is not timed; the attempted`cdb2`generic recast failed withLOCAL272 before launch and is preserved separately.

All32 cells completed source-bound C-A-A-C with original frozen tactics/routes,10 warmups and100 untrimmed native CUPTI cold-L2 CUDA-graph samples per phase.12,800samples and all seven negative rows are retained. No autotuning, sanitizer or compiler-policy changes. Per-cell ratios use the geometric mean of phase medians; group ratios use the geometric mean of cell ratios.

| Scope | Cells | Geomean |
|---|---:|---:|
| band/all | 32 | +1.233% |
| band/decode | 8 | +0.135% |
| band/middle | 8 | -0.004% |
| band/prefill | 16 | +2.414% |
| mode/CuteDSL W4A4 | 8 | +2.075% |
| mode/CuteDSL MXFP4x8 | 8 | +1.504% |
| mode/CuteDSL MXFP8 | 8 | +1.327% |
| mode/CuteDSL PER-TOKEN | 8 | +0.037% |
| Quantized-payload modes | 24 | +1.635% |

Every quantized prefill cell improves. W4A4 prefill gains are+2.30% to+5.97% with both phase-repeat spreads below0.26%; MXFP prefill gains are+1.47% to+4.72%, but several16K MX repeats are noisier. Decode and128-token results are effectively neutral. Per-token is neutral overall and retains the stable−0.544% EP16K loss; it is an unchanged-store-width comparator, **not** a binary-identical null control (its FC1 instruction stream also changed).

All56 paired guarded native compilation configurations keep identical resources, withLOCAL0 across224loaded-function records. There are17 non2032MHz/nonzero-reason clock quartiles out of512, none missing. Maximum phase-repeat spread is3.78%. No samples or cells are removed for these conditions.

## Complete matrix

| Model | EP/TP | Mode | 4 | 128 | 4096 | 16384 |
|---|---|---|---:|---:|---:|---:|
| nemo3-ultra | EP8 | CuteDSL MXFP4x8 | +0.000% | -0.062% | +3.614% | +3.660% |
| nemo3-ultra | EP8 | CuteDSL MXFP8 | +0.151% | -0.061% | +1.585% | +1.973% |
| nemo3-ultra | EP8 | CuteDSL PER-TOKEN | +0.080% | -0.066% | +0.397% | -0.544% |
| nemo3-ultra | EP8 | CuteDSL W4A4 | +0.115% | +0.047% | +3.664% | +5.965% |
| nemo3-ultra | TP8 | CuteDSL MXFP4x8 | +0.240% | -0.157% | +3.377% | +1.468% |
| nemo3-ultra | TP8 | CuteDSL MXFP8 | +0.090% | -0.094% | +2.353% | +4.716% |
| nemo3-ultra | TP8 | CuteDSL PER-TOKEN | +0.287% | +0.146% | +0.009% | -0.012% |
| nemo3-ultra | TP8 | CuteDSL W4A4 | +0.119% | +0.211% | +2.303% | +4.358% |

## Evidence and boundaries

- Raw bundle: `evidence/fc1-integer-store-screen/1793370953565557000/data`; full phase-median table and component deltas are in sibling`report/`.
- `report/resource-pairs.json` matches deterministic native compilation sequences; it does not claim a richer token-to-library join than the existing swap guard provides.
- `final-gate.json` binds16 selected exact calls/20native pairs. The initial qualification's metadata-only orchestration failure is preserved, while the separate fused leaf provides complete source postflight and four selected direct fused calls. Unfused resources are unchanged; the unrelated two-CTA fused signature grows122→125registers withLOCAL0 and is excluded from timing.
- Historical02dequalification manifests are preserved. `control-production-equivalence.json` verifies all13,245qualified inventory files against clean retainedbf072; the only qualification-to-timing changes are retained W4/Mega files, unused by this swap-only screen. The candidate overlay is solely the final swap source.
- Actual FP4 stores widen64→128bits; FP8 stores widen128→256bits. Per-token BF16 remains256bit. No new public flag or tuning axis.
- GPUs0–3 are idle/released. The experiment remains unstaged; no commit, push or PR publication was performed. Any extension/retention needs the parent's decision after independent data/resource review.
