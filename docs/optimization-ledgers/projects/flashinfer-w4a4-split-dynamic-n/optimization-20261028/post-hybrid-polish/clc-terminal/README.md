# CLC terminal-ticket peeling

Base: committed `61c2c367009340ca0ed218511ed9382512860f1b`.

The CLC scheduler currently rechecks terminal validity inside each iteration,
including its metadata acquire, cancel request, payload defaults and response
wait. The candidate loops only over valid physical tickets and publishes the
single terminal metadata entry after that loop.

- Valid tickets outside the live routed extent still request and consume the
  next CLC ticket. They are not mistaken for termination.
- Routed tickets acquire their existing info slot before the cancel request,
  then publish the same three fields with the same elected release.
- Both CTAs preserve their existing local metadata publication and response
  waits. Only rank zero issues cancel requests and the final producer tail.
- Terminal `(-1, 0, 0)` is published exactly once, including an initially empty
  scheduler, with the original acquire/commit/advance and IKET range.
- No pipeline instances, quorums, queue depths, atomics, PDL edges, tactics or
  static-scheduler source are changed.

`prove_protocol.py` compares ordered abstract events, payloads and pipeline
state advances for 20,470 combinations of routed/padded ticket sequences,
rank and ring depth. It also verifies that all source outside the scheduler
block is byte-identical. This is not a substitute for the paired GPU gate.

The control is the existing remote `61249` checkout plus its retained hybrid
patch. All 348 source hashes match committed `61c2`; that effective source
binding is separate from its actual Git HEAD. The candidate checkout has real
HEAD `61c2` and only the new unstaged scheduler patch.

The reused public-wrapper probe selects configs 0, 2, 5 and 11 at H512/I384:
NVFP4, per-token NVFP4, MXFP8 and MXFP4x8; one/two CTA; static/CLC; PDL off/on.
Its 16 changing route patterns cover balanced, skewed, empty, reactivated,
full/partial tiles and rows around 16/32/64. Final outputs and logical live
FC1/FC2/SF/per-token values are compared bit-exactly against the paired source
and across scheduler/PDL choices. Invalid padding values are not asserted.
The gate uses private compiler working directories and existing native cache
targets. Sanitizer and timing are not part of this gate.
