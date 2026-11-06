# Swap-AB pipeline audit

Source base: `82254e206a44b95d9925e4594fac936731f80d21`. The initial audit was read-only. The only subsequently authorized prototype is the one-line FC2 commit ownership change below; it remains unstaged. No GPU execution or performance claim is part of this audit.

## First candidate: commit FC2 bulk groups only from writer warps

`flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py:1235–1245` issues output TMA only in epilogue warps 0/1, but the original following `cp_async_bulk_commit_group()` runs in all four warps. Move that call inside the existing `if warp < 2`, after the existing elected store. This changes one indentation, adds no condition, state, barrier, tactic or helper, and applies to every dtype using the same FC2 bulk output path.

The source and patch are recorded in `fc2-writer-commit-source.json` and `fc2-writer-commit.patch`. Candidate SHA256: `2d7e69d946ae85c255061501df5aaf7673aca468204db0646742695b7a4cbe07`.

Correctness argument:

- Bulk groups are per executing thread, so nonwriter warps have no real bulk operations to commit. Their removal does not alter the issuing threads' group sequence. See the [PTX commit-group contract](https://docs.nvidia.com/cuda/parallel-thread-execution/#data-movement-and-conversion-instructions-cp-async-bulk-commit-group).
- All shared writes, the async proxy fence and the 128-thread publication barrier remain before the stores.
- The reuse wait at line 1216 and following 128-thread join remain unchanged. Writer threads still wait for exactly the same real committed groups; nonwriters wait on no pending groups. The join still prevents any writer from overwriting a source stage while either TMA issuer is reading it.
- The terminal wait/join at lines 1290–1292 also remain unchanged. Partial SIMT tails never write the TMA scratch or commit groups, and the cyclic overlap traversal is untouched.
- The TMA store and its commit remain in the same writer warp. The commit stays outside `elect_one`, matching the repository's normal whole-warp commit convention after internally elected TMA issue.
- FC1, CLC/static scheduling, one/two-CTA behavior, PDL, stage capacity, registers, accumulator releases, arithmetic and all public interfaces are unchanged.

Established in-repo reference: `flashinfer/moe_ep/kernel_src/sm100/next_cutedsl_megamoe/src/sources/kernel_src/blackwell/inference/mega/block_scaled_swap_ab_fc12_epilogue.py:3158–3165` puts TMA copy, commit and read-wait inside the existing writer-warp branch, then joins all epilogue writers.

Existing compiled evidence is source-bound: the older `cleanup-20261030/validation/config.json` in the prior project records exactly the current base kernel SHA `194b903854c74fc79a422ec67a0539d9f57414987c8cc0a3325e94226d642eb4`. Its `runs/candidate-w4a4-8/codegen/01-Sm100BlockScaledGroupedGemmKernel.ptx:1373–1387` branches nonwriters to the common commit, and the matching SASS contains `UTMACMDFLUSH` at `0x3d50` (also `0x56c0`, `0x7090`, `0x8a20`). This establishes real committed-group work in the base; it does not establish candidate codegen or timing.

Qualification: inspect candidate PTX/SASS to verify the same store count and writer grouping, with nonwriters bypassing the flush and no new local storage. Cover FC2 N16 (no bulk output), N32/64/128/256, one/two CTA, overlapping/nonoverlapping accumulator windows, per-token scaling and partial live-token slabs. Exact E2E tests use the existing oracle. Only a source-bound paired benchmark can establish an E2E speedup; source simplification alone does not imply one.

## Current dependency chain: preserve these contracts

The main kernel creates one shared weight/activation operand ring at lines 2648–2659. Weight warp 0 is the single byte-count announcer (`load_weight_stage`, lines 2538–2555); the independent activation producer waits on that ring's empty phase before reuse. MMA is the sole release owner and releases only after both channel tiles finish reading the shared B/SFB stage (3266–3270). Splitting announcers or releasing before both channel tiles would need new correctness arguments; neither is justified here.

FC1's four gather warps issue Gather4 into local B and four-byte cp.async into disjoint SFB. Local completion has one transaction announcement plus a compile-time bounded number of SF participants (2706–2715, 3481–3518). The activation-control warp acquires this combined local completion, crosses the async/shared proxy and publishes one arrival per CTA to the leader (2996–3024). The leader MMA waits for weight readiness, copies SFA while gathering can finish, then acquires gather readiness before SFB copy/MMA (3177–3220). The relay is required by this mixed TMA/cp.async and remote-CTA contract; it is not merely an idle warp to remove.

CLC publishes route/expert/live-row metadata through a single staged ring (2771–2834). Each role copies metadata before releasing its slot in `next_work` (2494–2499). The quorum includes six common consumer warps, four gather warps for FC1, and only CTA0's MMA warp (2680). Waiting/releasing once per role is distinct from the later operand lifetimes. A lane-0 metadata broadcast is not yet justified: three scalar shared loads to a common address are warp-broadcast memory accesses already, while explicit shuffle would add instructions. Inspect emitted uniformity before changing this.

PDL starts only after barrier/TMEM initialization. Gather FC1 must acquire the routing producer before reading routes/expert identity; it cannot prefetch expert-selected weight payload before that dependency under the current routing publication contract. FC2 preserves independent weight/scheduler/MMA runahead; payload consumers acquire upstream completion first (2732–2754), and independent roles acquire before signaling/exiting (2900–2913, 3558–3564). This is why the earlier merged-producer experiments needed extra cursors and polling. Do not introduce that machinery again for cosmetic ownership balance.

TMEM allocation, accumulator-empty/full transitions, overlapping-window early releases, terminal epilogue reads and final CTA join protect separate lifetimes. No further clearly redundant barrier was established in this pass. All four epilogue warps remain scratch writers even though only two issue output TMA; reducing their barrier quorum would be incorrect.

## Rubin and MegaMoE comparison

- Rubin gather source `flashinfer/fused_moe/cute_dsl/rubin/blockscaled_contiguous_gather_grouped_gemm_swiglu_fusion.py:1973–2078` also uses four elected Gather4 issuers with routing IDs held outside K. Its TMA path shares payload and weight transaction completion; scales have separate gather/transform pipelines (1408–1448, 1504–1525). It therefore cannot justify removing our combined payload/SF completion relay without changing the scale transport contract.
- SM100 MegaMoE `.../blackwell/inference/mega/block_scaled_swap_ab_fc12_mainloop_gen_specialized.py:983–1060,1164–1238` separates Gather4 payload issue from TMA scale publication and uses a producer rendezvous to ensure expected bytes are registered. Its optional live-row issue count is not a free transfer here: the corresponding local dynamic-gather and row-outer variants were already measured and rejected.
- Rubin prefetches descriptors before initialization (`:1374–1379`). That pattern is valid in principle, but the identical swap candidate already had no broad gain and a stable regression, so this audit does not recommend repeating it.
- MegaMoE's writer-owned output commit is directly transferable because it relies only on the same per-thread bulk-group semantics, not its different routing, communication, MMA or scale pipelines.

## Closed leads checked before proposing new work

Paths below are relative to the previous project `/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n`.

| Mechanism | Prior evidence and decision |
|---|---|
| Entire Gather4 payload loop before SF copies/arrival | `fc1-gather-20261028/full-20261029/payload-first/RESULTS.md`: 36 affected cells −0.178%; N3U EP W4A4 4096 −2.017% with low repeat spread. Do not repeat. This is separate from R8, which moved only completion publication. |
| Early TMA descriptor prefetch | `fc1-gather-20261028/optimization-next-20261029/prefetch/RESULTS.md`: −0.058% overall, tight V3 TP MXFP4x8 16K −2.101%; rejected. |
| Element/scales or crossed TMA producer ownership | `element-scale-ownership-20261029/README.md`: A/B −3.826%/−3.690% on 64 qualified cells each, added refill/cursor state and new stress-case local memory; rejected. Thin W4 FC1 split +0.1075% on 40 cells did not justify extra role logic. |
| Reduce control quota toward 120 to give epilogue 256 | Current 128/128/248 was retained for reducing inherited MX stress stack 160→128 B and LDL/STL 20+20→16+16. `.../control128-epilogue248-screen-r1/RESULTS.md` and `RETENTION.md`. Native timing was near neutral, but lowering control quota would undo useful resource work. |
| Dynamic live-group gather / row-outer loop | `.../live-groups-row-outer/RESULTS.md`: N3U EP W4A4 −1.343%; no consistent win despite fewer SHFLs. No narrower model gate. |
| Shared FP32 transpose, channel-interleaved MMA, role-local TMEM pointer | Listed with source-bound failures in `.../CLOSED_LEADS.md`; rejected after measured regressions or increased common spill traffic. |
| Custom all-stage producer tail, absmax reorder, optional gather relay | Explicitly excluded by current task; keep retained SDK tails, linear max chain and current required publication relay. |

## Local validation

Inverse indentation reconstructs base bytes exactly; Python AST parsing and `git diff --check` pass. Scoped pre-commit hooks are recorded separately. GPU codegen, numerical checks and performance remain pending and are owned by the parent campaign.

## Profiling-led second candidate, not implemented

The newer SM100 MegaMoE combined mainloop (`block_scaled_swap_ab_fc12_mainloop_gen_specialized.py:1362–1416`) queries the next AB slot after acquiring the current slot, before issuing its SF copies and MMAs. Current swap performs only the direct current-slot wait (`moe_swap_ab_kernel.py:3177`). An early nonblocking readiness hint could overlap that query with useful current-stage instruction issue, unlike the rejected W4 end-of-loop peek whose query immediately preceded the following wait.

This is not a barrier deletion and would add cursor/token state. Require an actual operand-wait signal in a large TP MX case before proposing it. A future-slot probe must not suspend behind an unissued current stage, especially when the operand ring contains one slot; use a proven nonblocking query, retain the current acquire if not ready, and do not use a lane-varying probe result to advance cursors. The stage release, SF order, partial-K section transition and final accumulator publication remain mandatory. No source edit or performance claim for this lead.

## Profiling follow-up: early-readiness lead closed on822

`profiling/v3-tp-mxfp8-16k/RESULTS.md` and `fc1-pc/pc-proof.json` bind a fresh native trace and actual loaded FC1 disassembly to base822. The two MMA blocking slow-wait paths have zero sampled instructions; the dominant scoreboard PCs are epilogue accumulator-full and gather operand-empty, and the barrier samples are primarily at the final CTA join. Do not add readiness/cursor state based on the aggregate stall percentage. Static geometry and the already-straight eight-MMA issue sequence provide no simpler supported change in this audited shape. This closes the speculative second candidate above on the measured source; it does not claim every supported workload has identical behavior.
