# Independent W4A16 operand depths

Unstaged prototype in `flashinfer-w4a16-stages-review`, based on retained `ce4a7d8c`, W4 control kernel SHA256 `de042712ac4fcab0f14eb5f870824416f65dce15e2243198b28ffb4226ac0d58`. Candidate `cf78403f1572bb8fe62f9ab5c3056d6d671bb82224631f572d127322887f44e2`, 42 additions/13 deletions in one file. No GPU result yet.

## Distinct mechanism and evidence boundary

The raw-weight and BF16-activation pipelines already have independent barriers and releases, but both are allocated with `num_load2trans_stage` (`moe_w4a16_kernel.py:1199,1229`). Raw weights subsequently occupy a separate decoded-weight ring. Current raw-A and B counts therefore do not represent equal storage along their respective producer-to-MMA paths.

Rubin MegaMoE independently allocates token and weight stage counts (`sm107/.../block_scaled_swap_ab_fc12_mainloop_gen_specialized.py:415–466`). Its fixed N256/six-token-stage policy is not imported. The original W4 five-WG plan explicitly deferred separate B depth, and the closed-lead/result/patch search found no measured W4 stage-repartition experiment. This is distinct from closed route batching, issue ordering, producer lookahead, raw-release placement, decoded-peek removal and register redistribution.

Older K3 iKET captures show larger B-ready waits after Gather4 while transform waits do not grow. They precede later retained issue-loop improvements and do not establish a present depth bottleneck. This proposal needs a source-paired screen; no speedup is assumed.

## Exact stage unit and ownership

- A raw stage holds the full per-CTA M×stage-K packed tile and its scales. Both decoder WGs jointly partition the same stage; they are not two successive K stages (`_setup_transform_partition`, lines579–612).
- `_transform_tile` acquires one raw stage and one decoded destination, completes every fragment, stores the transformed tile, then `_finish_transform_stage` fences the output, releases raw A and commits decoded A. Both state cursors advance once per stage-K tile (lines716–820). The last partial problem-K tile still uses a full physical stage.
- MMA advances decoded-A and B independently once per stage-K tile and releases both only after all K atoms using them (lines1955–2045). Neither stage index is used to address the other ring.
- At completed handoffs, with issued raw count `r`, decoded count `t`, and MMA-consumed count `m`, raw resident tiles are `[t,r)` and decoded resident tiles `[m,t)`. They are disjoint, so `r-m <= raw_depth + decoded_depth`. During transformation, the active raw tile additionally reserves a decoded slot; that transient duplicate does not count as another independent K tile. The available completed-plus-raw inventory is then at most the sum minus one.
- The sum is a queue-capacity/backpressure bound, **not** additive latency coverage. Decoder work, raw TMA delay, ready-vs-reserved slots and inter-tile imbalance remain performance risks.
- Keep cursors persistent across work tiles, count resets unchanged, all arrivals/releases/drains unchanged, and all minimum depths at two. No K-count clamping or altered PDL/CLC protocol.

## Compact planner objective and order

First run the existing allocation unchanged, preserving decoded depth `d`, accumulator/metadata counts, TMEM allocation and final output-store count. Let raw stage cost `R` include packed A, scales and its 16 barrier bytes; B stage cost `S` includes BF16 B and its 16 barrier bytes. The fixed operand budget is exactly `P = old_depth * (R + S)`. Do not borrow output-store bytes or remaining SMEM slack.

The continuous capacity balance `b = a + d`, `a*R + b*S = P` gives:

```
a = max(2, floor((P - d*S) / (R + S)))
b = min(ceil((P + d*R) / (R + S)), floor((P - a*R) / S))
```

Round the raw depth down and direct B depth up, subject to the unchanged byte budget and two-stage floor. Accept the split only when `b > old_depth`; otherwise preserve both original depths. This final condition avoids reducing raw prefetch capacity when the freed bytes cannot purchase another activation stage. Remaining bytes stay unallocated; output capacity is unchanged.

This is a single compile-time resource rule, applied to both gathered FC1 and regular-TMA FC2, with no model, dtype, token, cluster, N threshold or tuning axis. Existing stage validation remains. It preserves `min(b, a+d) >= old_depth`, but **does not guarantee a strict increase**: N128/group2 changes A4/B4/D2 to A2/B5/D2, so matched inventory remains four; the hypothesis is better direct-B latency hiding at the cost of less raw-weight prefetch. N192/group2 cannot afford another B stage and remains A3/B3/D2.

## CPU proof and complete tactic table

`prove_plan.py` executes the actual current `_compute_stages_and_tmem_cols` AST using native M128-per-CTA TMEM geometry shims and the actual CUTLASS pure-Python epilogue-size helper. It matches all 22 saved native Gather4 stage-count captures. It checks 144 supported storage configurations, 22,500 queue states, unchanged output/decoded counts, operand bytes at or below the old allocation, minimum depths, and nondecreasing matched inventory. These checks do not replace actual CuTe-layout, CUBIN or GPU correctness gates.

`TACTIC_TABLE.md` covers all 23 existing tactic pairs; `all-23-tactics-eight-arms.csv` expands all four models × EP/TP × both FC1 scheduler choices and static FC2 (552 rows). EP/TP problem dimensions and token counts do not enter this allocator. V3/V41F/K3 gated FC1 share counts; N3U ReLU2 FC1 has the ungated output reservation. Existing CLC decisions and tactics remain unchanged.

The implemented candidate planner matches the proposed result in all 144 CPU cases. Source proof normalizes only the new B-depth attribute and confirms that the complete kernel and wrapper ASTs otherwise match; every transform, release, MMA issue and epilogue method is unchanged. Only setup/allocation changes. All scoped pre-commit hooks pass, including mypy/ruff, and `git diff --check` passes. Actual CuTe struct padding, per-buffer alignment and allocated shared-memory size remain part of the compile gate; the conservative byte model is not a substitute.

## Proposed implementation and gate

Add one private B-stage count returned by the allocator. Use it only for B SMEM layout, B barrier arrays, B pipeline creation and B producer/consumer states; retain raw-A count everywhere else. Build B with the existing `sm100_utils.make_smem_layout_b` helper. Do not modify public interfaces, the shared CUTLASS utility, epilogue bodies, transform schedule or MMA issue math.

Before timing: source/CPU proof against the implemented planner, then paired codegen/resource checks for native N8/16/32/64/128/192, both CTA groups and both FC roles; preserve unchanged N192 binary evidence where possible. Existing W4 exact/graph cases must cover independent wrap periods, partial K, both layouts and activation contracts. Full refresh is not required before a small frozen-winner same-GPU CAAC screen. No GPU has been used for this proposal.
