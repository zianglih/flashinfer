# W4 raw-stage release at the last shared-memory read

Base: `b13963b0cc8409aeb92048b9ec7cf3be18f0a57c`; candidate is unstaged in the existing W4 raw-release review copy. R1 source and its patch remain frozen in `../w4a16-raw-release-6be/` and R1 is not retained.

Scale fragments have already been copied into registers before the constexpr weight-fragment loop. At its final synchronous `autovec_copy` from raw shared memory to registers, all shared input reads are complete. Release the raw pipeline's original state immediately, then advance that state and preserve its existing readiness peek. This removes the cloned state and can overlap arrival processing with the final fragment's register-only decode. The decoded TMEM/SMEM destination does not alias the raw stage; its store fence and publication commit remain unchanged.

The unchanged PipelineTmaAsync release retains its signaling-thread mask and multicast arrival count. No new barrier, extra synchronization, stage count, register quota, tactic, API or arithmetic contract is introduced. Code generation must verify that the final LDS precedes raw arrival, and decoded publication follows the stores. In particular, recheck the uniform/vector lowering changes seen for TP V3 FC2 in R1.

Qualification: four paired frozen-native FC1/FC2 compile captures; require identical loaded register/local/thread/shared attributes before 33 existing exact cases. Only then run the same 16-cell, fixed-tactic C-A-A-C strict-CUPTI screen with source/route/runtime guards and NVML telemetry. Keep diagnostics with keep-PTX/keep-CUBIN separate from normal-option performance. No sanitizer, retuning or external baseline rerun.
