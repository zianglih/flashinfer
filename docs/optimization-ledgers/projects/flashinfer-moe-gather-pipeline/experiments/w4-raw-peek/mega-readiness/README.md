# Held MegaMoE validation for raw TMA readiness TEST

No candidate source, GPU reservation, remote operation or launch is created by this preparation. Retained source is `2b8eb9d8`.

## Shared scope

`_MegaMixedInput` subclasses `Sm100W4A16GroupedGemmKernel` without overriding `_transform_tile`. The proposed replacement of its two `consumer_try_wait` peeks therefore affects split FC1/FC2 and Mega FC1/FC2. Mega constructs an ordinary `PipelineTmaAsync` raw pipeline and calls the shared transform at lines1597/1607 with its explicitly padded K extent. The dense W4 class has a separate transform method and is outside this change. No split-only option or public policy knob is needed. All blocking waits, releases, arrivals, phases and decoded-output lookahead must remain unchanged.

## Existing exact/native qualification

Reuse `experiments/w4-tail-dequant/mega-qualification/{capture_exact,run,analyze}.py` in a new leaf. It calls the repository's zero-tolerance W4 Mega helper under `MEGA_NO_DIST=1`, with H/I256/256 and384/640, experts4/topk2, tileN32, external deterministic combine. Capture the actual returned compiled library and preserve compiler arguments/options. Record actual CTA configuration rather than claiming coverage from the test name. The original helper, reference and distributed benchmark are byte-identical to the earlier GLM5 campaign.

Adapt only the old hardcoded source base, paths and node binding after source freeze. Seal current full-source control versus exactly the candidate kernel delta, and use reduced per-process source guards bound to those manifests. Verify exact output, LOCAL0, unchanged resources and actual native TRY→TEST at the intended raw-peek sites, with common waits/releases still present. A failed compile/resource/numerical gate stays explicit. Existing helper coverage alone is not distributed race qualification.

## Fresh distributed causal check, conditional on qualification

Reuse the completed `validation/glm5-r2-attempt3` harness, 13 frozen choices and104 eight-rank routing fingerprints; hashes are in `readiness.json`. Do not reuse old timing as the causal control. GLM5 is H6144/I2048/E256/top8/SwiGLU/EP8, eight B300 GPUs. Preserve the historical native contract: **three warmups**,100 strict-CUPTI graph/cold-L2 samples per token/phase, serialized C1/A1/A2/C2, no autotune or event fallback. Each sample is the maximum across ranks for that same iteration. Pool200 samples per arm for the reported median; keep all52 records/5200samples,416tactics/routes and all negatives. Tokens1/2 remain raw but are excluded from retention aggregates. This GLM estimator differs from the split-screen phase-geomean estimator and must stay labeled.

Use the recovery node and current release C++ cache cohort, not the stale `fi-gather-pipeline-1030` label from the prior script. Bind recovery readiness/cache-ready receipts by path+SHA and current ELF hashes, and refresh no-op Ninja/library/idle receipts before launch. Keep independent source-keyed CuTe cache paths and the existing persistent C++ cache. Source and native compiler options must stay identical apart from the qualified kernel delta.

Keep the established host rendezvous around compile/resource observation: otherwise a driver query can stall behind peers entering NVSHMEM work. Create every phase/rank compiler dump directory before compilation, retain the established exception-before-collective-cleanup hook and bounded TERM/KILL watchdog, and never let artifact failure become a false native qualification. No historical artifact misses or benchmark failures are deleted or imported into the new data.

All eight GPUs require a fresh parent reservation after current independent work finishes. Setup readiness is not authorization to launch. No sanitizer, new test fixture, new tactic, independent retuning, or historical baseline refresh is planned.
