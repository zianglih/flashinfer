# Original-guard epilogue qualification

Frozen kernel `924be385` on2d60 keeps the SF-row algebraic simplification and quantization-parameter sharing while restoring the original per-half valid-row guard for every format. No new condition, tactic, synchronization or memory policy is introduced.

- All96 changing-route exact replays passed across SF16/SF32 gated and Relu2 outputs, plus unscaled per-token BF16 gated/Relu2, with static/CLC and PDL off/on.
- All48 GEMM and10 combine pairs checked. All24 FC2 and8 per-token FC1 streams match retained instructions/resources. The independent audit additionally verifies complete encoded SASS identity for all8 per-token variants.
- No added branch sites, LOCAL/STACK spills or uniform spill/fill sites. Registers decrease by0–2 where changed. Static codegen is not an end-to-end timing claim.
- Existing659777 controls are reused only for exact/codegen after proving its delta to2d60 is exclusively the unexercised W4A16 kernel. Final performance uses fresh2d60 control passes.

| FC1 path | Non-NOP instruction delta | Register delta | Branch-site delta |
|---|---:|---:|---:|
| SF16 gated N64 | -1…-1 | +0…+0 | +0…+0 |
| Per-token gated | +0…+0 | +0…+0 | +0…+0 |
| SF16 Relu2 | -239…-201 | -2…+0 | +0…+0 |
| Per-token Relu2 | +0…+0 | +0…+0 | +0…+0 |
| SF32 gated | -113…-108 | +0…+0 | +0…+0 |
| SF32 Relu2 | -365…-362 | -2…+0 | +0…+0 |

Source proof: `scheduler-source-review.json`; raw gate proof: `scheduler-gate-review.json`; full per-token encoding proof: `scheduler-per-token-encoded-review.json`. Raw520-member archive verified by `evidence-verification.json`. No sanitizer. Earlier attempts and performance results remain immutable in sibling experiment directories.
