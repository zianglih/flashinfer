# Isolated 512-thread validation and benchmark adapters

These effort-only adapters admit the fixed two-decode-group, 512-thread candidate. They reuse the public numerical fixtures, sixteen-candidate lifecycle, distributed benchmark, split tactic recorder, source fingerprint, and original CUPTI loop. They do not change production source or any historical helper. CPU tests and synthetic plans are parser/control-flow checks; GPU admission, correctness, and performance remain pending.

- **Exact source:** `zero-dest-manifest-001.json` combines the six C1 changes relative to common source `4a3716c6…` with the scoped zero-destination proposal. Its only new file is `shim/w4a16/communication.py`: 1,573 inventoried source files, 338 required paths, exactly seven changed paths, prospective source `e2d88e6a564638efe464d5a586a2b0284e66cb0b14bb4b77c7743593a09a29e3`. The kernel digest is `2b85c9e3f727fddf60bc5327ecc63bdb38785367f17a398cdebf6bc32df8a17d`. All other files, including the native C++ build inputs and benchmark, must match the completed common-source owner. This is a proposed inventory, not a claim that the overlay has run.
- **Actual resource admission:** immediately after each new `_CompiledMega` is constructed, `resource_gate512.py` reads its compiled function's `.library`, resolves the named `CUkernel` and current-context `CUfunction`, and calls `cuFuncLoad` before reading `CU_FUNC_ATTRIBUTE_NUM_REGS`, maximum block size, static shared memory, and local memory. It requires actual initial REG128, 512 threads, and two decode groups. Compiler flags alone do not satisfy this gate. Query errors and rejected counts enter a single all-rank success reduction before any rank can launch this object's Mega kernel. Repeated checks on the same object return its private cached record without driver or collective work. The compiled object owns its library; no extra executor or external object-retention map is needed.
- **Runtime binding:** the exact inherited property owner is `CudaDialectJitCompiledFunction.library`, in installed `cutlass/cutlass_dsl/cuda_jit_executor.py` SHA256 `1589949f04c39184dc3ef9287720b029bb4f8e1161fb8e20a416977cb6bf6583`. The property explicitly supports accessing the single compiled CUDA library before first launch. It may perform its own lazy load; the gate never calls or separately pins `.to()`. The property implementation and source hash are checked before use, and the actual runtime class/file is recorded. Source/CPU method-resolution and installed driver API documentation are retained under `profiles/cuda132-jit-method-owner-001/`. The prepared compile-only probe intercepts `_ensure_compiled`, calls original compilation and resource admission, then raises a dedicated success sentinel before returning to the launch site. Ordinary setup kernels are allowed; this mode never calls the compiled Mega function.
- **Public/lifecycle admission:** original tolerances, per-route oracle, empty-rank behavior, cache ownership, and graph checks remain. Public mode selects M256/N128/C2, M256/N64/C2, or M128/N64/C1 or C2; flags become 8 only when the original fixture has no explicit value. Lifecycle mode checks all sixteen actual tactics. Public observation IDs live on their corresponding objects and only integer sets survive for result validation, avoiding stale `id()` reuse and workspace retention.
- **Timing boundary:** full13 still runs fixed CONTROL followed by independent auto16, 100 CUPTI iterations, three warmups, CUDA graph, cold L2. First-object admission is in setup, before timed replays; existing timing code is unchanged. Actual registers accompany every saved compiled choice. Online host-clock rankings, final CUPTI rows, and historical 640-thread results remain distinct.
- **Cache boundary:** only the completed same-stack owner's `TORCH_EXTENSIONS_DIR` and `FLASHINFER_WORKSPACE_BASE` are reused after source/runtime guards. DSL, driver, and knob caches are new. The owner must ensure prior cache writers have exited. Native reuse does not imply the full proposed source is identical to that historical owner.

Run commands from `/workspace/flashinfer-w4a16-megamoe` after the owner applies and fingerprints the exact candidate. The new `communication.py` must be included in the existing source inventory. Regenerate a separate declaration with `build_manifest.py` if the candidate changes; do not edit historical manifests. The validated CUDA 13.2 interpreter is `/usr/bin/python3`.

```bash
PROBE512=candidates/w4a16_dispatch_decode_reuse512_scoped/provenance512
MANIFEST512=$PROBE512/zero-dest-manifest-001.json
CACHE512=logs/cu132-cross-stack-full13-001/stack-manifest.json
PREFLIGHT512=logs/cu132-zero-dest512-preflight-001.json

CUDA_VISIBLE_DEVICES='' /usr/bin/python3 candidates/w4a16_c1_curated16/benchmark/preflight16.py \
  --expect-system-cuda 13.2 --output "$PREFLIGHT512"

# Omit --execute first to inspect each source-attested plan.
/usr/bin/python3 "$PROBE512/run_validation512.py" \
  --mode resource-probe --world-size 2 --tile m256n128 --cluster 2 \
  --candidate-manifest "$MANIFEST512" --native-cache-manifest "$CACHE512" \
  --preflight "$PREFLIGHT512" --name zero-dest512-resource-probe-ep2-001 --execute

/usr/bin/python3 "$PROBE512/run_validation512.py" \
  --mode public --world-size 2 --tile m256n128 --cluster 2 \
  --candidate-manifest "$MANIFEST512" --native-cache-manifest "$CACHE512" \
  --preflight "$PREFLIGHT512" --name zero-dest512-public-n128-ep2-001 --execute

/usr/bin/python3 "$PROBE512/run_validation512.py" \
  --mode lifecycle --world-size 2 \
  --candidate-manifest "$MANIFEST512" --native-cache-manifest "$CACHE512" \
  --preflight "$PREFLIGHT512" --name zero-dest512-lifecycle-ep2-001 --execute

# Run only after the owner's resource and numerical gates pass.
/usr/bin/python3 "$PROBE512/run_catalog16_512.py" cu132-zero-dest512-full13-001 \
  --candidate-manifest "$MANIFEST512" --native-cache-manifest "$CACHE512" \
  --preflight "$PREFLIGHT512" --execute

/usr/bin/python3 "$PROBE512/analyze_catalog16_512.py" cu132-zero-dest512-full13-001 \
  --output logs/cu132-zero-dest512-full13-001-analysis
```

Use separate names for EP1 and each additional declared public geometry. Both EP sizes and all needed public geometries are validation gates, not automatically established by the example EP2 command. Each process has a bounded timeout and explicit localhost rendezvous. The full13 analyzer requires all 52 latency rows, 208 split selections, 208 actual compiled observations, and 104 actual auto winners; no row-minimum substitution is supported.

Probe001 rejected both ranks before Mega because the original helper inspected the base JIT executor API; the CUDA dialect uses a different library representation. Original helper/tests/CPU evidence are archived under `failed-runtime-probe001/`, and the real failed run remains `logs/zero-dest512-resource-probe-ep2-001`. The repaired property-bound gate is still awaiting the owner's probe002; the earlier CPU-only success is not treated as runtime validation.
