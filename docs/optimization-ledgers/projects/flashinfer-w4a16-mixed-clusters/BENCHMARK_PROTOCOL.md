# W4A16 mixed-cluster benchmark protocol

This reconstructs the final published methodology of [FlashInfer #6277](https://github.com/flashinfer-ai/flashinfer/pull/6277), then specifies its reuse for this effort. Historical measurements are context, not a baseline for the new change. New setup, tests and captures are recorded separately in `OPTIMIZATION_LEDGER.md` and `evidence/remote/`.

## Completed outcome, 2026-10-24

The full13 original AUTO16 versus mixed-only AUTO18 comparison completed at
candidate `3d047d3f`; geometric-mean baseline/candidate is 0.992212x (T4+).
A separate matched AUTO36 screen at T64/T128/T4096 selected only atomic tactics
and did not establish a retained benefit. Its static catalog expansion was
rejected and both checkouts restored to clean `3d047d3f`. No samples are pooled.
[Draft PR7202](https://github.com/flashinfer-ai/flashinfer/pull/7202) contains both
raw evidence bundles and reproduction commands. Numerical/sanitizer qualification
remains deferred. Earlier planning and captures below are historical records.

## Current optimization workflow — user direction, 2026-10-24

**All performance benchmarks use AUTO, and the optimized arm tunes only new mixed4+2 tactics.** Iterate on the short GLM5 global-token grid **32,4096**, comparing pristine current-main **AUTO16/all** with candidate **mixed-only AUTO**. Candidate2 selected12 of28 product tactics; candidate3r adds group256 and selects18 of34. The project-only shared `policy_driver.py` wrapper filters the candidate factory to preferred `(4,1,1)` plus fallback `(2,1,1)`, while the unchanged native AUTO implementation compiles, times and selects among every retained tactic. The baseline uses the same wrapper with `all`, preserving its original 16 tactics. Use 100 untrimmed CUPTI samples, cold L2, real EP8 and the same native benchmark driver. Reuse correctly keyed compiled-code caches; source changes still require fresh workers. Both new arms disable the persistent knob cache with `FLASHINFER_MOE_EP_KNOB_CACHE=0`.

Run only the minimum mixed-kernel compile/liveness smoke needed to begin those comparisons. Rigorous numerical qualification and sanitizers are deferred until solid gains are retained. No fixed-tactic performance screens or new forced-fallback diagnostic runs belong to this iteration phase. After retaining gains, perform the full 13-point AUTO comparison and required correctness qualification. This direction supersedes both the earlier fixed-tactic screening proposal and the first exploratory candidate AUTO28 policy that could select original uniform tactics. Keep those prior results separate; do not pool them with the new filtered-policy pair.

After the candidate3r partial screens, the coordinating agent authorized one fresh full13 baseline/candidate pair at committed candidate `3d047d3f8e7923118ffea8b8d36151504ab1fa3d` to independently repeat the screened points and fill the grid. The T128 single-run improvement remains provisional; this authorization does not establish retained gain. Both full-grid arms explicitly use `separate-flashinfer-workspace-v1`, separating `FLASHINFER_WORKSPACE_BASE` by source while keeping the other compiled caches shared. Exact source and helper hashes are frozen in `evidence/remote/setup/full13-freeze-a1/`. Do not pool the earlier legacy-cache exploratory samples into this pair; broad numerics and sanitizer qualification remains deferred.

## Exact historical identities and evidence

- Final measured source: `866c80d0c70a90624b4c2056d12d1543d709609e`; original activation/reference and scheduler, 16 W4A16 tactics. The PR subsequently merged as `ceb589ce3e28bebcbb3b6628b5d4fcb5c2c2eceb` (merge identity from saved release audit; not refetched here).
- BEFORE library: `a7103ae2a97f38f4dbbf410c32acc7c6fe99cab1`, with the same final model benchmark driver, AUTO8. Final AUTO16 adds M128/N32 and M256/N32 to M256/N64 and M256/N128; K256, cluster `(2,1,1)`, group hints 512/1024, epilogue/dispatch token return.
- Final public comparison: **one fresh GLM5 AUTO16 EP8 sweep against the saved GLM5 BEFORE AUTO8 sweep**, 100 samples per point, not a paired/ABBA experiment. Historical K3/DeepSeek studies included reverted activation/scheduler variants and AUTO24 searches; do not label those results as final 866c AUTO16.
- The previous harness README recommends ABBA, but later run-specific instructions explicitly reused saved BEFORE. Preserve this distinction when describing the actual #6277 evidence.
- Source of truth: old project `PR6277_BODY_FINAL.md`, `runs/glm5-n32-866c-control-v1r1/recipe/run.py`, `runner/export_public_glm5_866c.py`. `OPTIMIZATION_LEDGER.md` and `DEVBOX_HANDOFF.md` contain older decisions and stale remote state; the final body and audited final captures supersede them.
- The final GLM5 result was mixed: T4–16384 geometric mean 1.00495x; decode 1.00777x; prefill 0.99747x. This is not evidence that mixed clusters help.

## Workloads and sample definition

Use synthetic NVFP4 routed-expert cores with BF16 activations, eight B300 GPUs, EP8/TP1. Keep model names precise:

| Native preset | Hidden D | Intermediate E | Experts | Top-k | Activation and routing |
|---|---:|---:|---:|---:|---|
| `glm5` | 6144 | 2048 | 256 | 8 | SwiGLU; sigmoid grouped routing, 8 groups/top4, scale 2.5 |
| `kimi-k3` | 3584 | 3072 | 896 | 16 | SiTU gate 4 / linear 25; CPU stable sigmoid top-k, 1 group, scale 1.0 |
| `deepseek-v41-flash` | 5120 | 2304 | 384 | 6 | SwiGLU clamp 10; CPU sqrt-softplus top-k, 1 group, scale 1.5 |

Final global-token grid: **1,2,4,8,16,32,64,128,256,512,4096,8192,16384**. Report all 13 points in the retained candidate's final comparison and exclude only T1/T2 from aggregate retention statistics. Decode aggregate is T4–512; prefill is T4096/8192/16384. The initial optimization screen uses **32,4096**. The coordinating agent subsequently authorized matched **16384** and **128,512** screens with candidate3r unchanged to check throughput and the middle range. Identify these as partial-grid AUTO screens; do not infer full-grid aggregate gains from them. Do not silently use the benchmark's default token grid, which includes 1024/2048 and omits 8192/16384. Weight seed `1000+rank`; activation seed `42+rank`; router-logit seed 137; routing-bias seed 911. Keep native per-rank token splitting/capacity calculations.

The measured forward includes input staging, dispatch, FC1, activation, FC2, token return and deterministic combine. It excludes routing preparation (`--precomputed-routing`), weight preparation, JIT, autotuning, graph capture and L2 flushing. Shared experts, router GEMM, attention, whole-model projections and checkpoint accuracy are outside scope; K3 is the latent routed shape, not the outer D7168 model.

The statistic is **median of per-iteration rank-MAX CUPTI GPU activity spans**, including device gaps between first and last activity, not max of each rank's median and not a sum of kernel durations. Use 100 untrimmed samples and 3 explicit benchmark warmups. `bench_gpu_time` additionally performs untimed graph preparation warmups and latency-estimation launches; `--warmup 3` is not the total number of preparatory launches.

CUPTI cold-L2 handling allocates a flush buffer of twice the device L2 size, zeros it and synchronizes before each measured replay. CUPTI records only replay activities. Do not substitute CUDA-event AUTO selection scores, hot-L2 measurements or timing with the flush inside the measured region. The native benchmark checks working CUPTI 13+ and must not fall back to CUDA events.

PDL enabled; fused TMA/in-kernel FC2 reduction disabled; fused deterministic combine enabled. Routing weights applied in combine: historical `apply_topk_in_fc1=False`, current name `apply_routing_weights_before_fc2=False`. `--no-fused-finalize` controls split variants; W4A16 Mega retains its deterministic combine. Keep activation math and the exact reference unchanged for this cluster-only feature.

## New comparison and fairness

1. Record current-main baseline commit and candidate commit/diff. Use the same current benchmark driver and `flashinfer/testing/utils.py` in both arms; **do not compare new measurements to old #6277 latencies as a causal speedup**.
2. Use native AUTO for every performance arm. Current short comparison is pristine current-main AUTO16/all versus candidate mixed-only AUTO at T32/T4096 (12 tactics for candidate2,18 for candidate3r). Keep activation math, routing, timer and inputs equal. The common project wrapper preserves native order and knob objects, filters only the optimized arm's candidate set, and leaves the product catalog and native AUTO timing/selection function unchanged. Freeze/hash the wrapper separately from the native driver; record per-rank policy calls, available/selected counts, candidate-list hash, and selected tactics. Every optimized winner must have preferred4/fallback2. This compares original-policy AUTO with new-tactic-only AUTO, not a forced fixed tactic.
3. Preserve the existing scheduler evidence for **actual preferred/fallback cluster counts**, active SM count and topology. Unit-v1 observed 33 preferred four-CTA clusters plus 8 fallback two-CTA clusters, totaling 148 CTAs. A requested fallback may resolve to zero; configuration presence alone does not prove physical mixing. Do not add a forced-fallback diagnostic during the current iteration phase. Retained-source correctness qualification must cover the final geometry.
4. Start every arm in a fresh torchrun process group. Serialize all GPU work. Keep short AUTO screens small for optimization feedback; prefer A/B/B/A for matched final baseline/candidate runs once gains are retained. Report selected tactics on every rank and label catalog enlargement explicitly.
5. Keep image, package pins, device allocation, clocks/power policy, model inputs, driver and timer identical. Capture `nvidia-smi` and topology. Use isolated per-source compile/cache directories or one correctly keyed warmed cache; never give only one arm untimed preparation. Compilation/autotuning are outside timing in either case. Do not delete useful caches or edit source while workers remain alive.
6. Cache files are not proof of compiled-kernel reuse. Historical CuTe DSL 4.7.1 direct `cute.compile` explicitly used `no_cache=True`; its frontend process-local callable cache was real. Re-audit this if the runtime changes. Fresh processes prevent old compiled callables surviving Python edits. Give both arms the same cache policy and record effective environments.
7. Pool raw samples only across same-arm repeats with matching source/runtime/protocol. Never average medians or pool baseline with candidate. Report each process's median/tactic, pooled median, quartiles and sample count. For small differences, examine run order and within-run drift; do not infer significance from pooled samples alone. Preserve failures and partial runs but exclude them from successful totals.

For **every new common-wrapper baseline/candidate pair**, `run.py` sets and records `FLASHINFER_MOE_EP_KNOB_CACHE=0` identically. This disables the persistent performance-knob cache, not the compiled-code caches. The original host `MegaKernelBackend._workspace_knobs` path returns `None` for AUTO; W4A16 frontend allocation can then resolve a persistent cached tactic before the explicit AUTO sweep starts. A candidate mixed winner in that shared cache can therefore make pristine baseline allocation reject fallback geometry. Disabling this preparation cache avoids cross-arm configuration contamination while retaining native AUTO selection and logged per-rank winners. Comparison requires matching effective environments and wrapper hashes. No measured native-driver patch is needed.

The first short AUTO16/AUTO28 pair began with compatible uniform cache entries and ran the full respective catalogs. Candidate2's AUTO28 run was deliberately stopped after T32 when the user changed policy. Do not retroactively describe those captures as persistent-cache-disabled, and do not mix them with the fresh cache-disabled AUTO16/all versus AUTO12/mixed-only pair.

## Historical environment and install recipe

Historical image `nvcr.io/nvidia/pytorch:26.05-py3`; CUDA 13.2.1; driver 590.48.01; Python 3.12.3; container Torch `2.12.0a0+5aff3928d8.nv26.5.50603568` retained. Other pins: CuTe DSL 4.7.1, cuda-python/bindings 13.2.0, cupti-python 13.2.0, nvidia-cuda-cupti 13.2.86, nvshmem4py-cu13 0.3.1, nvidia-nvshmem-cu13 3.6.5, pytest 8.4.2, apache-tvm-ffi 0.1.14.post1, cuda-core 1.2.1, cuda-pathfinder 1.5.4.

For a new devbox, follow the workspace rule to inspect the live NGC catalog immediately before requesting the newest explicit CUDA13.2 PyTorch tag; record that selected image/digest. The historical image is a reproduction identity, not permission to skip the live-image check. Retain the chosen container's Torch and record actual versions. Current source dependencies may require a different DSL; both arms must use the same tested stack.

Historical setup, in its dedicated checkout (adapt `MIXED_ROOT` to the new project; these commands have not been run):

```bash
cd "$MIXED_ROOT/flashinfer"
git submodule update --init 3rdparty/cccl 3rdparty/cutlass 3rdparty/nixl 3rdparty/spdlog
export BUILD_NVEP=0 BUILD_NIXL_EP=0 BUILD_NCCL_EP=0
export FLASHINFER_BUILD_NO_PIP=1 MAX_JOBS=8
unset PIP_CONSTRAINT
# Historical reproduction only; update the Torch pin for a new container.
cp "$MIXED_ROOT/harness/historical-runtime-constraints.txt" "$MIXED_ROOT/runtime-constraints.txt"
python3 -m pip install --disable-pip-version-check --upgrade-strategy only-if-needed \
  -c "$MIXED_ROOT/runtime-constraints.txt" \
  'nvidia-cutlass-dsl[cu13]==4.7.1' 'cuda-python==13.2.0' 'cuda-bindings==13.2.0' \
  'cupti-python==13.2.0' 'nvidia-cuda-cupti==13.2.86' \
  'nvshmem4py-cu13==0.3.1' 'nvidia-nvshmem-cu13==3.6.5' \
  'setuptools>=77' 'packaging>=24' 'apache-tvm-ffi>=0.1.11,<0.2'
python3 -m pip install --disable-pip-version-check --upgrade-strategy only-if-needed \
  -c "$MIXED_ROOT/runtime-constraints.txt" --no-build-isolation -e '.[cu13]'
python3 -m pip install 'pytest==8.4.2'
python3 -m pip install --no-deps \
  'apache-tvm-ffi==0.1.14.post1' 'cuda-core==1.2.1' 'cuda-pathfinder==1.5.4'
```

`harness/run.py` sets the historical 4over6 switches, fatal CUPTI warning, lazy CUDA module loading and four cache paths; captures commit/diff/full source hashes, package versions, GPU inventory, full logs, raw records and per-rank AUTO tactic receipts. It invokes the native current benchmark without changing its timing code. Its `--image` is required and records the caller's explicit tag/digest; it does not discover/verify the image itself.

```bash
python3 harness/run.py --source "$MIXED_ROOT/flashinfer" \
  --driver "$MIXED_ROOT/flashinfer/benchmarks/bench_cute_dsl_moe_distributed.py" \
  --output "$MIXED_ROOT/runs/glm5-candidate-mixed-only-short-a1" --arm candidate-mixed-only-short-a1 \
  --model glm5 --policy candidate-mixed-only --knobs auto --tactic-policy mixed-only \
  --cache-root "$MIXED_ROOT/compile-cache/candidate" --image "$SELECTED_IMAGE" \
  --tokens 32,4096 --warmup 3 --iters 100 --port 29671
```

For the baseline, use `--source "$MIXED_ROOT/baseline"`, the **same candidate driver path**, `--policy current-main-native-auto16-all --tactic-policy all`, and a correctly keyed compiled-code cache; choose a fresh output and port. `remote/policy_pair.sh` records the current serialized pair and deliberately reuses one correctly keyed compiled-code cache for both arms. Repeat with separate fresh output names for other arms/models. `--dry-run` only prints the command. The capture helper accepts only `--knobs auto`, and comparison rejects fixed-knob metadata, mismatched policy-wrapper hashes, or a uniform winner in the mixed-only arm. Earlier captures retain their frozen recipes and are not pooled with this policy.

## Correctness and first-use boundary

After solid gains are retained, qualify the final source with existing zero-tolerance W4A16 reference tests, plus focused mixed-cluster geometry/scheduler boundaries and actual nonzero fallback execution. Until then, limit new GPU correctness work to the minimum compile/liveness smoke. Preserve BF16-bit equality including signed zero. Final qualification should verify 4->2 and uniform degenerate cases, partial token/feature tails, random/skewed routes, empty/refill experts, both token-return paths, static/atomic paths if supported, and graph replay. A final performance result is not review-ready without required correctness checks.

Historical #6277: eight N32 EP2 cases + nine original epilogue EP4 cases = 17 logical cases / 52 rank-local passes. Supplemental standalone port (`HashInfer #14`, source `2ea143e05394768ad01ee0f79d99f0d857ea9fc1`) qualified GLM5 and K3, EP4/EP8, random/skewed routing, all 13 powers of two T1–4096, all16 tactics, O3/eager, two launches/tactic: 104 logical cases / 624 rank-local passes. This is **not** evidence for new cluster code and not upstream suite execution.

Cached compilation exposed a first-use race: one rank could launch while a peer was still zeroing freshly allocated symmetric workspace. The qualification harness used local `torch.cuda.synchronize()` **plus an EP process-group barrier after zeroing and before first launch**, retained one module-scoped runtime owner, and destroyed each case's layer/workspace. A delayed rank reproduced the race before the guard. This proves only collectively prepared launches; do not claim unsynchronized production first-use safety or change measurement timing to hide a race.

Prior sanitizer scope: B300 EP4/EP8 all16 tactics and both routes; memcheck/synccheck T1/T128/T1024, racecheck **T1 only**, 36 clean rank logs. Historical Compute Sanitizer2026.3 memcheck used `--check-tensor-ops no` for a legal 2CTA TMA false positive. Re-evaluate on the new runtime and record the exact exclusion; do not silently generalize the old exception or claim tensor-op checking. No old totals count toward new qualification.

## Selected final bounded static-mode trial

After the unchanged candidate3r full13 capture completes and its source/measurement receipts are frozen, the coordinating agent selected one final **GLM5 EP8 T64/T128/T4096** screen: fresh pristine-main **AUTO16/all** versus **mixed-only AUTO36**, comprising the existing18 atomic choices and18 copies using the existing static scheduler. The product catalog would be52; IKR remains off. Apply/sync only after the explicit idle/lock handoff. See [AUTO52 decision and source-release plan](experiments/AUTO52_MIXED_STATIC.md) for exact patch/source hashes and pending host checks.

The earlier preparation condition requiring PC evidence of work-ID or handoff cost was **not met**. This later, bounded decision tests established source behavior: static removes fallback registration, work-ID atomic claims and their broadcasts while retaining all common tile mapping, readiness and arithmetic. It is a hypothesis test, not a profile-derived diagnosis. It introduces no new tile, group, return-mode or math axis. Static may lose performance through uneven deterministic work assignment, and36 candidates add untimed AUTO preparation cost.

Keep the native driver/wrapper, routes/seeds, runtime, three explicit warmups,100 untrimmed cold-L2 rank-MAX CUPTI samples, and persistent-knob-cache0 unchanged. Both arms use fresh serialized EP8 workers and `separate-flashinfer-workspace-v1`, with source-specific FlashInfer workspaces and shared CuTe DSL/CUDA/Triton caches. Capture all candidate counts/list hashes and rank winners including scheduler mode. An atomic winner does not demonstrate benefit from static. Preserve this screen independently from candidate3r full13 and older iterations; do not pool samples or claim a full-grid gain from three points. Broader numerical/sanitizer checks remain deferred until retained gains, and historical static scheduler-record tests do not replace full-kernel qualification.

Release update: the full13 pair completed and Rubin reported idle/locks available at23:14:47UTC. Root applied the exact catalog/test patch and froze the separate static experiment at `f14e4bae9379703fd5693d8ee993faae23e130d5`, parent candidate3r, with [source receipt](evidence/candidate4s-commit-freeze.json). Kernel and native-driver bytes remain unchanged. Scoped pre-commit/diff checks passed; package-level host and GPU results must be recorded independently when available. Root authorized the selected pair, without changing the completed full13 source or evidence.
