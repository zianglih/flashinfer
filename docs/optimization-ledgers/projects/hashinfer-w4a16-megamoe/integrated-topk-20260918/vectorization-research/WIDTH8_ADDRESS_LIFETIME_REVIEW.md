# Width8 address lifetime and width4 priority

Read-only source/generated-code review, 2026-09-19. Current PR8 is d01f074
(534 plus the proved redundant inner guard removal). No GPU run or source
mutation is part of this note. Width4 is a separately authorized experiment.

## Priority 1: width4 weighted combine (authorized isolated trial)

This was not tested on PR8 False. The prior K1/e26 width4 experiment was the
PR9 True score-free arithmetic mode and had mixed results; it is context, not
an answer for the weighted recurrence. L1/L2 adjacent16, I1 head8/bulk16 and
N1/N2 coalesced16 all moved in the other direction and remain unpromoted.

One private width constant4, two64-bit copy atoms, and its docstring preserve
the exact first score multiply/later ordered packed FP32 FMA recurrence.
The existing output alignment expression becomes8bytes, so no stronger input
or output alignment is introduced. Width4 gives two independent packed chains
per worker instead of four. It doubles worker/score-prepare counts and halves
memory/arithmetic per worker, trading metadata and loop cost for more of the
existing retired workers participating. No role, register-budget, CTA, barrier,
transport, public knob or autotune dimension changes.

At H7168 with148CTAs, the first128-thread strip spans18944 workers. Four
retired WGs provide75776 workers per grid pass. Existing assignment gives
both dequant WGs the first two strips, then epilogue and control strips.

| Local tokens | Width8 workers | Width4 workers | Main coverage change |
|---:|---:|---:|---|
| 1 | 896 | 1792 | 7 ->14 first-strip CTAs |
| 16 | 14336 | 28672 | Starts second dequant strip |
| 32 | 28672 | 57344 | Recruits epilogue/control strips |
| 64 | 57344 | 114688 | More than one full grid pass |

GlobalT128/256/512 on balancedEP8 correspond to the last three rows. At
smaller globalT, active ranks can have only one local token. Prefill may pay
more score loads/coordinate setup and loop trips; this is a concrete experiment,
not an established win. Full13 compares exact104 outputs against retainedA3,
with historicalA1 shown separately. A3 is3de; candidateparentd01 also contains
534 benchmark documentation/default-token changes and the removed guard that
was already constexprfalse for H7168. Executed benchmark/timer helpers and
explicit13 tokens remain identical.

## Priority 2: reuse the live linear worker index for address formation

The existing caller already bounds and retains worker_idx=w. For Q=H/8,
`t=w//Q` and `h=w%Q`, existing addresses in BF16 elements are:

```
output = t*H + h*8 = w*8
route0 = t*K*H + h*8 = w*8 + t*(K-1)*H
route k = route0 + k*H
```

Use the already-live w and t to form those addresses, rather than preserving
h and the common64-bit h*8 subexpression through the full reduction. Promote
w and t toInt64 BEFORE multiplication, retain existing pointer/layout
alignment, and retain initial/continuation score preparation and all drains.
No claim is made that signed32 products fit for every accepted dimension.
The existing frontend requires contiguous BF16 reduced_output
(`frontend.py:556–570`), and the symmetric combine allocation is fixed
contiguous(T,K,H) (`:729–736`), so the identities do not require a new layout
contract. Zero/inactive rows remain excluded by the existing caller guard.

Concrete generated evidence is the fully collected matched exact3de baseline
at H7168/T16384/tactic1 under
`combine-packed-bf16-expand/codegen-selected/early-matched/baseline/`.
Its selected SASS does the following after the second640-thread rendezvous:

```
0x15bd0 IMAD.WIDE R48, R0, 0x8, RZ       # h*8, 64bit
0x15be0 IMAD.WIDE R2, R44, 0xe000, R48   # t*K*H + h*8
0x15bf0 LEA ...                         # BF16 byte offset + base
0x15c00 LEA.HI.X ...
0x15c10 first route LDG128
...
0x161e0 IMAD.WIDE R48, R44, 0x1c00, R48 # t*H + h*8
0x16480 LEA ...                         # output address
0x164c0 LEA.HI.X ...
0x16530 output STG128
```

Thus the h*8 pair R48/R49 is retained into the approximately147-instruction
body, updated midway to the output offset, and used near its end, while w is
independently retained inR45 for continuation.
A pointer/index rewrite could eliminate that long-lived pair and the separate
hidden-tile state; it might also simplify the output address. This is an
instruction/lifetime target directly visible in generated code, **not a proven
instruction-count saving**: ptxas can select an equally long alternative,
rematerialize state, or change base-pointer placement. Current resources have
REG96/STACK0/LOCAL0, so there is no spill defect and no basis for claiming
occupancy improvement. Reject a candidate that merely shuffles instructions
without a measured benefit. A future generated comparison must show the actual
lifetime/address reduction with the same route loads and ordered arithmetic.

This is distinct from measured unsigned-worker H1 (changes quotient lowering),
packed-BF16 G1 (conversion instructions), and the documented unrun coordinate
recurrence (only continuation divmod). It preserves width8 worker ownership
and applies to the first decode pass, unlike the continuation-only recurrence.
It should remain independent of the active width4 experiment.

## Ideas not recommended again

Matched3de already issues seven of eight route LDG128 operations before the
first packed multiply; explicit route prefetch has no demonstrated missing
ILP to repair. G1's measured96->64 BF16 expansion instructions did not yield a
retained result. Input ILP pair loops, deferred donation and256-bit load/store
variants were already tested. Score broadcast would replace naturally merged
same-address loads with shuffle/shared machinery; no supported smaller sequence
was found. Avoid copying or changing protected dispatch_prep/pull solely to
reuse routing-ID or score metadata. Source count reductions alone are not
performance evidence.
