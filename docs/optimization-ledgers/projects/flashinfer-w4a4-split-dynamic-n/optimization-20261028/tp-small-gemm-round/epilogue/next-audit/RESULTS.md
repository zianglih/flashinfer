# Bounded TP small-GEMM source audit

Canonical source: `2d60c885dee645aaaaf0358e126649ab39d91ce7`. Source hashes and historical frozen native-winner inputs are bound in `summary.json`; `winner-capacity.csv` covers 616 scaled GEMM phases excluding tokens 1/2. This is a source/profiler audit, not new performance evidence.

## One proposed candidate: cap static launch capacity

`moe_swap_ab.py:220–233` already selects static scheduling when the allocated work fits concurrently. `moe_swap_ab_kernel.py:2371–2375` nevertheless launches the whole SM budget. Each guaranteed-empty cluster initializes pipeline barriers, allocates/retrieves TMEM and handles PDL before reading the actual route count at lines 2645–2690.

Calculate the launch cluster count as `max(1, min(resident_cluster_budget, channel_tiles * allocated_route_tiles))`. Channel tiling and CTA-group size are compile-time values; routed capacity remains a launch-time host-wrapper shape argument so compilation is still shared across token counts. No GPU metadata readback, new tactic, model/dtype policy, or device branch is needed.

The existing 83df frozen winners expose four retained cells: V3 TP8, token 4, FC1 in W4A4, per-token, MXFP8 and MXFP4x8. Each changes 148 to 128 physical CTAs. The measured route sample has 124 live CTAs, but the proposal uses only the safe allocated 128 bound. All other retained scaled winner launches are unchanged. Expected benefit is bounded decode startup; no prefill gain is predicted.

Safety invariants:
- `expert_idx.shape[0] = num_routes // route_tile` in the wrapper (lines 2127–2130). This is allocated capacity, not current GPU `num_tiles[0]`; every valid route distribution must fit it. `get_max_num_tiles` supplies the tight worst-case bound for public routing.
- Multiply cluster count by `cta_group_size` after capping, so one/two-CTA clusters remain complete. The existing constructor already requires at least one cluster in the SM budget.
- If allocated or actual work is zero, preserve one full physical cluster. It executes the existing dependency waits, ancestor publication and final join; no CTA0/PDL publication is lost.
- If capacity is below the old grid, every live static cluster keeps its original first tile and has no second tile under either grid. Only guaranteed-empty clusters disappear. If capacity reaches/exceeds the budget, the grid/stride is unchanged.
- The CLC branch still supplies its existing grid. Scheduler rings, cancellation, barriers and kernel instructions are unchanged.
- W4A16 separately uses a fixed persistent grid (`moe_w4a16_kernel.py:2831`); this candidate does not modify it.

## Why this will not close the large MX prefill gap

The retained 83df V3 TP8 MXFP4x8 16K trace reports 1547.306 us graph span, with prepare 313.778 us and combine 367.075 us of nonoverlapped interval extension: 680.853 us, about 44%. These are materialized routing/output costs of the current four-stage design. A fused legacy finalize or direct-gather path can avoid some of that traffic; the costs are not mathematically unavoidable, but removing them would change dataflow beyond a barrier/instruction cleanup. The largest comparisons against legacy fused MX therefore mix algorithmic IO differences with GEMM quality.

FC1/FC2 extend that same trace by 340.962/486.291 us. Those frozen winners are static persistent kernels: barrier/TMEM setup occurs once per resident CTA, not once per output tile. Removing a final teardown join cannot explain a large per-wave benefit. Current N3U FC1 PC sampling also locates almost all barrier samples at the required final join; producer-empty and accumulator-full waits protect real reuse dependencies.

The current profile is still historical (83df, with later retained instruction cleanups). Old d1767 NCU FC2 write/long-scoreboard counters predate compact output and are not presented as current counters.

## Second lead not promoted

Physical short-K stages still reserve/load a full TMA stage while the retained emitter skips unused MMA atoms. There are 33 retained FC2 phases with whole reduction shorter than the selected stage, all NVFP4 V3/K3 TP (K256/384 versus stage512). However K256 can already use an existing K4 tactic; unconditionally shrinking K8 would remove the selected staging/resource policy. K384 requires nonstandard layout/alignment work. There is no evidence yet that this is a better general policy, so no second implementation is recommended.

Ring depth must not be capped to reduction-stage count: the persistent ring prefetches across output tiles. Rejected prepare/SF coalescing, CLC ticket publication, compact-tail indexing, common-STMatrix, broad finalizer geometry and protected-prefix deferral experiments remain closed. The separate current SF-parameter/formula effort is not duplicated here.

Evidence: `tp-ep-post-sanitizer/retained-refresh/83dfef8a6563/nsys-tp-prefill/RESULTS.md`; `tp-small-gemm-round/producers/fc1-pc/RESULTS.md`; `producers/AUDIT.md`; `scheduler/r1-integrated/RESULTS.md`; `epilogue/RESULTS.md`; `finalizer/RESULTS.md`; `tp-ep-post-sanitizer/producer-audit.md` and `prepare-sf-coalescing/{README.md,r3/README.md}`.
