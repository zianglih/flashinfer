# Gate provenance

The unchanged library control passed 24 exact replays under helper r1. Candidate attempts r1 and r2 failed in host provenance checks before kernel compilation: tuple/list GPU capability serialization, then the pre-fix versus final benchmark file SHA. Both failures are preserved.

Helper r2 only normalizes capability to a JSON list. Helper r3 permits the exact unused benchmark hash pair 8078d09b… → cf5cd581… alongside the intended core delta, and asserts the benchmark was not imported. The saved inputs, public wrapper calls, compilation, graph capture and replay bodies are unchanged; the control bundle and all tensor identities remain exact. No numerical/kernel assertion was weakened. R3 reuses the completed control rather than replaying it.

The later performance bracket uses current-nemo-mx-d97923eab9a0 as control, whose benchmark bytes exactly equal the candidate. Thus only the intended core file differs during timing. Both deployed sources remain at frozen0b7; local candidate was advanced to pushed benchmark-only d02 with identical kernel bytes/diff, recorded separately.

The bounded gate and fixed screen use static scheduler selections. CLC, empty-route reuse and inline epilogue coverage will be added only if the measured result warrants retention, as requested by the parent.
