# Empty FC1 bulk drain: independent source/native review

The bounded source and native-code checks pass. This candidate removes only the empty FC1 `cp_async_bulk_commit_group` / `cp_async_bulk_wait_group(0, read=True)` conditional. Removing that exact AST node from safe-FC2 control604935 reproduces the complete candidate b1d82a module. The21 frozen input hashes, sealed helper, runner/preflight, base28a source and control package agree with the completed FC1 cohort. Prospective production sourcee9a725 is computed from the one-file replacement; it has not been installed or GPU-tested by this audit.

| Geometry | Matched control SASS | Candidate SASS | Text bytes control→candidate | REG | Stack/locals | MMA |
|---|---:|---:|---|---:|---|---:|
| M256/N128/C2 | 5776 | 5768 | 92416→92288 | 128 | 0 /0 | 16 |
| M256/N64/C2 | 5448 | 5440 | 87168→87040 | 128 | 0 /0 | 16 |

Each geometry loses exactly one epilogue UTMACMDFLUSH, one DEPBAR, one branch and five addressed NOPs. N128 also substitutes one IADD3 with VIADD; this small scheduling change is preserved in the report. Transform decode opcode counts, matrix instructions, register redistribution, named-barrier and arrival counts are unchanged. All other actual producer/dispatch drains retain identical bodies and PCs. Source, package/native/Torch identities and fake descriptor/config/compile options match the controls; each capture's before/after source and artifact snapshots agree. No local instruction or declaration is introduced.

The current W4A16 epilogue issues ordinary BF16 stores. FC1's CopyUniversalOp stores are candidate epilogue430–432 and504–512; its transpose uses TMEM operations, which do not produce a bulk-copy group. The constructor fixes BF16, non-UBULK FC2 and no in-kernel reduction at69–80. The inherited FC2 STG selection remains vendor epilogue_refactor1964–1977/3126–3148 and ordinary store2932–2978. Real transport bulk producers/drains belong to separate dispatch warps, including token_comm1113–1114,1415–1416,1460–1461. This empty-group proof does not cover vendor quantized FC1/TMA or UBULK FC2 paths.

The ordinary-store publication order remains explicit:

- N128 control: named barrier11e40 → CTA/GPU/ERRBAR/CGAERRBAR11f90–11fc0 → release REDG11fd0. Candidate: named barrier11e20 → same fence sequence11f60–11f90 → release REDG11fa0.
- N64 control: named barrier10950 → fences10aa0–10ad0 → release REDG10ae0. Candidate: named barrier10930 → fences10a70–10aa0 → release REDG10ab0.

The barrier remains ID1/count128. Source retains all TMEM waits/releases, phase-aware tracker update and publication, including next-work consumption before prior-tile signaling. Flag_batch110–119 reaches the release-GPU atomic; the consumer uses acquire-GPU loads. Native instruction ordering corroborates these retained source edges; it does not establish a numerical or performance result.

Evidence: `preparation-review.json` and `codegen-comparison.json`, plus the two complete candidate capture folders and the exact28a controls from the preceding FC1 cohort. No source, native package, remote environment or GPU state was changed by this read-only review. Code quality permits a later numerical/lifecycle gate; no promotion or end-to-end gain is claimed.
