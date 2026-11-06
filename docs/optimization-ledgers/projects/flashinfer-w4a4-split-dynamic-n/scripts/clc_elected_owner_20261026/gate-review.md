# Independent gate coverage review

Reviewed the prepared `gate/probe_elected_owner.py`, `gate/run_pair_gate.py`, and `gate/validate.py` before launch.

The gate uses the public wrapper with explicit six-field `True/True` scheduler tactics on both sources, and records actual compiled CLC/prefetch/K-stage settings. Eight cases cover all four requested formats with intended one-/two-CTA geometry, narrow and wide N, M512 channel grouping, both activation contracts, PDL off/on, and inline/dedicated epilogues. Four graph replays per PDL mode change balanced → skewed → no-local-work → reactivated routes, exercising ordinary, padded, terminal and persistent scheduling. Source-paired input/output hashes plus within-source zero-tolerance checks provide 64 exact replays per source.

Source hashes are verified before/after processes; no native AUTO or latency claim is made. Codegen capture compares 32 FC1/FC2 × PDL core pairs and checks storage/stages/UMMA commits and absence of spills. This is sufficient bounded initial coverage for the scheduler-only change, while remaining narrower than sanitizer or exhaustive routing coverage.

One hardening request sent to the harness owner: assert actual compiled `cta_group_size` matches each config's requested group, both FC phases and both PDL modes are present for each config, and each format's actual CTA set is `{1,2}`. Existing control/candidate equality alone does not prove the requested geometry was admitted. No production changes or GPU work were performed by this review.
