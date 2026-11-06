# Rebased kernel and launch-wrapper scope audit

Reviewed against upstream `215f83cb27e39b6b973c0691b93fc378a53a10e4` on
2026-10-26. The review began at `24da0138fd67dc7172ef3dd9e6d1358e2b059a53`;
the parent subsequently folded the agreed cleanup and public-default restoration
into clean `eb141478505103f4bc65d10fb655f3deb3cd71dc`. No GPU work, commit, push, or new
source checkout was performed by this audit agent.

## Result and exact cleanup

The replacement of the old Blackwell FC1/FC2 kernels is necessary and remains
complete. No new device indexing, layout, arithmetic, barrier, or resource-policy
defect was found in this pass. The cleanup is confined to two host wrappers:

- Restore upstream's explicit missing-global-scale check for FP4 output.
- Apply the additional normalized-output requirement only to Blackwell. The
  previously retained check unintentionally rejected Rubin non-FP4 calls that
  upstream allowed. This restores upstream admission; it does not attempt to
  broaden or repair Rubin's output-quantization implementation.
- Restore both public wrappers' upstream geometry defaults. Private Blackwell
  implementation defaults and every device function remain unchanged.

The other seven owned files are byte-identical to the initial snapshot. All
64 active device/JIT function ASTs are identical. The exact edit is saved in
`kernel-cleanup.patch`, with source hashes in `kernel-static-checks.json`.

## Upstream/Rubin integration

- `flashinfer/fused_moe/cute_dsl/rubin/` has no diff against the new upstream
  base. No Rubin device code is changed.
- The two old architecture-dispatching compilation factories now serve Rubin
  alone; Blackwell returns through the new shared launcher first. Removing
  unreachable old Blackwell constructor branches, per-token pointers, and
  `is_rubin` ternaries is a direct consequence of replacing Blackwell. Restoring
  them only to reduce the textual diff would preserve dead implementation.
- An AST-extracted CPU comparison of the actual upstream/current factories
  passes **416 gather and 128 finalize cases**. It compares constructor args,
  `cute.compile` argument order/types represented by stubs, cache keys, repeat
  cache hits, and errors. It includes localized half-GEMM forwarding, SiTU,
  clamp/custom-activation checks, PDL, fused/unfused finalize, per-token rejection,
  and router-scale rejection. This is a host protocol proof, not Rubin GPU or
  code-generation validation.
- The rebase correctly preserves upstream Rubin unfused-finalize support:
  `use_fused_finalize` reaches the Rubin constructor; the older PR-only rejection
  is gone. The existing Rubin FP8/SF pointer representation is also upstream code.
- Public parameters, annotations, argument kinds and defaults now exactly match
  upstream, and no K, cache-hint, scheduler, or prefetch tuning knob was exposed
  publicly. One retained API default difference was found and corrected below.

### Public-default boundary corrected

The retained PR had changed both public wrappers to
`mma_tiler_mn=(128,128)`/`cluster_shape_mn=(1,1)`. A Rubin caller supplying its MMA
tiler but omitting the cluster would therefore observe a changed default. Both
public signatures now restore upstream `(256,128)`/`(2,1)` exactly. The private
Blackwell implementations retain their existing defaults.

The source-bound benchmark callsite proof covers the single `bench_cute_dsl`
implementation shared by all three model presets and both table families. The
public whole-MoE wrapper's runner passes selected per-phase geometry explicitly;
all four low-level calls (ordinary private and localized public) pass explicit
MMA and cluster geometry. Thus these restored public defaults do not alter those
benchmark launches. TRT and W4A16 do not use the blockscaled wrappers. This is a
source callsite proof; the parent restarted the six fresh tables on final eb141478.

## Full owned scope inspected

- Both top-level blockscaled wrappers: dispatch, validation, scale/output
  allocation, pointer order, private behavior controls, cache keys, runtime-N
  launcher, SM reservation/grid bounds, and architecture-specific tails.
- Blackwell FC1 adapter and shared FC1/FC2 core: capability checks, K/stage/TMEM
  planning, logical-B copy extent, SF layouts, descriptor updates, persistent
  scheduler/CLC, initial-weight prefetch, producer/MMA/epilogue roles, and drain.
- `blackwell/utils.py`: added blockscaled epilogue, gating/SiTU, quantized output,
  per-token scaling, TMEM ownership/transposition, bulk scatter and fused atomics.
- Routed preparation and deterministic combine; full PR deltas and surrounding
  entry/exit code in the shared per-token quantizer and W4A16 kernel.

The earlier retained dead-helper/doc cleanup and detailed invariants remain in
`../audit-final-cleanup/kernel.md`. This rebased audit rechecked the upstream
integration and source equality instead of repeating prior performance trials.

## Branch and dependency classification

| Branch or check | Reason retained |
|---|---|
| FP4/FP8 and SF16/SF32 instruction choices | Native instruction/descriptor representation and numerical scaling. These are real type distinctions, not model policy. |
| M128/M256/M512 and one/two CTA ownership | Supported physical channel ownership/reuse layouts. Logical M512 shares B/SFB over two channel tiles; this does not claim the ISA forbids other reuse counts. |
| Physical N at least 32 and live MMA N rounded 16 | Current TMEM ownership/epilogue contract. Logical B copies only the valid requested extent while retaining K-slab/stage strides. |
| TMA versus cp.async SFB at canonical atom boundaries | Canonical SF atoms cover 128 rows; narrower routes require indexed copies. Group-two narrow copies have a real cross-CTA readiness edge. |
| Cluster SF join | Cluster-scope release/acquire and per-stage storage are required before leader group-wide S2T; metadata is included in both automatic K planning and final stage fitting. |
| Accumulator/scratch/stage limits | Architecture capacity and actual shared layouts determine fit. Two accumulator buffers and 64-column early release are implemented ownership contracts, not universal ISA limits. |
| Private explicit K4/K8 and FC1 scheduler choice | General autotune choices. The fallback planner ranking is a performance policy; persisted tactic cache version4 distinguishes the expanded search. |
| Effective CLC admission | Honors explicit SM reservations, work capacity and CUDA grid-Y bounds. It is independent of model names/dimensions. Queue acquisition precedes cancellation. |
| PDL publication owner | Static physical XYZ CTA0, or executing cluster leader under cancellation. Every CTA still signals; dependent payload waits remain intact. |
| Bulk output / mixed output admission | Implemented output-layout and measured performance boundaries. Narrow bulk stores and extra mixed output types were not widened during cleanup without evidence. |
| Prepare/combine vectorization | Alignment and vector ownership contracts plus retained generic token-count/thread policies; not all such branches are hardware requirements. |

No model name, hidden/intermediate dimension, expert count or benchmark-shape
whitelist appears in the shared resource/prefetch policy. Prefetch structurally
supports the admitted one/two-CTA and static/CLC configurations, including
per-token paths. Existing bounded runtime evidence is separate; this review does
not assert exhaustive hardware coverage.

## Surrounding changes retained for correctness

- W4A16's removed up/gate shared-memory permutation follows the common prepared
  up16/gate16 weight order. Payload and scale transforms consume the same order;
  retaining the old permutation would double-transform those prepared weights.
- The per-token quantizer's startup publication/trigger change is needed by
  early weight-prefetch consumers. It republishes completed ancestor metadata;
  its own new payload remains protected by the dependency wait.
- Separate phase adapters and the generic launcher validate different contracts:
  phase-specific supported output modes versus actual explicit-K storage. Their
  checks were not deleted as superficial duplication.
- iKET markers, cache hierarchy, PDL waits/signals, barrier counts, prepare/combine
  math and mature W4A16 paths were not altered in this cleanup.

## Reproduction and validation boundary

```sh
python3 audit-rebased-20261026/audit_kernel_scope.py
```

`kernel-static-checks.json` binds the nine initial/final files, exact patch,
576 output-validation cases (288 Rubin cases exactly match upstream), 544 Rubin
factory cases, exact upstream public-default equivalence, the explicit benchmark
geometry callsites, and 64 unchanged active function
ASTs. Blackwell success/rejection outcomes are unchanged by the validation fix;
the FP4 error text returns to upstream wording. All owned files parse/compile as
Python without importing CUDA. `kernel-final-precommit.json`/`.log` record the
final two-file scoped pre-commit run at eb141478 with identical before/after
source hashes. The earlier one-file 3c0ec82f check remains in
`kernel-precommit.json`/`.log`.

No new emitted-code or GPU equivalence is claimed. Source fingerprints may
invalidate compilation caches despite unchanged active ASTs. The parent owns
the fresh source-bound B300 validation/performance campaign and publication.
