# Transform acquisition audit and narrow load-only proposal

This is a source/history and existing-codegen audit, not an implementation or a performance result. No production file, GPU process, or compiler job was changed or launched. Exactly two transform warpgroups remain fixed. Any experiment below is gated on the separate 512-thread candidate first passing codegen and runtime validation.

## Existing implementation and lifetime boundary

`audit.py` verifies that `_transform_tile` and `_setup_transform_partitions` in current `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py` are AST-identical to PR4048 commit `8ed63e75d218cfef01d86ee14f8f834e2d5d4d95`. Current full-file SHA256 is `4a870648549397c4ef8d4db52b4bfe3dde3ff09feed94abd942ea945f3185866`. `evidence.json` records both file and method hashes and source-correlated instruction excerpts.

The current helper has this order:

1. Reset the work-local raw/decoded counts and issue readiness probes, lines460–471. These are try operations; they do not acquire the decoded destination for a write.
2. Wait for the current raw packed-weight/scale stage, lines474–477; form the producer's source view, lines478–487.
3. Complete the blocking decoded-stage acquire, lines488–491.
4. Load compact scales, lines492–500. For each constexpr fragment, load packed values, decode and place BF16 values in the existing register tensor, lines502–530. The final fragment advances the logical raw state and probes the next raw stage, lines507–514; it does not release the current stage.
5. Perform the collective register-to-TMEM copy, lines532–539; fence TMEM stores at543; release the saved current raw stage at546; commit/advance the decoded stage at547–548; probe the next decoded stage at549–552.

Partition setup splits the final transform-block mode evenly between the two groups, lines346–372, then allocates existing packed and BF16 RMEM tensors, lines374–382. Scale ownership is divided with the same group coordinate, lines384–388. The fragment tiler is bounded by `transform_fragment_size`, lines407–425. These ownership and layout rules are unchanged by the proposal.

Current Mega calls FC1 with fragment128 and FC2 with fragment32 (`shim/w4a16/kernel.py:620,640–644`). It does not inherit the old split path's later one-K FC2 fragment128 selection. Its two transform groups keep their raw and decoded pipeline states across FC1/FC2 work tiles (`kernel.py:1202–1229`); only counts reset inside `_transform_tile`. Raw/decoded ring index and phase must remain intact.

The kernel already overlaps different work tiles through separate weight-TMA, transform, activation-TMA, MMA and epilogue consumers. FC2 work publication is not withheld until FC1 activation finishes; only its activation producer waits for the FC1 output flags. See the independently traced [FC2 metadata/wait map](../w4a16_register_overlap_audit/FC2_METADATA_WAIT_MAP.md). This existing structural overlap must not be described as a retained explicit next-fragment lookahead: those lookahead experiments were rejected.

## Native code already overlaps conversion and stores

These are matched fake-descriptor **offline codegen** captures. The 512 scoped capture has not executed MegaMoE. Each recorded hot transform body contains four `LDS.128`, 64 E2M1 pair-conversion instructions, and eight `STTM.x8`; these are static instruction counts, not execution counts.

| Capture / phase | Decoded wait | First packed LDS | First conversion | First STTM | Last conversion | Last STTM | Packed LDS before first conversion |
| --- | --- | --- | --- | --- | --- | --- | ---: |
| control640 FC1 | 0x6510 | 0x6570 | 0x6780 | 0x6aa0 | 0x7170 | 0x7290 | 3 |
| control640 FC2 | 0x7460 | 0x7550 | 0x76e0 | 0x7960 | 0x8100 | 0x8230 | 3 |
| scoped512 FC1 | 0xb520 | 0xb5d0 | 0xb7b0 | 0xb8f0 | 0xc160 | 0xc260 | 4 |
| scoped512 FC2 | 0xc430 | 0xc500 | 0xc6f0 | 0xc830 | 0xd060 | 0xd1d0 | 4 |

All packed and scale shared loads follow the decoded wait in these captures. The failed-wait branch and matching polling query were inspected, not inferred only from a line tag. In contrast, the first TMEM store precedes the last conversion: the compiler already distributes the one source-level collective copy among conversions. Moving the entire decode before a new blocking wait can constrain this schedule and keep the complete decoded tensor live across that wait if the compiler honors the hoist. If the compiler sinks it again, the proposed overlap has not materialized. There is no justification for rewriting this into explicit per-fragment TMEM stores.

The scoped512 capture's known stack slot holds cluster-derived barrier destination metadata, not transform data. Its separate zero-destination refinement is not combined here. The pending 128-register transform role permits a different schedule than Mega's current 80-register transform cap, but it is not a historically new budget: the retained PR4048 split kernel already used two same-K transform groups with 128 registers each.

## Prior trials that constrain the proposal

Source: `../flashinfer-w4a16/w4a16_optimization_experiments.md` relative to the projects directory. The ledger's main sweeps used **B200 / CUDA13.2 / DSL compiler13.3 / CUPTI graphs**, not the current B300 environment. Ratios below are restored-baseline latency divided by candidate latency. Historical explanations of causes are hypotheses; the observed outcomes are the evidence.

| Prior change | Ledger lines | Historical outcome |
| --- | --- | --- |
| FC2 scale load before decoded acquire | 4727–4750 | Six numerical cases passed; EP8/4096 0.432479 vs adjacent 0.434335 ms, 1.0043x; rejected as noise. |
| FC2 full decode before acquire, acquire just before collective TMEM copy | 5486–5510 | Six passed; 0.436751 vs 0.433487 ms, 0.9925x; rejected. Do not repeat. |
| Next 32-value fragment's packed load before the current decode | 5511–5533 | Six passed; 0.443919 vs 0.440079 ms, 0.9914x; rejected. This is within-loop lookahead, not a first-load hoist across the decoded wait. |
| Immediate explicit TMEM copy per decoded fragment | 5535–5570 | First flattened layout was invalid; corrected final-mode partition passed six. 0.435007 vs 0.433471 ms, 0.9965x; rejected. |
| Raw-stage release before the collective TMEM store | 5443–5484 | Six passed; full-sweep EP geomean 0.9923x, TP 0.9980x; rejected. Preserve the release boundary. |
| Full packed-tile preload before decode | 1264–1286 | EP geomean 0.9884x, TP 0.9829x; rejected. |
| Earlier 128-value packed-fragment lookahead | 1288–1309 | Repeated EP geomeans 1.0001x / 1.0019x; neutral, rejected. |

Earlier Mega candidates03/04 targeted the obsolete direct-global-to-SMEM producer. They had no raw TMA stage, so their global-load/acquire placement is not evidence that the current TMEM pipeline lacks prefetching.

## At most one distinct follow-up: first FC2 packed load only

The bounded hypothesis is that the **first packed shared-load latency**, issued after raw readiness, can overlap an actual decoded-stage wait. It does not add a logical pipeline stage. It does not move any scale loads, conversions, or TMEM writes ahead of that wait.

Proposed source delta, only if the 512 baseline is validated and this experiment is approved:

- After the existing raw `consumer_wait` and source-view construction, copy only `tAsA_input_slice[(None,0)]` into the existing `tArA_load[(None,0)]` for FC2.
- Keep `producer_acquire`, the compact-scale copy, the fragment conversion loop and collective TMEM copy in their current order. Skip only the `idx==0` packed copy using a constexpr condition.
- Keep FC1 unchanged. Avoid copying `_transform_tile` into a 120-line subclass override; if implemented, use one private compile-time experiment selection in the shared helper, default false, with only Mega FC2 opting in. This is an implementation proposal, not a public knob or an autotune dimension.

At FC2 fragment32, this hoists **16 packed bytes = four 32-bit payload registers per transform thread** across the wait. There are **zero extra scale payload registers and zero decoded BF16 payload registers** across the wait. These are exact logical payload sizes, not a promise of four more physical allocated registers: address/control liveness and compiler allocation still need matched codegen. It lengthens the first packed fragment's live interval; it does not preserve every live interval. No extra RMEM tensor is required.

Safety follows from the unchanged raw-stage ownership: the producer has already waited for packed weights and scales and does not release them until after the same TMEM copy/fence. Each group preloads its existing disjoint fragment. No decoded destination is touched before acquisition; no early raw-state advance, extra barrier arrival, descriptor change, phase reset, or producer-tail change is introduced. Padded K tails still use the same TMA-filled source view. Keep the last-fragment readiness probe and the saved-state release exactly where they are.

Do not add scale preloading, full decode, next-fragment buffering, early release, or explicit fragment stores to this arm. Those would repeat historical trials or obscure the one tested mechanism.

## Evidence gate and bounded validation

The current two-group global256 N64/stage3 PC capture had 295 samples in verified free-decoded-stage sleep sites, zero in raw-ready sleep sites and 26,296 in other source-correlated transform instructions. It was strongly rank-skewed. Those values establish that a real decoded wait can occur; they do not establish a dominant bottleneck, a latency fraction, or a likely speedup. Zero samples do not establish zero stalls. Full integrity, source mapping and limitations remain in [the capture-specific audit](../../profiles/tmem-n64-stage3-current-ncu-pc-001/independent-audit/ANALYSIS.md). There is no current production PC evidence for the pending 512 variant.

After the separate 512 codegen/runtime gates, the first useful check would be matched baseline/candidate codegen: exactly one FC2 packed `LDS.128` before the matching decoded wait, no added packed/SF loads or spills, and preserved conversion-to-`STTM.x8` interleaving. If the load is sunk after the wait, the proposed mechanism did not survive compilation. Do not time an arm merely because its Python source moved.

If that gate passes, reuse existing public exact/numerical/graph/ring/tail and all-curated-tactic lifecycle tests, both return modes, then a bounded same-source baseline/candidate/restored-baseline timing at small, middle and dense controls before any full sweep. Exactly two transform groups and all graph/timing boundaries stay fixed. Any PC follow-up must use coordinated all-rank capture/replay and compare source-specific wait/load-dependency PCs; whole-kernel sample percentages or profiler durations are not production timing. No speedup is claimed here, and no new profiling is requested before the pending baseline gates.

Reproduce the CPU audit with `python3 candidates/w4a16_transform_acquire_audit/audit.py` from the effort root. `evidence.json` retains the exact capture filenames/hashes and reviewed instruction orders.
