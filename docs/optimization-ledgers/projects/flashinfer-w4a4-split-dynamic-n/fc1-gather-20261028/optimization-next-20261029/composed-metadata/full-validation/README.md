# Composed lane metadata: full EP/TP validation

The measured source is retained as `c0c0bc41c70100c694ac55585990971aba8b7fb9`
in the clean canonical `flashinfer-fc1-gather-review`. It replaces the four-row
vector/scalar-tail mapping split with lane-owned mapping loads and four warp
shuffles. Control112 and independent weight-scale copies came from its base
`7106faf3082f63f3c94a4dc04b7fd0a77388f209`. The superseded composed review copy
has been removed; remote measurement source remains immutable.

- Kernel SHA256: `3225acf2dfeba54df42481b3186267b1bde642da9887b98cb966d5383d8635af`.
- Full-index patch SHA256: `43f4d19ad016afcfca0b90bc7d0c759cdfad934c85bba4ba36c00140374a5b80`.
- Source and deployed patch match; `local-source.json` and `preparation.json`
  record the transition and source hashes. Superseded local component copies
  were removed after verification; remote measured controls remain immutable.
- B300 GPUs4/6/7, CUDA13.2, `nvcr.io/nvidia/pytorch:26.05-py3`. Nine persistent
  native-cache links are preserved. Normal CuTe compilation options and strict
  source cache keys are used.
- Fifteen exact checks passed before performance: seven focused repository
  cases plus eight local M512 checks across four formats and CLC off/on.
  No repository tests or sanitizer were added/run.

## Comparison and reuse

All15 jobs use the original fixed winners and routes, unfused output, input
quantization included for NVFP4, cold L2,10 warmups and100 strict CUPTI samples.
Tokens: `1,2,4,8,16,32,64,128,256,512,4096,8192,16384`.

The30 fresh candidate phases are AA, not a new interleaved CAAC measurement.
They reuse the two original clean-fb66 control phases from
`../../composed/full-validation/evidence/perf`. Each job retains the exact GPU
assignment and verifies the physical UUID, source hashes, original raw-result
hashes, cache manifest, routing identity and key/runner/tactic observations.
No controls or external baselines are rerun.

There are468 raw cells and93,600 new samples plus93,600 reused control samples.
Displayed summaries exclude1–2 tokens; retention also excludes unchanged
W4A16 diagnostic cells, leaving308 affected displayed cells. Unsupported
V41F TP MX modes and K3 MXFP8 remain absent.

The isolated44-cell metadata screen against112 is preserved at
`../../../full-20261029/lane-metadata/RESULTS.md`: affected gmean+0.510%,
prefill+1.038%, decode+0.007%. This full campaign validates composition with
the retained scale-factor ordering and broader token/model coverage.

## Reproduce local analysis

From the project root after fetching and verifying the evidence envelope:

```sh
python3 fc1-gather-20261028/optimization-next-20261029/composed-metadata/full-validation/analyze_perf.py \
  fc1-gather-20261028/optimization-next-20261029/composed-metadata/full-validation/evidence/perf \
  --baseline fc1-gather-20261028/optimization-next-20261029/composed/full-validation/evidence/perf \
  --output fc1-gather-20261028/optimization-next-20261029/composed-metadata/full-validation/report
```

Retained as `c0c0bc41c70100c694ac55585990971aba8b7fb9`: all measured source hashes match the clean canonical `flashinfer-fc1-gather-review`. The superseded composed review copy was removed after the cp.async experiment froze its independent source. Remote measurement/tuning source remains immutable.
