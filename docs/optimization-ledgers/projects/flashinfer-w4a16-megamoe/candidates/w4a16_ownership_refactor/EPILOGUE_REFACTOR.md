# Independently owned W4A16 epilogue

The primary source now owns the W4A16 epilogue under
`flashinfer/moe_ep/kernel_src/cutedsl_megamoe/src/moe_nvfp4_w4a16/`:

- `epilogue.py` owns the actual BF16 constructor, phase loop, FC1/FC2 contexts,
  completion signaling, FC1 arithmetic and accumulator release behavior.
  It has no FP4 base initializer or W4A4 epilogue inheritance/import.
- `tmem_epilogue.py` owns the required 16x32 TMEM transpose, BF16 FC2
  alpha/cast/reorder/store functions, per-issue mapping and local/peer router.
  It derives those selected operations from the saved NVIDIA BSD epilogue,
  preserving attribution. Quantization, SF output, UBLK/REDG and the overlapping
  accumulator variant were not brought across.

The only imports into the NVFP4 sibling are its pure-Python `contract` mapping
and neutral `moe_persistent_scheduler` interfaces. Neither imports a compute
kernel or epilogue. `src`/`common` provide transport metadata, symmetric pointer
mapping, scalar math, range instrumentation and flag batching. W4A16 owns
`BlockPhase` through its local phase scheduler. Existing vendored files were
not edited by this extraction.

The original W4A16 admission guard already requires unquantized BF16 combine,
STG, no in-kernel top-k reduction and no accumulator overlap. Resolving those
existing constants yields the owned FC2 router, completion method and store
path. Both local dispatch return and direct peer return remain. The existing
four-field optional argument record is named `W4A16EpiArgs`; its internal field
order is preserved, including the unused `fc1_norm_const` and `topk_scores`
slots. Stage counts remain initialized as before; the kernel's subsequent
S2/S3 configuration remains the kernel owner's responsibility.

CPU checks from the current formatted bytes:

- 22 method/class bodies or field records match the saved implementation's AST
  after documentation and the argument-record rename are normalized. These
  include the entire W4A16 run loop, FC1 arithmetic/handoff and FC2 accumulator
  release paths, plus invariant-context serialization.
- Four more bodies match after resolving only the BF16 constants already
  enforced by the original guard: FC2 done signaling, router construction,
  peer pointer prefetch and BF16 STG.
- Constructor state matches across 600 host combinations of the five accepted
  tile/cluster geometries, both returns, hidden predicate cases, clamp values
  (including nonfinite values) and original completion-batch normalization.
- All 1,536 per-issue BF16 store mappings across N64/N128 match the original
  pure-Python Contract tables. This executes neither CuTe nor CUDA.
- Ruff check and format check pass for both primary files.

Reproduce the bounded comparison:

```sh
python3 candidates/w4a16_ownership_refactor/check_owned_epilogue.py
```

Exact source hashes and compared methods are in `epilogue-host-checks.json`.
This establishes source/host equivalence only. Native compilation, resources,
PTX/SASS and numerical validation of the complete refactor remain outstanding;
the earlier CLC numerical resource-gate failure is not a passing test.

`prepare_owned_epilogue.py` is the preserved one-time extraction script from
before the user-directed relocation, not a runtime helper or a command to
regenerate the current source tree.
