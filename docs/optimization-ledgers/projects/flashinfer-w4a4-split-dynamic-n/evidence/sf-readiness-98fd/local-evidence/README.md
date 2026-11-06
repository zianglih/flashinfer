# Independent SF readiness, compact broadcast, concurrent TMA issuers

Fresh actual98fd clone `flashinfer-sf-readiness-review`, two unstagedfiles.
Composes frozen compact a958760e and existing-warp issue e2c7089c. Eligible only
NVFP4 generatedFP4 gatedFC1N16; all other paths retain98fd numerical/geometry.
OneCTA M128/trueB-C16,4operandstages,2SFslots,320threads unchanged from compact.

- Warp0 issues A,warp2 issues B. Each independently waits payload empty and
  atomically announces its own byte count before TMA; full expected arrivals2.
  Weight32768B andactivation4096B sum36864B perstage.
- Warp1 issues SFA on a separatefull barrier, expectedarrival1/4096B. The
  existing128 SFproducer threads all firstwait ab.empty; SFA's unused private
  emptyhalf is never consulted. SFA andSFB have identical sharedsource lifetime.
- Publisher waits only SFAfull andSFBcp.asyncfull, then acquires TMEMSFempty,
  CPs both scales and issues two completion notifications: SFfull for MMA,
  sharedab.empty for source reuse. Both are actual tcgen05.commit completion;
  sourcebuffers cannot recycle after merely issuing CP.
- MMA waits publishedSF andjointA/B payload, fences beforeTCGENoperations,
  executes unchanged nativeMMA and releases payload+TMEMSF afterfinaluse.
- Four-stage source state andtwo-stage TMEMstate stayindependent and advance
  persistently acrossalltiles/K. Producer tail drains sharedSFempty through
  existingabtail; warp0 drains payloadempties withoutarming unusedtwoarrival
  phases. No independent SFAempty drain is required because allSFAproducers
  wait exactly the sameabempty barrier asSFB andabtailcoversboth sources.

Added SFA pipeline metadata64B; no additional operand buffers. Existing
producer/MMA/epilogue warp assignments and128TMEMcolumn proof preserved.
Explicit tcgen05 completion follows currentPTX cross-warp nonpipelined semantics.

Gate: reuse exact saved98fd seven-case oracle, runcandidate only; then native
T32/T128N16 ABA/BAB phase/fullchain onB200-92GPU3 with10warmup100coldL2graphCUPTI,
all100samples and exactpre/post. Source/data/nativecache hashes checked. No
primarybenchmark or baseline rerun, no broadnumerical/sanitizers beforegain.
