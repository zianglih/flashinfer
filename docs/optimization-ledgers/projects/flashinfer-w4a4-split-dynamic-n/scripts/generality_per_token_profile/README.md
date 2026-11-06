# Per-token prefill diagnostic

Prepared only; do not launch until the parent decides the quantizer performance screens leave an unresolved regression.

`prepare.py` binds a saved native AUTO cache, exact source receipt, route fingerprints, and the public per-token selector. Default is V3 T4096 on GPU6: copy, general PDL, late single-warp publication, and startup single-warp publication. These four arms use the same selected V3 FC1/FC2 geometry. Other models are selectable; V41's source-native choices differ and must not be described as a matched-geometry comparison.

`run.py` executes the existing public `--profile-cuda` path under Nsight Systems graph-node tracing, five replays per source. The observer verifies saved tactic hits, routes, source bytes and actual CUDA13.2/CuTe4.7.1 imports. It appends keep-PTX/cubin flags without replacing existing compiler options, and saves compiler-bound resources/SASS for FC1, FC2, and per-token quantization. Initial activation quantization is outside the captured MoE region. `summarize.py` separates the timed FC2 requantizer from both GEMMs and reports phase lifetimes, overlap, and observed launch resources.

These are diagnostic phase durations, not replacements for the native10/100 cold-L2 CUPTI medians. Nsight Systems preserves the public graph and PDL chain; isolated NCU replay would serialize kernels and should only be added after the whole-chain evidence identifies a specific question.

Prepared plan: `evidence/generality-per-token-prefill-profile-ready-r1/plan.json`.
Saved-data audit: `evidence/generality-per-token-prefill-audit-r1/audit.json`.

Remote command after staging the prepared directory and authorization:

```sh
source /workspace/flashinfer-w4a4-split-dynamic-n/scripts/recovery442/env_candidate.sh
/workspace/flashinfer-w4a4-split-dynamic-n/.venv/bin/python run.py \
  --plan plan.json --output /workspace/flashinfer-w4a4-split-dynamic-n/logs/NEW_TAG \
  --python /workspace/flashinfer-w4a4-split-dynamic-n/.venv/bin/python \
  --native-cache /workspace/flashinfer-w4a4-split-dynamic-n/cache/gap-c2-native \
  --cuda-arch 10.3a
```
