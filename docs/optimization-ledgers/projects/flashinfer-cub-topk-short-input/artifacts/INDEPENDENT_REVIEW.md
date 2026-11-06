# Independent final evidence review

Reviewed the saved evidence locally on 2026-09-13. No GPU execution, source edits, or GitHub operations were performed for this review.

**Result:** no runtime or test-evidence blocker found. One reporting correction is required: the selected controls exercise deterministic behavior, but do not include a `sorted=True` call. Describe the sorted gate as unchanged by source inspection, rather than GPU tested in this selection.

## Verified evidence

- Recomputed sizes and SHA256 hashes for all **35 files** in `remote-final/evidence-manifest.json`, including the copied native module. All match.
- Independently parsed every JUnit testcase and checked its associated log hash. Base dispatch: **6 failures, 0 errors, 0 skips**, all three APIs and both SMALL/LARGE ties at width 64 / k=2048. Each failure reaches a CUB workspace query and reports `cub_topk requires 0 < top_k <= d, got top_k=2048, d=64`. Fixed dispatch: **21 passed, 0 skipped**. Existing controls: **122 passed, 0 skipped**. Raw pytest summaries report 4.39 s, 4.20 s, and 4.42 s respectively; these are validation durations, not performance measurements.
- Compared recorded source hashes against local Git objects. The failing phase uses `flashinfer/topk.py` from base `488ffbd9fe4455c3b4c3030cf668b5603c6698e4`, with the new tests retained. Both passing phases use clean revision `62ff0a1751a537af89e5e2353ea1ca72954ba165`. All phases use test SHA256 `89f9d48087e01c180686128d61bd7718699ab4f73e0ff3c8224ca9497b841c2c`. This is a controlled parent-runtime comparison, not a claim that the entire checkout was switched to the base.
- Verified all nine baseline source hashes against base Git objects; the eight recorded native/JIT source files remain byte-identical at the fix. Only `flashinfer/topk.py` and `tests/utils/test_topk.py` differ between revisions. The 21,139,440-byte copied `topk.so` hashes to `06b44eb1709cbe1a25706d267b29b1dc783b5bdfe21db65c0ff1780cafa1af21`, matching baseline smoke, before/after validation, and final proof. Baseline records show a fresh SM103a JIT build with no top-k AOT library; the corrected setup smoke reused that build.
- Environment evidence agrees on one visible NVIDIA B300 SXM6 AC GPU, SM103, image `nvcr.io/nvidia/pytorch:26.05-py3`, Python 3.12.3, image Torch `2.12.0a0+5aff3928d8.nv26.05` / CUDA 13.2, and native compiler 13.2.78. Final saved proof records the expected clean head and no GPU compute processes.

## Coverage and claim boundaries

The 18 automatic cases cover three APIs × two tie modes × oversized/normal/equal physical width. The exact test matrix matches the XML names. Checks cover full-row eager output and graph replay, then changed scores and metadata with full/partial/empty transform rows, exact selected sets and padding, plain value/index correspondence, nonidentity page translation with page size 64, ragged offsets, and supplied paged output addresses. Real CUB workspace-query spies establish no CUB dispatch for oversized input and retained CUB dispatch for normal/equal input. Three additional cases preserve explicit-CUB rejection.

The 122 existing controls comprise 108 tie-mode cases, six compact-page graph replay cases, three CUB nonpositive-length cases, three CUB workspace cases, and two deterministic trivial-width cases. New oversized cases use FP32; related controls additionally cover FP16/BF16, but do not establish oversized behavior for every dtype or architecture.

Supported publication scope is the automatic physical-width guard and its existing filtered-native behavior on these cases. Do not claim a full top-k suite pass, a new native k limit, native support for negative lengths, universal oversized-input support, or speedup. CuTe/cuTile/cuDNN/MoE paths were not validated in the retained image environment. Historical SGLang GLM benchmark results used FI083 with the explicit native override and must remain attributed to that earlier configuration.
