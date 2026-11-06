# MMA readiness qualification boundary

Candidate source remains `e9088366`, base `49c91adf`, with only the carried operand-readiness TEST change. Root approved bounded GPU4 exact/native qualification after source and lifetime review. No performance run is authorized yet.

The isolated gate uses eight matched control/candidate pairs (16 calls): narrow ordinary W4A8, wide two-CTA MXFP8 with a partial K tile, native CLC one/two CTA SF16/K96, per-token wide `channel_tiles=2`, long-K two-CTA MXFP4x8, and two separate one-stage ring cases. The last two change only the existing private constructor `num_stages` argument to 1 in both arms. They are correctness diagnostics, not native selected tactics. All calls reuse the existing zero-tolerance numerical oracle and compiler/cache settings.

The candidate prelaunch guard joins the actual same-case control capture and checks all recorded stage/CTA/CLC/PDL geometry plus native resources. It allows no new local memory or register growth. The chosen wide SF16 channel-two case has no inherited local-memory allowance; any failure stops the gate and is preserved. Native TEST placement, fallback waits, per-role instruction growth and all resource changes still require review before timing.

W4 remains outside this change. Its current raw readiness query already has a substantial independent decode/store window; a direct TEST substitution there is not proposed. PTX TRY may suspend, but native independent-issue behavior must be measured rather than inferred from the mnemonic alone. TEST is required here to guarantee that a speculative depth-one query cannot suspend before the current release.
