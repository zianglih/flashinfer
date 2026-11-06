# Prepare/combine audit at retained61c2

Read-only,2026-10-28. No source edits or GPU jobs. Conclusion: no strong new small instruction/data-movement candidate beyond the active FC2-drain and SF-producer experiments. Do not reopen previously rejected prepare remapping, SF-only traversal, vector-outer/LDG256 combine, or shape-specific cache policy on this evidence.

## Current source and fresh evidence

- `moe_swap_ab_prepare.py:98–105` has the required routing PDL wait and early dependent launch; `:120–184` copies payload only for valid routed rows and zeros only invalid logical SF rows. There is no shared memory or CTA barrier to remove. Payload uses256-bit copies when the existing row/pointer contract permits, with the native128-bit compatibility case at`:293–298`. SF values preload before payload, and the canonical128-row bit indexing is already retained. Eliminating SF zeros would invalidate downstream full-tile MMA semantics. A new row grouping would revisit the rejected sparse/decode parallelism tradeoff.
- `moe_finalize.py:160–170` preloads routing and scales before its sole required PDL wait. `:174–203` uses128-bit input/output vectors and packed FP32 multiply/FMA, preserving ascending-slot rounding. There is no shared-memory synchronization. The route-dependent reads cannot move before FC2 completion; dropping them or reordering the reduction changes the output contract.
- The current swapAB caller passes `input_is_expanded=False` (`fused_moe.py:963–971`). The historical compact-index audit at61249 describedTrue plus a private dense index; both private dense-index state and the extra metadata lookup are now gone. Its proposed complete-index simplification is therefore obsolete. The5/7-vector exact-divisor branch currently does not apply to swapAB. The prior public geometry experiment causally changed only8W4A16 cases and lost0.555% GM; no new scaled-layout benefit is established. Extending it now would be a new experiment with the already-observed register increase, not a proven simplification.

Fresh NSYS is bound to the348-file equivalent retained61c2 source and fixed public winners/routes in `../profile/results.json`:

| TP8/EP1,16K,MXFP4x8 | Prepare duration / extension(us) | Combine duration / extension(us) | Combine CTAs / registers |
|---|---:|---:|---:|
| V3 |311.426 /311.170|342.674 /337.874|32768 /64|
| K3 |304.515 /303.683|342.115 /338.227|16384 /68|

Both kernels report zero shared memory. These timings diagnose contributions; they are not paired retention timings or fresh per-PC bandwidth/stall counters.

## Traffic cross-check

The frozen routing histograms confirm every TP route is local. V3 has7168hidden×8routes, K3 has3584hidden×16routes: both read1,879,048,192useful BF16 bytes(1792MiB) in combine at16K, rather than a smaller K3 input estimate. Final outputs add234,881,024bytes(V3) and117,440,512bytes(K3). Exact calculations and routing/source hashes are in `audit-receipt.json`.

- v3: 131,072 local routes; 5.483TB/s useful reads, 6.169TB/s including final output writes, using kernel duration.
- kimi-k3: 262,144 local routes; 5.492TB/s useful reads, 5.836TB/s including final output writes, using kernel duration.

This explains why K3 and V3 can have nearly equal combine time despite different CTA counts. Logical traffic is not measured DRAM traffic; cache residency and overlap matter. NSYS alone does not prove a bandwidth floor. If another combine experiment is desired, first obtain current achieved DRAM/L2 bandwidth and source-PC stalls for these two unchanged kernels. That can distinguish memory-throughput limits from dependent-load latency or instruction pressure before selecting a different policy. No new cache hints or geometry exception are justified by this audit alone.

## Closed evidence

`../../tp-small-gemm-round/prepare-combine-next-audit/RESULTS.md`, `../../tp-small-gemm-round/finalizer/ATTRIBUTION-CORRECTION.md`, and `../../tp-ep-post-sanitizer/next-prepare-audit/README.md` preserve the earlier rejected experiments and historical PC analysis. Their timings and compact-output descriptions must not be relabeled as current61c2 behavior.
