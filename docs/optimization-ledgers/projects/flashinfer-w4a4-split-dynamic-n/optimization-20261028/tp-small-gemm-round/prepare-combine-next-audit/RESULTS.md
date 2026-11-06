# TP prepare/combine audit at 61249e0b

Read-only audit, 2026-10-28. Source is clean retained `61249e0bbd40dd2c6e583e4e48ff95e055a3c7f8`. No source variant, GPU launch or timing was created. The in-flight full refresh remains authoritative for current end-to-end gaps; all stage/profile numbers below are explicitly historical.

## What is left, and what is already removed

The 83df TP8/EP1 MXFP4x8 T16384 trace attributes 313.778 + 367.075 µs of the V3 1547.306 µs span to prepare/combine extension (44.0%); K3 is 334.418 + 321.779 of1867.004 µs (35.1%). Extension avoids double-counting overlapping intervals but is not a dependency-DAG proof. K3's older d1767 NCU shows long-scoreboard stalls at prepare87.74% and combine93.17%. The prepare source-counter analysis places68.68% of sampled long-scoreboard stalls at the payload STG256 waiting on its LDG256 result; routing/limit reads are also visible. These observations support a memory/dataflow constraint, not a missing barrier-removal opportunity. They are not timings or counters for61249.

For TP with all experts local, useful output traffic scales with `R = tokens × top_k`, even though expert intermediate width shrinks with TP. At16384 tokens, the current unfused BF16 contract requires:

| Model | Hidden / top-k | FC2 useful output write | Combine useful input read | Final output write | MXFP8 routed payload write |
|---|---:|---:|---:|---:|---:|
| V3 | 7168 / 8 | 1792 MiB | 1792 MiB | 224 MiB | 896 MiB |
| V41F | 5120 / 6 | 960 MiB | 960 MiB | 160 MiB | 480 MiB |
| K3 | 3584 / 16 | 1792 MiB | 1792 MiB | 112 MiB | 896 MiB |
| N3U | 2048 / 22 | 1408 MiB | 1408 MiB | 64 MiB | 704 MiB |

These are logical global-memory bytes, not predicted DRAM bytes or latency. The MXFP8 payload column describes the format's byte cost, not benchmark support for every model/topology; V41F TP MX is excluded from the current comparison. FP4 routed payload bytes are half that column. Cache can reuse source activations; neither this table nor sampled stalls imply every routed read hits DRAM. EP local work depends on actual routing, not a guaranteed1/EP fraction.

Current source already handles the obvious padding/setup savings:

- `moe_swap_ab_prepare.py:145–209`: payload reads/writes occur only for valid logical routes; physical SF padding and storage beyond live tiles stay untouched. Only invalid **logical** SF rows are zeroed. SF preload and256-bit payload copies are already present; fixed-atom bit indexing is retained. The grid is already bounded by metadata capacity and hardware thread capacity at318–327.
- `moe_utils.py:137–199`: routing allocation uses the tight worst-case tile bound. Reducing it based on an observed distribution would break general graph replay or require device-to-host synchronization. Allocation capacity is not the number of payload bytes actually copied.
- `_get_output_workspace` in `moe_swap_ab.py:58–75` and the FC2 compact path remove padded BF16 output storage for bulk-capable epilogues. Prefixes pack valid rows, full slabs use ordinary2D TMA, tails preserve compact bounds, and only the channel-zero owner publishes inverse indices. Non-bulk plans compile out the workspace. No further all-expert padded-output allocation is left to remove.
- `moe_finalize.py:155–212`: eight BF16 elements per thread use128-bit vectors, paired FP32 arithmetic, pre-wait routing/weight loads, and post-wait expert reads. The public scaled core passes `input_is_expanded=True` even with compact metadata, so existing exact-divisor geometry already applies. The flag describes how the original mapping supplies validity; private dense indices override payload addresses. W4A16 uses theFalse default. This distinction corrects the earlier finalizer experiment attribution.
- Workspace allocation, tensor descriptor construction and Python cache lookup are outside the captured GPU replay timer. Optimizing those can improve setup/uncaptured latency but cannot be credited as a CUPTI graph improvement. Reusing mutable workspaces also introduces lifetime/concurrency questions.

Consequently, the old fused MX baseline avoids an explicit BF16 intermediate/combine round trip and may avoid this regular-TMA preparation pass. Its gap cannot be assigned wholly to inefficient GEMM scheduling. Under the chosen regular-TMA plus unfused-output contract, eliminating all of those bytes requires a larger dataflow change, not a small launch/padding cleanup.

## One new, bounded instruction-sanity lead

**Make the private compact inverse index a complete mapping, including negative sentinels.** Currently combine preloads the original mapping to retain validity (`moe_finalize.py:166–170`), then loads the private dense inverse index after FC2's wait for valid slots (`:184–187`). Nonlocal dense entries are intentionally uninitialized. This duplicates mapping state and keeps `top_k` row values live across the PDL wait, in addition to the existing routing weights.

A possible experiment would initialize the private index buffer to−1 in the existing prepare grid, independently of the live-tile loop, and let FC2 overwrite valid entries as it already does. Compact combine could then load only that complete mapping after its existing wait, using one value for validity and address. Preserve the generic expanded/permuted paths and the private workspace API; there is no new tactic or dtype/model selector. This is distinct from the rejected warp-coalesced metadata, vector-outer reduction and affine FC2-tail experiments.

Necessary proof and tradeoffs before any implementation:

- Initial sentinel writes must cover all expanded slots on **every** invocation/graph replay, including empty local routing. No initialization may be moved outside capture or rely on allocator contents. Caller-owned sort buffers stay untouched.
- Prepare completion must precede FC2's writes. Current FC2 epilogue warps execute `griddepcontrol_wait()` at kernel2678–2687 before prefix/index use at2885–2891, so the existing dependency chain can protect initialization without an added barrier. Combine must still read private indices only after its FC2 wait.
- The unique channel-zero writer, arbitrary static/CLC order, one/two-CTA ownership, negative nonlocal routes and all-masked tokens must remain valid. A dense index ofzero is valid, not a mask.
- Keep original slot-zero multiply, subsequent ascending-slot RN FP32 FMAs, subnormal/signed-zero behavior and final BF16 conversion. Do not compact or reorder the reduction slots.
- Extra initialization is4 bytes per expanded route:0.5/0.375/1/1.375 MiB at16K for V3/V41F/K3/N3U. It adds a metadata loop to prepare and shifts validity resolution behind the wait. Lower live registers/one fewer mapping load are hypotheses until SASS proves them; uniform-load caching may make the existing duplicate cheap. Test exact empty/reactivated graphs and source-paired resource/codegen first. This is a possible metadata simplification, **not** a predicted solution to the dominant payload traffic or a claimed speedup.

No second small candidate has comparably clear scope. In particular, payload lookahead/double buffering would lengthen live registers and add loop-control work; existing evidence does not show enough unhidden per-CTA reuse to prefer it over the established parallel row copy.

## Closed directions remain closed

- Prepare SF-only coalescingR1 traded output sectors for strided source loads/repeated route traversal. R2/R3's32rows×4lanes lost sparse-row payload parallelism; corrected R3 still regressed decode2.66–21.57% despite TP-prefill gains. No token/TP bypass is proposed.
- The finalizer one-line geometry experiment is still rejected, but its original36-cell attribution was wrong: the only8 affected public cases are W4A16 V3/V41F prefill (GM−0.554918%, worst−1.611653%). All scaled public calls already passTrue, including compact output. See `../finalizer/ATTRIBUTION-CORRECTION.md`; the scaled−3.501% row is not candidate-effect evidence. Vector-outer combine added42–54% static instructions in important cases. Wide256-bit combine loads, one-warp geometry, selective scale loads and broad prefetch policies were also rejected.
- Compact FC2 affine-tail addressing removed instructions but repeated EP16K regressions reached−4.678%; common-STMatrix unification increased instructions/registers. Neither should be retried as cosmetic simplification.
- Do not replace working regular TMA with LDG/gather, fuse reduction, drop invalid-SF zeros or reassociate FP32 arithmetic merely to reduce the table's byte count. Each changes an established contract or discards qualified behavior.

## Evidence

- `../static-grid/composed/RETENTION.md`: the already-retained empty-launch bound; no new padding benefit is claimed here.
- `../../tp-ep-post-sanitizer/retained-refresh/83dfef8a6563/nsys-tp-prefill/RESULTS.md`: source/winner-bound retained-stage traces.
- `../../tp-ep-post-sanitizer/profile-evidence/RESULTS.md`: historical source-bound NCU/NSYS.
- `../../tp-ep-post-sanitizer/next-prepare-audit/README.md`: per-PC dependency attribution; its fixed-index lead is already retained.
- `../../tp-ep-post-sanitizer/prepare-sf-coalescing/{README.md,r2/README.md,r3/README.md}`.
- `../finalizer/RESULTS.md`, `../epilogue/RESULTS.md`, `../../../optimization-20261027/finalize-vector/RESULTS.md`, `../../../scripts/finalize_geometry_experiment/README.md`.
- `audit-receipt.json` binds the current source and evidence documents. No modified repository files or active review clone.
