# Final cleanup evidence

Independent helper/evidence variant; all prior final-adf and originala65 archives remain unchanged.

The input fingerprint runs on clean2b7 on GPU5 outside timing. It reuses the unchanged fingerprint implementation, hashes activations/router/routes at all13 tokens and full inputs/weights at1/32; remaining weight construction relies on exact V3 create_inputs AST, seed42 and runtime continuity. The current fused_moe.py is freshly source-bound. Historical72/24 API migration gate remains labeled historical; current cleanup correctness binds the68-case gate.

`prepare_bridge.py` verifies original/final input/routing/timer AST contracts. `dependency-proof.json` pins identical timer/quantization modules. `launch_fingerprint.py` uses hash-checked50K transport chunks; `fetch_fingerprint.py` preserves rawstdout and hashes. No native timing is launched here.

`python3 scripts/b300_cleanup_final_comparison/summarize.py --config evidence/b300-cleanup-final-bridge-r1/final-2b7-config.json --output evidence/b300-cleanup-final-bridge-r1/final-2b7-summary.json` compares archiveda65 C1/C2 against upcoming fresh2b7 A1/A2 on original GPUs2/4/6. Chronology is archived_controls_fresh_candidate, not a new C-A-A-C bracket.

`python3 scripts/b300_cleanup_final_comparison/summarize_paired.py --tag api-cleanup-final-r1` audits the separate adf-to2b7 fresh C-A-A-C comparison for both models. Benchmark SHA is identical, so compare receives no benchmark bridge. Outputs are evidence/api-cleanup-final-r1/{v3,v41}-paired.{json,md}.
