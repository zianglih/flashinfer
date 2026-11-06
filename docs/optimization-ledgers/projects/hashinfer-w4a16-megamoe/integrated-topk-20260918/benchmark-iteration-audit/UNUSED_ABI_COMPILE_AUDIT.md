# Benchmark-only ABI preparation audit

Read-only audit; no production files, worker, runtime, GPU state, or existing evidence changed. Current source: `d01f074947d2cc754d6062c2b2ffe674e1577a34`. The just-completed ca05 S2 worker uses the same preparation and public benchmark paths.

## Actual opportunity

The public AUTO4 benchmark currently makes **8 `cute.compile` calls per row per rank**, not 4 ABIs for every tactic. The complete S2 records show exactly 8 calls for each of 13 rows on each of 8 ranks (832 total calls). This is API invocation evidence, not measured backend code-generation count: compiler cache hits may reduce work.

The source explains the eight calls:

1. The private autotuner compiles and executes the actual int32/vector input ABI for each of the four tactics.
2. It reapplies the winning configuration, invalidating that frontend's workspace/callable state, and compiles the actual ABI again for the final public forward.
3. Public backend `compute()` calls `_warm_staging_variants()`, compiling the three other winner ABIs: int32/generic, int64/generic, int64/vector. Subsequent calls see cached entries.

Only step 3 is avoidable in this fixed-fixture benchmark. Do not remove any tactic, alter the winner application, or infer a 37.5% wall-time reduction from call counts. The potential change is 8 to 5 compile API calls per row/rank; actual iteration savings need separate host-side measurement.

## Narrow optional worker design

A benchmark-only wrapper around frontend `_compile` can keep production warmup, cache layout, capture-readiness method, public `forward`, and the entire timing/autotune code unchanged:

- Preserve the original method and delegate without argument changes for `(torch.int32, True)`.
- For the three *synthetic warmup requests* only, return a uniquely tagged callable that always raises an explicit unsupported-benchmark-ABI error. Never alias these entries to the allowed compiled kernel.
- Assert the actual `inputs.staging_inputs` exists and classifies as int32/vector before accepting a compile request. A separate wrapper of `_staging_key` can reject any live source that classifies differently before lookup; `_warm_staging_variants` constructs its synthetic keys directly, so this does not suppress its normal loop.
- The sentinel must also raise if invoked, providing a second guard. The four-entry cache still satisfies the unchanged public capture readiness check, but three entries are deliberately rejecting stubs, not compiled support. Record this restricted harness contract explicitly; it must never be described as full public ABI validation.
- Patch only inside the existing benchmark worker process, before the benchmark creates layers, and restore both methods in `finally`. Scope by exact expected class/method fingerprints. Keep the exception-preserving compile observer and record actual compilations plus omitted synthetic requests separately.

This leaves `layer.warmup(tensors)` itself and its real eager launch intact, preserves every original private autotune warmup/graph/replay, and still times the unchanged `lambda: layer.forward(tensors)` via the same CUPTI graph helper. The wrapper sees the same compile key, descriptors, options and live input strides for every kernel that executes. No source-level kernel edit, new dtype/alignment promise, or alternative launch thunk is required.

A more transparent alternative is an actual-ABI-only `_warm_staging_variants` plus a benchmark-specific capture readiness checker that requires that exact real callable. That avoids placeholder entries but overrides more production preparation behavior. Simply making warmup a no-op fails the existing `len(_staging_variants) == 4` graph-readiness contract; populating all keys with the allowed kernel is unsafe because it could silently run a mismatched ABI.

## Required guardrails before any adoption

- The exported fixture explicitly converts routing IDs to contiguous int32, and BF16 hidden inputs have `(H, 1)` stride and 16-byte-aligned addresses. Check the *actual classification* on every rank/row, including empty ranks for 1/2/4 tokens; do not assume alignment from allocation provenance.
- Keep source dtype/strides, 4 tactics, O3, current fixture/digests, 3 warmups, 100 cold-L2 rankMAX CUPTI graph samples, source/host closure, and 104 exact finite cross-arm outputs unchanged.
- Record the reduced ABI coverage and omitted requests. The harness is unsuitable for generic-stride/int64/native correctness tests, where all four real ABIs must remain compiled and checked.
- A bounded initial validation should compare the actually executed generated code/resources and outputs to the ordinary worker, and measure host preparation time. No timing benefit is claimed from this read-only audit.
- Do not change the already-frozen hu115 runtime. Apply only in a future independently reviewed benchmark worker after root approval.

## Source and evidence anchors

Paths relative to `integrated-topk-20260918/reducer-inner-guard-cleanup/hashinfer`:

- `hashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/frontend.py:265`: actual ABI lazy compilation.
- `frontend.py:270`: public four-ABI warmup; comment explicitly distinguishes private autotune.
- `frontend.py:285`: unchanged compile descriptor/options construction.
- `frontend.py:313`: actual classification uses ID dtype, hidden stride, and address alignment.
- `frontend.py:419` and `:449`: public callable selection and launch; no substitution with a raw kernel thunk.
- `hashinfer/moe_ep/backends/mega/kernel/sm100/bf16_nvfp4_bf16_cutedsl/backend.py:182`: four-entry capture readiness contract.
- `backend.py:233` and `:264`: private tuning then final forward and full ABI preparation.
- `hashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/autotune.py:205`: each tactic gets only actual ABI eager preparation and graph timing.
- `hashinfer/moe_ep/modes/mega_layer.py:298`: public warmup delegates to full eager forward and synchronization.

Executed worker/benchmark: `cta-ready-staging/decode13-benchmark-hu15-recovery/{worker,benchmark}.py`. Rank compile records: `collected/assembled-evidence/perf-candidate/S2/rank{0..7}-evidence.json`. Timing/source/closure audit: `independent-file-timing-audit.json` SHA `645db008b620be09d39fb406f5744e25b559ba887138d771d418df7ec66f8f36`.
