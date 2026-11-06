# SM100 ternary absolute-maximum experiment

Rejected experiment; its verified local/remote candidate source copies were removed.
The source was based on
`d02c487a15d0636e902c3f7a5e0bf7cf4a03156d`. The immutable remote sources
are based on `0b7fe901` plus the byte-identical benchmark overlay; every
executed source hash is bound to the local d02 source in `compile-config.json`. Only the shared Blackwell epilogue
`_absmax` and one local NVVM wrapper change (+20/−4). No tactic, layout, storage,
barrier, activation, weight preparation, W4A16, or Rubin changes.

The old 16-value reduction expresses 32 binary maxima in a serial dependency
chain. The candidate uses eight ternary absolute maxima at depth three. This
is a source count, not a measured instruction reduction. The earlier
`scripts/fc1-native-audit/README.md:111` note is superseded by
`scripts/fc1_arithmetic_experiment/README.md`: a nine-operation inline-PTX
ternary tree was GPU-tested on 7829/B200 and rejected as neutral (324.3685→
324.2410 µs isolated NVFP4 FC1 at 16K). This candidate folds its redundant
`max(abs(values[15]),0,0)` into the next merge and uses NVVM instead of inline
PTX. That historical source count is not evidence of an instruction reduction
against the current compiler. Both preparation trials were subsequently rejected.

The installed CuTe DSL 4.7.1 APIs were inspected with GPUs hidden (`sdk.json`).
`cute.arch.fmax` accepts only two operands, and its `abs=True` also computes
XOR sign. The underlying `nvvm.fmax` supports `c=` and `abs=True`; the ternary
form supplies absolute magnitude without XOR sign. Existing SM100 utilities
already use its `c=` API, so no version branch or inline-assembly helper is
needed.

The [PTX max specification](https://docs.nvidia.com/cuda/parallel-thread-execution/#floating-point-instructions-max)
supports three inputs from PTX 8.8 on SM100+. Without `.NaN`, a numeric operand
wins over NaN; without `.ftz`, subnormals are preserved. The final merge includes
positive zero, retaining all-NaN→+0 and signed-zero→+0 behavior. Infinity and
finite magnitudes are unchanged. Intermediate NaN payloads cannot affect the
final numeric result.

`prove_semantics.py` executes source-extracted old/new reductions against a
bit-pattern model of those PTX operations. It passes 75,842 vectors / 1,213,472
elements, including all 65,536 NaN-position masks, signed zero, positive and
negative subnormals, infinities, signaling/quiet NaNs, and 10,000 random vectors.
This proves the algebra under the documented operation semantics, not device
lowering. `source.json` also pins the full-index patch, unchanged surrounding
AST/header, clean index, and passing scoped pre-commit checks.

The current source-paired V3 NVFP4 T16384 FC1 compile is complete
(`codegen-review.json`). Both arms emit 5,543 non-NOP instructions, including
128 FMNMX3 instructions: the compiler already folds the original source into
eight ternary maxima per 16-value group. The candidate keeps eight instructions
and shortens all 16 emitted reduction dependency chains from depth eight to
three. Both use 86 registers, zero stack/local memory and identical geometry,
stages and shared storage. Instruction scheduling/register allocation differs;
this is not a claim of binary identity or fewer instructions.

The device special-value probe has passed all 75,842 vectors for both arms.
The first FC1 whole-storage check exposed nondeterministic within-expert routing
order, rather than a numerical mismatch: all numerical inputs and expert metadata
matched, but physical route order and corresponding output storage differed.
The corrected bounded gate compares every live payload/SF byte in sorted
expanded-route order, checks unique/equal IDs and expert ownership, independently
decodes the 128-row/4-scale physical SF atoms using each arm's actual row, and
retains physical hashes separately. Inactive padding is excluded. Original
failed checks remain in separate immutable output directories.

The corrected six native FC1 cases pass: 88,101,888 live payload/SF bytes per
arm. The final helper-only tuple/list comparison failed after all six cases
had persisted; a separate offline admission receipt proves saved JSON tactic,
input, output and source equality without rerunning GPUs. Both original worker
failures are retained. See `exact-evidence/amax-tree-exact-v2/gate-validation.json`.

The six-cell V3 public C-A-A-C screen is complete (`summary.json`, `results.md`):
2,400 raw samples, 100 cold-L2 CUDAgraph CUPTI samples and ten warmups per leg,
fixed native winners, input quantization included for NV and excluded for MX.
Overall 1.00063× is neutral. Decode differences are −0.01% to −0.03%; NV16K
is +0.02%. MX4x8 16K +2.12% and MX8 16K −1.67% have repeat drift of 2.9–4.7%,
so neither is treated as a stable gain/regression. A periodic GPU telemetry
sampler covered all MX legs but began after the first NV leg; it cannot assign
clocks to every individual subsecond measured interval.

`unchanged-codegen.json` proves exact SASS instruction/control-word and resource
identity for per-token FC1, per-token FC2, MXFP8 FC2 and MXFP4x8 FC2. Both affected
MX FC1 kernels also retain their instruction mix/count and 88 registers. All
six paired kernels have no stack/local operations. No end-to-end speedup is claimed.

The final Nemo ReLU2 NV16K pair passes 127,287,360 live FC1 payload/SF bytes
per arm across 44,197 rows, including both 16-element reductions in the
nongated 32-channel path (`nemo-summary.json`). Both reduction depths fall
from eight to three; registers fall from 102 to 100, non-NOP instructions from
1,724 to 1,723, with no spills. Its 400-sample saved-winner CAAC bracket is
574.884 / 581.397 / 578.052 / 574.180 µs: 0.991047×, or a measured 0.8953%
slowdown. Control/candidate repeat drift is −0.122%/−0.575%. This slight
prefill loss is recorded explicitly; it is not evidence of an end-to-end gain.
Per-leg clock/power/temperature snapshots are retained. The same frozen
source is separate from the parent's packed per-token FC2 experiment.

All bounded work is complete: 75,842 device special-value vectors, seven native
FC1 byte pairs (215,389,248 live bytes per arm), generated-code/resource checks,
and seven timing cells / 2,800 raw samples. `source.json` pins the final
validation receipts. The candidate was rejected: the compiler already emits eight ternary operations
from the simpler original loop, decode does not improve, and both Nemo
candidate legs are slower. Shorter dependency depth does not justify the
larger source and prefill loss. All evidence/helpers and compilation caches
remain; `cleanup.json` records source-only deletion and GPU4 release.
