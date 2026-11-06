# Held SF-coordinate-cache performance screen

Prepared locally only; no deployment, cache creation, GPU reservation or launch.
The qualification owner retains the sole source snapshots. Performance release
remains pending the completed native review and the parent's decision.

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
  release cache. These directories have not been materialized by this plan.
  No cache clear or cross-arm quantizer-cache reuse is planned.
- **Cohort:** `fi-gather-pipeline-resume-1030`, C2/ziangli;
  `runtime/recovery-paired-error` runtime/readiness/cache-ready receipts.
  Fresh source, generated-release-Ninja, ELF/no-op and GPU-idle checks remain
  required before any authorized launch. Current readiness is a historical
  binding, not a fresh idle claim.

`prepare.py` adapts the previous config locally. All 12 execution/observer
helpers, jobs, choices, routes, timing parameters and native guards are
byte-identical to startup-weight-cache. `config.diff` contains only the source
bindings, private runtime cache paths, labels and output leaf; its sole source
delta is the qualified swap kernel. Existing full inventory pre/post boundaries
and the 71-file per-process guards remain unchanged.

Prepared config SHA256:
`1971cb0eaede6bae3fb41b2465d01072ce9b454fc5423677a1d0c1e1430b7f2b`.
Plan SHA256:
`15b18b6c88576de7ad7721c4a243fa34dbbe020feb201a52972e3576dc6a25df`.
`preparation.json` binds the unchanged input/helper hashes and source records.

After release, use the existing campaign controller and report pipeline in the
new `runs/sf-coordinate-cache-screen` leaf. No launch wrapper is enabled here.
No baseline rerun, retune, repetition or matrix expansion is included.
