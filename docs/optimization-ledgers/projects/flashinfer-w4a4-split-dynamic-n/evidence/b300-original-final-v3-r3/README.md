# Fresh B300 original-to-retained V3 evidence

- Original: `a65d5b09e7e4c4c5c160b0161c48becd100b3970`; retained: `853aaf69d706b291afee477f738956b997033f53`.
- Same c2 B300 host, CUDA13.2, native AUTO, EP8/TP1, no per-token activation scales, no fused finalize, initial quantization excluded, no communication. Native 10-warmup/100-iteration cold-L2 CUDA-graph CUPTI timing, PDL on.
- Stable GPU assignments: NVFP4 GPU2, MXFP8 GPU4, mixed MXFP4×MXFP8 GPU6. Every format uses C1–A1–A2–C2 on its same GPU. Each job is a fresh process with no saved autotune choices loaded; source-specific compiler caches are reused for repeats.
- All13 points are preserved: 1,2,4,8,16,32,64,128,256,512,4096,8192,16384. Retention excludes1/2. Decode is4–512; prefill is4096/8192/16384.
- `paired-summary.json` contains every full-precision native median, direct paired ratios and group geometric means, source/runtime/GPU/route validations and an absolute-path input hash map. These observers retain native medians, not individual iteration samples. All raw stdout/stderr, tactic files and receipts are under `raw/`.
- Untimed fingerprint boundary: all13 activation/router tensors and exact native route IDs/weights/full histograms match. Original full input hashes are preserved for all13; retained expert weights were hashed at tokens1/32 only. Other retained weight construction relies explicitly on proven V3 create_inputs AST equivalence, identical runtime and seed42. This is not a zero-tolerance numerical-output test.
- The initial r1 companion failed on dtype reinterpretation of a scalar tensor before recording a row; r2 flattened before reinterpretation. No timing body changed. The r2 coordinator was stopped alone to avoid redundant full retained-weight hashing; its original child finished untouched. The r3 companion adopted the bounded hash policy above. All failures/revisions are preserved.
- Six compiled smoke jobs passed before the full12-job campaign. Production snapshots were clean and exact pins were checked before/after every subprocess. The summary audits the source, archive SHA map, timing helper proof, runtime, GPU identity, chronology, route-derived histograms, saved tactics and cache provenance.

Recompute the summary only into a fresh output location (the helper refuses to overwrite):

```bash
python3 scripts/b300_original_final_campaign/summarize.py --evidence evidence/b300-original-final-v3-r3
```

Exact executed commands are preserved in `raw/campaign/receipt.json` and each per-job receipt. The upstream benchmark and archived measurement bodies were unchanged; the only archived observer compatibility delta accepts the four known additional V3 configuration fields, with an explicit byte/AST proof.
