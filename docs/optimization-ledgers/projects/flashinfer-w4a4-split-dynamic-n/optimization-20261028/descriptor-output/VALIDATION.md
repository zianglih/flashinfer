# Descriptor-bounded output validation

This experiment owns helpers and evidence here; source remains unstaged in
`../../flashinfer-descriptor-output-review`. The source baseline is the padded
output R2 candidate, not the older compact-output retained branch. No sanitizer.

## Existing runtime, verified 2026-10-28

- `/usr/local/bin/h` is the managed HAI CLI.
- C3/infra: `fi-moe-nvfp4-port-1026` and `fi-moe-sanitize-1028`, each 8 B300 GPUs.
  All 16 GPUs were idle during read-only inventory. GPU allocations must be
  assigned by the coordinating agent before launching work.
- Existing image: `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2; no new box requested.
- Python: `/data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python`.
- Dependency overlay: `/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps`.
- Prior R2 root: `/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/padded-output/r2/validation`.
  Its `flashinfer-candidate/` is the paired control, `compile/` has nine working
  persistent native-cache links. Never remove either role's native cache.
- Machine-readable receipts: `inventory-primary.json`, `inventory-secondary.json`.

## Focused gate

1. Freeze candidate source hashes and a binary diff; deploy into a new project
   directory without touching prior R2 or retained snapshots. Use a separate
   strict CuTe DSL cache and reuse the nine persistent native-cache targets.
2. Run paired exact output checks with fixed inputs, routing, and explicit
   tactics. Static/CLC, PDL off/on, one-/two-CTA, balanced/skewed/empty/reactivated
   routing are required. Replay the same CUDA graph after changing routing.
3. W4A16: SwiGLU, SiTU, GeGLU-tanh, ReLU-squared, both old/swap-AB weight layouts;
   capture FC1 intermediate and FC2 output tensors. Blockscaled: NVFP4,
   NVFP4 per-token, MXFP8, MXFP4x8; capture FC2. Swap-AB FC1 stays SIMT.
4. Poison captured output tensors with NaNs before replay. Candidate valid rows
   must match R2 exactly; candidate out-of-bound expert rows must retain the
   sentinel. W4A16 reuses prepare storage for FC2, so inspect only padding rows
   which prepare does not write. Include a zero-live-expert replay followed by a
   nonempty replay to detect stale descriptors.
5. Capture representative PTX/SASS/resource usage: descriptor publication and
   acquire instructions, TMA store paths, no output SIMT tail fallback in the
   requested stages, and no unexpected local spills.
6. Run existing exact wrapper/functional tests. Do not add tests of the reference
   implementation, broaden sanitizer coverage, or commit helper scripts.

The earlier blockscaled gate is
`../padded-output/r2/validation/probe_pair.py`; its source-specific compact output
assertions must not be reused unchanged. The existing smoke selection is in
`../padded-output/r2/validation/run_smoke.py`. W4A16 boundary tests are
`tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoeW4A16::test_route_tile_boundary_accuracy`.

## Performance after correctness

Reuse `../padded-output/r2/validation/{observe_benchmark.py,arm_contracts.py,nested_timing.py}`
and `run_perf.py`, with a fresh source-bound config. Benchmark through
`benchmarks/bench_moe_deepseek.py` using saved fixed winners and strict CUPTI.
Use tokens 4/64/4096/16384 first across V3/V41F/K3/N3U and EP/TP; NV includes input
quantization, all swap-AB arms use unfused finalize. Use the R2 measurements as
the incremental baseline, preserving the actual GPU UUID match, and report
timing drift if controls are reused rather than interleaved.

Persistent environment shared by the earlier runner:

```sh
export FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1
export FLASHINFER_CUDA_ARCH_LIST=10.3a
export FLASHINFER_DIST_AWARE_AUTOTUNE=0
export TRTLLM_ENABLE_PDL=1
export MAX_JOBS=8
export OMP_NUM_THREADS=1
```

Source correctness commands and source manifests will be recorded alongside
the first deployed candidate. This note is a preparation plan, not a claim that
the new implementation has compiled or passed.

## Descriptor proof and first full gates (2026-10-28)

The final implementation snapshot is `full-gate-03`, source HEAD
`61249e0bbd40dd2c6e583e4e48ff95e055a3c7f8` plus its recorded unstaged patch.
The 349-file SHA256 manifest matched the local review copy after deployment.

Passed on B300/CUDA 13.2:

- Shared descriptor proof: 16 BF16/FP32 cases, PDL off/on, two independent output
  templates, changing partial bounds, empty routes, reactivation, exact payload,
  and untouched NaN padding. This ran on snapshot02; shared helper and prepare
  hashes are identical in final03.
- Actual FP32 FC2: 32 cases on final03, with row- and channel-varying exactly
  representable values, one/two CTA, both requested scheduler settings, PDL off/on, and four changing
  routing replays. Exact outputs and untouched padding.
- NVFP4 N16 and W4A16 N16: 16 source-paired graph replays each on final03;
  canonicalized intermediate outputs and final outputs are byte-identical to
  the padded-output R2 control. Static/CLC and PDL off/on also agree exactly.
- Existing pytest selection: 11 passed on snapshot02, including six W4 weight
  scale mappings, two W4 route boundaries, old/swap layout update checks, and
  direct swap-AB FC1 N16 partial K. The relevant W4/prepare sources are identical
  between snapshot02 and final03. Peer-owned raw receipts are stored separately.

The early proof found two genuine compile-time pointer-alignment issues that
were fixed in the shared helper before full gates. Subsequent failed proof runs
were harness issues: a cached CUDA stream outside graph capture, element-index
swizzle versus pointer swizzle in synthetic shared stores, and a synthetic W4
raw-2D store assuming a flat tile shape. Production W4 is tested through native
`cute.copy` in the full kernel instead. Early full gates also incorrectly hashed
routed workspace rows in the nondeterministic routing order; the final harness
canonicalizes these rows by expanded route ID while preserving cross-PDL/CLC
and cross-source exactness. The failed raw-order comparisons already had
identical final output hashes. All earlier receipts remain separate from the
passing final03 evidence.

Remaining full dtype/layout gates and the CUPTI screen are in progress. No
sanitizer was run, as requested. Performance is owned by the separate
`tma_store_cutlass_audit` agent, with the R2 candidate as the reused control and
actual GPU UUIDs matched to the original measurements.

## Full canonical output gate complete

`full-gate-03/gate-summary.json` records 224 successful candidate graph replays
across all 14 configurations, paired against 224 control replays. All valid
intermediate values (canonicalized by expanded route ID) and final outputs are
byte-identical, including cross-CLC and cross-PDL comparisons. Every candidate
padding check passed. All 112 captured candidate GEMM compilations contain zero
`tensormap.replace` instructions and zero SASS local load/store spill sites;
descriptor publication remains in prepare.

The W4 fused-finalize compatibility smoke also passed all four paired cases
(old/swap layout × PDL off/on), with exact FC1 and exact final values in these
cases. Its required final-output threshold was `rtol=atol=1e-2`, since fused
reduction is outside the bit-exact reference contract. No source test was added.

Verified raw small artifacts are in
`full-gate-03/evidence-metadata/`, with SHA256 receipts in
`full-gate-03/gate-evidence-receipt.json`. Larger PTX, SASS, and CUBIN files remain
in the corresponding durable remote snapshot directories. The shared native
compilation cache was preserved throughout.

## Wide output staging coverage

The final03 direct output oracle passed 192 FP16/FP32 cases over N16/N128/N256,
one/two CTA, PDL off/on, partial/empty/reactivated routes, exact varied payloads,
and untouched padding. Compiled metadata confirms one store stage at N16, two
at N128/N256, and overlapping accumulators at N256 for both output types.
The four-live-tile allocation causes the normal small-grid policy to fold
requested CLC to static; a separate supplemental probe increases allocated
capacity while retaining four live tiles to force actual CLC. Its result is
recorded separately instead of claiming the requested flag alone proves CLC.

Both existing C3 devboxes disappeared from the infra inventory after the completed
main and direct gates. The supplemental active-CLC FP16/FP32 oracle had launched
on primary GPU4, PID1127324, but its completion could not yet be collected. Do
not claim it passed until its persistent `active-clc-outputs/receipt.json` is
recovered. Existing completed receipts and source postflight are already local.

## Supplemental actual-CLC proof recovered and passed

The first supplemental attempt failed the host metadata-capacity check before
launch: its larger allocation needed equally sized metadata arrays, despite only
four live entries. Padding those helper arrays fixed the probe; no implementation
change was required. On `fi-moe-descriptor-recover-1028` (C3/ziangli), all 96
FP16/FP32 checks passed with actual CLC asserted in all 24 compiled variants.
Coverage is N16/N128/N256 × one/two CTA × PDL off/on × four changing bounds.
Final03 source hashes were verified afterward. Verified artifacts are in
`recovery-1028/active-clc-evidence/`; summary is `active-clc-verification.json`.

A subsequent W4-only barrier relocation is being evaluated as **source04**.
All evidence above describes source03; it must not be presented as source04
validation without the separate affected-W4 gate.
## Source04 affected-W4 gate complete

Source04 changes only `moe_w4a16_kernel.py` versus source03, moving the existing
SMEM reuse wait and warpgroup synchronization to just before the next shared
write. Its SHA256 is
`777baf6bb832a5152022f8f3e9364f3bddba944c3e17fa2913f68170ea562110`.
All other 348 manifest entries match source03. The control for this follow-up
is frozen source03, not R2.

- All 96 candidate graph replays, paired with 96 source03 replays, passed over
  the six W4 configurations (8–13). Final and canonicalized FC1/FC2 values are
  byte-identical across sources, CLC/static scheduling, and PDL off/on. Partial,
  empty, and reactivated routing preserve every checked NaN padding row.
- All 48 captured candidate GEMM compilations have zero `tensormap.replace`,
  zero SASS local load/store sites, and zero reported stack/local bytes.
- All 10 focused existing W4 tests passed (zero failure/error/skip). Four paired
  fused-finalize compatibility cases passed with exact FC1 and observed final
  maximum absolute difference zero; the fused reduction remains outside the
  universal bit-exact contract.
- Source SHA256 manifests were checked before and after each runtime phase.
  No sanitizer was run. Unchanged blockscaled and shared-helper source retains
  the separately identified source03 evidence above; those tests were not
  redundantly rerun for the W4-only wait relocation.

The verified consolidation is `full-gate-04/validation-status.json`; per-compile
metadata is `full-gate-04/compiler-resource-summary.json`. Reproduce local
receipt checks with `python3 summarize_source04.py` from this directory. Raw
receipts and resource reports are in `full-gate-04/evidence-metadata/`; existing
pytest and fused receipts are in `source04-existing-gate/`. GPUs 2–4 were released
to the performance owner after the completed receipts were fetched. Performance
results are maintained separately and do not affect this correctness claim.
