# Retained N3U TP8 per-token FC2 and intermediate quantizer diagnostic

Current source c1ac8ce7, unchanged swap482b and quantizer0d8693. Frozen public call, tokens16384, TP8/EP1, route tile256, FC1M128/N256/oneCTA, FC2M256/N256/twoCTA, Ksteps4, sharedCLC=true. Include initial activation quantization, ordinary per-token MSE4over6 recipe, no retune.

Reuse the measured alpha experiment control phases only for the native timeline: about446us exposed intermediate quantization and478us exposed FC2. This profile uses retained source, not the rejected alpha candidate.

NCU metrics then SourceCounters if needed, targeting each stage inside the complete public CUDA Graph with application replay and the original PDL dependency chain. Uncontrolled clocks/caches as in existing diagnostics; benchmark graph performs its original pre-window L2 flush. NCU duration is diagnostic and cannot replace CUPTI E2E data. No isolated kernel launch, historical baseline rerun, numerical oracle change or compiler flag change.

Both actual swap compiled ELFs and actual quantizer cached object device images are retained. Quantizer object capture calls the original loader unchanged, copies the kernels_binary symbol (installed CUDA fatbinary), and asks cuobjdump to extract its device ELF. PTX is present only for an observed fresh compilation, otherwise explicitly unavailable. Resource queries happen before graph profiling.

Prior history: per-token-handoff-475 was a CUPTI audit on an older128-threadK640 quantizer. Current K640 policy is64threads; no same-current N3U per-token FC2/quantizer NCU profile was found. Closed scalar-hoist/spill, SF lane coalescing/interleave and alpha-prefetch candidates are excluded from this investigation.

Attempt0 stopped before profiling because the passive extractor expected a bare ELF rather than a CUDA fatbinary. Its complete logs and helper are retained under the remote attempt0-extractor-fatbin leaf; the correction changes only artifact extraction.
