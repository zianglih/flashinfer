# MoE gather pipeline optimization

Optimization work remains **paused**. The user requested integration and a
performance refresh after the [retention decision](RETENTION_REVIEW.md).
Fork PR #9 is merged into upstream PR #7290's branch at
`a620ce7790b32f7f0ae524a811417d2c6cee1152`, tree-identical to retained `8bc69ee4`.
The original W4 scale-byte helper is restored; all other retained changes remain.
Upstream PR #7290 is open. See the [merge receipt](upstream-merge-refresh/merge-receipt.json)
and [fresh benchmark plan](integration/pr7290-refresh-20261030/PLAN.md).

The integration refresh is complete: seven exact smoke calls passed and all 468
supported candidate cells were freshly measured with 93,600 CUPTI samples.
The unchanged historical external baselines were reused. Both heatmaps, the PR
body and four existing native-table comments are updated and verified by readback.
See the [final handoff](upstream-merge-refresh/FINAL.md). No new optimization
experiments are scheduled.

- Source: independent clone `flashinfer/`, branch `codex/w4a4-split-dynamic-n`.
- Frozen control: `82254e206a44b95d9925e4594fac936731f80d21`.
- Scope: Blackwell swap-AB and W4A16; V3, V41F, K3, N3U; EP and TP;
  all supported quantization modes. FC1 gathers original activations; FC2
  retains regular TMA.
- Retention: general policies, unchanged tactic space and numerical contract.
  Do not retain neutral changes that add kernel complexity. Slight prefill
  regression may be justified by decode gains. Include negative results.
- Timing: public `benchmarks/bench_moe_deepseek.py`, strict CUPTI, cold L2,
  CUDA graphs, 10 warmups and 100 samples. Run tokens 1 and 2 but exclude
  them from retention and plots. Include NVFP4 input quantization.
- Historical external baselines and tools remain in
  `../flashinfer-w4a4-split-dynamic-n/cleanup-20261030/performance/`.
  Those results were measured at `326c4a79`, with equivalent production
  kernels to the frozen control. Do not relabel historical measurements.
- Active experiment source changes stay unstaged until selected for retention.
  Use immutable source snapshots during GPU runs.

## Runtime

Current node: `fi-gather-pipeline-resume-1030`, same eight C2 B300 GPUs and
explicit image below. The current native-library cohort and cache bindings are
in [the cache recovery record](experiments/sf-coordinate-cache/CACHE_RECOVERY.md):
`moe_utils` ELF `046552b8`, with the other three C++ modules unchanged. Use its
`cache-recovery/readiness-current.json` and `cache-ready-current.json` receipts.
Earlier raw records retain their original cohorts; do not reuse their timing
phases as current controls. New source arms need private DSL/cached-ops roots,
canonical generated/CUBIN paths, and actual normal-load/no-op verification.

Requested C2 B300 devbox `fi-gather-pipeline-1030`, namespace `ziangli`, eight
GPUs, bare, explicit `nvcr.io/nvidia/pytorch:26.05-py3`. NVIDIA's live NGC tag
catalog was checked on 2026-10-30. The 26.05 release supplies CUDA 13.2.1;
26.06 and 26.07 release notes identify CUDA 13.3. Later release-note pages
were unavailable through the browser. Record actual runtime and image digest
after allocation. Persist native C++ and DSL caches under cluster storage.

## References

- [Upstream PR #7290](https://github.com/flashinfer-ai/flashinfer/pull/7290)
- [Historical fork PR #8](https://github.com/zianglih/flashinfer/pull/8)
- [NGC tags](https://catalog.ngc.nvidia.com/orgs/nvidia/-/containers/pytorch/-/tags)
- [26.05 release notes](https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel-26-05.html)
- Existing local ledgers: `fc1-gather-20261028`, `element-scale-ownership-20261029`,
  `upstream-integration-20261029`, and `cleanup-20261030` in the prior project.

## First qualified experiments

The first compact sweeps completed with 100,000 audited CUPTI samples. They
support instruction cleanup, not a material end-to-end speedup claim:

| Candidate | Retention cells | Geometric mean change |
|---|---:|---:|
| FC2 bulk commits owned by the existing writer warps | 84 | +0.076% |
| W4A16 packed-scale selection folded into the existing PRMT, R2 | 24 | +0.082% |
| Compile-time MMA scale-byte selectors | 30 | -0.055% |

All negative rows remain in the reports. Some large EP prefill rows have
substantial clock/repeat variation and need component attribution before a
non-regression conclusion. The initial W4 R1 variant repacked two-scale
fragments, added FC2 instructions, and is superseded by R2; its timings are
historical experiment evidence only. W4 R2 leaves those FC2 cubins unchanged.

- Source audits and proof/codegen receipts: `audits/` and `validation/`.
- Full compact reports: `evidence/r1-compact/1793358417877966000/report/`,
  `evidence/r2-w4-compact/1793358674260664000/report/`, and
  `evidence/static-sf-compact/1793358674260782000/report/`.
- Independent timing/source audit: `audits/compact-pair-peer.json`.
- Fresh NCU and CUPTI attribution: `profiling/v3-tp-mxfp8-16k/`.
- The shared W4 utility passed the fresh GLM5 MegaMoE comparison in
  `validation/glm5-r2-attempt3/RESULTS.md`: +0.032% overall is neutral amid
  repeated-phase variation, with six fewer shifts and unchanged resources.
- The composed source passed six exact calls, including actual CLC launches
  and both W4 layouts: `validation/composed-exact/RESULTS.md`.
- Two simpler fixed weight-cache policies were rejected after measured losses:
  `experiments/cache-priorities/RESULTS.md`. Their review copies are removed.

These are separate experiments. Do not multiply their ratios or present them
as measured performance of a combined source revision.

## Historical fork publication before the selected revert

[Fork PR #9](https://github.com/zianglih/flashinfer/pull/9) published the retained
`c1ac8ce7341039db65195b99445fcdeb193cf226` checkpoint. That full view has 468 cells:
39 fresh W4A16 TP measurements and 429 source-qualified reused rows. Five
heatmaps, four existing native-table comments and the 97.2 MB XZ archive are
published under immutable artifact commit `7961a1f13b620e45741fd7057a72f1f248789448`.
`publication-w4-tail-cutoff/` records exact PR/comment readbacks, HTTP/image/archive
checks, primary CAAC and separate diagnostic ACCA evidence. The fresh cutoff
comparison is +0.422% decode, +0.339% middle and -0.459% prefill; N3U TP16K
remains about1% adverse in both orders. This is a general predicate simplification,
not a broad throughput claim. Historical measured revisions and the recovery
native-library cohort remain explicit. Upstream PR7290 remains unchanged.

The previous SiTU publication at2b8 remains intact in `publication-w4-paired-situ/`
and immutable artifact commit `00d53906d316d1bbd7430cfb2789ea3108d95d31`.
For commit attribution of historical W4 prefill red cells, see
`audits/w4-prefill-attribution-c1ac.md` and its linked original trace; do not infer isolated commit effects
from mixed-session heatmaps.

Initial fork revision `02de7785c10847b3528340840bed40bd405d85b4` contained the
three instruction cleanups above: 11 additions and 7 deletions across the
swap kernel and shared W4 helper.

Its initial combined refresh covered 468 cells, 93,600 CUPTI samples, and 1,088
zero-local-memory main functions. Historical retained-baseline geometric mean
is +0.059%, effectively neutral. Four heatmaps, 15 native tables, 62 untouched
stdout logs, and source/provenance receipts are published under the immutable
artifact commit `fa66f71f9ddfaa814089cfa2d0a5d0a75fbded4c`. The four PR comments
contain the native table blocks verbatim; `publication/pr-verification.json`
records their verified readback.

Current source/ownership state:
- Reserved CLC metadata zero-padding is rejected before timing and its review
  copy is retired. Native STS consolidation is offset by zero materialization;
  all four exact calls/six native pairs pass with unchanged resources. Evidence
  remains in `experiments/clc-info-vector/`; production metadata is unchanged.
- Initial-ring-fill weight/SFA cache priority is rejected and its review copy
  is retired. Full56 CAAC is −0.091% overall/−0.163% prefill,34 negatives;
  11 FC2 register increases (+2–16), LOCAL0 and unchanged driver CTA capacity.
  All22,400 samples,59 clock exceptions/two missing quartiles and exact R0/R1
  source/native evidence remain in `experiments/startup-weight-cache/`.
- `flashinfer/` is clean at pushed `c1ac8ce7`.
- W4 transform cutoff is retained; the completed review copy is retired.
  `experiments/w4-tail-cutoff/` preserves qualification and all39 primary rows.
- Paired 4over6 error scoring is rejected and its review copy is retired. The
  exact/native gate and 26 reference tests passed, but the full 42-cell screen
  regresses CuTe PER-TOKEN −0.3062% and TRTLLM PER-TOKEN −0.1183%, including
  tight normal-clock N3U TP prefill losses up to −3.694%. All 16,800 samples,
  23 negatives and clock gaps remain in [the experiment results](experiments/paired-4over6-error/RESULTS.md).
  Source, patch and [retirement evidence](experiments/paired-4over6-error/retirement/receipt.json)
  are preserved; canonical c1ac and published evidence are unchanged.
- Pre-wait alpha prefetch is rejected and its review copy is retired. The56-cell
  screen regresses overall -0.216% and prefill -0.375%, with26 negative cells,
  including tight TP per-token losses up to -2.996%. The selected20 exact arm
  results/30 native pairs had no register growth; the full screen includes four
  FC2 register increases, with LOCAL0 and unchanged occupancy. All22,400 samples,
  58 clock-exception quartiles and one missing quartile remain in
  `experiments/alpha-prefetch/`; source/patch and retirement receipts are preserved.
  This closes the earlier unfinished pre-wait mechanism separately from rejected
  post-wait alpha reuse. No alpha change was retained.
- SF/payload interleaving was rejected after all56 cells: -0.246% overall,
  -0.413% prefill,32 negatives. Its review copy is retired; all22,400 samples
  and qualification/retirement evidence remain in `experiments/sf-payload-interleave/`.
- Terminal-PDL deletion was rejected after native register growth and repeated
  performance losses. Its source copy is retired; evidence remains in
  `experiments/terminal-pdl/`.
- W4 tail dequantization was retained as `bf072d26`: all 24 token 4–512
  cases improve, with six prefill losses up to 0.75% explicitly accepted. The
  completed source copy is retired; all 39 affected cells and 15,600 samples
  remain in `experiments/w4-tail-dequant/`. A separate publication refresh
  preserves the original historical evidence. That earlier refresh links plots
  and native tables from artifact commit `a9a53858`; the verified 17.9MB XZ
  package preserves all raw data. See `publication-w4-tail/pr-verification.json`.
- Integer-carried FC1 stores are retained as `49c91adf`: all 18 quantized
  N3U prefill cells improve, with the small per-token EP losses preserved.
  All 104 affected cells and 41,600 samples remain under
  `experiments/fc1-integer-store-performance/`. The completed source copy is
  retired. `publication-integer-store/` contains the verified full refresh,
  published as artifact commit `c6f93723`; native table comments are read back
  exactly. The transaction-width follow-up was rejected as neutral with extra loop
  complexity; its completed review copy is retired. Native N3U TP MXFP4x8
  decode diagnosis is complete under `profiling/n3u-tp-mx4x8-32/`.
- Fixed-cache, static-SF, and adjacent-store review copies are retired.
  Their patches and evidence remain in `experiments/`. The adjacent-store
  experiment introduced local-memory lowering without wider stores and was
  rejected before timing.
- Original devbox disappeared during the readiness screen; its cause is unknown.
  Replacement `fi-gather-pipeline-recovery-1030` is on the same C2 B300 node and
  image, with persistent source/cache/run data intact. Exact dependency recovery
  passed under `runtime/recovery-1030/`. Routing and MoE helper libraries rebuilt
  under unchanged release commands; their old and new ELF identities are explicit.
  The parallel infra devbox was
  previously released. Persistent C++ caches remain on cluster storage.

The earlier swap paired-SiTU review is retired. Its source/native and full
performance evidence remain under `experiments/swap-paired-situ/`; the historical
qualification was based on49 with the disjoint W4 composition recorded separately.

W4 paired SiTU was retained as `2b8eb9d8`: 26 paired K3 EP/TP cells,
10,400 samples, and 12 exact calls. It removes scalar arithmetic and simplifies
the existing helper; +0.275% over 22 retention cells does not establish a broad
speedup. Nine primary negative cells and a separate six-cell ACCA repeat remain
in `experiments/w4-paired-situ/`. The full publication refresh is verified
under `publication-w4-paired-situ/`; its completed source copy is retired.

Alpha reuse was rejected: +0.011% over 56 cells is neutral, while K3 TP
per-token prefill lost 1.065% with tight repeat spread. Its source copy is
retired and evidence remains in `experiments/epilogue-alpha-reuse/`.

The W4 partial-group follow-up was rejected after its full V41F TP sweep:
only +0.217% across retention cells, insufficient for 57 added source lines and
extra native dispatch. Prefill clock variation and negative results are
preserved in `experiments/w4-partial-group/RESULTS.md`. Its source copy is retired.
Distributed gather-barrier initialization was also rejected: +0.031% across
56 points is neutral despite the startup instruction reduction. Its added lane
mapping did not earn retention. Evidence remains in
`experiments/gather-barrier-init/`; the source copy is retired.


Early MMA readiness was rejected after all 56 paired points: −0.036% with
36 negative cells, extra query/state, and some register growth. Original and
recovery jobs are kept as separate native-library cohorts; both raw replays and
the disjoint union passed. See `experiments/mma-readiness/combined56/` and
`audits/mma-readiness-combined-data-root.json`.

The synchronization lineage audit (`audits/retained-sync-lineage.json`) checks
226 primitive calls and their enclosing branches/loops against the original
fork base. The retained writer-only bulk commit is the only changed ownership;
W4 tail skipping nests a readiness hint under an equivalent final-stage guard.
Earlier dependency audits remain applicable, with these explicit differences.

## Active review copies

No active source review remains. The SF pointer-shuffle candidate was rejected at the native gate: two wide FC1s had driver local48/16 (native stack48/16) before invocation; narrow G1 passed with unchanged native images. Its exact source/patch/helpers and all evidence are preserved in `experiments/sf-pointer-shuffle/`, including retirement. The earlier coordinate-cache review is also retired; immutable profile/source/cache artifacts remain. Main stays clean at `c1ac8ce7`; current ownership is recorded in `runtime/active-experiments.json`.


The W4 output-ring candidate was rejected: full104-cell primary timing was
+0.118% across88 retention cells, insufficient to justify explicit wrap control
for1–4 fewer native instructions. The separate six-cell ACCA diagnostic preserves
the K3 prefill loss and its variation; no primary row was replaced. Its review
copy is retired, and all evidence/plots/native tables remain under
`experiments/w4-output-ring/`.
