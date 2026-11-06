# Held SF-coordinate-cache performance screen

Prepared locally only; no deployment, cache mutation, GPU reservation or launch
by this task. Root conditionally authorized one screen after the completed
native gate and the qualification owner's GPU/cache release. The owner retains
the sole snapshots and is restoring the canonical native-cache input paths.
The original `1971cb0e` preparation is preserved in `pre-recovery-held/`, and
the first `9d900e5c` preparation in `pre-fresh-cohort-held/`.

- **Scope:** the existing startup-weight-cache matrix: 23 jobs, 28 supported
  non-W4 arms, all four models and EP/TP, tokens 32 and 16384. This is 56 cells
  and 22,400 samples. Unsupported arms remain absent.
- **Method:** unchanged C-A-A-C, 10 warmups and 100 strict CUPTI samples per
  phase, cold-L2 CUDA graphs, frozen routes and explicit native tactics.
  NVFP4 includes input quantization. Keep all four phase medians, negatives,
  resource records, and clock exceptions or missing windows.
- **Sources:** retained `c1ac8ce7` / swap `482b636a` versus its sole swap overlay
  `15d6eb18`. Qualification source records are `a4e7f5a4` and `c8279fb5` under
  `experiments/sf-coordinate-cache/qualification`; they are not rewritten.
- **Cache plan:** separate real workspaces at
  `/data/ziangli/flashinfer-moe-gather-pipeline/cache/sf-coordinate-cache/{control,candidate}`,
  each with its own `cute` and `.cache/flashinfer/0.0.0+unknown/103a/cached_ops`.
  Only the four unchanged C++ module directories are shared with the persistent
  release cache. The qualification owner materializes these directories.
  `generated` resolves to the canonical shared generated root, and each phase
  explicitly sets `FLASHINFER_CUBIN_DIR` to the canonical cubin input directory.
  No cache clear or cross-arm quantizer-cache reuse is planned.
- **Cohort:** `fi-gather-pipeline-resume-1030`, C2/ziangli. Runtime metadata
  remains `recovery-paired-error/runtime.json` (`ad49506c`). The explicitly
  adopted current cache/readiness receipts are `cache-recovery/cache-ready-current.json`
  (`ad6b3a6d`) and `readiness-current.json` (`e466ac7c`): fresh same-source
  `moe_utils` ELF `046552b8`, three original ELFs and all original Ninja hashes.
  Original identity restoration failed and is preserved; it is not relabeled
  successful. All 11 qualification pairs rerun freshly in this cohort.
  Fresh source, actual per-arm normal JIT load, generated-root resolution,
  adopted-current Ninja/ELF no-op and GPU-idle checks remain required before launch.
  Current readiness is a historical
  binding, not a fresh idle claim.

`prepare.py` adapts the previous config locally. Eleven helpers are byte-identical
to startup-weight-cache; `run_perf.py` adds only the explicit cubin-directory
phase environment binding. Removing that line reproduces the original bytes.
Jobs, choices, routes, timing parameters, observers and native guards are unchanged.
`environment-binding.diff` and its proof seal this correction. `config.diff` contains the source
bindings, private runtime cache paths, labels and output leaf; its sole source
delta is the qualified swap kernel. Existing full inventory pre/post boundaries
and the 71-file per-process guards remain unchanged.

Prepared config SHA256:
`9d900e5c07481cbc1359b39d3045a8d9b2691f1682692fdf2db8997054dbcdbb`.
Plan SHA256:
`75474df8cbcd98b5557c31c22c573da63f3ee6901063d52698a6bbb6b22d1702`.
`preparation.json` binds the unchanged input/helper hashes and source records.

After release, use the existing campaign controller and report pipeline in the
new `runs/sf-coordinate-cache-screen` leaf. The launch wrapper remains held.
No baseline rerun, retune, repetition or matrix expansion is included.
