# Preserve original comments and documentation

Retained and pushed `2995bfda8338ca6ae623fbc2657d44e35e665627` on `54f5c682`. Restore still-accurate original wording in benchmark/test descriptions, tactic documentation, wrapper examples, quantizer comments and combine documentation. Keep the changed operand/layout/scheduler/API descriptions where upstream prose no longer applies. Restore the original copyright year; all existing headers match upstream.

`proof.json` and `source.patch` bind the twelve-file change. Executable ASTs match after removing only actual docstrings and normalizing source line numbers; type comments and ignore tags remain equal. Scoped pre-commit passes. No GPU or benchmark rerun. The overall upstream PR diff is 57 lines smaller.

Per-component notes are in `kernel/`, `host/`, `benchmark/` and `quantizer/`. Publication changes only the current diff-size table. The review clone was advanced clean to the pushed commit and removed; canonical source, historical scripts and evidence remain.
