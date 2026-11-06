# FC1 gather host and harness review

Reviewed the frozen host/kernel contract at d35fcfda + R1 kernel b0c061b7. The host source remains b0575e7f; only FC1 opts into gather. The core, shared prepare, W4A16 and public API/tactic contract are unchanged.

- The original activation/SF pointers reach FC1 with the original map. FC1 does not allocate or launch standalone prepare. Its weight/scheduler metadata cannot run ahead of routing: all roles acquire the ancestor before reading num_tiles. The retained activation control warp republishes completed routing for FC2; FC2 still overlaps independent weights before its payload wait.
- Gather CLC metadata consumers are 320 leader / 288 follower threads: weight 32 + gather 128 + epilogue 128 + leader MMA 32. The dormant activation warp is excluded. Initial TMEM retrieval and final join include all 384 threads. SF completion separately counts 128 gather arrivals per CTA; the existing operand-empty protocol protects reuse.
- The source-only partial evaluator in check_fc2_specialization.py reduces kernel and load_weight_stage exactly to the d35 AST for gather_input=False, apart from the unused None parameter. This is an intended-source proof, not an emitted-code claim. Runtime-first Boolean role guards still require compilation to establish dead-body pruning; they must not trace None-only operands in the opposite specialization.

## Harness

The source-bound observer enforces the complete requested backend set and routing identities. The runner preserves public functional API, fixed managed-cache winners, no autotuning, 10 warmups and 100 cold-L2 CUPTI samples per phase, exact raw medians, zero timer fallback, unchanged winner cache, per-phase source verification, and isolated compiler CWD. C/A/A/C is same-device and the W4A16 arm remains a negative control. External baselines are not measured again. Four token counts are 8, 256, 4096, 16384; this is not the full token matrix.

Two findings were corrected before test dispatch: all assigned GPUs are preflighted before launching any process and every Popen is recorded immediately; the launch checks clean d35 control HEAD. Deployment was already completed, so the latter prelaunch check binds its original fresh control hashes. The runner records GPU UUID before and after each phase and asserts the initial identity before each phase. The final after-phase UUID is recorded for audit, not separately asserted by the current runner.

The 32 existing selected tests are counted exactly from collection/JUnit, with no skips allowed and source checks before/after. This is not a new exhaustive all-tactic/PDL/CLC matrix. The new gather branch still needs the GPU tests; no sanitizer was requested. No GPU jobs or production edits were performed for this review.
