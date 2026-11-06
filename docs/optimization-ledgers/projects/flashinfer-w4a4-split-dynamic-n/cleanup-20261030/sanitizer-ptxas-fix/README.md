# Preserve native PTXAS settings during manual TMEM instrumentation

The sanitizer previously rejected any preexisting `--ptxas-options`, which prevented W4A16 FC1 gather compilation with its retained register limit. The script now shell-parses the compile options, merges existing PTXAS payloads in their original order, appends `-g-tmem-access-check`, and safely serializes one combined option. It does not hardcode the register limit or modify kernels. The existing O3 collision guard and `--keep-ptx` remain intact.

Validation: 15 CPU cases passed using the exact option registry and parser AST from the installed CuTe DSL 4.8 compiler source (SHA256 `26a940ac92440a63561411b0818c3f88da363b1247ab54fcb5572d242d382c3b`). Covers the actual source-traced launcher option, quoted/spaced/equals forms, multiple PTXAS payloads, an unrelated flag and quoted dump path, unchanged non-TMEM-instrumented modes, and O3 collision rejection. Parser code executes locally without compiler, MLIR or GPU imports. Scoped pre-commit, py_compile and diff-check passed.

No sanitizer or GPU execution. The production kernel files and performance snapshot at `326c4a79` are unchanged. Changes remain unstaged for root review.
