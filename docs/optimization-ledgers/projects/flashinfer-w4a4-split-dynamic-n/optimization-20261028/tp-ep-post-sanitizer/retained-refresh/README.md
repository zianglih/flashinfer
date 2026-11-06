# Retained-source EP/TP refresh

Local helpers for fresh managed AUTO followed by two frozen public-script
CUDA-graph/CUPTI passes. External TRTLLM, non-swap CuTe and pre-PR W4A16 controls
are reused from the verified EP/TP reports. No external baseline is rerun.

- `prepare.py --head <clean pushed commit>` freezes all previously tracked source
  hashes plus changed paths and writes an immutable remote setup helper.
- Execute the generated helper with the existing `remote_box.py`; it clones
  inside this project, links unchanged native C++ artifacts, and verifies both
  source bytes and saved routing identities. CuTe/native caches stay persistent.
- Freeze `launch_template.py` with an explicit two-box GPU assignment only after
  candidate qualification, source publication and device-idle checks.
- Each worker verifies AUTO winners, frozen cache contents, source/helper hashes,
  exact routing identity, 100 raw CUPTI samples, cold L2 and graph replay. It
  forbids event fallback and any replay retuning.
- Four models, both EP and TP, tokens1/2/4/8/16/32/64/128/256/512/4096/8192/16384.
  Tokens1/2 remain raw evidence, excluded from displayed tables and retention.
  NVFP4 includes input quantization; MX is prequantized. Swap-AB is unfused.
- Skip K3 MXFP8 in both topologies and V41F TP4 MX: neither saved comparison
  backend supports them. This is benchmark scope, not kernel dispatch policy.
- Fetch source/runtime, all helper files, receipts, logs, raw results, frozen
  cache manifests and managed-cache files for independent local assembly.

## Completed retained head

`83dfef8a656384f5cd10db847602593bb6f9b2c6` is published and verified.
The final validation passed 95 pytest cases, 11 cache tests and 384 focused
sanitizer graph replays (192 compiled GEMMs, zero errors/warnings). Its evidence
is in `validation/fc2-final/83dfef8a6563/`; the earlier broad 150-case run remains
explicitly bound to d1767.

The complete refresh used 15 measured jobs on two eight-B300 devboxes, plus one
unsupported skip receipt. All 1,537 archived files, 936 medians and 93,600 CUPTI
samples were verified; no external control was rerun. Results, plots, exact raw
CSV and provenance are in `83dfef8a6563/report/`. Tokens 1/2 are raw-only.

`83dfef8a6563/publication-reviewed/publication.json` records the verified PR body
update (60,513 bytes, SHA256
`f283fdbf05adfe33e290e33472e07b67c8dd43b9bc66e4268736e657131ae04c`).
Both plots and validation commands are immutable assets at fork commit
`810889741c61b05510f70a6691cde748b526a6f5`.

Relative to the published d1767 campaign, affected-format TP prefill is +6.241%
and EP prefill +0.169% by geometric mean. These freshly autotuned historical
ratios are distinct from the causal fixed-winner compact-FC2 screen (+4.678% TP
prefill). Significant TP prefill gaps versus controls remain. See
`83dfef8a6563/report/independent-stats/SUMMARY.md` for all aggregates, boundaries
and outliers; do not substitute selected reruns for the full published matrix.
