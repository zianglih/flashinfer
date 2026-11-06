# Held static vector-copy rounds

Unapplied follow-up to fused BF16 activation staging. The active first staging
AUTO remains unchanged. No new public field, Mega kernel change, GPU launch or
native compilation is part of this preparation.

The first staging candidate's actual H7168/int32 capture uses 18 registers,
128 threads and no shared/local memory. Its vector accesses are correctly
`LDG.E.128` / `STG.E.128`, but SASS addresses `0x1f0–0x2b0` retain a runtime
backedge. Each of seven rounds loads one vector and consumes it in the store
before taking that backedge. The exact capture is
`logs/cu132-recovery0909d-bf16-staging-direct-validation-001/staging/stage-native/`:
cubin `71b54067`, PTX `90171e2f`, SASS `fe3e7230`.

`source.patch` replaces only that copy loop with compile-time complete rounds
and a compile-time-selected remainder. The remainder has one necessary lane
predicate. H7168 has seven complete rounds and no remainder; H288 has only
36 remainder vectors. This exposes independent loads/stores to the compiler;
native scheduling and performance are still unknown. Routing copies, signed
ID conversion, empty/tail semantics, dynamic shapes and host caching stay
unchanged. BF16 expert weights remain in the existing RMEM/TMEM path; this
kernel copies input activations only.

`source-proof.json` checks whole-module AST restoration and exact, once-only
vector-index coverage for twelve widths, including H7200 with seven full
rounds plus four remainder vectors. These are source checks, not a CuTe or GPU
validation claim. Patch `baaef60b` changes staging kernel `d7dde1c9` to
`a262e44b`; no full runtime source has been selected.

If selected after the initial staging AUTO completes, reuse the same nine
copy/graph cases and existing H7168 native-object capture. Add H7200 to the
existing vector-loop test parametrization to execute full rounds and a tail
together; reuse its exact Torch bit oracle. Keep the complete AUTO13/100
comparison against the then-retained Mega result, with 8–4096 deciding
retention. Do not start an additional baseline or profiling cohort for this
held patch. More static code/register pressure is a tradeoff to inspect.
