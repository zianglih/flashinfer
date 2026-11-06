# Split W4A16 Gather4: preferred four-CTA / fallback two-CTA experiment

Prepared 2026-10-25. This is a split-backend experiment; no MegaMoE source is changed.

## Pinned prior evidence

[FlashInfer PR #7202](https://github.com/flashinfer-ai/flashinfer/pull/7202) is an open draft at `3d047d3f8e7923118ffea8b8d36151504ab1fa3d`. Its full live context is saved in `pr7202-context.json`; the relevant source snapshots are in `pr7202-source/`.

- Prior backend: W4A16 MegaMoE, two-CTA M256 MMA, preferred cluster `(4,1,1)`, fallback `(2,1,1)`.
- Primary comparison: original uniform2 AUTO16 vs mixed-only AUTO18, native AUTO selection, then 100 untrimmed cold-L2 CUPTI samples per point, maximum rank activity span, median; 13 token counts with T1/T2 excluded only from aggregates. Both arms measured fresh in that experiment.
- Results already recorded: overall geometric mean **0.992212x**, decode **0.991270x**, prefill **0.994731x**. These establish no retained MegaMoE performance gain and must not be described as split Gather4 evidence.
- Separate static AUTO36 screen was rejected: T64 **0.980920x**, T128 **0.998785x**, T4096 **1.007074x**; every selected tactic was atomic, not a new static tactic. No need to rerun these historical measurements.
- On that 148-SM B300: `P = max_active_clusters(4) = 33`, total uniform2 capacity `2 * max_active_clusters(2) = 148`, and `F = 8` physical fallback clusters. Logical grid count is `P + F/2 = 37`. Mixed placement is runtime best-effort, so these counts are capacity accounting, not proof of the actual placement of a particular launch.

## Primary implementation references

- [PR7202 host occupancy and normalization](https://github.com/zianglih/flashinfer/blob/3d047d3f8e7923118ffea8b8d36151504ab1fa3d/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/frontend.py#L216): strict occupancy; zero preferred capacity rejects explicit mixed launch; no fallback remainder normalizes to uniform4.
- [PR7202 mixed B pipeline and runtime geometry](https://github.com/zianglih/flashinfer/blob/3d047d3f8e7923118ffea8b8d36151504ab1fa3d/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py#L1276): actual `block_in_cluster_dim`, one/two activation-reader pairs, per-pair producer leader, runtime multicast mask.
- Local unchanged generic reference: `flashinfer/flashinfer/moe_ep/kernel_src/sm100/next_cutedsl_megamoe/src/blackwell_genphase_sources/kernel_src/blackwell/custom_mix_cga_helpers.py`, especially `PipelineTmaUmmaMixedCga.create` and producer/consumer methods. This experiment uses a narrow split-owned constructor instead of importing MegaMoE helpers.
- Local CUTLASS tutorial: `flashinfer/3rdparty/cutlass/examples/python/CuTeDSL/blackwell/tutorial_gemm/fp16_gemm_4.py:682` selects actual cluster geometry; `:755` gives separate CLC scheduler parameters; `:784` deliberately retains preferred scheduler parameters for static fallback; `:969` launches `cluster=preferred, fallback_cluster=fallback`.
- [CUDA 13.2 preferred cluster launch documentation](https://docs.nvidia.com/cuda/archive/13.2.2/cuda-programming-guide/03-advanced/advanced-host-programming.html#launching-with-clusters-using-cudalaunchkernelex): CC10.0+, runtime may use either geometry; preferred dimensions must be integer multiples of minimum dimensions and divide the grid.
- [PTX Gather4 mode](https://docs.nvidia.com/cuda/parallel-thread-execution/#tensor-tiled-scatter4-gather4-modes): four independent rows from a 2D source, one row per bounding box, no interleave. [PTX TMA instruction](https://docs.nvidia.com/cuda/parallel-thread-execution/#data-movement-and-conversion-instructions-cp-async-bulk-tensor) permits Gather4 with multicast and two-CTA groups; each multicast mask refers to physical cluster ranks.

## Bounded split implementation

Append two candidates after the existing 23 candidates: FC1 `M256/N128/K256` or `M256/N192/K256`, logical cluster4 with runtime fallback2; FC2 remains the existing uniform cluster2 with the same N. Use static persistent scheduling for these two FC1 candidates; existing uniform candidates retain CLC selection. FC2 descriptor and kernel behavior remain unchanged.

Host occupancy uses a cached strict per-device CUTLASS query and computes `F = ((2*C2 - 4*P)//4)*2`. Positive F passes fallback geometry `(2,1)` to the kernel; F=0 passes `None`; P=0 filters AUTO candidates and rejects an explicit mixed tactic. Occupancy query failures propagate rather than substituting an SM-count estimate. Kernel compilation keys include fallback geometry and logical grid count.

Kernel integration:

1. Add optional constructor argument `fallback_cluster_shape_mn=None` at the end; limit the mixed path to FC1/M256/preferred4/fallback2 and static scheduling.
2. Read actual physical size with `cute.arch.block_in_cluster_dim()[0]`. Keep logical scheduler channel coordinates derived from `bidx % 4`. Keep physical cluster rank for TMA masks, peer addresses and barriers. Reusing physical rank in the scheduler would duplicate the first channel pair on the second fallback cluster.
3. The split-owned B pipeline has full barrier transaction bytes unchanged, empty-barrier arrival count `actual_cluster_m//2`, reader mask `(1 << actual_cluster_m)-1`, no producer multicast mask, and one producer leader per two-CTA MMA pair. Existing MMA code already releases B only from the pair leader.
4. Gather4 descriptor is common to both physical sizes. Preferred4 loads `N/4` rows per CTA and multicasts within same-V CTAs; fallback2 loads `N/2` rows per CTA. Shared B allocation remains `N/2` rows per CTA. Runtime dynamic-N source shifting remains per two-CTA pair. Select runtime counts/masks before the K loop; retain uniform descriptor/address values for TMA issue.
5. Launch logical grid `(4,1,P+F/2)` with preferred `(4,1,1)` and fallback `(2,1,1)`. Existing raw-weight, transform, accumulator and TMEM ownership remain pair-local.

Off-tree proposal: `mixed-host-helper.patch` and `mixed-proposal/`. These files were generated without editing the production launcher/tuner so the v5 instruction-hoist screen remains isolated.

After root archived v5, the host/helper/tuner proposal and existing-test extensions were applied unstaged. Production includes an explicit unsupported-device branch for CC below 10 or fewer than four SMs, then strict occupancy queries. The helper preserves NVIDIA BSD attribution. Because CUTLASS's barrier constructors validate counts with ordinary Python conditionals, `_MixedReaderBarriers` passes a static positive count to constructor validation and overrides only initialization to emit the actual one/two-reader count; all wait/arrive methods are inherited. Local Ruff, Python syntax, and whitespace checks passed; runtime validation is owned by the parent agent.

## Focused validation boundaries

- Extend the existing `test_route_tile_boundary_accuracy` parameter list with the two mixed FC1 tactics; the test already covers N192 tails 1 and half+1, top-k 2/3, and exact shared reference assertions. No dedicated dynamic test file is needed.
- Existing host enumeration assertion must include `(256,(4,1))` only for FC1 with N128/N192 and FC2 cluster2.
- Prove actual fallback use with an experiment-only runtime geometry receipt/probe. Permanent outputs and kernel behavior should not include instrumentation counters. Capacity arithmetic alone is not a placement proof.
- Rerun the same split before/after methodology for these new candidates. Previous MegaMoE results above are context, not substituted measurement.

The experiment-only `make_forced_fallback_source.py` generates a separate kernel source with the mixed logical4 kernel launched physically as cluster2 and no fallback attribute. It changes only the launch geometry: logical scheduler parameters, runtime B reader counts, row partitions, and multicast handling remain the mixed implementation. Use it for the eight existing mixed boundary cases, restore the production source before timings, and record both source hashes. `probe_mixed_launch.py` separately records actual runtime placement; the probe needs an initialized CUDA context before its occupancy query.

## Follow-up review and code-generation helpers

The read-only v6 review found no new ownership or synchronization blocker. Preferred4 CTAs use physical ranks for same-V activation multicast and one/two MMA-reader completion counts, while both fallback pairs retain their distinct logical channel coordinates. Raw weight, transform, accumulator and TMEM pipelines stay pair-local. Every CTA continues executing the shared-input pipeline on partial channel tiles; output predicates handle channel tails. Static route workspace dimensions are independent of physical cluster size.

Runtime costs to inspect in generated code: the per-row-group physical-width guard, 32 cached uniform row IDs, and uncached row shuffles inside K. Preferred4 N128 needs 32 source rows per CTA and caches all of them. Preferred4 N192 needs 48 rows and shuffles its final 16 inside K. Fallback2 requires 64/96 rows and retains the runtime guards even though its physical size is fixed for the launch. This is a code-generation hypothesis, not measured attribution.

`capture_fc1_ptx.py` now accepts `--route-tile 128|192`, `--cluster-m 2|4`, and `--hidden-size N` (positive multiple of 256). Defaults remain N128/cluster2/K256. It uses two full valid route tiles, matching activation/mapping/output sizes and route limits, and records shape/occupancy plus expected per-physical-size issue counts. `inspect_codegen.sh PROJECT LABEL` accepts the same optional flags, preserves the previous default output paths, captures top-k 3/8, and saves `ptxas -v` resource output to each `ptxas.log`. PTX call-site count is explicitly distinct from executed issue count and actual runtime placement.

`inspect_offered_tactics.py` calls the actual runner's tactic filter with shape-only meta tensors and strict CUDA occupancy. All workload dimensions and token counts are explicit CLI inputs. It records complete offered lists and verifies both registered mixed candidates are offered when preferred4 capacity is positive. Source-extracted `can_implement` checks passed both mixed FC1 and uniform FC2 for N128/N192 at H7168/I2048, H6144/I2048, and H256/I512; this static check does not replace the runtime runner receipt. All helper edits passed local syntax and Ruff checks; no GPU work was executed by the review agent.
