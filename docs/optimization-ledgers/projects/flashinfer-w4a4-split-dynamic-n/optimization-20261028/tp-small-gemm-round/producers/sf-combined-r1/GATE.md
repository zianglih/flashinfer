# Combined SF epilogue qualification

Candidate `9cb4cc76` on retained `2d60c885` combines the SF-row algebraic simplification with common quantization-parameter extraction and the half-local tuple scope fix. Source, patch and pre-commit receipts are in this directory.

- All96 changing-route exact replays passed, covering SF16 gated/Relu2, SF32 gated/Relu2 and unscaled per-token BF16 gated/Relu2, each with static/CLC scheduling and PDL off/on.
- All48 GEMM and10 combine codegen pairs were checked. All24 FC2 and10 combine instruction streams/resources are unchanged;4 gated per-token FC1 streams are also unchanged.
- No LOCAL/STACK spills or uniform spill/fill growth. These are compile/codegen observations, not a timing claim.
- Controls are reused from659777 because its only delta to2d60 is the unexercised W4A16 kernel. Original control source/helper receipts remain unchanged; `evidence/reuse-control.json` binds them.

| FC1 path | Non-NOP instruction delta | Register delta | Branch-site delta |
|---|---:|---:|---:|
| SF16 gated N64 | -1…-1 | +0…+0 | +0…+0 |
| Per-token gated | +0…+0 | +0…+0 | +0…+0 |
| SF16 Relu2 | -207…-177 | -6…-2 | +16…+16 |
| Per-token Relu2 | +35…+59 | +0…+4 | +16…+16 |
| SF32 gated | -113…-108 | +0…+0 | +0…+0 |
| SF32 Relu2 | -334…-319 | -4…+0 | +16…+16 |

The outer valid-row guard adds16 static branch sites on Relu2 paths, including the per-token path. The performance screen must include that changed path; it is not an unchanged sanity control. All61 synchronization/fence/PDL AST calls are unchanged.

The earlier pure-params SF16 Relu2 compile failure is retained separately in `../sf-params-r1/supplement`; it is resolved by this scope fix, without changing quantization arithmetic. No sanitizer was run.

Raw archive and521 checked member hashes: `evidence-verification.json`. Independent source/raw audit: `scheduler-source-review.json`, `scheduler-gate-review.json`. Final timing/retention remains pending.
