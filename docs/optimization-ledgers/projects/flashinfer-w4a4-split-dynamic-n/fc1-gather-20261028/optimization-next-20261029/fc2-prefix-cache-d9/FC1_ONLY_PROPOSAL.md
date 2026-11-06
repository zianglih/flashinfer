# FC1-only protected-span proposal, corrected after planner audit

This records the CPU-verified proposal before implementation. The audited source is retained `9037f6d46fcb45eac04be04c182104336c8b1e7c`, whose swap kernel is identical to d9: SHA256 `5037dea841027df0e3fccb4b214b2ea763408e5fd9c1233868c0356508e5cb0b`. No GPU validation or performance claim has been made for this proposal.

## Correction and source trace

The previous proposal incorrectly claimed that FC2's `overlap_activation_accumulators=False` disables automatic K selection's preference for overlap. It does **not**. `_select_k_steps` preserves overlap when the accumulator occupies half of TMEM and either activation overlap is enabled **or** `bulk_output_bytes > 0 and channel_tiles == 1`. Globally widening `_accumulator_storage` therefore changes eligibility used by the FC2 K planner, even if its epilogue later retains the old 64-column condition.

Both paths must use the same release contract:

- Constructor lines 1483/1568: automatic K selection precedes actual accumulator storage and eligibility for the selected K.
- `_select_k_steps` lines 1795–1821: the existing preserve-overlap predicate filters each K candidate using `_k_stage_capacity` eligibility, then maximizes staged K coverage. Preserve that predicate and its tie-breaking.
- `_k_stage_capacity` lines 1748–1766: `_accumulator_storage` supplies both eligibility and the physical accumulator stages used by shared-memory planning.
- Actual setup lines 2279–2303: FC1 protects the scale footprint rounded to 32 columns; FC2 protects exactly 64 columns.
- `can_implement` line 1985 ignores eligibility and uses only physical stage capacity.
- Host calls in `moe_swap_ab.py` lines 506/625 pass `None` for FC1 and `False` for FC2.

## One eligibility helper and explicit private release limit

Reuse `_accumulator_storage(acc_cols, scale_cols, max_release_cols)` as the single eligibility helper. Preserve its physical-stage computation and error, and change only its eligibility predicate:

```python
can_overlap = 2 * acc_cols == capacity and scale_cols <= max_release_cols
```

Resolve the private integer once in the constructor, before automatic K selection:

```python
max_release_cols = (
    cute.arch.get_max_tmem_alloc_cols("sm_100") // 2
    if overlap_activation_accumulators is not False
    else 64
)
```

The variable-slab activation epilogue can consume its entire accumulator window before releasing it. The bulk TMA/SIMT epilogue has a fixed 64-column release boundary. These are ownership contracts, not model/dtype heuristics. Keep the existing activation-overlap argument to `_select_k_steps`: **whether to preserve overlap** and **how much the epilogue can release** are distinct facts. Do not infer the former from the numeric width.

Pass this same private integer through `_select_k_steps` to `_k_stage_capacity`, and directly to the constructor's `_accumulator_storage` call. `_k_stage_capacity` forwards it to that helper. Keep all shared-memory arithmetic and the current `preserve_overlap` expression unchanged. `can_implement` passes 64 explicitly; its capacity-only result remains identical. There is no public argument, autotune dimension, fallback, or runtime calculation.

Remove the global `sf_footprint > 64` rejection in actual setup because the helper already enforces the selected epilogue's release limit. Preserve explicit activation-overlap validation. FC2's one-channel and bulk-token conditions, 64-column protected interval, cyclic order, full-only commits, and every wait/release remain unchanged. FC1's rounded footprint and release-step calculation also remain unchanged.

The retained `run_overlapping_fc1` already traverses 32-column slabs cyclically over its virtual accumulator interval, including multiple channel tiles, and releases after `overlap_activation_steps`. No register snapshot or epilogue-body rewrite is needed. Every protected slab and its existing TMEM scratch transpose must complete before release; skipped slabs reach the same one-time logical release boundary.

## FC2 equivalence

For every current FC2 call the activation-overlap argument is False, so the proposed release limit is exactly 64. The helper therefore returns identical physical stages and eligibility, including inactive-overlap cases. K-capacity evaluation returns identical budgets/eligibility; selection retains its predicate, stage requests, ordering and tie-breaking. Both K choices and rejections are identical. Actual scratch choice, overlap flags, protected interval, accumulator stride/reservation and TMEM allocation are also identical. The removed assertion was already implied by FC2's unchanged eligibility predicate.

This proof does not depend on CLC metadata depth, shared-memory budget, dtype, or problem reduction length. Generated-code equivalence still needs a compile gate.

## CPU verification

Run `python3 fc1-gather-20261028/optimization-next-20261029/fc2-prefix-cache-d9/audit_fc1_only_policy.py` from the project root. Results are in `fc1-only-policy-equivalence.json`; inspectable AST-extracted models are `policy-retained-extracted.py.txt` and `policy-proposed-extracted.py.txt`. No CUDA or FlashInfer module is imported and no repository file is edited.

Retained methods are extracted directly from the pinned source AST. The proposal changes only the private release-limit handoff and the helper predicate. Local CUTLASS source supplies the hardware constants: 512 TMEM columns and **232,448 shared-memory bytes** for SM100/SM103.

| FC2 check | Cases | Result |
| --- | ---: | --- |
| Per-K capacity and raw overlap eligibility | 4,704 | Identical |
| Automatic K selection, including explicit stage requests | 21,150 | Identical |
| Explicit-K actual storage/output states and rejection boundaries | 24,870 | Identical |

Coverage includes all six legal operand/scale dtype combinations, M128/256/512, N16/32/64/128/256, K steps 4/8, legal native MMA K/alignment choices, CLC on/off, and metadata depths 1/2/3/4/8/64/128. Each geometry checks every fitting explicit operand-stage count plus its next rejection boundary; automatic K also checks None and a distant request of 1024. Maximum fitted depth is 11. Metadata depths are a finite sample; the algebraic proof covers other positive depths. Actual problem K is absent from these planning functions, so supported reduction lengths and partial-K tails do not alter equivalence. Bulk-output contracts use the complete byte-budget classes 0 and 2; BF16 and FP16 both use 2.

The deliberately incorrect global widening changes **170 FC2 K choices**: 168 explicit-depth requests and two default-depth requests. A simple counterexample is FP4×FP4, SF16, M128/N256, native K64, one requested operand stage, bulk BF16 output, no CLC: retained/corrected choose K steps 4; global widening chooses 8. The two default-depth counterexamples use the legal but unusually large 128-stage CLC metadata budget (M256/N256, native K96); these are boundary checks, not measured native winners.

FC1 changes intentionally: 840 actual states and 896 automatic-K requests differ, counting both None and explicit True activation-overlap contracts. For example, FP4×FP4 SF16 M128/N256 with native K64 and automatic depth changes K steps 4→8; explicit K8 gains a 96-column protected span. **A frozen native tactic containing automatic K can therefore compile differently without retuning.** Future measurements must report resolved K/stage/overlap geometry.

## Evidence and remaining qualification

The entire 12-cell prefix-cache candidate remains rejected. N3U EP/TP4096 W4A4 gains coincided with FC1 completion-frontier reductions of 11.200/6.702 µs and nearly neutral FC2. K3/V3/V41F TP per-token losses coincided with FC2 extensions of 34.916/31.072/28.028 µs while FC1 moved less than 0.26 µs. This motivates FC1-only investigation; it does not establish its causal speedup.

A separate implementation needs focused exact/lifetime coverage, FC2 PTX/CUBIN equivalence, and a bounded fixed-winner screen that reports resolved FC1 K/stage changes and retains negative rows. Coordinate with the independent native-FC1 epilogue work before editing the shared kernel. No compiler, GPU, sanitizer, or performance validation has been run for this proposal.
