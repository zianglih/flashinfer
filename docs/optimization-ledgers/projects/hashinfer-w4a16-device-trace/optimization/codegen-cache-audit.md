# Native artifact availability audit

CPU-only inspection on `devbox-hashinfer-trace-labels-0924-0`, C2/ziangli,
using its installed CuTe DSL 4.8 runtime. No GPU compilation, kernel launch,
benchmark, or frozen candidate edit was performed.

## Runtime artifact contract

Installed files under
`/usr/local/lib/python3.12/dist-packages/nvidia_cutlass_dsl/dsl_packages/cutlass`:

- `base_dsl/jit_executor.py`: `JitFunctionArtifacts` declares PTX as text or
  None, CUBIN as text-path/bytes or None, and SASS as text or None.
- Its `__post_init__` eagerly reads a retained artifact file when the field
  names an existing path. PTX is read as text; CUBIN is read as binary bytes.
- `JitCompiledFunction` and `CudaDialectJitCompiledFunction` expose these
  fields through `__ptx__`, `__cubin__`, and `__sass__`. A missing artifact is
  returned as None; the property itself does not regenerate it.
- `base_dsl/dsl.py` passes the compiler's full PTX/CUBIN paths to that object.

The exporter therefore accepts direct PTX text, retained file paths, and
binary CUBIN bytes. It also tolerates PathLike and binary buffer values, and
fails explicitly for absent artifacts, missing CUBIN paths, non-ELF cubins,
or PTX without an entry. Retention and fresh caches are configured before
importing CuTe.

## Existing cache inspection

`base_dsl/cache_helpers.py` resolves the default cache to
`/tmp/root/cutlass_python_cache` in this container. That directory contained
no files when inspected. The existing optimization benchmark cache directories
hold `hashinfer-knobs.json`; they are tactic-selection caches, not cubin stores.

The effort's older SASS files include instrumented kernel variants, but no
exact-source native control/store16 artifact was established by this audit.
Neither a matching kernel name nor a store-width opcode is sufficient to bind
an artifact to a frozen source, capacity, ABI, and compiler configuration.
The scheduled explicit codegen exports remain necessary.

## Exporter verification

`codegen-exporter-check.json` records local source digest checks for control,
store16, store32, store64, counts_overlap, and parallel_payload against the
current source manifest. Synthetic x32/x64 stores and packing instructions
exercise the summary, including separation of two functions with reset PCs.
Artifact path/text/bytes handling and rejection of missing artifacts were
checked locally. The prior instrumented SASS was used only as parser coverage;
its instruction counts are not native performance evidence.
