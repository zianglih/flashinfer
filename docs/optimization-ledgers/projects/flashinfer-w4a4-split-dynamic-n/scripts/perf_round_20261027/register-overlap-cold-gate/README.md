# Exact cold-spill exception for composed register/overlap gate

Production source remains patch `651b8a969484270c8ecd5b396f6f5dc7dab26c1e58d4d19ddf0a5fecc858f3c2` on `f7182d5c`. No register budget, allocator, or epilogue change was made after the original guard stopped FC1 PDL-on before callable launch.

Independent review is `../register-overlap-gate/independent-cold-spill-review.json`, with a reproducible checker beside it. It proves that the single startup STL stores the shared-memory base and the only LDL occurs in the final two-CTA TMEM-deallocation slow wait, dominated by final CTA barrier 1 and warp 0. That path cannot return to the mainloop or epilogue. The physical pool remains exactly 53,760 registers.

`register_guard.py` preserves all original resource checks and permits this single exact PTX/SASS artifact, instruction pair, eight-byte stack frame, and geometry/role identity. All other spills still fail before launch. Raw spill observations remain explicit in the report; an allowed artifact is labeled `exact_reviewed_startup_teardown_pair`, never zero-spill. Nine CPU positive and mutation tests pass (`cpu-validation.json`).

The startup cost is 1,280 bytes of local stores per CTA; the allocator warp reloads at most 128 bytes per slow-wait iteration. The static first-TMEM-read-to-release distance drops from 709/703 to 169 instructions for PDL off/on, respectively. This is mechanism evidence, not a performance result. Full exact/resource coverage and paired timing remain required.

Keep the original strict helper and failed smoke artifacts immutable. Deploy this directory separately and reuse source-matched complete control results. Do not broaden the allowance for new spills without another independent review.
