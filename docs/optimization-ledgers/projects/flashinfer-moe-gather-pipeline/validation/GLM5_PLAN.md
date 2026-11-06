# Conditional GLM5 shared-helper regression check

Do not launch until split W4 qualification/performance supports retaining the scale-selector candidate and the parent reserves all eight GPUs. No distributed launch may overlap any independent GPU experiment.

## Reuse and source scope

Reuse the prior project's `upstream-integration-20261029/megamoe-glm5/{native_frozen.py,frozen-tactics.json,analyze.py}` contract. Do **not** rerun AUTO: all 13 historical per-token tactic dictionaries are explicit. Current `bench_cute_dsl_moe_distributed.py` differs from the measured 437 version only by omitting four unused inherited metadata fields in `DISTRIBUTED_MODEL_JSON`; routing, workload construction, MegaMoE launch, and timing are unchanged. This is evidence for reusing workload/tactics/harness, not historical timing reuse for the helper comparison.

Both new arms must use HEAD82254e production. Control keeps helper d5105227; candidate usesd3afcec4. The current candidate-r2 source also contains a separate swap-AB FC2 store change. MegaMoE does not execute that kernel, but use a helper-only immutable candidate snapshot for the strongest source-isolation claim: full manifests must differ only in `moe_w4a16_utils.py`. Do not modify the active split candidate or old source copies. All native asset symlinks should retain their current persistent paths; compare actual Ninja descriptions before launch, preserving old CPP cache artifacts. Per-process relevant-source guards can be hash-bound to the full before/after source manifests to avoid expensive repeated full-Weka scans.

The affected path is `_MegaMixedInput(Sm100W4A16GroupedGemmKernel)` → inherited `_transform_tile` → modified shared utility. MegaMoE's own raw-release override is unchanged. Preserve an actual compiled MegaMoE PTX/cubin/resources receipt; demonstrate the selected-byte PRMT and removed extraction in that native specialization rather than assuming a helper source diff proves different device code.

## Workload and timing

- C2 `fi-gather-pipeline-1030`, all8 B300, current observed runtime/image, no clock changes.
- Native distributed benchmark `--model glm5 --parallel-modes ep --num-gpus 8 --variants w4a16_megamoe`: D6144/I2048, 256 experts, top8, SwiGLU; actual EP8.
- Tokens1,2,4,8,16,32,64,128,256,512,4096,8192,16384. Measure1/2 but exclude from retention aggregates.
- Serialized fresh process groups C1→A1→A2→C2; same frozen per-token tactics and rank-local routing fingerprints. No new tuning, no independent arm selection.
- Native precomputed routing, PDL, fused deterministic MegaMoE combine; in-kernel FC2 reduction disabled. Existing `--no-fused-finalize` CLI relates to split variants and does not disable MegaMoE's deterministic combine.
- Three warmups and100 untrimmed cold-L2 CUDA-graph CUPTI samples per phase/token, matching the original GLM5 methodology. Rank-MAX spans **per iteration**, then medians; never max of per-rank medians.
- Validate52 timing records,5,200 samples,416 per-rank tactic records and416 route fingerprints; every phase must match all8 ranks and the frozen map. Make any CUDA-event fallback fatal and audit all logs for fallback warnings, not only missing-CUPTI warnings.
- Keep complete raw arrays, phase medians, pooled200-sample arm medians, spread and stock NVML telemetry. Include negative rows and variability; no uniform non-regression claim from positive geomean alone.

## Commands and environment

Adapt the original wrapper only for new source/artifact paths and source/resource receipts. Its timed call remains the native benchmark function. Representative invocation per phase:

```bash
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0
export FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1
export FLASHINFER_NVFP4_4OVER6=1 FLASHINFER_NVFP4_4OVER6_E4M3_USE_256=1
export FLASHINFER_NVFP4_4OVER6_ERR_MODE=MSE
export FLASHINFER_NVFP4_4OVER6_ERR_USE_FAST_MATH=1
export FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=1
# Set PYTHONPATH/MEGA_SOURCE, MEGA_FROZEN_TACTICS, persistent CPP and
# per-source DSL caches to the source-qualified paths recorded for the phase.
torchrun --master-addr=127.0.0.1 --master-port=29672 --nproc-per-node=8 \
  native_frozen.py --model glm5 --mode benchmark --parallel-modes ep \
  --num-gpus 8 --variants w4a16_megamoe \
  --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 \
  --timing cupti --cuda-graph --precomputed-routing --no-fused-finalize \
  --warmup 3 --iters 100 --log-timing-samples --megamoe-knobs auto
```

The wrapper replaces `auto` with the required frozen dictionary before each layer construction; add a guard against any actual autotune invocation. Each new group uses a distinct free rendezvous port.

No sanitizer or broad new tests are part of this comparison. No GPU work was launched to prepare this plan.
