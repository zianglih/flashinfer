# No-peek reference numerics: saved audit passed

Source `02a1db353c03544e14c2a7f0d2998ed5e6506990037f4cabc92562d305983f7c`
completed all five original reference-only jobs. The independent audit calls
`fresh_session.validate_job_outputs` once per job and checks 59 summary evidence
files and 107 direct hashes. It performs no GPU/native execution, live cache
inspection, or recursive baseline validation.

| Geometry / EP | Rank-tests | Compiled objects |
|---|---:|---:|
| M256/N64/C2, EP1 | 2 | 8 |
| M256/N64/C2, EP2 | 4 | 16 |
| M256/N128/C2, EP2 | 4 | 16 |
| M128/N64/C1, EP2 | 4 | 16 |
| M128/N64/C2, EP2 | 4 | 16 |
| Total | 18 | 72 |

All 54 setup/call/teardown reports pass. All 72 observed objects have raw depth5,
REG96, 640 threads, two decode groups, register pool61440 and local0. Exact loaded
source/helper aliases, commands, source before/after and immediate native
predecessors agree. All five native before/after files are byte-identical
`055618ecfc9f530f058009845beb7ee099d0cf4215aa3e59f916d0f3104995b8`,
including all 22 entries and the JIT log.

Both return modes complete the unchanged reference oracles: ordinary empty/refill,
H288/I448/M257 partial K, exact scale/routing, and stable/changed graph assertions.
The successful bodies imply 18 empty/refill sequences, 18 exact scale/routing cases,
54 stable graph comparisons and 18 changed graph comparisons; these are not separate
runtime replay counters. No raw7 long-K or fitter allocation coverage is claimed.

Original launcher84539 exits0 with all five ordered completion paths and exact UUID
`FRESH_MODERN640_VALIDATION_56f85a6219344e54bb11196005dbab9d_EXIT=0`.
Final fetch78118 and job3 fetch94508 close0. Summary SHA
`0868be3758eddbf76e5e5afe941a580ac2ce60ddb5dfc05bcb2fa65e376ccad9`;
launcher SHA `cd0c5c7c2200b434d432ec3d1af285308b00a614590304e84e88a0964eb30df1`.
Numeric map f269b580 and preflight0fc85c1e remain exact.

One frozen prose discrepancy is retained: the first manifest's
`native_cache_session_kind` says completed register AUTO, while its exact
`native_predecessor` and `cache_policy` correctly bind completed raw7 AUTO plus
restoration. The actual chain is correct. No frozen byte or validator was changed.
The retained performance baseline remains register574cf, separate from this
immediate native predecessor.

[Audit JSON](audit.json), SHA
`62ecd4b43b4fb154bf1ae681f0094c24acc041183fabd1f3656e66e21ea74878`,
contains all direct evidence hashes. [Original saved-validator output](validation-check.log)
has SHA `e256582866d99a35e5eba1738d1cedc9061395c845e4bdbbec19058d64223429`.
AUTO performance and retention are separate; this numerical audit adds no launch gate.
