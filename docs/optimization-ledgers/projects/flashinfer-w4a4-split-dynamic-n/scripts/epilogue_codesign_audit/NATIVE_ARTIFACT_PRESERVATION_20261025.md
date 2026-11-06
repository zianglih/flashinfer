# Actual native CuTe compilation artifacts

CPU/source audit only; no kernel import, compilation, or GPU launch was performed for this note.

The installed CuTe DSL 4.7.1 supports the documented environment controls:

```sh
export CUTE_DSL_KEEP=ptx,cubin
export CUTE_DSL_DUMP_DIR=/absolute/unique/experiment/artifact-directory
```

Set both before the process imports CuTe. This preserves artifacts from the **actual native `cute.compile` invocations**; it does not require a separate exporter compilation or DEBUG/LINEINFO/optimization changes. Both controls must be recorded in the run receipt. SASS can be disassembled afterward from the saved cubin. `KEEP=sass` is also supported, but additionally requires a compatible nvdisasm installation; it is unnecessary for the minimal capture.

Primary references: [CUTLASS 4.7 debugging, generated artifacts](https://docs.nvidia.com/cutlass/4.7.0/media/docs/pythonDSL/guides/debugging.html#save-generated-artifacts-to-files), [CUTLASS 4.7 JIT options](https://docs.nvidia.com/cutlass/4.7.0/media/docs/pythonDSL/cute_dsl_general/dsl_jit_compilation_options.html). The equivalent per-call options are `--keep-ptx --keep-cubin`; environment controls avoid editing production `cute.compile` callsites.

Installed-source proof, read from `/workspace/flashinfer-w4a4-split-dynamic-n/.venv/lib/python3.12/site-packages/nvidia_cutlass_dsl/dsl_packages`:

| Saved local file | SHA256 | Relevant behavior |
|---|---|---|
| `cute471-artifact-sources/env_manager.py` | `8597e5d158865b4dd6fb0ed73f12564a0d12af9bcac8353f622345e7467dffa1` | Lines 520–536 document KEEP/DUMP_DIR; 611–666 parse them. Deprecated KEEP_PTX/KEEP_CUBIN still work, but are unnecessary. |
| `cute471-artifact-sources/compiler.py` | `91f5428a98e8cf8e5b9a6c665fab9690373124f0d67449aa00e537ec70f52f56` | Lines 1042–1045 enable artifact output; 1067–1092 assign dump directory and `<mangled-function>.<arch>.ptx/cubin` paths. |
| `cute471-launch-sources/cutlass/base_dsl/dsl.py` | `3f48d11009b190b54904742c103d58f972b6925fac68b645fcc65faddb8212b0` | Lines 2854–2860 disable DSL JIT caching for requested PTX/CUBIN/SASS. Lines 2339–2343 attach paths to JitFunctionArtifacts. Lines 2883–2897 select the generated name then apply environment settings. |

Important limits:

- KEEP disables the DSL's own JIT cache so the artifacts are actually emitted. The existing split host `_blockscaled_kernel_cache` and preparation `_CACHE` still retain compiled callable objects, so repeated captured kernel invocations do not recompile. Compilation remains outside the GPU timed replay. Do not claim host compile latency is unchanged.
- Dump names are not globally unique across separately loaded source classes. Do not assume one process-wide dump directory permanently preserves both arms or every specialization. Preserve/hash outputs after each arm's initial untimed compile before a later compile can reuse a filename, or run one arm per process with a separate directory. Environment values themselves are cached, so changing only `os.environ` between already-imported arms is not a sound isolation mechanism.
- A path in JitFunctionArtifacts is metadata, not proof that a later compile has not overwritten that file. Bind source/tactic/actual compiled callable and artifact hashes at preservation time.
- Previously completed PDL results retain their declared **regenerated compile-only** codegen attribution. This note does not retroactively turn those objects into artifacts from their timing process.
