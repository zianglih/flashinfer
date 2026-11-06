# ACC1 / decoded3 native review

All three current captures pass: REG96, STACK0, LOCAL0,640 threads and the
unchanged144/80/64/96/96 role allocation. All retain16 MMA instructions and no
LDL/STL. Each compiles once with zero device allocations/launches/collectives.

N64 has5504 listed instructions and its complete instruction stream equals the
shared-layout control. N128 has6016 versus6032. ManualM128/N128 has5808; no
matched old manual capture is used for a reduction claim. Exact source/stage,
resource and SASS records are in native-review.json.

N128 source-correlated PTX fixes the accumulator full/empty barriers at shared
base+160/+168. Producer wait uses that fixed empty barrier, its MMA destination
has no dynamic accumulator-stage offset, and decoded A starts at ACCbase+128.
The decoded ring wraps at3. MMA producer parity starts1 and flips unconditionally
once per work (line4984); epilogue parity starts0 and flips once per work
(line7592). Its FC1/FC2 waits use the fixed full barrier. This is one physical
slot, not a two-slot layout hidden behind a one-stage logical pipeline.

Manual one-CTA MMA shows the same physical ACC1/decoded3 contract and producer
parity flip at4772; its H7168 native layout fits B2/raw2. That native large-shape
allocation is distinct from the smaller manual numerical fixtures. N64 retains
ACC2/decoded3/B3/raw5; M256N128 uses ACC1/decoded3/B3/raw4. No source/public
parameter change beyond the reviewed private compile-time allocation is added.

Both FC epilogues retain release after final TMEM scratch reads before remaining
register/store work, as reviewed in ROOT_SOURCE_REVIEW.md. Fresh numerical
validation is running separately. Native checks do not establish latency gains.
