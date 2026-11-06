# Final public API benchmark campaign

Launched with parent authorization on clean adf02fdd4a8fd2a5d4d2ca54b6969cd65572d93d. Exact 85 source pins match the validated public API prototype; focused53 passed before launch. The independent review copy remains unstaged and untouched.

V3 EP8: GPU2 NVFP4, GPU4 MX family. V4.1-Flash EP4: GPU3 NVFP4, GPU7 MX family. Each model runs clean8b C1, final A1, final A2, clean8b C2 sequentially. A1 supplies the four complete public backend tables; controls and A2 use CuTe-only selectors. A separate V3 mixed-format A1/A2 uses GPU6 to preserve the original-control GPU identity.

All13 tokens are measured with native AUTO,10 warmup/100 timed iterations, cold L2, CUDA graphs/CUPTI, PDL enabled, no fused finalize/per-token quantization/initial activation quantization. Tokens1/2 remain reported and excluded from retention aggregates. No original a65 timing is rerun. Its final comparison is explicitly archived controls plus fresh candidate observations, not a new C-A-A-C bracket.

The optional compiler-cache reuse preflight found the previous CUTE_DSL_CACHE_DIR directories absent. It stopped before GPU launch. The recovery preserved source/helper bytes and proceeded without copying caches. launch.json records artifacts_present=false and reused=false for both sources. AUTO timing/config files are never loaded.

Raw artifacts will be fetched to evidence/public-api-final-adf-r1-{v3,v41}-{c1,a1,a2,c2}/raw and evidence/public-api-final-adf-r1-v3-mixed-original-{a1,a2}/raw. Summaries use the explicit public API migration bridge backed by72 byte-exact outputs and24 input/tactic/core-policy comparisons; this is not a whole-assembly AST identity claim.

## Completion

All10 native arms completed and were fetched unchanged. Full public A1 tables contain13 rows for both models/families. Final focused53 passed. See completion.json, v3-paired.json and v41-paired.json. The public interface correction is approximately performance-neutral; no speedup is attributed to this API-only change. Original-to-final performance is separately reported by evidence/b300-public-final-bridge-r1/final-adf-summary.json using archived a65 controls and fresh final candidate observations.
