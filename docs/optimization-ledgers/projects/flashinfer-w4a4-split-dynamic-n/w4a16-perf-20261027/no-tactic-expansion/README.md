# Remove W4A16 CLC tactic expansion

User explicitly rejected doubling tactics on performance grounds. Restore the exact1496 W4A16 tactic schema, list and FC1-only scheduling heuristic; retain shared preparation, scheduler metadata synchronization cleanup, static weight extents and the SM-budget cache key. The unpublished a2beb1f1 commit is superseded; no46-tactic change has been pushed.

Use the original23 native winners for same-GPU source-paired timing. Historical46-tactic results remain in composed/ and composed-recheck/ and must not be attributed to this candidate.

Final commit: `0b7fe90151340d4fca6a5ec41a91019dde743819`, pushed and read back from PR #7290. The final source passes 50 existing tests and 72 targeted checks; identical-cache CAAC is neutral at 1.0002x overall. See `retention.json`, `gate-validation.json`, `publication.json` and `../composed23/speedups.md`. All four completed local source copies were removed; durable experiment artifacts and persistent GPU caches remain.
