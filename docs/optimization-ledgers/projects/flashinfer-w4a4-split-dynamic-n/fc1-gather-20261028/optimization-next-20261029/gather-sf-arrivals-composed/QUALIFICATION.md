# Final SF-owner composition qualification

Ready for integration on `b8ccad2d7892b9eb11ed2c9a8470fae7b5e4798b`. Frozen candidate kernel: `77a5495cca8dedef5bccfaacde64a1004b9a7c421175511f12ffef2d996439b3`.

- Fresh candidate: **41 exact cases passed**, 80 matched compiled functions. All419 fetched evidence files hash-verified. Base and candidate source manifests contain514 files; base bytes match Gitb8ccad2, and only the swap kernel differs.
- Resource qualification: no REG, STACK, LOCAL, local-load or local-store site growth against immutable77391 controls. Two inherited synthetic MX FC1 cases remain REG168/STACK160 with20LDL/20STL. All other captured cases have no stack/local sites. Do not claim every synthetic kernel is spill-free.
- PhysicalN16/32/64/128/256, one-/two-CTA, static/CLC and all four swap formats are covered. Actual emitted local barrier counts match17/33/65/129/129. Actual-source enumeration covers194,048 row-block cases. Reverting only the SF count and owner predicate restores the entire b8ccad2 module AST.
- The41 controls/80 captures are reused only after identical514-source and selector/capture-helper checks. No control execution, performance run, retuning or sanitizer was added. The earlier12+3 CAAC rows remain isolated77391 evidence, not measurements of this final composition.
- Scoped pre-commit passed without modifying the frozen source. The single8+/5− delta is `candidate.patch`; review remains unstaged pending parent integration.

For the full benchmark binder, use `evidence/config.json` → `sources.candidate` or identical `evidence/source-candidate.json`. This is the remote manifest object with repo, actualGitHEAD, source hashes, patch hash and persistent workspace path. Its logical source is b8ccad2 plus the SF change; bind it to the final commit only after verifying all514 bytes. `source.json` also provides local base/candidate maps but is not the remote runtime object.

Archive SHA256: `915a5b505c8ddb99d57c92c01e0a47aa416b685827686ab24a996c80b633d55b`.

The direct deployment command exceeded the shell argument limit before execution; the identical payload was transferred in hash-verified chunks. Failure and recovery receipts are preserved. No qualified source or test behavior changed.
