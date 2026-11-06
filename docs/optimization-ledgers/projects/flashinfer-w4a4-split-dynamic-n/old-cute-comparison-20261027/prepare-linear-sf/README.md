# Destination-linear SF prefill screen

Candidate: `flashinfer-prepare-linear-sf-review`, based on0b7. Only canonical scale-factor ownership changes, from source-row lanes to consecutive destination words. Payload copy, full-grid occupancy, PDL, buffer allocation and public API remain unchanged. The existing constexpr SF-storage branch keeps BF16 unaffected.

This revives the previously closed decode-only candidate for a specifically unmeasured prefill question. Current NCU preparation counters show scattered-store traffic, high memory-latency stalls and low DRAM throughput. No performance gain is assumed. GPU0 is reserved for bounded byte checks followed by fixed native-winner C-A-A-C public timing, not AUTO.

Historical source and decode-only evidence: `scripts/prep_linear_sf_experiment`. The current implementation is adapted to the retained shared BF16/blockscaled prepare. No shared-memory transpose or synchronization is added.

## Result: rejected

All 48 graph byte checks passed, including BF16 and its 16-byte-aligned view, FP4 SF16/SF32, FP8 SF32, wide D7168 NV/MX inputs, empty/partial/full routes and PDL on/off. The scale-index inverse reproduces the original canonical destination mapping, preserves zero padding and introduces no new barrier. Both measured arms retain 2,368 preparation CTAs.

The source-bound C–A–A–C screen produced four cells / 1,600 samples. Independent analysis validates 64 collected artifact hashes, 80 fixed-cache hits, 32 actual FC1/FC2 dispatches, matching routes/tactics and unchanged source receipts. Full numbers and repeat drift are in `results.md`; all raw measurements are in `raw-samples.csv`.

V3 NV128 −0.54%; V3 NV16K +0.05%; V3 MXFP8 16K −5.04%; Nemo NV16K −0.23%. The four-cell geometric mean is 0.985388×. MXFP8 controls remain stable (737.3005/738.663us), while both candidate passes are substantially slower (779.749/774.532us); neither NV arm supplies a compensating prefill gain. Reject the policy without another rerun. Reduced destination store fragmentation did not improve the complete pipeline; the screen does not isolate whether additional mapping/source gathers or other effects caused the regression.

The exact owned local/remote candidate source clones were removed only after validating their frozen patches and clean indexes. Persistent native/DSL caches, external data symlink target, helpers, receipts and results remain; see `cleanup.json`. GPU0 is released.
