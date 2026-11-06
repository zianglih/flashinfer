# Full retention campaign

Combined gate passed: 24 existing exact accuracy tests and 96 static/CLC × PDL graph replays. The full eight-GPU campaign completed all 54 phases successfully; all eight family receipts are verified. The final 1,066-file raw evidence archive has SHA256 `96c6008403d6e6a34006302f7a1758925b41a443b04d452a2470a65800707fcd` and is extracted under `evidence/`. Frozen source is e2728a290 plus patch `9b546843c47859284472540efe24ad1fa6ebea6d4c539f182d436ef66d371d18`; configuration SHA256 is `f9f97e387432d38483010ae79014ea7d850ebf222ab31d55be9a086623593587`.

The remote campaign root is `/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261027/retained-rerun`. Supply `current-source.json` with `repo`, `head`, `workspace_base`, `native_source_verified: true`, and `benchmark_source_sha256`. Its source and native cache must already be frozen and verified. `make_deploy.py` embeds the unchanged strict observer plus the updated runner into `deploy_campaign_remote.py`; run it through the existing project `swap-ab-exact-20261027/remote.py` transport. Deployment does not launch GPU jobs.

`launch_campaign_remote.py` launches only when all eight GPUs are idle. Assignment is V3 NV/MX on 0/1, V41F NV/MX on 2/3, K3 NV/MX on 4/5, and N3U NV/MX on 6/7. Keep the original model defaults: V41F EP4; others EP8. All 13 token counts run; final summary omits 1/2.

Each candidate swap-ab arm receives fresh native AUTO, followed by frozen C-A-A-C measurements. Unchanged non-swap/pre-PR control arms reuse their completed prior native winner cache only after full source/API/workload byte equivalence, cache hash, receipt hash, and source manifest checks. Original timing rows are never consumed. All control timing samples are fresh. Candidate AUTO retains the original native family command, including TRTLLM arms, without a new tuning policy.

Sources are `current` (selected candidate), `legacy` (clean e2728 current-PR non-swap implementation), and `prepr` (002529 old-layout W4A16). NV legacy is unfused; legacy MX is fused where its unfused path does not exist; legacy K3 MX is N/A. Candidate is unfused. NV includes initial activation quantization; MX is prequantized.

Expected phase structure is 8 candidate AUTO phases plus 46 frozen phases. Every timing uses 10 warmups and 100 cold-L2 CUDA-graph CUPTI samples. Event fallback is a hard error. The observer verifies actual CuTe/TRTLLM native cache hits, saved runner/tactic identity, unchanged frozen cache hashes, and identical route hashes. Source-private CuTe caches reuse verified persistent native C++ artifacts; no cache deletion.

The result assembler is owned by the MXFP/prepare agent. Preserve all phase logs, native printed CSV, results JSON, receipts, source manifests, helper hashes, and winner caches in the final evidence archive.
