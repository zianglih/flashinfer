# FlashInfer automatic CUB dispatch for short score widths

Read-only audit prepared while the GLM-5.2 serving benchmark continues. Do not
implement, change its backend, or create the separate upstream draft PR until
the SGLang benchmark work is published and finished. No GPU was used for this
audit and no source repository was edited.

## Finding and evidence

Current fetched FlashInfer main is
`488ffbd9fe4455c3b4c3030cf668b5603c6698e4`; the benchmark remains pinned to
`083a9fd39e7ddda43a8b912ef50f7a13390287f9`. Both contain the same defect:
`can_use_cub_topk` does not receive `k`, so automatic dispatch can select CUB
when `k` exceeds the physical score width `input.size(1)`. The selected CUB
workspace query rejects the call before a selection kernel launches.

The observed SGLang startup failure is preserved in
`failed-startups/topk-cub-short-input/mega-1/server.log` and described in
`SETUP_FAILURES.md`:

```text
cub_topk requires 0 < top_k <= d, got top_k=2048, d=64
```

This is distinct from the earlier stale image AOT missing-export failure. A
Python dispatch correction will not repair an incompatible prebuilt top-k
module. The current benchmark uses a top-k module rebuilt from FI083 and the
same explicit `FLASHINFER_TOPK_ALGO=default` compatibility setting in every arm.
Those measurements must retain their original source/backend provenance.

All four files below have identical Git blob IDs at the benchmark pin and the
fetched main pin:

| File | Blob ID |
|---|---|
| `flashinfer/topk.py` | `eada459bb6272ed841c875a4f5daac0e694b2644` |
| `csrc/cub_topk.cu` | `32166db13ff9aeabed0934d0d0bd94e3df9db186` |
| `include/flashinfer/topk.cuh` | `e4d7f05661577a9f67df253feb4ce36c3176af57` |
| `tests/utils/test_topk.py` | `f4b07e7fef9ac617cd7635e5b75b32826b863059` |

The most recent relevant merged change is
`286eee4e2999a825716eab68e597cb1ee0881e1b`, CUB backend PR #4442. Targeted
`git log origin/main -- <top-k files>` and `git log --all -G
'can_use_cub_topk|top_k <= max_len|top_k <= input.size' -- flashinfer/topk.py
csrc/cub_topk.cu` found no later correction. This is a fetched-history check,
not an exhaustive search of open/unfetched PRs. No GitHub API was called.
A broader unrelated-tree grep encountered a partial-clone missing-object
fetch error; the source files and history needed for this audit were readable.
Use a separate project-owned clone for the later fix rather than modifying the
benchmark checkout, and refresh the duplicate check immediately before work.

## API and backend contracts

All source links below use the exact audited main revision.

- **Shared gate:** [topk.py:649](https://github.com/flashinfer-ai/flashinfer/blob/488ffbd9fe4455c3b4c3030cf668b5603c6698e4/flashinfer/topk.py#L649)
  checks dtype, architecture, width ceiling, sorted/deterministic mode and
  backend override, but has no `k` argument. The three callers are
  [plain:962](https://github.com/flashinfer-ai/flashinfer/blob/488ffbd9fe4455c3b4c3030cf668b5603c6698e4/flashinfer/topk.py#L962),
  [paged:1221](https://github.com/flashinfer-ai/flashinfer/blob/488ffbd9fe4455c3b4c3030cf668b5603c6698e4/flashinfer/topk.py#L1221),
  and [ragged:1400](https://github.com/flashinfer-ai/flashinfer/blob/488ffbd9fe4455c3b4c3030cf668b5603c6698e4/flashinfer/topk.py#L1400).
  At four FP32 rows, width 64, `tie_break=LARGE`, `dsa_graph_safe=True`, all
  three benefit predicates choose CUB. Paged selection also chooses it in the
  corresponding eager tie-break case without the graph-safe flag; ragged
  heuristics differ, so do not generalize one API's eager thresholds to another.
- **CUB shape bound:** [cub_topk.cu:440–468](https://github.com/flashinfer-ai/flashinfer/blob/488ffbd9fe4455c3b4c3030cf668b5603c6698e4/csrc/cub_topk.cu#L440)
  requires `0 < k <= physical width` for every CUB entry/workspace query.
  This differs from the device-resident per-row `lengths`: CUB supports
  nonpositive/short rows when the physical shape is eligible and fills the
  unselected output suffix with `-1`
  ([tail kernel](https://github.com/flashinfer-ai/flashinfer/blob/488ffbd9fe4455c3b4c3030cf668b5603c6698e4/csrc/cub_topk.cu#L157)).
  Do not copy `lengths` to the host or use `min(lengths)` as the gate.
- **Native short rows:** the filtered kernel's
  [trivial case](https://github.com/flashinfer-ai/flashinfer/blob/488ffbd9fe4455c3b4c3030cf668b5603c6698e4/include/flashinfer/topk.cuh#L2595)
  handles `length <= k`. Plain output contains valid local indices and their
  values, then index `-1` / value `0` padding. Paged output translates valid
  local token indices and pads both transformed and optional raw outputs with
  `-1`. Ragged output adds the per-row offset only to valid indices; padding
  stays `-1`. This filtered plain behavior is implementation evidence, not a
  claim that `torch.topk` or every native/cluster configuration accepts `k > d`.
- **Native limit:** `FILTERED_TOPK_MAX_K=2048`
  ([constant](https://github.com/flashinfer-ai/flashinfer/blob/488ffbd9fe4455c3b4c3030cf668b5603c6698e4/include/flashinfer/topk.cuh#L2515)).
  `dsa_graph_safe=True` or nonzero tie-break requires this backend and sufficient
  shared memory; all three native dispatchers reject `k > 2048`
  ([dispatchers](https://github.com/flashinfer-ai/flashinfer/blob/488ffbd9fe4455c3b4c3030cf668b5603c6698e4/include/flashinfer/topk.cuh#L3648)).
  Multi-CTA native modes have a different contract; 2048 is not a universal
  native top-k maximum. The proposed fallback does not add support for
  graph-safe/tie-break `k=4096 > d`.
- **Forced CUB today:** `FLASHINFER_TOPK_ALGO=cub` bypasses benefit heuristics,
  but still obeys the existing eligibility checks. In particular, sorted or
  deterministic calls fall through to native even when CUB is requested.
  For the supported dtype/device, unsorted, nondeterministic `k > d` case,
  forced CUB currently reaches the workspace query and raises the CUB shape
  error. Preserve that behavior in this narrowly scoped automatic-dispatch fix.
- **Tie-break:** `SMALL`/`LARGE` chooses smaller/larger *local* indices among
  equal values at the selection boundary, before page/offset translation. It
  does not promise output ordering. Use exact selected-set comparisons, then
  check index/value or raw/transformed correspondence; do not compare unsorted
  CUB output position-by-position with native. For a row whose length is at
  most `k`, all valid positions are selected regardless of tie mode. CUB
  tie-break requires SM90+; dtype support remains FP32/FP16/BF16 and physical
  width remains at most `2**21`. Preserve existing sorted/deterministic,
  negative-length CUB-only, NaN and signed-zero behavior rather than expanding
  those contracts in this patch. Negative lengths must not enter the native
  fallback tests: existing tests explicitly treat them as native undefined
  behavior.

## Minimal implementation

Change only `flashinfer/topk.py` and `tests/utils/test_topk.py` unless verification
finds another necessary issue. Add `k` to the shared gate and pass it from all
three public wrappers. After obtaining `d`, add an automatic-selection guard:

```python
# CUB cannot produce k outputs when k exceeds the physical score width.
# Let native dispatch retain its padded short-row behavior in automatic mode;
# explicit CUB requests keep the binding's shape validation.
if algo is None and k > d:
    return False
```

The helper already rejects other non-CUB overrides before this point. The
`is_cub_*_beneficial` functions and C++ bindings should remain unchanged.
`k == d` remains CUB eligible. Do not add synchronization, workspace growth,
input padding, index postprocessing, CUB kernel changes, global `k <= 2048`
validation, or a blanket short-logical-row CUB bypass. Do not silently switch
an explicit forced-CUB oversized call to native as a side effect of this fix.

## Focused regression plan

Use the existing test file, `set_topk_algo("auto")` fixture (which unsets the
environment), `can_implement_filtered_topk()`, CUB tie-break device guard, and
existing exact reference helpers. Do not use the broad tests' approximate
0.98 selection tolerance for these cases.

1. **Automatic oversized shape, all three APIs:** four rows, physical width
   64, `k=2048`, FP32, both SMALL and LARGE, `dsa_graph_safe=True`, unsorted and
   nondeterministic. For page-table/ragged use lengths `[64, 63, 32, 0]`;
   paged uses `page_size=64`, nonidentity page IDs, supplied `out` and
   `out_raw_indices`; ragged uses distinct nonzero offsets. Plain has no
   lengths input: verify all 64 valid `(index, value)` pairs and 1984 exact
   `(-1, 0)` pairs per row. Run eager, capture after normal side-stream warmup,
   then replay with changed scores/page IDs/offsets and changed lengths.
   Capture with full rows before shrinking to partial/empty rows to detect
   stale tails. Require exact valid selected sets, padding, raw-to-page
   mapping, output dtype/shape and caller-provided pointer preservation.
   The unpatched source must fail on the CUB workspace query. If additional
   dtype coverage is wanted, parameterize this small paged startup case over
   FP16/BF16 without multiplying the whole broader suite.
2. **Normal automatic CUB control:** four FP32 rows, width 4096, `k=2048`, both
   tie modes, `dsa_graph_safe=True`, all three APIs, with paged size64. These
   exact shapes pass current CUB benefit gates. Use equal-valued full rows to
   check smallest/largest boundary selection plus transform lengths
   `[4096, 2048, 1024, 0]` to keep CUB's short-logical-row behavior covered.
   Run eager and replay after in-place metadata/score updates. Observe the
   real CUB workspace-query wrapper with `unittest.mock.patch.object(...,
   wraps=...)` or an equivalently small call counter to prove this is still
   CUB, rather than merely observing equal outputs. Include `k == width` as
   a compact eligibility/boundary assertion so `>` cannot accidentally become
   `>=`. Existing larger tie tests already cover extensive value patterns.
3. **Forced shape rejection, all three APIs:** supported device/dtype,
   `FLASHINFER_TOPK_ALGO=cub`, width64/k2048, unsorted and nondeterministic;
   assert the existing `RuntimeError` containing `0 < top_k <= d`. No graph
   capture is needed for this host-side rejection. The same valid normal
   control with forced CUB should still succeed through the existing tests.

An optional single paged `dsa_graph_safe=True, k=4096, width64` assertion can
document the native filtered limit (`TopKPageTableTransform ... not supported`)
after automatic CUB declines. Do not turn that unsupported case into new
padding/kernel work. Existing deterministic/sorted, compact-page graph replay,
tie-boundary and CUB nonpositive-length tests should be rerun rather than
duplicated.

## Validation and publication boundary

The current `setup/native-topk-probe.json` records six passing FI083 native
paged checks: widths64/4096/8192, k2048, page64, four full/partial/empty rows,
each eager and graph replay. They establish the benchmark workaround's scoped
behavior, not a test of the proposed automatic fix or current-main serving.

After the benchmark is finished, implement in an isolated checkout based on
freshly verified main, then record the exact tested commit, image, GPU and
native module source identity. First reproduce the new regression failure on
the untouched base; run the new exact tests after the fix and the existing
related controls on C2. Candidate focused selection (final new test names may
differ):

```bash
python -m pytest -q tests/utils/test_topk.py \
  -k 'cub_auto_short_width or cub_auto_valid_width or cub_forced_short_width or compact_pages_cuda_graph_replay or cub_transform_nonpositive_lengths or tie_break_modes'
```

Do not call static inspection or the old native probe an automatic-dispatch
GPU pass. The separate upstream draft PR should describe an auto-dispatch
shape guard, native padded semantics, preserved forced-CUB rejection, and
exact eager/graph validation. It should not claim the existing SGLang serving
measurements used the fix, remove their native-top-k limitation, or combine
the image AOT compatibility issue into this change.
