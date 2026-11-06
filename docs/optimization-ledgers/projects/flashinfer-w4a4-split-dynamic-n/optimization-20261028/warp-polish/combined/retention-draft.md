# Provisional retention record

Candidate `b45b218b` is a general instruction/ownership cleanup with a neutral full frozen-winner screen: **+0.129%** geometric mean across all 176 retention cells, **+0.245%** decode (T4–64), **+0.328%** T128–256 and **−0.115%** prefill (T512–16384). T1/T2 were run and excluded. This does not establish a material end-to-end speedup. Final performance retention remains conditional on the targeted contemporaneous ABBA check of the large 16K MX negatives.

| Model | Format | All T≥4 | Decode T4–64 | T128–256 | Prefill T512–16384 |
|---|---|---:|---:|---:|---:|
| V3 EP8 | W4A4 | +0.322% | +0.417% | +0.043% | +0.343% |
| V3 EP8 | PER-TOKEN | +0.258% | +0.246% | +0.722% | +0.043% |
| V3 EP8 | MXFP8 | +0.055% | +0.117% | +0.180% | -0.085% |
| V3 EP8 | MXFP4x8 | +0.344% | +0.050% | +0.545% | +0.613% |
| V41F EP4 | W4A4 | +0.119% | -0.021% | +0.542% | +0.083% |
| V41F EP4 | PER-TOKEN | +0.471% | +0.830% | +0.419% | +0.049% |
| V41F EP4 | MXFP8 | +0.061% | +0.041% | +0.137% | +0.047% |
| V41F EP4 | MXFP4x8 | +0.406% | +0.463% | +0.098% | +0.489% |
| K3 EP8 | W4A4 | +0.422% | +0.223% | +0.602% | +0.581% |
| K3 EP8 | PER-TOKEN | -0.179% | -0.389% | +0.799% | -0.403% |
| K3 EP8 | MXFP8 | -0.253% | +0.541% | +0.032% | -1.376% |
| K3 EP8 | MXFP4x8 | -0.687% | -0.026% | -0.184% | -1.756% |
| N3U EP8 | W4A4 | +0.311% | +0.531% | +0.727% | -0.171% |
| N3U EP8 | PER-TOKEN | +0.387% | +0.406% | +0.513% | +0.300% |
| N3U EP8 | MXFP8 | -0.106% | +0.314% | -0.051% | -0.656% |
| N3U EP8 | MXFP4x8 | +0.147% | +0.188% | +0.139% | +0.100% |

The comparison reuses saved `99f4d0c27` A1/A2 baseline medians and native winners; fresh candidate A1/A2 uses identical routes and tactic keys, unfused finalize, CUPTI cold-L2 graph timing, 10 warmups and 100 samples. NVFP4 includes input quantization. Six workers completed all 208 cells. Independent raw-output verification checked all 41,600 candidate CUPTI samples, median arithmetic, cache-hit winner identities and result hashes. Positive percentages mean `baseline / candidate - 1`; all negative cells remain in every applicable aggregate.

Largest negatives are K3 MXFP4x8 T16384 **−5.796%**, K3 MXFP8 T16384 **−5.309%**, and N3U MXFP8 T16384 **−3.845%**. Their candidate A2/A1 latency spreads are +0.360%, +0.613%, and +0.506%. Stable candidate passes do not establish causality against an older baseline; clock/thermal/system drift remains possible. Do not attribute these gaps to the source change or dismiss them as noise before the producer ABBA evidence is available.

Qualification and scope:

- Full gate: 176 exact output-byte graph replays and 88 matched FC1/FC2 codegen captures; no local/stack/spill sites, unchanged named-barrier sites and stage/TMEM/shared-memory allocations.
- Follower CTAs skip the entire MMA metadata/K bookkeeping path; local CLC metadata arrivals now reflect actual owners (224 leader / 192 follower). Necessary dependency/lifetime joins remain. This is the instruction-sanity retention argument even if timing stays neutral.
- Activation SF TMA reuses the existing payload cache policy at all 404 generated sites. No model/dtype/tactic-specific policy was added.
- PDL-off captures remove all 88 prior GDC sites across 44 kernels; PDL-on source bodies are unchanged by that guard. This cleanup is not a claimed source of gains for PDL-on cells.
- Source receipts verify 342 files: only the swap-AB kernel differs. Public API signatures, all class members except the kernel body, wrappers and tactic definitions are unchanged. The only helper signature extension is the private activation-SF TMA cache-policy argument. Legacy/Rubin/W4A16 source is untouched.
- Root reports all applicable pre-commit hooks passed on the same unchanged kernel hash, including mypy and Ruff. Sanitizer remains skipped.

Evidence: `retention-analysis.json`, `analyze_retention.py`, `LOCAL_VERIFICATION.json`, `codegen-summary.json`, `composition-proof.json`, `GATE_RESULTS.md`, and the raw `full-evidence/` and `gate-evidence/` trees. No commit/push was made by this subtask.
