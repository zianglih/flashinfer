# PR #6277 future B300 recipe: native-interface audit

Audited the clean project-local FlashInfer checkout at **`48fce528a70b7bc10c26307dfd2155491d50cfe9`** on 2026-10-09. No GPU, container, HAI, or benchmark execution was performed as part of this independent source/recipe review. The historical b730 collectors, captures, and published figures remain separate evidence.

**The native driver now supplies the required GLM5 and Kimi K3 workloads without a source patch.** It does not supply the historical patch's actual-routing observations. A clean-source rerun must retain that distinction in its metadata and renderer.

## Native workload and command

`benchmarks/bench_cute_dsl_moe_distributed.py:113–149` defines these presets:

| Native flag | D / E / N / K | Activation | Routing |
|---|---|---|---|
| `--model glm5` | 6144 / 2048 / 256 / 8 | ordinary SwiGLU, no clamp | fused DeepSeek; 8 groups, top 4 groups; scale 2.5 |
| `--model kimi-k3` | 3584 / 3072 / 896 / 16 | SiTU, gate 4, linear 25; no clamp | CPU FP32 sigmoid + correction-bias selection; scale 1 |

Both use synthetic NVFP4 weights and the routed expert core. K3's residual width 7168, outer latent projections, latent RMSNorm, shared experts, router GEMM and attention are outside this benchmark. Its native checkpoint remains MXFP4; this recipe does not represent native-checkpoint serving. EP8 gives 32/112 local experts for GLM5/K3. Useful FC1+FC2 work is `6TKDE`, respectively `603,979,776T` and `1,056,964,608T` FLOPs.

For each model, the native production command can remain:

```bash
torchrun --master-addr=127.0.0.1 --master-port=29500 --nproc-per-node=8 \
  benchmarks/bench_cute_dsl_moe_distributed.py \
  --model glm5 --mode benchmark --parallel-modes ep --num-gpus 8 \
  --variants w4a4,w4a16,w4a4_megamoe,w4a16_megamoe \
  --num-tokens 4,8,16,32,64,128,256,512,4096,8192,16384 \
  --timing cupti --cuda-graph --precomputed-routing \
  --no-fused-finalize --megamoe-knobs auto \
  --warmup 3 --iters 100 --log-timing-samples
```

Replace only `--model glm5` with `--model kimi-k3` for K3. Use two fresh native sweeps and pool each point's 200 full-precision samples. The explicit token list is required: the native default includes 1/2/1024/2048 and omits 8192/16384.

## Controls and source anchors

- **SiTU in all four arms:** split configuration at driver lines 677–730 selects typed `SiTU`; Mega configuration at 1327–1337 passes the same activation/scales. GLM5 selects ordinary `SwiGLU()`.
- **Routing:** driver lines 843–921 retain input seed `42 + rank`, global router seed 137, correction-bias seed 911, and BF16-generated correction bias for both requested models. K3 CPU routing uses a stable descending sort, lower expert IDs on ties, unbiased sigmoid weights normalized by `sum + 1e-20`, then scale 1. This is the historical patched K3 algorithm now native. Empty ranks return safely. The CLI requires precomputed routes for K3 and EP-only mode for precomputed routing (2205–2236).
- **PDL:** `--no-pdl` is a `store_false` flag, so omitting it leaves `args.enable_pdl=True` (2127–2132); split `ExecutionConfig` receives it at 725. This CLI setting explicitly controls the split kernels. Do not interpret its value as a separately measured inter-kernel PDL benefit for the fused Mega implementation.
- **No fused TMA finalize:** pass `--no-fused-finalize`; it makes split `MoEFinalizeConfig.use_fused_finalize=False` (729, 2121–2125). The native default is true, so the explicit flag matters.
- **No FC1 route weighting / no fused FC2 reduction:** omit `--apply-topk-in-fc1` (2091–2094); the driver passes false and hardcodes `enable_in_kernel_fc2_reduce=False` for both Mega variants (1335–1337). Both candidate generators restrict this field to false. Selected `MEGAMOE_TACTIC_JSON` records can additionally be checked outside native execution. This replaces the old patch's extra rejection guard without modifying kernels or the driver.
- **W4A16 fused deterministic combine stays active:** `bf16_nvfp4/frontend.py:893–905` passes the real output `y` as `reduced_output` when FC2 reduction is false; the persistent Mega tail executes under `not in_kernel_fc2_reduce and reduced_output is not None` (`megamoe_kernel.py:1516`, 1613, 1649). Disabling atomic FC2 reduction does not disable this combine.
- **Native timing:** `_run_distributed_iterations` and `_check_megamoe_output` have exactly the same AST as b730. CUPTI uses `bench_gpu_time(... repeat_iters=args.iters, enable_cupti=True, use_cuda_graph=args.cuda_graph, cold_l2_cache=True, aggregate_op=max)` at 972–981. Preparation, routing, native AUTO, graph capture and L2 flush remain outside the measured forward. Full forward GPU activity spans include communication, staging, activation quantization, expert computation and combine.
- **CUPTI failure handling:** driver 2300–2313 requires CUPTI 13+ and exercises its timestamp API. The shared timing utility still contains its general missing-CUPTI fallback, so retaining the existing collector's native callback preflight and fatal fallback warning is appropriate; a requested timer string alone is not a runtime receipt.
- **Native AUTO changes are intentional:** W4A16 `bf16_nvfp4/autotune.py:17–45` now has 16 non-atomic tactics: four tiles `(128,32,256)`, `(256,32,256)`, `(256,64,256)`, `(256,128,256)` × two group sizes × two return modes. This is a new implementation campaign, not a continuation of the old measured b730 series.

## Native output and missing historical observations

| Record | Available evidence |
|---|---|
| `DISTRIBUTED_MODEL_JSON` (2272–2282) | model name, all native CFG fields, synthetic routed-core scope, precomputed-routing flag, input/weight/router seeds |
| `DISTRIBUTED_TIMING_SAMPLES_JSON` (1009–1031) | full raw rank-max sample array, token count, world size, timer, warmup/iteration counts, CUDA graph, precomputed routing, route-weight placement, cold-L2 and aggregation labels |
| `DISTRIBUTED_CSV` (1884–1887) | six-decimal-ms per-sweep median; validate against raw samples, but pool the full samples for publication |
| `MEGAMOE_TACTIC_JSON` (1390–1403) | native selected AUTO knobs for each rank, variant and token count |
| `REFCHECK_CSV` (1280–1283) | same-weight W4A16 Mega-versus-split tolerant check only |

There is **no `DISTRIBUTED_ROUTING_JSON`**. Native output does not record ordered route-ID/weight digests, expert histograms, owner-rank histograms, observed active-expert counts, or measured route equality across arms/sweeps/hardware. Fixed seeds and source establish the routing construction; they do not replace an observation of actual generated tensors. Uniform expected active experts can still be derived as `N[1-(1-K/N)^T]`, explicitly a theoretical traffic reference, not an actual occupancy measurement or a FLOP multiplier.

The native MODEL record also lacks K3 `model_hidden_size=7168` and the explicit excluded-operations array. Those may be declared as recipe scope metadata from the audited model contract, clearly separate from fields emitted by the driver. Source SHA/clean status, runtime versions, image digest, GPU identity, command, recipe hashes and completion status must still be collected by the outer recipe.

## Reference precheck boundary

**Updated acceptance policy:** the user explicitly accepts MegaMoE against `tests/moe_ep/w4a16_reference.py` and does not require split/backend parity. The initial GLM5 T32 parity precheck failed and remains a diagnostic artifact; no tolerance was relaxed. The collector now uses the independently verified, reused same-source exact qualification described below. The following parity-check analysis records the initial design, not a required gate for the revised campaign.

The native `--refcheck` checks only W4A16 Mega against same-weight split W4A16 using `abs(error) <= 1e-2 + 1e-2*abs(reference)`, rejects nonfinite values, and synchronizes pass/fail across ranks. Its implementation is unchanged. A separate T32 / 3-warmup / 10-iteration precheck remains a useful unrun sanity gate; it is not a PyTorch oracle, W4A4 validation, exact-bit test or model-quality result.

The new W4A16 SiTU epilogue uses `cute.math.tanh(..., approx=True)` (`bf16_nvfp4/epilogue.py:455–499`). The PR deliberately changes the previous approximation and may change numerical bits while retaining SiTU semantics. The historical b730 precheck PASS and its error numbers must not be reused for this head. No assertion that the new head passes this precheck is made here; if it fails, preserve the failure instead of silently loosening tolerance.

## Static validation and fingerprints

Verified clean `HEAD`, inspected all four native configuration paths, and evaluated only the standalone dataclass/preset AST using standard-library `dataclasses` (no Torch/FlashInfer imports). Both model definitions match the table. The native timing, reference-check and token-partition ASTs match b730 exactly. No runtime qualification has been performed.

| Source file (relative to FlashInfer) | SHA256 |
|---|---|
| `benchmarks/bench_cute_dsl_moe_distributed.py` | `cd70541b397a6c278219e1f8bacc7941d0e3903618f88448e1a7aad29d8e2726` |
| `benchmarks/bench_moe_deepseek.py` | `9561d42c798eecbdbc2e3edd31889c0475ff1a56dcd6be7b164ffa7068a86371` |
| `flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/frontend.py` | `114584f1f565017fb7ebf8e3d7e861a7cb631f4e84547ca96cf5269b9b4dea75` |
| `flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/autotune.py` | `2c66d4748d2e53121411fb547c7f030bad18cb4f3b6ad2ee80b2c6f64d334726` |
| `flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/epilogue.py` | `913eedf1ef5543455599c7c4b81011d54940ea79f2766b32b4c45fd43c012377` |
| `flashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/shim/autotune.py` | `07d51edddaa032b0ab22600d2a11cd4d8e9642cdd075a3434de794cc11e4afca` |

The future recipe should use a separate clean-source schema and preserve the historical b730 validator. Reject incorrect model CFGs, timer flags, sample counts, nonfinite samples, missing cases/sweeps, and selected FC2-reduction tactics. Do not fabricate legacy routing records to satisfy the old renderer.

## New collector review

Reviewed `hai/h/ziangli/nvfp4-w4a16-blog/plots/b300-rerun/{collect.sh,prepare_source.py,source_cache.py}` without executing a container or GPU work. One inherited manifest field initially said `dirty=True`; it was corrected to `dirty=False` with `patch_applied=False` before completion of this review.

The preparer now writes an empty compatibility patch outside the checkout and a clean-source audit receipt. It verifies the exact commit, source cleanliness and two benchmark hashes; it does not modify FlashInfer. The unchanged source-cache supervisor seals the full diff and submodule state, maintains a stable physical path, and holds its lifetime lock. The collector explicitly selects `MODEL_CONFIGS[CAPTURE_MODEL]`, avoiding the native module's default `CFG` value before CLI parsing.

The capture validator checks the exact native command, one matching model record per process, all 44 timing/CSV cases and 176 per-rank Mega tactic records per production sweep, 100 finite positive raw samples per case, median/CSV agreement, forbidden-reduction flags, receipt hashes, and the separate T32 native precheck. Two successful sweeps are required before marking the native capture complete. It records actual-routing observations as unavailable and does not call either historical renderer.

Independent static validation: `bash -n` passed, and both model `--dry-run` commands completed without creating output paths. Each emitted precheck and production command passed the new validator's exact command contract. A second source reviewer independently confirmed all six source hashes and the PDL/reduction/combine/refcheck/SiTU analysis. The implementation's separate CPU log fixtures are validator checks only. No GPU result, successful native precheck, or measured figure is claimed by this review.

## Independent renderer review

Reviewed the frozen standalone `plots/b300-rerun/render.py` (`a259c7d294753f682972f392d5c82da3d00dafb435c85372260c252cc7a660cd`) and its collector integration. It consumes only validated native clean-source captures; it does not import either historical renderer or manufacture missing route observations. The collector renders into `/capture/plots`, records a separate `plot-status.json`, and preserves a valid raw capture if rendering fails. Local CLI output defaults to `plots/b300-rerun/{glm5,kimi-k3}`. Historical model folders and their ancestors are rejected; all seven destination files are checked for symlinks, including broken links, and multiple hard links before any output is written.

Independent CPU-only checks used the implementation's explicitly marked `SYNTHETIC-render-glm5` and `SYNTHETIC-render-kimi-k3` fixtures. For each model, all 44 points retain 8,800 full-precision samples and pool 200 values per point before taking the median. The unequal sweep distributions distinguish this from taking the median of sweep medians. Useful FLOPs are exactly `6TKDE`, aggregate TFLOP/s divides by pooled milliseconds times `1e9`, and per-GPU throughput divides by eight. All 11 Mega ratios equal the corresponding inverse pooled-latency ratios within floating-point precision.

Intercepting `Figure.savefig` independently confirmed four throughput curves, logarithmic token and throughput axes, a linear Mega-only ratio axis, separate 4–512 and 4096–16384 ratio segments, and all 11 two-decimal ratio annotations. Synthetic figures carry an explicit watermark. Input capture hashes and file modification times remained unchanged. The independently inspected exports round-trip every raw sample through schema-1 `samples-b300.json`, hash-bound by schema-2 `measured-points.json`; schema-1 ratio metadata binds the measured-point hash. Each of the seven exported files is below 500 KiB. These are renderer/validator checks, not performance measurements; actual native results require a separate completed-capture audit.

## Reused exact qualification

`validation/b300-rerun/exact-qualification/receipt.json` packages the final PR #6277 instruction-reference qualification: eight EP2 logical cases, sixteen rank-local passes, zero failures/errors/skips, finished at `2026-10-09T09:32:51.012404+00:00`. The raw log has two `8 passed, 14 deselected` summaries and both JUnit files contain exactly the eight expected cases. Its scope is D288/E448/N16/K2 and explicit M128/M256 N32 tiles, including SwiGLU and SiTU; it is not the full GLM5/K3 benchmark grid.

The prior test ran assembled source on an earlier checkout HEAD. This review independently matched all 4,018 recorded source files and 102 test files to both `git archive 48fce528a70b7bc10c26307dfd2155491d50cfe9` and the current clean checkout. Before/after maps, nine receipt-bound artifacts, and both JUnit hashes also match. The compact source verification states this assembly history explicitly. Its receipt uses capture-relative `qualification/` paths so the complete folder can be copied into each capture without rewriting hashes. The builder is `validation/b300-rerun/package_exact_qualification.py`; it performs CPU/file verification only.

Per the accepted policy, the existing verified gate is reused and no further GPU test is requested. Reproduction commands and coverage details remain in `PR6277_EXACT_REFERENCE_RUNBOOK.md`.
