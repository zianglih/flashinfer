Repaired elected-owner gate passed for candidate patch `d8ca478d88600876d317374b3f07b873a30f4dd550bd7665a8bad88855069d20` against retained kernel `9b4721b08057d0a488c1f0236467acb75c48cd00`. Host policy remained full720 with explicit six-field True/True CLC tactics.

- 64 source-paired exact graph replays per source, 32 paired core compilations. Four formats each cover actual one- and two-CTA groups, both FC phases and PDL off/on; cases include live work beyond resident capacity, skewed routing, empty local work, padded capacity, and reactivated local work.
- Original completed controls were reused on the same GPUs with the identical frozen probe. Only the repaired candidate ran again. Repaired source and private DSL cache receipts are in `evidence-v2/deploy-candidate-v2.json`; native C++ sources/cache remain shared and unchanged.
- No spills, local memory, or stack. Shared-memory storage, pipeline stages, MMA/CTA geometry and UMMA commit counts match. Register deltas range from -5 to +4.
- Static SASS instruction counts increase by 7 to 54 per kernel (653 total across 32 variants). Each variant removes two static PTX election sites; other recorded PTX site counts do not change. These counts do not measure dynamic work or latency. No performance or retention claim follows from this gate.
- Local validation exactly matches remote `gate-validation.json`. `evidence-v2/artifact-manifest.json` verifies all 316 collected files. This is a bounded exact replay/codegen gate, not an exhaustive correctness or sanitizer result.

The earlier candidate `5da2bd3f` failed IR dominance verification and remains documented separately in `failure-v1.md`. The one-line repaired lane predicate fixed the compile boundary without changing the intended owner protocol.
