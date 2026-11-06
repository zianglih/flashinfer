# Isolated follow-ups to prep256-v1

Both variants start from the archived `prep256-v1` source, without the separately proposed early-PDL signal. The active checkout is unchanged. Each directory contains complete launcher, preparation and GEMM files plus a SHA-256 manifest. `candidate-*.patch` applies to baseline `36740c36a32a6c6d1c7d8162823fe823912de741`; `*-from-prep256-v1.patch` contains only the isolated follow-up.

## prep256-threads256-v1

Two constant changes: preparation threads increase from 128 to 256, and the hardware thread-capacity grid divisor increases from 128 to 256. At H7168, a row contains 448 copies of 32 bytes. This reduces the unrolled per-row copy passes from four to two while retaining the same total payload transfers. It halves the maximum concurrently resident row-CTA count at equal occupancy and matches the native permutation's block size. Neither effect establishes a speedup; measure preparation and full-chain timing.

The original GEMM source and launcher are byte-identical to prep256-v1. The 128-bit alignment fallback, valid-row masking, top-k specialization and PDL placement remain unchanged.

## static-mk-v1

M and K become `cutlass.Constexpr` arguments in the grouped GEMM wrapper. The host cache explicitly gains M and K entries, because unlike #7290 these dimensions were previously excluded. Compilation still receives them, and subsequent compiled runtime calls omit them. Routed N and token count retain `cutlass.Int64` annotations, remain in the runtime call, and remain excluded from the host compilation cache key.

This is dimension specialization only. Every kernel method body is AST-identical to the baseline; the only kernel AST differences are the two wrapper annotations. Top-k, original 23 tactics, dynamic MMA N, stage policy, arithmetic, workspace ownership, FC2, and combine contracts are unchanged. The preparation source is byte-identical to prep256-v1. The deliberate cost is separate compilation/cache entries per M/K shape.

Source reference: neighboring #7290 `scripts/static_shapes_experiment/README.md`, which retained wrapper dimension specialization while keeping routes and tokens dynamic. Its performance numbers do not establish W4A16 performance.

## Validation and optional code generation

Ruff, Python compilation, and focused AST checks pass for both snapshots. GPU tests and timing are pending; no new test file was added. The existing bit-exact route coverage remains the numerical gate.

`capture_prep_codegen.py` is an optional compile-only diagnostic. It creates dump/cache directories, checks an explicit expected source SHA, and captures H7168 top-k 3/8 with both 256-bit and 128-bit alignment specializations. It saves PTX, compiler-produced and separately assembled cubins, ptxas logs, SASS, constant-division evidence, and CUDA-driver register/local-memory/occupancy queries. It infers the thread count from the selected preparation class, so it can inspect either preparation variant. It does not launch kernels or time anything. Use a ptxas version supporting the emitted PTX; CUDA 13.2's ptxas previously could not parse the current DSL's PTX 9.3.

No 16-CTA/SM residency claim is made until that resource query confirms actual occupancy. Compilation and code generation must not overlap measured benchmark arms.

## prep256-threads256-early-pdl-v3

This artifact combines the independently screened 256-thread preparation with the already audited early-PDL placement. Relative to `prep256-threads256-v1`, its sole delta moves `griddepcontrol_launch_dependents` immediately after the dependency wait. It retains 256 threads and the matching grid divisor. There is no static-M/K change. `prep256-threads256-early-pdl-v3-from-threads256.patch` is the isolated delta; `candidate-prep256-threads256-early-pdl-v3.patch` applies to the original baseline. Prep SHA-256: `e569c3ac37560d07beb4ad86efb9f992ab418bae580ae1606f813f46cd92c606`. Local syntax, Ruff, AST composition and both patch checks pass; GPU execution is owned by root/bench.

## Alignment and empty-work boundary audit

The existing 24 route-boundary tests use newly allocated H256 inputs and routed workspace. They cover route tails and top-k2/3 but do not construct 16-byte-offset views, so they do not exercise the 128-bit alignment fallback. They also do not inspect preparation-only inactive-storage canaries or zero capacity.

No source blocker was found: both pointer bases and row width gate vector alignment; vector columns cannot cross the row boundary; mapping is loaded only after the valid-row limit check; row pointer arithmetic is64-bit; zero capacity returns before compilation or launch. Zero active tiles at positive capacity still launches the selected preparation kernel, whose row loop does no work.

`probe_prep_alignment.py` is an off-tree byte-comparison harness, initially syntax-checked only. It requires the selected source SHA and refuses to overwrite results. The 48 cases cover H7168, top-k3/8, all four combinations of 32-byte and exactly16-byte-aligned input/output bases, PDL off/on, zero/three active tiles, and zero capacity. Valid rows include short/full/half-plus-one tiles; invalid mapping entries contain -1. It compares the whole backing allocation against independent CPU bytes, including invalid rows, unused capacity and prefix/suffix canaries, and verifies source bytes are unchanged. Optional `--compare-native` also compares the same allocations with the native permutation's contract. Run only after timed screens; it is not a repository test or performance measurement.

The static-M/K audit found no additional blocker. `use_dynamic_n` selection, runtime valid-token inputs to MMA idesc, and the two-CTA source shift are unchanged. The wrapper retains dynamic N/token arguments and the host cache omits both, while explicitly keying specialized M/K. GPU compile/exact checks remain necessary for compiler constant-folding behavior.
