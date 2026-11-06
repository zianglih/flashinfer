# Final cleaned regular-TMA paired campaign

This outer wrapper preserves the frozen measurement helpers and dirty-source adapter. The reviewed implementation stays unstaged in `regular-tma-review`, based on442d2aa53f68b4640c3ab5118a76f1599ff60d34. Its full source/patch manifest is pinned to9f174d224c41b18fd59f51deb360464f70654724ed1acf91d38aa1a55fe1e1f2.

Order is original immutable B1, fresh A1, fresh A2, fresh B2. All three modes complete each arm before the next begins. NVFP4 uses GPU0; MXFP8 and mixed W4A8 run sequentially on GPU1. Both candidate arm directories intentionally keep the original adapter's `A1-{mode}.json` filenames; their outer directory gives the actual arm identity. Native caches remain separate for baseline and candidate. The candidate uses the exact manifest-specific CuTe cache already approved by the frozen adapter.

The unchanged native AUTO methodology runs13token counts:1,2,4,8,16,32,64,128,256,512,4096,8192,16384. Timing is10warmups and100cold-L2 CUDA-graph CUPTI iterations, reporting medians. Tokens1/2 are retained in raw tables but excluded from decode4–512, prefill4096/8192/16384, and overall retention aggregates. Input quantization is outside timing; routed payload/SF preparation is inside timing. The helpers save medians, cache winners and logs, not individual100samples.

Parent-executed commands, from the remote project, are:

```bash
bash scripts/regular_tma_final_campaign/run_candidate_arm.sh A1
bash scripts/regular_tma_final_campaign/run_candidate_arm.sh A2
bash scripts/regular_tma_final_campaign/run_baseline_arm_v2.sh
source scripts/recovery442/env_candidate.sh
.venv/bin/python scripts/regular_tma_final_campaign/verify_final.py
```

Original B1 is never launched. An existing arm directory blocks retry. The first B2 wrapper failed in CPU-only validation because `/workspace` is a symlink and receipt paths must remain relative; it created no B2 directory or GPU work. The original files and failure log are preserved. V2 changes only canonicalizing the repository path and preserving original relative receipt paths. Its prior-arm check passed remotely before launch.

`verify_final.py` reruns unchanged candidate postflight for both A arms, validates original B1 and fresh B2 through the frozen recovery policy and preparation contract, and checks exact source/helper/build/software/GPU/cache identities. Global chronology is checked across all modes. It computes each token's `sqrt(B1*B2/(A1*A2))`, then geometric means; also reports A2/A1 and B2/B1 drift. No fixed-tactic minima substitute for AUTO. CPU checks reproduced156 previously archived rows and156cache winners with379assertions and refusals for overlap, NaN timing, and missing winners.

After final verification, the local read-only archive command is:

```bash
python3 scripts/regular_tma_final_campaign/archive_final.py
```

It fetches all156rows/caches/logs, preflight/postflight/launch receipts, exactly three changed implementation files, the full source manifest/patch, frozen adapters/helpers, native-build/environment evidence and the CPU-only failure record. It independently recomputes the complete paired summary locally, preserves all AUTO winners, and writes `evidence/regular-tma-final-review/summary.{json,md}` plus digest manifests. Numerical and sanitizer validation are separate. No initcheck or zero-context-memory claim is made by this campaign.
