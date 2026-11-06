# Final kernel cleanup audit

Reviewed on 2026-10-26 in `flashinfer-generality-review`, initially clean at
`74388819899d0abfd1a12102f7cc108bda13c812`, against PR base
`a65d5b09e7e4c4c5c160b0161c48becd100b3970`. All cleanup remains unstaged.
No GPU work, commits, pushes, or additional checkouts were used in this pass.

## Result and cleanup

No new high-confidence indexing, scaling, layout, or synchronization defect was
found in the reviewed kernel implementation. The stale kernel replacement is
preserved in full. This is a static review, not a claim that every possible
configuration has runtime coverage.

- Removed `blackwell.utils.blk_reduce_fp32` and `blk_reduce_fp16`, left over from
  the superseded FC2 implementation. A search of all 4,799 tracked Python files
  found no remaining Blackwell caller/import; Hopper and Rubin retain separate
  implementations. `blk_reduce_bf16` remains because W4A16 uses it.
- Corrected the combine documentation: blockscaled FC2 now reads published
  routing metadata during prefetch, before its payload dependency wait.
- Clarified that the shared epilogue consumes 128 channels **per CTA**, including
  when the GEMM has two CTAs. Updated its invalid-configuration error text.
- Removed two redundant comments beside the canonical scale-factor path.

The active implementation was not refactored merely to reduce line count.
In particular, W4A16's identity aliases, existing scheduling/stage choices,
active iKET markers, all barriers, mathematical expressions, and layout
construction are unchanged.

## Scope read

- Entire shared SM100 core and FC1/FC2 capability adapters: constructor,
  capability admission, TMEM/SMEM planning, tensor layouts, TMA setup, dynamic
  descriptors, startup, producer/MMA/epilogue roles, CLC queue, and teardown.
- Entire added blockscaled epilogue in `blackwell/utils.py`, including gated and
  per-token scaling, SiTU, native output quantization, TMEM transpose, overlapping
  windows, bulk scatter, and atomic fused finalize.
- Entire routed preparation and deterministic combine kernels.
- Full PR deltas to W4A16 and the per-token NVFP4 quantizer, with surrounding
  transform, entry, trigger, and output paths. Unrelated W4A16/quantizer kernels
  were not refactored.
- Relevant host callsites were read to verify direct behavior knobs, input
  publication, and the actual caller contracts. Host/tuner/API edits belong to
  the parent agent and are outside this patch.

## Remaining branches: reason and boundary

| Branch or restriction | Classification and audit conclusion |
|---|---|
| FP4/FP8 operand and E4M3/E8M0 scale selection | Native MMA instruction/descriptor encoding and numerical quantization contract. Homogeneous FP4 uses the appropriate SF16/SF32 instruction; mixed FP4 weights occupy byte slots for `mxf8f6f4`. These are not model-specific policies. |
| Logical M128/M256/M512; one/two CTA | Implemented ownership/layout family: each CTA owns 128 channels, M512 reuses B/SFB across two physical M256 channel tiles. It is not a claim that the ISA forbids other logical reuse counts. Partial-channel output masks and second-channel-tile release order remain necessary. |
| Allocated N at least 32; live N rounded to 16 | Current TMEM transpose/ownership contract. The logical B copy extent is smaller where needed, while preserving the original physical K-slab/stage strides. This is not a claim that all native MMA instructions have a minimum N16. |
| Route N128+ uses TMA SFB; smaller tiles use cp.async | Canonical scales have 128-row atoms. Smaller route starts can lie inside an atom and require indexed copies. TMA's separate K/row coordinates preserve tail zero-fill without entering another row atom. |
| Narrow group-two scale readiness join | Real cross-CTA dependency: both local cp.async publications must complete before group-wide S2T. Leader barrier initialization, cluster release/acquire, stage phase, and metadata accounting remain intact. |
| TMEM accumulator count and overlapping windows | Capacity is queried from the SM100 architecture; accumulator and scale columns determine eligibility. At most two buffers and the 64-column early-release window are implemented epilogue ownership limits, separate from hardware capacity. |
| K4/K8 and operand-stage counts | Supported internal tactic choices, evaluated using actual layout bytes, scale/TMEM capacity, epilogue scratch, and metadata. SharedStorage is checked against architecture capacity after construction. The automatic fallback ranking is a policy, not a universal performance optimum; native AUTO can select explicit per-phase K. |
| Static versus CLC scheduler | Private tuning choice; effective CLC admission additionally honors SM reservations, work capacity, and CUDA grid-Y limits. CLC metadata slots are acquired before issuing the next cancellation; terminal metadata is consumed/released by every participating role. |
| PDL publication owner | Static launch: physical `(x,y,z)==(0,0,0)`. CLC: each executing cluster's leader, because a fixed initial CTA could be canceled. All first-trigger positions and payload waits remain unchanged. |
| Bulk output only for supported BF16/FP16 scatter and wide route tiles | Output-format/store ownership plus a retained measured implementation/performance boundary. The narrow path remains the TMEM-transpose/direct-store path. This is not an ISA prohibition on narrow bulk stores. |
| Mixed FC1 output E4M3; mixed FC2 output BF16 adapter checks | Existing supported API/coverage restrictions, not inferred hardware limitations. Broadening them would require a distinct numerical/output-layout gate and was not part of cleanup. |
| Prepare 32-byte payload and four-scale alignment | Required by its 256-bit vector payload copies and packed scale copy/layout contract. SF padding through the final canonical atom remains required; unused payload rows are masked by consumers. |
| Combine thread/vector selection | Retained generic token-count/vectorization policy, including divisor-based final-CTA packing. The pre-existing `8`/`1024` token cutoffs and current vector candidates were not reclassified as hardware limits or altered without timing evidence. |

There is no model name, hidden/intermediate-size, expert-count, or workload-name
whitelist in the shared GEMM planner or prefetch path. That statement does not
mean every branch is an ISA limit or that the whole backend has no performance
policy: the boundaries above remain explicit.

## Pipeline invariants checked

- **Startup:** the scheduler's initial tile and the prefetch tile use the same
  cluster-aware flattening. Full-ring priming is bounded by actual stage count
  and reduction tiles. Padded/empty work does not acquire the operand ring.
  The regular producer skips only weight stages already primed for that tile.
- **Dependency ownership:** A/SFA prefetch has no dtype, tile-size, one-CTA, or
  static-only gate. Published ancestor routing is ready before those reads;
  B/SFB payload remains after the dependency wait. This applies structurally to
  admitted one/two-CTA, static/CLC paths; existing bounded runtime evidence is
  separate from this source review.
- **Barriers:** group-scaled expected TMA bytes use the logical B copy extent;
  local scale cp.async and group-wide S2T have their distinct readiness edge.
  Both channel MMAs complete before an operand slot is released. Accumulator
  ownership is released after protected TMEM reads, including skipped-output
  and padded-slab cases. Independent cloned producer-tail states are retained.
- **Epilogue:** up16/gate16 ordering agrees with the prepared weight layout;
  SF32 joins the adjacent 16-channel fragments; per-token scales retain original
  versus routed indexing. Scatter and fused output use different destination
  contracts. Wide bulk writes mask an entirely empty second CTA.
- **Prepare/quantizer/combine:** prepare preserves payload/SF bytes and zeroes
  invalid canonical SF rows. The per-token quantizer republishes immutable
  ancestor metadata with its CTA0 fence; its own payload remains protected by
  the consumer wait. Combine masks nonlocal rows before loading and preserves
  the separate first-slot multiply plus ordered FP32 FMA rounding contract.
- **W4A16:** only the shared prepared gated-weight order changed in this PR;
  both payload and scale transforms consume that same order. The retained
  decoder and unrelated pipeline policies remain intact.

## Static evidence

`kernel-static-checks.json` records all seven before/after hashes and confirms:

- all **64 active** `@cute.jit`, `@cute.kernel`, and `@dsl_user_op` function ASTs
  are identical after removing docstrings;
- whole modules are identical after allowing only the two dead definitions,
  docs/comments, and the exact invalid-epilogue error-text correction;
- all seven files parse/compile as Python, without importing CUDA;
- whole-repository symbol reachability is recorded, including the separate
  Hopper/Rubin definitions and retained W4A16 BF16 caller.

Reproduce with:

```sh
python3 audit-final-cleanup/audit_kernel_cleanup.py
```

Scoped pre-commit passed without further source changes; see
`kernel-precommit.json` and `kernel-precommit.log`. The initial formatter pass is
preserved in `kernel-precommit-format-pass.log`. `git diff --check` passed for
owned files. `kernel-cleanup.patch` contains only this agent's owned cleanup.
Baseline snapshots live under `kernel-baseline/`.

No new runtime or emitted-code identity is claimed: source fingerprints may
change compilation cache entries even when active ASTs are unchanged. Existing
retained-source evidence remains in `evidence/generality-scheduler-tests-r5`,
`evidence/generality-scheduler-replay-r5`, and
`evidence/generality-retained-74388819-independent`. This cleanup pass did not
repeat those gates or broaden their coverage.
