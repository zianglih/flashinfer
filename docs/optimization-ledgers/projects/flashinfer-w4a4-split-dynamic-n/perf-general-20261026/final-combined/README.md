# Final six-table validation and PR-body draft

`summarize.py` writes only local artifacts; it never publishes or collects remote
files. Root owns both collections and the PR update.

```bash
python3 perf-general-20261026/final-combined/summarize.py --prepare-only
# After root confirms both collections are complete:
python3 perf-general-20261026/final-combined/summarize.py
```

Inputs are the final guard NV campaign in `../final-guard-nv/raw` and preceding
scheduler/row-limit MX campaign in `../scheduler-row-limits/full/raw`. Each must
have a completed collection manifest, preflight and per-model receipt. The
established parser validates all native medians, printed cells/ratios/winners,
native AUTO caches, model/EP, routing hashes/histograms, quantization recipes,
input-quantization scope, and the 10/100 cold-L2 CUDA-graph CUPTI contract.

The final report contains six outputs, 78 token rows and 208 printed ratios. The
top W4A4 comparison excludes tokens 1/2; all raw outputs retain them. The body
preserves the retained PR template, component line counts and all six outputs,
and includes commands/raw output for the 197 unique final-source existing tests.
Source-paired exact gates are explicitly scoped to their measured revisions.

Source pins (both based on `dd266b91`):

- NVFP4: patch `f8ba9aeec6cd3f10925ca67712d7743468772145bcb71f70bef54de2386189ee`,
  exactly matching committed tree `7f4e1703d984831efc13eea63a868b3e558d243b`.
- MX: patch `2b0bd7eaa43af0fbfe6935d3d06f52550c3e916da437172945afbb2b4a4178d1`,
  exactly matching committed tree `c69d7034be06e7386944db46b2fa816729b9d364`.

The validator rechecks the commit patch hashes, frozen working copies and source
isolation. The entire quantizer module AST is identical after masking the one
changed per-token method body; all other source files match. Both MX selectors
disable per-token activation and the wrapper rejects MX inputs with per-token
scales. MX evidence keeps its actual preceding-source provenance instead of being
represented as measured on the guard commit. TRT/CuTe per-token arms share the
timed initial quantizer, so the same-sweep TRT values remain the comparison.

Outputs: `preparation.json`, `validation.json`, `summary.{json,md}`,
`raw-tables.md`, and `pr-body-draft.md`. A failed completeness or hash check stops
before emitting final output. Source comparisons against the fresh 0def sweep
are descriptive; causal same-GPU CAAC evidence remains in the experiment ledger.
