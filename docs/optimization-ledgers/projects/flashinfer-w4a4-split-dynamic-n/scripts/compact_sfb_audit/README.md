# Compact SFB and producer orchestration audit

Read-only source review, 2026-10-25. Production remains clean98fd. No GPU work
or experiment-source changes were performed. Owner's broadcast core is
`flashinfer-compact-sf-broadcast-review`, SHA256
`a958760e4a8f9dbaf0986dae48a2b1692d1ffadb6e635030028e75611a7a673f`;
its epilogue is the frozen physical-N16 source. The earlier four-warp STTM
draft is a different, unmeasured design.

## Mapping result

No static mapping blocker found. [check_mapping.py](check_mapping.py) checks
3,808 combinations: valid rows0..16, route starts on both sides of canonical
128-row boundaries, K64..7168 including partial K512 stages, all32 local
TMEM rows, all4 warp quarters, all8 native K64 subgroups and all4 SF bytes.
There are15,597,568 scale-byte checks and the same number of padding-zero
checks; [check_mapping.json](check_mapping.json) records the result. This is
symbolic CPU evidence, not proof of the compiler's emitted copy descriptors.

For producer thread `t`, let `r=t//4`, `w=t%4`, atom `a=0..3`:

- SMEM byte offset is `stage*2048 + a*512 + r*16 + w*4`.
- Even word positions0/2 contain the four scale bytes for native K64 subgroup
  `2*a+w//2`. Odd positions1/3 are zero. Rows at or beyond validN are zero.
- The source is the original canonical row `route_start+r`, at channel
  `k_tile*512 + 64*(2*a+w//2)`. SourceK beyond the logical reduction is zero.
- `CP32x128b.warpx4` broadcasts the atom to all four quarters. Quarter `q`
  receives local row `r` at TMEM row `32*q+r`; column `4*a` holds subgroup
  `2*a`, and column `4*a+2` holds subgroup `2*a+1`.
- Native MMA step `j=0..7` reads `SFBbase+2*j`, with selector `SFB_ID=0`.
  All four byte subcolumns belong to that token's K16 scales. Byte offsets
  inside a word are not TMEM column offsets.

The current standard half-K helper is used only to construct the copy view:
four512B atoms/16 TMEM columns. The real MMA still has8 K64 steps and a full-K
shape; its compact branch explicitly supplies the step address. Source
anchors in the reviewed core: address/selector150–178, layouts688–702,
producer1224–1245, MMA views1537–1555, publication1665–1720.

Two accumulator slots occupy `[0,16)` and `[16,32)`. Scale slot0 is
SFA`[32,64)`/SFB`[64,80)`; slot1 is SFA`[80,112)`/SFB`[112,128)`.
Last SFB reads are columns78/126. The two-stage allocation is128 columns.
Without physicalC16, compactSFB plus two SF slots still rounds160→256;
without compactSFB, physicalC16 plus two SF slots rounds160→256. Both
changes are needed for128. SFB SMEM is2048B/stage rather than4096, while
TRT's four-warp register-store design uses512B. These are not the same
storage or publication cost.

The current gate excludes SF32, FC2, other route widths and BF16-output
per-token mode. Do not extend the explicit `+2*j` selector rule to those
contracts without their own mapping. Padding is still written, so inactive
SF rows cannot carry NaNs into a live token's scale selection.

## Completion and compiler boundaries

The publisher waits original A/AB stage readiness, obtains a scale slot,
issues CP, then uses a TCGEN05 completion arrival. MMA waits that completion
and an after-thread-sync fence before reading the slot. MMA completion
returns the scale slot and original operand SMEM. The published source
maintains a separate stage index/phase for each ring, including persistent
tile boundaries. This preserves the existing lifetime protocol; it does
not yet free SF source SMEM earlier than operand payload.

Remaining focused GPU gates: verify four emitted SFB CP operations at
columns0/4/8/12, SFB MMA addresses0/2/.../14, selector0 and the two actual
slot bases; compile legality and exact values for shortK/partialN/persistent
tiles; no unintended register spill. No performance conclusion follows
from the CPU mapping.

Official references: [PTX CP multicast](https://docs.nvidia.com/cuda/parallel-thread-execution/index.html#tcgen05-instructions-tcgen05-cp)
defines the32x128b broadcast to all4 quarters; [scale factor B4X](https://docs.nvidia.com/cuda/parallel-thread-execution/index.html#tcgen05-mma-scale-factor-b-layout-4x)
requires four bytes and selector0; [CUTLASS4.7 helper](https://github.com/NVIDIA/cutlass/blob/v4.7.0/python/CuTeDSL/cutlass/utils/blockscaled_layout.py#L184)
constructs canonical SF atoms and corresponding TMEM copy views. The current
published documentation is PTX9.4; the existing archived control PTX already
uses the same `.32x128b.warpx4` instruction under our pinned CUDA13.2 toolchain.

## TRT roles and register budgets

Exact source identities and current cubin boundaries are in
[the Gen audit](../trtllm_gen_decode_audit/README.md). The following is from
published PR2917 revision64ed071e, **not a claim that newer measured cubins
were built from that revision**. N8/N16 below name its selected persistent
FC1 source examples, not merely a logical token count.

|Role|N8 Gather4 warps|N16 LDGSTS warps|Explicit per-thread register limit|
|---|---|---|---:|
|Epilogue|0–3|0–3|160 inc|
|SFB register publisher|4–7|4–7|72 dec|
|B payload loader|8–9|8–9|48 dec|
|SFB loader|10–11|10|48 dec|
|A weight TMA|12|11|48 dec|
|SFA TMA|13|12|48 dec|
|SFA publisher|14|13|48 dec|
|MMA|15|14|48 dec|
|Scheduler|16|15|48 dec|
|Padding|17–19|none|48 dec|

Source anchors in N8-TMA-P: role declarations204/396/588/798/1029/1300/
1576/2097/2715/2763; corresponding N16-LDGSTS-P192/384/628/838/1325/
1596/1927/2880/3791. Every role has a warp predicate and an explicit
`setmaxnreg` near its declaration. Source names are listed in the linked audit.

TRT therefore has20/16 warps, including5 SF-publication warps, versus our
9-warps98fd N16: producer0–3, epilogue4–7, MMA8. Our warp0 issues A/SFA/B
TMA, all4 producers copy SFB, and MMA8 publishes scales. Our existing
compiler-reported resources are64regs/thread, zero local memory; the
physicalN16 epilogue gives50regs/thread. The publisher prototype adds warp9
and a second scale slot. Our source has no dynamic register redistribution.
TRT's newer actual FC1 cubins report96/128 aggregate registers/thread with
zero local memory; those are different measurements from old source role
caps. Do not compare160 to64 as if both were whole-kernel allocation.

Current operand SMEM alone remains above half of an SM, so copying TRT's
register limits cannot unlock a second resident CTA for this geometry.
The extra-warp producer tests actually raised compiled FC1 registers64→74
and regressed full chain; neither spill nor a register occupancy bottleneck
was established. Dynamic register tuning should remain a separate,
evidence-driven axis rather than being bundled with concurrency.

## Smallest orchestration step

1. **Already being implemented by the producer owner:** assign A/SFA/B TMA
   to existing producer warps0/1/2. Keep288 threads, one full barrier with
   three per-role `arrive_and_expect_tx` arrivals, and the original single
   post-MMA empty barrier. Each role advertises only its own byte count
   before its first copy; all three arrivals must occur even when a role's
   transfer is zero-sized. This is smaller than the rejected extra-warp
   independent-ring designs. It preserves TMA and existing operand storage.
   See [build_distributed_tma.py](../producer_roles_experiment/build_distributed_tma.py).
   Its current SF-acquire placement still bounds producer lookahead; this
   is concurrent issue, not fully independent unbounded pipelines.
2. **Possible later composition, not implemented here:** let existing
   producer warp3 perform compact SF publication after its128-thread-ring
   contribution, instead of adding warp9. In the compact mapping warp3
   only zero-fills rows24..31; it has no live N16 SF loads. Keep its SF
   commit before waiting for source readiness, so the source barrier can
   complete. It can then acquire/publish the TMEM slot and advance; the
   other three producers may continue ahead. Preserve two SF slots and
   completion fences. The tradeoff is delayed warp3 participation in the
   next SF stage, so timing must decide whether it beats the extra warp.

Do not combine these tests with reducing SF producers to64 threads:
that would additionally require initializing untouched padding in every
SMEM stage, a correct proxy fence, and revised barrier counts. It is a
different ownership change and unnecessary for the first minimal test.
