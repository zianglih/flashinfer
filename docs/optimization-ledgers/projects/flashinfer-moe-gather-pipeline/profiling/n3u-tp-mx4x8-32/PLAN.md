# N3U TP8 MXFP4x8, 32 tokens

Read-only diagnosis on retained `49c91adf47d30fc2049c76cbaf34d0ccf3291434`; no source, tactic, clock or baseline changes. GPU4 on `fi-gather-pipeline-1030`, C2/ziangli, is exclusively assigned for these diagnostics. Its UUID is `GPU-bab88130-5692-5702-ff8d-8f2f966ed945`.

The immutable timing/profiling source is the existing `candidate-fc1-integer-store-perf` snapshot, honestly labeled bf072 plus swap kernel `482b636a…`. `retained-source-equivalence.json` verifies all 13,245 inventory files against committed49c. The persistent C++ cache stays in its existing location; release library/Ninja hashes and dry-run no-op are verified before and after collection.

## Reuse native timing, collect only missing counters

- The just-completed integer-store remaining campaign already has two source-identical candidate passes at this exact point. `analyze_cupti.py` independently replays all200 strict native CUPTI intervals, checks phase/route/source hashes and recomputes overlap-aware extensions. It writes `native-cupti.json`; no new timing comparison is needed.
- Historical374's gap audit had an exact-case component row (FC1 exposed62.65us, FC245.65us, combine6.92us), but the bounded current/old profiling and ledger search found no matching native NCU/PC capture. Saved N3U native profiles cover W4A4/W4A16 at16K instead. Per-token32 work and rejected SF/pipeline variants are separate contracts and are not reopened.
- Historical TRT115.873us versus retained125.569us is the requested −7.722% ranking signal. It is reused evidence, not a fresh source-paired or same-run backend comparison.

Frozen choice: routeN16; FC1/FC2 `(M128,N16),(1,1),False`; K steps `(8,4)`; sharedCLC false. The saved route has704 assignments across385 nonempty experts, maximum seven tokens per expert. Those facts motivate sparse-work/startup attribution but do not justify a new shape policy.

NCU runs FC1/FC2 metrics and SourceCounters serially on GPU4, one selected kernel per application replay, using the public functional benchmark and its existing profile entry point. Native returned CuTe ELF/PTX/SASS and driver attributes are saved before launching each compiled callable. No iKET/source instrumentation, compiler option modification, event fallback, retuning, or cache disabling is introduced. NCU clock/cache control is `none`; profiler times will not replace CUPTI values or support a performance claim.

The root driver retains full source checks at collection boundaries, a scoped source check in each app replay, frozen route/tactic/cache assertions and unchanged register policies. Geometry receipts include stages, accumulator storage, CLC and overlap state. The actual instruction PCs will be mapped only to captured native images.

## Preserved preparation failure

The first attempt stopped before the first owned FC1 launch because `compiled.__cubin__` named a file in a dump directory that had not been created. Its controller/log/receipt remain in the top-level remote folder. `r1/` differs only by explicitly creating that directory, as the already-successful qualification harness does. Native source, compiler flags and caches remain unchanged; the failure is not a numerical result.
