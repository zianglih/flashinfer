# Gathered SFB: omit copies for rows outside the actual MMA N

**Recommendation: a focused prototype is justified.** Predicate the SF `cp.async` instruction itself with `row < rounded_mma_n`, where `rounded_mma_n = round_up(valid, 8 * cta_group_size)`. Keep source zero-fill for issued invalid/padded rows, all 128 asynchronous arrivals, the relay, operand release, PDL and FC2 unchanged. This is one logical-consumption rule across supported dtypes and tactics, not a model or token-count heuristic.

Read-only audit of `374ed4c07ee3a8c30a30026018a96d8f613ac4b5`; no source changes or GPU work. `proof.json` binds the kernel and records 11,904 CPU ownership/bank cases. That proof checks source-derived formulas, not generated hardware behavior.

## Existing producer and the proposed boundary

In `flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py`:

- Lines 3506–3525 map the 128 gather threads bijectively onto a canonical 128-row SF block, with each thread owning one aligned four-byte word per K block. The optional second row block starts at row 128.
- Lines 3546–3579 currently issue every word for all 128/256 rows. `(row < valid) & (channel < K)` controls the source size: a false predicate still issues an asynchronous copy that writes four zero bytes.
- `_blockscaled_dynamic_mma`, lines 219–225, rounds the instruction's actual N to `8 * cta_group_size`.

Only rows below that rounded N can contribute to this tile's MMA. Cache the row-valid-for-MMA predicate outside K, alongside existing route metadata; use it to suppress the instruction, not to replace the source-size predicate. Preserve the existing source-size predicate inside the issued instruction. Thus real rows load their scale, `valid <= row < rounded_mma_n` still zero-fill, and K-tail words still zero-fill exactly as today.

The predicate must use **global N in both CTAs**, not `rounded_mma_n / cta_group_size` and not the CTA's payload offset. SFB is intentionally full-N and replicated; only the payload is divided between CTAs.

No new public argument or tactic axis is needed. A DSL `if` may lower to branches; inspect generated code before deciding whether a small inline predicated `cp.async.ca.shared.global` primitive is preferable. The existing `cute.copy_atom_call(..., pred=...)` alone is not an instruction-skip mechanism.

## Why S2T does not make skipped rows live

The shared SF layout keeps four adjacent scale bytes for a single token row. In one 128-row block, byte addresses are:

```
(row % 32) * 16 + (row // 32) * 4 + scale_byte
```

K words add 512 B, and row banks add `sf_stage_bytes`. These terms do not overlap. See CUTLASS `python/CuTeDSL/cutlass/utils/blockscaled_layout.py:40` (`BlockScaledBasicChunk`) and `:187` (`make_smem_layout_sfb`).

`_s2t_partition` at kernel line 2519 uses `Cp4x32x128bOp`. CUTLASS `include/cute/atom/copy_traits_sm100.hpp:3757` gives the one- and two-CTA source layout: the broadcast axis has zero source stride, so it duplicates the same bytes into subpartitions. It does not combine different token rows. `mma_traits_sm100_frag.hpp:438` likewise preserves the row/K scale identity through the SFB replication layout.

The full-N S2T transaction still reads skipped shared rows and writes their arbitrary/stale values into unused TMEM row positions. That is deliberate: this proposal reduces SF zero-store work, **not** S2T copy volume. It does not read an invalid address. Do not claim sanitizer coverage or removal of all SF traffic. All shared/TMEM positions the current MMA actually consumes remain initialized.

## K96 bank placement

The kernel's dynamic K96 target layout at lines 3171–3202 rearranges whole 128-row banks while retaining their internal row/scale mapping. Let `W = sf_cols / 4` and `q` be the SF-word index:

- N <= 128: bank 0 occupies word slots `q`; unused bank 1 occupies `W + q`.
- N > 128: banks occupy `2*q + bank`.

The unused bank cannot overwrite bank 0 in the narrow case. If N exceeds 128, the predicate retains all of bank 0 and the required rounded prefix of bank 1. N rounding never crosses the 128 boundary without `valid` also crossing it. K96 scale-ID byte selection and the mixed six/four-scale K updates change K addressing, not token identity. The CPU proof checks both bank cases and SF16/SF32 stage geometries; a K96 runtime exact gate is still required.

## Barrier, reuse and output contracts

- Kernel lines 2764–2770 initialize each local gather barrier to **129** arrivals: one explicit Gather4 byte-accounting arrival and all **128** `cp_async_mbarrier_arrive_noinc` arrivals. Keep these unchanged and outside the row predicate, including threads that issue no SF copy. The PTX [asynchronous barrier-arrival contract](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#parallel-synchronization-and-communication-instructions-cp-async-mbarrier-arrive) tracks prior copies from that thread; suppressing a copy does not suppress its explicit arrival.
- Gather4 expected bytes are unchanged. SF copies are tracked by arrivals, not bulk transaction-byte accounting.
- The relay still waits for local completion, publishes the async shared view, and signals the MMA leader. The existing operand release still follows both channel MMAs, preventing stage reuse from racing an S2T read.
- A later tile with more live rows overwrites every row it needs before its own completion signal. A later narrower tile may leave stale data only outside its own MMA N. Do not move the predicate across tile metadata updates.
- Epilogue activation/quantization is token-separable. `_run_token_group` (lines 777–935) only stores rows below `valid`; SF32 joins adjacent channel fragments of the same token, not different tokens. No public output-padding zero contract is introduced or removed. No reference change is needed.

## Qualification and expected scope of savings

For a 128-row SF block, rounding to 8/16 rows can omit 93.75%/87.5% of four-byte SF writes. This is avoided zero-fill/shared-store work; invalid rows already avoid source HBM reads. Active lanes and warp instruction issuance are not the same count, and extra predicate/control work can outweigh savings. No speedup claim follows from these percentages.

Before timing: inspect SASS for instruction predication, no unexpected branch duplication or spills, and FC2 equivalence. Run existing exact selectors covering tiny routes, both CTA groups, both SF formats, route tails and K96 mixed-K tails; retain the poisoned-adjacent-scale-row case. A local replay that reuses a stage through larger/smaller/larger `valid` values would directly stress stale data without adding a repository test file. Never skip the zero-fill between `valid` and rounded MMA N or for consumed K-tail scale words. Then use a small matched-tactic decode/prefill screen; reject if the generated implementation is more complex or slower overall.
