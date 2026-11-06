# Compile out disabled PDL primitives

Prepared as a separate patch only; none of the four measured review copies or
canonical source was modified. `pdl-compile-time-guard.patch` applies to99f4.

The common `griddepcontrol_wait()` and `griddepcontrol_launch_dependents()`
helpers emit inline PTX unconditionally. The swap-AB kernel currently calls one
startup wait and one signal even when `enable_pdl=False`. These instructions
have no useful dependency to enforce on that ordinary stream launch. Guard the
startup wait/role predicate and both launch boundaries with the existing
compile-time `enable_pdl`. Also explicitly gate the three delayed role waits,
so every call respects the same behavioral knob even for a private constructor
whose prefetch flag differs from enable_pdl.

`verify_pdl_guard.py` specializes both source ASTs for all eight combinations of
enable_pdl, prefetch_weights_before_wait and the two signal boundaries. All four
PDL-on kernel bodies are identical after compile-time specialization. All four
PDL-off bodies contain zero dependency wait/signal calls. The original public
PDL-off case contained two call sites. Barrier, TMEM, operand, metadata and
output lifetimes are unchanged. Existing useful comments and license remain.

This is instruction-sanity cleanup, with no speedup claim. Ordinary launches
already respect stream dependencies, and public wrappers set
prefetch_weights_before_wait=enable_pdl; disabled PDL therefore does not expose
payload before its producer completes. The descriptor screen runs with PDL on,
so this should not change its measured specialization after compilation, but
that must be checked in generated code. The gate should assert zero
`griddepcontrol` PTX for disabled variants and compare normalized PDL-on PTX or
SASS before retaining the cleanup. Exact graph replay qualification already
covers both modes. No new API or tactic is introduced.

Checks completed: Python AST parsing, repository Ruff formatting, clean apply
against99f4, and the reproducible eight-case AST proof. Compiler and GPU checks
remain pending. The proof receipt records the exact source/patch hashes.
