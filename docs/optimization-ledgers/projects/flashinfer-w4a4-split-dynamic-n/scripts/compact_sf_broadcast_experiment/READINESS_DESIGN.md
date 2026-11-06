# Next coordinated readiness design (not implemented here)

The measured compact publisher still waits `a_pipe` before copying scales. That
barrier covers A payload + SFA + B payload. Thus the full weight/payload transfer
must complete before SF publication starts; adding cross-warp CP completion can
serialize work that the original MMA warp pipelined. The negative result cannot
isolate a properly independent SF producer.

Minimal independent-SF readiness plan:

- Keep joint A+B payload TMA ring, expected transaction bytes exclude SFA.
- Add a four-stage SFA TMA ring (eight64-bit barriers,64B metadata).
- Existing weight producer issues SFA into that ring; SFB remains existing
  cp.async source ring, compact2048B perstage for the current narrowcontract.
- Publisher waits SFA/SFB source rings only, acquires one of two TMEM SF slots,
  issues all S2T copies, commits published-SFfull completion. Two additional
  TCGENcompletion arrivals release SFA/SFB source rings after copies, beforeMMA.
- MMA waits A+B payload and published-SFfull, executes unchanged native MMA,
  then releases payload ring and TMEMSFempty. It must stop releasing sourceSF.
- Each role keeps separate persistent ring state and advances once per tile/K.
  Producer tail uses cloned state for each ring; publisher tail waitsSFempty.
- Current128TMEM-column ownership and original terminal CTA barrier remain.
  No sourceSF buffer can be overwritten before publication completes; no TMEM
  slot can be overwritten before final MMA use completes.

Composition requires coordination with the separate existing-warp TMA-issuer
experiment. Do not overwrite that owner's source. Preserve all original timing
snapshots and use a fresh actualsourcecopy/hash epoch for the combined design.
No runtime token/model-specific dispatch or production changes are proposed.
