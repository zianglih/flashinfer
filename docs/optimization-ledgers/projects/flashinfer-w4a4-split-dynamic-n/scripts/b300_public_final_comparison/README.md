# Archived original controls to fresh public-wrapper results

This adapter does not launch timing. It preserves the original NV public-wrapper and MX internal-assembly observations and compares them with fresh public-wrapper observations. It never rewrites raw observations to create common metadata fields.

`prepare_bridge.py` binds the exact source, proves unchanged native timing and V3 input generation (the sole specialization removes the V4.1 routing-bias dtype conditional), checks the original/current native routing call, and binds the 72-output / 24-input-tactic-policy-launch public API migration gate. `fingerprint_public.py` runs outside measurement: all13 activation/router and route hashes, full expert-weight/input hashes at tokens1/32, unchanged actual runtime and all85 source pins. Full-weight identity for other tokens relies on the exact input AST and seed/runtime; it is not rehashed or claimed as full-grid hash coverage.

`summarize.py --config <config.json> --output <new-summary.json>` requires a clean final85-file receipt and full13-token public observer archives. Configuration:

```json
{
  "archived_summary": "/absolute/project/evidence/b300-original-final-v3-r3/paired-summary.json",
  "bridge": "/absolute/project/evidence/b300-public-final-bridge-r1/bridge.json",
  "fingerprint": "/absolute/project/evidence/b300-public-final-bridge-r1/raw/fingerprint.json",
  "dependency_proof": "/absolute/project/evidence/b300-public-final-bridge-r1/dependency-proof.json",
  "final_source": "/absolute/project/evidence/final-source/source.json",
  "candidates": {
    "nvfp4": {"A1": "/absolute/A1-V3/raw", "A2": "/absolute/A2-V3/raw"},
    "mxfp8": {"A1": "/absolute/A1-V3/raw", "A2": "/absolute/A2-V3/raw"},
    "mxfp4": {"A1": "/absolute/A1-V3-mixed-GPU6/raw", "A2": "/absolute/A2-V3-mixed-GPU6/raw"}
  }
}
```

Each candidate directory contains `receipt.json` and its `nvfp4/observed/results.json` or `mxfp/observed/results.json`, stdout/stderr status receipts and all saved AUTO caches. NV must use the original GPU2 UUID; homogeneous MX GPU4; mixed GPU6. The adapter rejects missing/different source pins, token grid, native timer, CLI flags, configured environment values, saved-tactic loading, route fingerprints/histograms, selected public-wrapper cache names, GPU identities or actual runtime/JIT versions. `CUTE_DSL_CACHE_DIR` is checked only as the recorded configuration value; it does not prove persistent CuTe compiler-cache reuse because this runtime does not consume that variable.

Output retains the renderer's `formats.<mode>.rows[].medians_ms`, `speedup` and `aggregates` fields, plus:

- `chronology.kind = archived_controls_fresh_candidate`, per-mode/arm timestamps, `new_temporal_bracket = false`. Direct `sqrt(C1*C2/(A1*A2))`, no new-control claim, no incremental ratio multiplication; tokens1/2 excluded from every aggregate.
- `observations[mode][arm]`: the original raw observer JSON path. `observation_receipts[mode][arm]`: its original campaign receipt or native public-table runner receipt. All paths are covered by `inputs_sha256`.
- `runtime[mode]`: canonical common actual runtime (`cutlass_dsl=4.7.1`, `torch_cuda=13.2`, import/executable paths, CUPTI), plus `jit_packages` and the explicit distribution-metadata distinction.
- `runtime_bridge[mode].arms[arm]`: raw observation/receipt paths, provenance kind, actual imported CuTe/Torch fields, original distribution metadata, exact JIT versions. Candidate metadata comes from its runner receipt, not invented fields on the observer. CUPTI package-path provenance comes from the source-pinned fingerprint using the same resolved executable and environment; the original observer recorded its compiled extension, whereas the fingerprint records package `__init__.py`. Their resolved package directories and package/library versions must match; the two file names are not claimed identical.
- `runtime_bridge[mode].driver_evidence`: archived bootstrap nvidia-smi receipt and fresh runner receipts. Original timed observers recorded UUID/name only. The bootstrap has the same host/UUID and records595.91.07; no container `CUDA_DRIVER_VERSION` comparison.
- `fingerprint_bridge`: proof/receipt paths and the four exact benchmark/preparation/public-API/tuner scope-file hashes. This explicitly permits separately measured kernel changes without claiming whole-source identity with the earlier fingerprint.
- `tactics[mode][arm][token]`: native cache operation and selected tactic; caches remain hash-bound. Original MX names remain `BenchmarkSplitMxfp8::*`; final names are `CuteDslMoEWrapper::run::w8a8::Swiglu` / `w4a8`.

The original observer enumerated `nvidia-cutlass-dsl=4.4.2` after the active venv distribution, while recording the actual imported module as4.7.1 at its venv path. Fresh receipts select metadata4.7.1. Compare actual imports and exact `nvidia-nvvm`/`nvidia-cuda-nvcc=13.3.73` plus CUDA-CUPTI13.4.58. Do not require whole `compiler_distributions` dictionaries to match, and do not insert a fabricated dictionary into native raw observations.

The old helper plan that added two PDL keywords to archived MX assembly is superseded. Fresh final candidates must use the current `bench_moe_deepseek.py` public wrapper, with API and behavior selection in the library.
