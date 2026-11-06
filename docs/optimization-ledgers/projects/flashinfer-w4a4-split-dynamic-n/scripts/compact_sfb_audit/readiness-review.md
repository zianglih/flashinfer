# Independent-SF readiness composition: CPU review

Reviewed actual source `flashinfer-sf-readiness-review` core SHA256
`0f570a27aec49f767b414b7e4fcc163433598b5d344cc8b86fb4114d9802f9d1`.
Epilogue SHA256 remains
`e14d3300a97fa508b0039065a6b29b876a0e14d20a5456ef18bf0a662c168274`.
No source edits or GPU work by this reviewer. No blocking finding; emitted
instructions and runtime values remain the focused smoke boundary.

|Resource|Ready notification|Reuse notification|Index domain|
|---|---|---|---|
|A/B payload SMEM|Two elected TMA arrivals,32768+4096B|MMA completion|4 operand stages|
|SFA SMEM|One elected TMA arrival,4096B|Shared `ab.empty`, CP completion|4 operand stages|
|SFB SMEM|128 cp.async producer contributions|Same `ab.empty`, CP completion|4 operand stages|
|SFA/SFB TMEM|Publisher CP completion|MMA completion|2 scale slots|
|Accumulator TMEM|MMA completion|128 epilogue consumers|2 accumulator slots|

Source anchors in the reviewed core:

-968–1001: payload producer count2 and separate SFA count1;1020–1040:
  independent scale-slot ring. The narrow eligibility gate excludes group2,
  widerN and other output/scale contracts through their existing admission
  constraints and `physical_n16` predicate.
-1152–1250: all128 source producers first wait `ab.empty`. Warp0 supplies A,
  warp1 supplies SFA, warp2 supplies B. Atomic per-role expect+arrival precedes
  its TMA, preventing an early barrier phase transition. TMA tails zero-fill
  without changing the advertised physical transfer size.
-1382–1395: sharedSF tail uses a cloned stage state. Warp0 drains payload
  empties with waits only, avoiding extra arrivals on a two-producer full
  barrier. SFA's separately allocated empty half is intentionally unused;
  shared `ab.empty` protects and drains both scale sources.
-1583–1595: MMA waits published scales and payload independently, then applies
  the cross-thread TMEM fence.1697–1704 releases payload and the TMEM scale
  slot after MMA; no duplicate shared-SF source release remains here.
-1743–1790: publisher waits SFA-full and SFB-full, then the appropriate TMEM
  slot; both CPs precede its full arrival and shared source-empty arrival.
  `ab.consumer_release` is a TCGEN05 completion notification, not an ordinary
  synchronous arrival: custom_pipeline.py551–555 uses its TCGen05Mma empty
  barrier established at511–515. Thus SF source reuse follows CP completion.
  Its four-stage source index and two-stage TMEM index advance independently
  across persistent tiles. Final tail plus whole-CTA320-thread barrier protects
  teardown, which retains the original128-thread TMEM deallocation protocol.

The compact map and two SF slots are unchanged from the separately checked
broadcast version:128 total TMEM columns. This review does not broaden its
format/per-token coverage.

Performance interpretation: current-stage payload completion no longer blocks
SF publication. However producer warp0/2 still wait payload-empty before their
SFB contribution, so the source loops retain bounded coupling through payload
reuse. This is not fully independent lookahead. It is a deliberate small
orchestration step; no timing benefit is assumed.
