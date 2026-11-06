# W4A16 implementation cleanup

Performance experiments are paused at user request. This cleanup starts at
`dde36ec13`, retained source `03da8ead`, and removes 869 net implementation lines
across ten owned files. The public API, supported configurations, prepared-weight
layout, five warpgroups with two decoders, and shared token communication remain.
No vendored, shared W4A4, benchmark or test source changes are included.

- Scheduler: use flat dataclasses and ordered MLIR reconstruction; remove unused
  group/offset/activation-scale state and unsupported private non-swap branches.
  The physical work ring remains eight words, with slot four reserved zero.
- Epilogue: call the fixed BF16 operations directly, specialize the actual TMEM
  transpose paths, and share the normal/last-subtile implementation through a
  compile-time flag. Release, fence, store and completion ordering is preserved.
- Kernel: remove unused workspace/activation-scale state and no-op hooks, simplify
  declared-region views, and pass FC2 alpha directly with the same flattened
  kernel argument order. Scalar alpha alignment and count-buffer aliases remain.
- Host: remove duplicate compile/config state and the one-use staging wrapper.
  Keep the eight autotune candidates and ordering unchanged.

Combined file-scoped pre-commit passed, including mypy and Ruff. Independent
source reviews passed. The first local check exposed one shared count-buffer
view that needed its explicit Int32/stride-two alias; that was corrected before
this passing check. Native compilation and existing numerical/graph suites are
pending. No performance preservation or new speedup is claimed yet. Historical
Final performance remains pinned to measured source `c8efa`.

`loc-reduction.json` records per-file counts. Subtask details are in the sibling
`w4a16_implementation_reduction/scheduler`, `w4a16_epilogue_scope_cleanup`, and
`w4a16_host_complexity_cleanup` directories. Review artifacts here bind exact
source bytes. No new test framework is added.

## Native admission correction

Initial source `40fec0ef` failed all three native compile fixtures before native
code generation. Tuple reconstruction of `_DynamicLoadBalanceState` reached the
installed CuTe `PipelineState.__get_mlir_types__`, which accesses `.count.type`
on an `Int32` wrapper. This had not been exercised by the local Python checks.
The original per-field reconstruction avoids that tuple type-query path.

The correction retains the dataclass and rebuilds each nested field using its
own extracted value count and reconstruction hook. It adds seven lines; the
final implementation reduction is 869 lines. The primitive-only fused state
keeps tuple reconstruction. Independent review agreed with the diagnosis and
minimal correction. Scheduler-scoped hooks pass. The failed logs remain under
`profiles/cu132-recovery0911a-transport-implementation-cleanup-default-candidate-parallel/`.
Corrected native and existing numerical validation are pending.

## Completed validation and commit

Corrected source `eb9cc9a1`, manifest `51b972d9`, is committed as
`a8b5a47cdeb7b09f784d6a76d35b952bd1e4e3e5`. All 1,577 committed source files
match the frozen manifest. Final reduction: 869 net implementation lines
(6,504 to 5,635 across ten files), with no benchmark or test edits.

- Native3 passes with unchanged resources, stage fits and protected ordering;
  each fixture has 16 fewer instructions from removed scheduler bookkeeping.
- Host 80 passes and one existing missing-DeepGEMM skip; EP1 42 passes;
  EP2 25 passes per rank; two M128 C1/C2 static/S3 oracle calls per rank pass.
- All applicable hooks pass, including mypy and Ruff. Final source/native/idle
  closure passes on CUDA 13.2 B300. No benchmark ran for cleanup validation.

Full results: `execution/validation-completion001.json` (SHA `fdb61867`).
The user subsequently requested resuming broader performance work after cleanup,
using established MegaMoE orchestration patterns and avoiding marginal lifetime
tweaks. That work is separate from this completed cleanup.
