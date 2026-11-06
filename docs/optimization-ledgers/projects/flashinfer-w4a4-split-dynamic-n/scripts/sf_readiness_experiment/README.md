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

## Completed bounded gate

All seven candidate cases match the frozen control oracle. All FC1 output/SF,
FC2 output and full final bytes match before and after native measurements.
The 36 ordered arms retain all 3,600 samples (10 warmups, 100 cold-L2
CUDA-graph/CUPTI samples per arm).

| Tokens | Full control medians (us) | Full candidate medians (us) | Control/candidate | FC1 ratio | Unchanged FC2 ratio |
|---:|---|---|---:|---:|---:|
|32|107.8400 / 107.7600 / 107.7765|107.9840 / 108.2880 / 108.8325|0.994690|0.995486|1.000298|
|128|144.4325 / 144.0645 / 144.1920|144.6080 / 145.0880 / 145.5520|0.994124|0.994513|1.000002|

Do not retain this particular schedule. This comparison establishes that the
correctly decoupled 320-thread pipeline has no gain in these two cases; it does
not rule out reducing producer coordination or SF publication overhead.
Candidate resources: 50 registers/thread, 173,056 B dynamic SMEM, 128 TMEM
columns, no local memory, one driver-reported resident CTA/SM. Control resources:
64 registers, 197,504 B SMEM, 128 TMEM columns, no local memory, one CTA/SM.
The additional 64 B metadata changes the aligned SMEM allocation by 128 B
relative to the earlier compact broadcast variant.

[Complete summary](../../evidence/sf-readiness-98fd/summary.json), archive SHA256
`26d0edd6457485c99154c03934a361912b884f51257775759d0551bb213ac358`.
Actual candidate core SHA256
`0f570a27aec49f767b414b7e4fcc163433598b5d344cc8b86fb4114d9802f9d1`.
No AUTO campaign, broad dtype validation or sanitizers were run for this negative
gate. The independent source remains unstaged; production is unchanged.
