V3 helper-isolated election (`96cfbfbe7c2c779fcdaf9e46ce76f19d2989d879903f5037c8eefeb152925dc8`) passed the same source-bound gate against retained9b4721b0, reusing completed controls and unchanged full720 host policy/probe.

- 64 exact graph replays per source,32 core pairs; four formats each cover actual1/2CTA, FC1/FC2 and PDLoff/on. Empty/skewed/padded/reactivated and more-than-resident routing remain covered.
- No local memory/stack/spill; pipeline geometry, stages, shared storage and UMMA commit counts unchanged. Register delta−5…+4.
- Static SASS delta−7…+32 per kernel, +197 overall (v2 was+653). All32 query neighborhoods remove v2's ELECT/BRA.U.ANY peeling; whole-kernel BRA.U.ANY counts match controls. Existing epilogue BRA.U.ANY instructions remain in some variants. Ordinary BSSY-pair delta is0 or1; reconvergent-pair delta0. PTX elect.sync is one site lower; other recorded PTX site counts unchanged.
- Representative FC1/PDL1 static counts: config0 1233→1240, config1 1557→1563, config5 6379→6411. These describe codegen, not dynamic instruction work or performance.
- `validation-v3.json` matches remote `gate-v3-validation.json`; all316 evidence files pass `artifact-manifest.json`. Full opcode/query neighborhoods are in `sass-opcodes-v3.json`.

Remote v2 source, gate, and timing remain frozen. This bounded gate makes no exhaustive correctness, sanitizer, or retention claim.
