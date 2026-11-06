# Plain decoded-slot producer acquisition

Base b13963b0. Remove only cached `trans2mma_pipeline.producer_try_acquire` lookahead and its carried status from the W4 transform warpgroup. Use the existing plain `producer_acquire(state)` at the original acquisition point. Preserve raw-input `consumer_try_wait`, original cloned raw-state release after decoded stores, decoded commit, all resets/advances, barriers, stages, quotas, tactics, math, PDL and API.

The cached decoded-slot status is only a readiness hint; a plain producer acquire waits for exactly the same stage and phase. This tests simpler control/state lifetimes without repeating the rejected early raw-release schedule. R1/R2 raw-release results remain in their separate folders. Ledger search found no prior experiment removing this specific producer lookahead; the earlier retained W4 MMA-consumer plain wait explicitly preserved it.

Qualification: eight paired native FC1/FC2 captures with identical runtime resources required before the same33 existing exact cases. If plausible, run the same16-cell fixed-winner C-A-A-C strict-CUPTI/NVML screen on GPUs0/3. Diagnostic keep-PTX/CUBIN is separate from normal performance compilation. No sanitizer, retuning or new tests.
