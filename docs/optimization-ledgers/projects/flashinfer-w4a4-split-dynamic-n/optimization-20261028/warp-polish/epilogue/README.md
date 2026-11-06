# Adjacent-warp SF32 exchange

Base: `99f4d0c277746fb706d10a4bb303c98c5f31e0a9`. The isolated adjacent-warp barrier candidate was screened and rejected: overall geometric change −0.094%, decode −0.003%, prefill −0.230%; see `../screen-summary.md` and the parent screen receipts. Its closed review clone was removed. Patch and ownership proof remain here as local history.

The gated SF32 epilogue combines two 16-channel warp fragments into a 32-channel
scale. Its scratch exchange reads only the adjacent warp (`warp ^ 1`), but both
publication and reuse barriers currently join all four epilogue warps. The
candidate gives warp pair 0/1 barrier 6 and pair 2/3 barrier 7, each with 64
participants. It keeps both barriers, all math, all scratch addresses and every
accumulator/operand lifetime operation.

## Ownership proof

- Epilogue-relative warp `w` writes only scratch row `w`, then reads row `w ^ 1`.
  Pair 0/1 therefore accesses rows 0/1, while pair 2/3 accesses rows 2/3. Neither
  pair reads or writes the other's rows.
- Each publication barrier joins exactly the 64 threads that produce and consume
  those two rows. Every lane executes the same barrier instruction and every
  lane within a warp supplies the same ID. Both warp pairs execute the same
  control flow, but they need not arrive simultaneously.
- The second barrier remains. It orders both warps' previous reads before either
  warp may overwrite its row in the next helper invocation. It is necessary even
  when the next invocation belongs to a different token/channel/work tile.
- Live-token predicates surrounding the helper are CTA-uniform. Per-token and
  output-channel predicates do not enclose either pair barrier. No pair can lose
  a participant on partial routes or padded channels.
- The helper is instantiated only for gated SF32 scale generation. Bulk output
  and this path are compile-time exclusive, so their use of barrier 6 cannot
  overlap. The kernel's other named barriers are 1 (final all-role join) and 3
  (TMEM retrieval). Barrier 7 is unused before this candidate; operand, CLC and
  accumulator mbarriers are a separate resource.
- Accumulator early release still counts every epilogue thread and preserves the
  existing TMEM read fences. A fast pair cannot authorize MMA overwrite until
  the slow pair reaches the same release. The final full-CTA join, bulk-drain
  protocol and two-CTA deallocation handshake remain unchanged.

The saved installed CuTe 4.8 `NamedBarrier` accepts `Union[int, Int32]` IDs;
`optimization-20261027/warp-specialization/installed-helpers.py:601` documents
this. Thus the dynamic pair ID does not require an inline-PTX implementation or
new runtime dispatch. Codegen must still verify the two 64-thread joins and
measure any extra ID arithmetic/register cost.

## Audit boundaries and prior experiments

Preserve the startup barrier/TMEM join, last-use TMEM fences, shared operand
ring, accumulator overlap windows, SF32 publication/reuse joins, bulk-store
publication/reuse/drain joins, and peer-CTA deallocation rendezvous. Their
producer-consumer relationships remain live after the role redesign.

Previously rejected per-token single-transpose, SF32 double buffering,
protected-prefix buffering, metadata preloading, physical-N16, register
transpose, register-budget-only and deferred bulk-drain experiments are not
repeated here. This patch changes the participant set of an existing exchange,
not its storage, expression order or lifetime. SF16, non-gated Relu2, FC2,
legacy, Rubin and W4A16 source paths are untouched.

Potential follow-up: MMA accumulator `producer_tail` may duplicate the final
join, but removal is a separate experiment requiring a proof that remote empty
arrival transactions have completed before barrier storage teardown. Consumer
math completion alone is insufficient evidence. It is not part of this patch.

## Qualification plan

Use source-paired exact replays spanning gated activations, narrow/wide route
tiles, one/two CTA, one/two channel tiles, partial/empty/reactivated routes,
CLC/static and PDL on/off. Include unchanged SF16 and Relu2 controls. Inspect
PTX/SASS and resource deltas before timing. Frozen native-winner public-chain
CUPTI screens use all four models and supported formats, input quantization for
NVFP4, unfused swap-AB output, existing persistent native caches and private
strict DSL caches. Sanitizer remains skipped.

Local static checks: `git diff --check` and Python byte-compilation pass.


Later epilogue work is recorded in `PROFILING.md`, `routed-fc2/` (rejected and source clone removed), and `scatter4/`, `scatter4-r3/`, and `scatter4-r4/` (all rejected and closed after source-paired exact/codegen gates and independent CUPTI screens). The scalar-looking `_absmax` loop already lowers to eight native FMNMX3 instructions with absolute source modifiers in config0 FC1; an explicit max3/abs PTX rewrite would duplicate compiler work. Evidence: `../combined/gate-evidence/outputs/candidate/config0-clc0-fc1-pdl0.sass`, lines1433–1463. No such rewrite was proposed.
