# Reuse the prefetched first weight-cache hint

Active isolated experiment based on retained `1e69d0a391fd926d21a35388cacf2df3c1c22baf`. Local review clone: `flashinfer-first-hint-perf-review`, one unstaged kernel diff; canonical and frozen campaign sources remain untouched.

PDL startup already computes the weight/SFA cache hint for its first valid work tile. The candidate initializes a safe default and reuses that value when the producer first encounters the same tile. Later tiles keep the original adjacent-expert comparison. Static and CLC use their existing shared initial-work mapping. There is no API, tactic, cache policy, routing, barrier or output change.

This adds a longer-lived 64-bit value and a first-tile branch. The experiment is rejected if that control/register cost outweighs eliminating the redundant first-tile neighbor reads. PDL-off generated code should remain unchanged. The invalid initial-route case must not use an uninitialized hint.

Static checks pass: AST, Ruff check/format and `git diff --check`. Both remote control and candidate use exactly1e69d0a39; the two formatting-only differences from the frozen pre-commit source were AST-checked. Their native C++ sources and resolved data tree are identical, and native compilation artifacts are shared while CuTe artifacts use separate source namespaces.

Bounded gate: NVFP4 one-CTA N16, per-token NVFP4 two-CTA N128, MXFP4x8 two-CTA N16; shared CLC off/on, PDL off/on, balanced/skewed/empty/reactivated routing. Forty-eight output-storage-bit replays per source, with PTX/cubin/SASS/resource capture for24 kernel pairs. GPU2 only; no sanitizer or AUTO sweep.

The gate passed96 source-paired storage-bit replays total. All12 PDL-off SASS files are byte-identical. All12 PDL-on variants have flat or lower registers and zero local-memory loads/stores; pipeline and memory geometry are unchanged. Static instructions increase1–31 sites and branch sites increase0–2, because the later-tile path remains. The representative CLC MXFP4x8 FC1 SASS explicitly bypasses both neighbor LDGs on the prefetched first tile (`first-tile-load-bypass-proof.json`). Gate archive:207 files, SHA256 `9b9cc883f646983cb45bfe6c01e5c8fadc66a20df9f7273df63dcbc21867ba19`.

The five-cell frozen-native-winner public-API C-A-A-C screen is complete: N3U MXFP4x8 T4, V3 W4A4 T4, K3 MXFP4x8 T64, and N3U W4A4 T4096/T16384. Each phase uses100 CUPTI cold-L2 CUDA-graph samples,10 warmups, matched routing and the existing retained winner. NVFP4 includes input quantization. There is no AUTO run, new tactic or benchmark-source change.

`RESULTS.md` and `validated-timing.json` contain the completed20-pass/2,000-sample results. The two T4 cells improve0.29–0.35%; K3 T64 and N3U T16384 are neutral. N3U T4096 is inconclusive (−0.173% versus0.373% candidate repeat drift). A broader frozen-winner screen and reversed T4096 repeat are proposed; no retention or source publication has occurred. Timing archive SHA256: `4e322c4d87c34e85d2a5427c360470343b8c7d2ad04c10eb73257ac9cbe06645`.
