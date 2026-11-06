# Why the current trace shows two combine warp groups per CTA

Source `cd7cc07`; 128 global tokens / EP4 means 32 final output rows per GPU. No source or runtime change was needed for this audit.

Four groups are eligible: WG3 (warps 12–15), WG4 (16–19), WG0 (0–3), WG1 (4–7). The work mapping is group-major across the complete 148-CTA launch, in that priority order. Each thread reduces eight hidden elements over all eight expert contributions, giving `32 * (6144 / 8) = 24,576` thread chunks. One group stripe covers `148 * 128 = 18,944` chunks.

| Group | First worker in CTA0 | Active CTAs | Assigned thread chunks |
|---|---:|---|---:|
| WG3 | 0 | 0–147 | 18,944 |
| WG4 | 18,944 | 0–43 | 5,632 |
| WG0 | 37,888 | none | 0 |
| WG1 | 56,832 | none | 0 |

Recorded CTA0 and CTA1 therefore have actual reduction calls only on WG3 and WG4. All four rank traces contain exactly one combine range for each warp 12–19 in each recorded CTA (16 ranges/rank). Full-grid assignment arithmetic covers every output chunk exactly once; global CTA coverage above is derived from source, not a full-grid capture.

Current `megamoe_kernel.py:1014` computes `(logical_group * sm_count + cta_linear_id) * 128 + lane_in_group`; `topk_reduce.py:18` sets eight elements/thread. Transform roles prepare logical groups 0/1 at `megamoe_kernel.py:1591`; other non-dispatch roles prepare logical groups 2/3 at line 1628. The actual work guard and marker are at lines 1642–1644.

`_prepare_reduce_worker` has identical AST to parent `40d0ceb`. The marker change moved `combine_reduce_topk_bf16` from outside to inside the existing `while worker_idx < num_workers` loop. The previous trace emitted empty combine ranges on WG0/WG1. The new trace accurately exposes assigned work. Four-group eligibility does not guarantee four active groups at small token counts. No compute optimization is proposed or retained by this audit.

Machine-readable derivation, exact output coverage and all four rank participant checks: `combine-assignment-check.json`. These are CPU source/trace checks; no new GPU capture or performance comparison was run.
