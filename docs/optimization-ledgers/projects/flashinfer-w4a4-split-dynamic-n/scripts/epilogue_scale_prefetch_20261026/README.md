# Epilogue scale prefetch experiment

Independent unstaged source: `flashinfer-pipeline-20261026`, parent `0def601d6603df828ea39679b41ccbce64f7f09e`. Only the shared Blackwell core changes. No public API, tactics, buffers, barriers, arithmetic, dtype selection, cache hint, PDL ordering, or architecture changes.

Both the inline and dedicated epilogue roles currently fetch invariant `norm_const[0]` and per-expert `alpha[expert]` after `acc_pipe.consumer_wait`. This candidate loads the invariant norm once per role after the existing PDL dependency wait, and loads expert alpha as soon as the role knows its tile, before waiting for accumulator readiness. Inline epilogues can overlap alpha with their own operand producer loop. Dedicated epilogue roles can overlap it with MMA/preceding work. All source data dependencies and numerical values stay unchanged. Zero-work CTAs can read the valid invariant scalar when one is supplied, but cannot read expert alpha without a valid work tile.

This is distinct from prior first-route metadata staging (which explicitly did not move alpha), output-row/rounded-route-scale preloads in the existing epilogue, and rejected separate TMA/SF producer experiments. It introduces no runtime first-tile predicate or extra producer role.

The compiler may already hoist these loads, or may sink them back to first use. Generated PTX/SASS must establish whether the movement actually happened before attributing any timing difference to prefetch. One extra live FP32 value across the MMA wait may affect allocation. Test every supported dtype through existing tolerance-based coverage, then use the existing model-family cold-L2 CUDA-graph CUPTI benchmark with adjacent controls. A fixed-tactic screen is diagnostic; retain only after current-source AUTO evidence across V3, V41-Flash and K3. No model-specific/dtype-specific policy is allowed.

Initial validation: Python compilation and diff checks pass. Scoped pre-commit passes. GPU compile, existing-suite checks, codegen and timing are pending; no performance claim.

## Public-profile artifact observer

`inspect_profile.py` runs the unchanged `bench_moe_deepseek.py --profile-cuda` path, with one profile replay and the current saved tactic cache. It does not modify timing hooks, source, routing, tactics or kernel launch arguments. Only core compiler calls receive appended `--keep-ptx --keep-cubin` flags; original options are preserved. It refuses cache misses, a route-width mismatch and more than the expected two core compilations. Each process covers one model/token/dtype case; use fresh output directories and independent source-keyed compiler caches.

The observer records exact source/patch/cache hashes, driver register/static/dynamic-SMEM/local-memory/occupancy resources, PTX/CUBIN/SASS, and scalar-load parameter origins with nearby mbarrier/TMEM sites. PTX indexes are conservative lexical aids; manual CFG and SASS inspection is required to claim actual load movement. SASS LDL/STL counts and driver local memory identify spills independently of PTX virtual registers.

Example (replace root paths, saved cache and expected route width with the recorded current-control case):

```bash
python inspect_profile.py --repo /data/.../control-0def601d \
  --expected-head 0def601d6603df828ea39679b41ccbce64f7f09e \
  --expected-core-sha bfcc8b0c1d673415f8cec598d6599717c91af85db29c7e9e8c14d9e2d73bf57e \
  --model v41-flash --backend cute-dsl --tokens 32 \
  --expected-route-n 16 --cache /data/.../control-cache.json \
  --output /data/.../codegen/control-nv-small
```

Run NVFP4 (`cute-dsl`) and MXFP8 (`cute-dsl-mxfp8`) at one saved small-N and one saved large-N case per source. NVFP4 includes initial activation quantization, matching the current campaign contract. This profiler output is diagnostic and never substitutes for benchmark medians. The parser was smoke-checked on an archived PTX artifact; GPU compilation and ordering verification remain pending.
