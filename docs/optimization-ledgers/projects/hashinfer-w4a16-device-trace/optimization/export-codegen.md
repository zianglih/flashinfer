# Uninstrumented codegen export

`export_codegen.py` wraps an existing driver, captures target `cute.compile` return values, and writes PTX/cubin/SASS/resources plus a JSON manifest on rank0. Other ranks execute unchanged compile calls. Before importing CuTe it sets `CUTE_DSL_KEEP=ptx,cubin` and per-rank independent CUDA/CuTe cache/dump paths. These are diagnostic driver runs, not controlled performance samples.

Verified by CPU-only inspection of the current C2 environment: CuTe DSL4.8 exposes `__ptx__`, `__cubin__`, `__sass__`; `St32x32bOp(Repetition(16),Unpack.NONE)` is accepted. No GPU compile/run was performed while authoring the helper.

Each manifest artifact includes `staging_abi`: routing IDs dtype, hidden contiguous/vector-copy choice, pointer element dtype/alignment/address space, and stride descriptor types. Use `routing_ids_dtype == "Int32"` with `hidden_contiguous_vector_copy == true` to locate the timed uniform fixture ABI among the numerical coverage compiles. Pointer addresses and tensor contents are never recorded. Both directly callable kernel instances and bound kernel methods are recognized; `compile_callable_type` records which form was observed.

The exporter requires `HASHINFER_OPT_SOURCE` and verifies its complete Python-source digest against `source-manifest.json` beside the helper (`--source-manifest` overrides that location). Copy the current manifest with the helper. It confirms the imported kernel class comes from that source root and checks the source again after compilation and driver completion. Each artifact records the source fingerprint; the manifest includes per-file hashes, original commit, exporter/driver hashes, capacity, world size, shape, tactic, and staging ABI.

SASS summaries now include plain STTM.x32/x64 (and the other widths), full opcode histograms, MOV/IMAD.MOV, register-to-register MOV, PRMT/UPRMT, shifts, logic, packed conversions/arithmetic, local-memory operations, and register redistribution. Store excerpts retain 96 preceding and 32 following instructions within their own function, with separate static counts. `tmem_store_instructions` retains all native store operands, including distinct layouts. These are static counts; packing-related opcodes may also implement unrelated math/address work.

For sparse-workload regressions, capture the actual native capacity and ABI as well as uniform256. A T4 specialization can differ in whole-kernel layout, staging loops, and register allocation even with the same N64/G512 tactic. Wider TMEM operands might require extra register arrangement, but only matched native SASS can establish that mechanism.

Example after existing performance collection has finished (use current remote source/helper paths, fresh output/cache directory, and the exact fixed winner JSON):

```sh
export HASHINFER_OPT_SOURCE=/workspace/hashinfer-trace/optimization/predecode
export HASHINFER_OPT_FIXTURE=uniform256
export HASHINFER_OPT_LABEL=predecode-codegen
python -m torch.distributed.run --nproc-per-node=4 --master-port=29672 \
  /workspace/hashinfer-trace/optimization/export_codegen.py \
  --output /workspace/hashinfer-trace/codegen-predecode \
  --driver /workspace/hashinfer-trace/optimization/benchmark.py -- \
  --num-gpus 4 --num-tokens 1024 --warmup 0 --iters 1 \
  --timing cupti --cuda-graph --cache-dir /workspace/hashinfer-trace/codegen-predecode-knobs \
  --megamoe-knobs '{"cluster_shape_mnk":[2,1,1],"group_hint":512,"epi_flag_batch":[2,4],"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"use_2cta_instrs":true,"flag_batch":4,"token_back_mode":"epi_warps","in_kernel_fc2_reduce":false,"num_sched_stages":2,"enable_iket":false}'
```

The example fixes the original native trace winner; use the newly measured winner instead if it differs. The actual driver still performs normal workload preparation/launch/cleanup; schedule it with exclusive GPU ownership and fresh output/cache paths.

Inspect control, predecode, and store16 using identical workload/tactic/compiler flags. Compare resource reports, PTX local declarations, static LDL/STL instructions, and register-fed STTM stores. Static local accesses alone are not a dynamic spill measurement. Whole-kernel static STTM counts include epilogue operations; inspect the decoder regions separately. For predecode, prove packed-weight/scale loads and BF16 decode finish before decoded-empty acquisition, with all64 per-thread output registers intact until their TMEM store. Require decoded-full publication after the store fence. For repetition16, prove equivalent TMEM address coverage and expected four x16 stores in place of eight x8 without extra packing/spill costs. Preserve independent raw, decoded, activation and accumulator completion rings.
