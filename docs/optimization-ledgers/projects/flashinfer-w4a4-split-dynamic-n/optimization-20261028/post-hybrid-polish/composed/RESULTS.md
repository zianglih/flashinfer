# Provisional pipeline-polish composition

The unchanged frozen SF-prefix, FC2 drain guard, and CLC terminal-ticket patches apply cleanly on `61c2c367009340ca0ed218511ed9382512860f1b`. Only `moe_swap_ab_kernel.py` differs, with +54/-31 unstaged lines. This is interaction qualification, not a retention decision.

- Candidate kernel: `b668b2736ea9770e0ca2d45a91f461601953bfaa20f8f807731a641fa20d93d8`.
- Patch: `678a1e0acdb137fd8101c418dd0ad1eb3e4fdcc58bba81acb8e0c68e226c521f`.
- Control has actual Git HEAD `61249e0b` plus the retained hybrid patch; all 348 pinned source files equal committed `61c2c367`. Candidate has actual Git HEAD `61c2c367` plus the composed patch.
- Scoped pre-commit passed without changing source. Individual frozen sources remain unchanged.

## Qualification

The existing public-API exact replay harness ran configs 0/2/5/11 on B300 GPU6 of `fi-moe-descriptor-recover-1028`, with private compile directories and persistent native caches. H=512, I=384, tokens=385, top-k=2. It covers W4A4, per-token W4A4, MXFP4x8 and MXFP8; one/two CTA; static/CLC; PDL off/on; and 16 changing routing patterns per variant, including empty, reactivated, full tiles and short tails.

- 256 exact source-paired replay records passed. Final outputs and live logical intermediates match; invalid padding values are not asserted.
- All 32 GEMM pairs preserve register/shared/local/stack resources and local/uniform spill counts.
- All eight static FC1 PTX and encoded SASS streams are identical. Ten of sixteen complete static GEMM streams are identical. Changed static FC2 non-NOP sites range from -12 to +3; CLC whole-kernel sites range from -8 to +7. These are static sites, not executed instruction counts.
- All 348 pinned files per source pass postflight. The controller finished and GPU6 was idle at handoff.
- The raw archive contains 296 hash-verified files, including raw PTX, cubins, SASS, resources and exact replay records. Archive SHA256: `0d521c89fe046384d599c3d23d527c07c8be5f870efa4f1e2b7685bdd5a1d2e7`.

No sanitizer or performance timing was run by this gate. The separate SF-prefix qualification retains three one-CTA per-token FC2 uniform-spill growth cases outside this bounded composition matrix; those are not waived by these results. Individual timing screens and the parent-owned provisional full refresh determine retention.

## Replay commands

From this artifact directory, the CPU-only verification is:

```sh
python3 finalize_gate.py
```

`launch.json` and `evidence/gate-controller.json` contain the actual GPU commands. `config.json` binds the interpreter, helpers, source hashes and cache workspaces. `composition-proof.json` binds the three unchanged input patches.
