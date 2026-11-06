# Composed-source validation and full swap refresh

Frozen source: clean retained `1b0f1f69` plus the four-file W4 composition. The manifest guards514 files including the new shared `inline_ptx.py`; tracked patch SHA `abaeac5e6a88c78eec9a04731b48ecaee573f0e00a3c5a24a000158323245899`. No source changes were made by this validation task.

- C3 `fi-gather-opt-1029`, B300/SM103, `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2, CuTe DSL4.8.0.
- Existing exact gate: **17 passed**, zero failure/error/skip (7 public smoke, 8 local dtype/CLC cases, 2 half-warp cases). No sanitizer.
- Additional codegen driver: two existing public exact tests passed on both clean and composed sources, covering one-CTA SiTU MXFP8 and two-CTA SwiGLU W4A8. All four FC1/FC2 kernels have byte-identical SASS and identical resource usage. Swap Gather4 continues using `shared::cta`, including two-CTA MMA, with its existing relay.
- Raw exact receipts, JUnit, logs, PTX/CUBIN/SASS/resources and complete source manifests are in `evidence/`. Codegen diagnostic flags were used only for this gate, never for performance timing.

| Phase | CTA group | Route N | SASS | Resources |
|---|---:|---:|---|---|
| FC1 | 1 | 16 | identical | identical |
| FC2 | 1 | 16 | identical | identical |
| FC1 | 2 | 128 | identical | identical |
| FC2 | 2 | 128 | identical | identical |

## Fresh full refresh

Remote root: `/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/fc1-gather-20261028/optimization-next-20261029/composed-w4-full`.

23 jobs cover28 supported model/topology/dtype arms ×13tokens =364 cells; W4A16 is excluded because its separate104-cell campaign is complete. Tokens:1,2,4,8,16,32,64,128,256,512,4096,8192,16384. Original frozen winners are used for1–512; all84 native-prefill winners for4096/8192/16384, including losing K3 selections, are preserved. No tuning or baseline rerun.

Fresh AA uses100 strict CUPTI samples per pass/cell, 10warmups and cold-L2 CUDA graph replay, for72,800 new samples. NVFP4 arms include the input activation quantizer. All swap arms use the public functional API and unfused finalize. Source hashes, exact patch, routing identities, frozen tactic hits, timing mechanism, sample counts, physical GPU UUID within each AA job, and actual CUDA runtime register budgets (120/128/256) are checked. Normal compiler settings and both persistent native caches and explicit persistent CuTe cache are retained.

**Evidence boundary:** This is a replacement node. Historical baseline timings are used only for the end-to-end scoreboard; no same-GPU causal comparison against those older measurements is claimed. Reporting bands: decode4–64, middle128–512, prefill4096–16384; tokens1/2 remain measured but excluded from reported retention statistics.

Preparation and launch receipts are `full-preparation.json` and `full-launch.json`. `status_full_remote.py` is a read-only monitor. Campaign uses GPUs0–4; remote sources are frozen and independent of subsequent Git commit operations.

## Completion and publication handoff

- All23 jobs /46 AA phases completed. Independent CPU audit verified364 cells,72,800 strict-CUPTI observations, frozen routes/tactics, normal compiler/cache settings and864 actual-runtime register checks. Every captured FC1 has zero CUDA runtime local-storage bytes.
- `published-source-equivalence.json` proves all514 frozen source files exactly match pushed `475cae6b28a536e24aa8da2ed488d0f00fb5305b`.
- Full raw refresh: `full-evidence/`; candidate-only audit: `full-report/{cells.csv,summary.json,runtime-guards.json}`.
- Primary5-dtype comparison, using historical `d35fcfda` controls for every dtype and current468 candidates (including W4): `primary/report/{cells.csv,summary.json,ep-table.md,tp-table.md,raw-a2-compact.md,provenance.json}`. Compatible with the existing `composed/full-validation/plot_publication.py` renderer. W4 is now included in aggregates. EP decode/middle/prefill/overall: +1.45/+0.58/−0.62/+0.65%; TP: +1.61/+4.11/+12.84/+5.25%.
- Supporting9-column historical TRTLLM/non-swap comparisons: `publication/{ep,tp}/{summary-cells.csv,summary-table.md,native-a2-output.md,provenance.json}`. All88 baseline raw hashes and baseline values/status/fused markers are unchanged.
- W4 raw candidate passes come from the completed104-cell `full-20261029/w4a16-full` campaign.513of514 source files match the published composition; the sole difference is its unexecuted swap kernel. The W4 kernels, wrapper, common PTX helper and every other guarded dependency match exactly. That campaign's fresh same-GPUfb66 control remains separate support; the primary table uses d35 and the external9-column W4 field uses its historical pre-PR layout baseline.
- Repeatability limitation: AA spread is7.45% for N3U EP MXFP8 T16384 and7.03% for K3 EP MXFP4x8 T16384; next largest3.47%. Exact point-level spreads are retained. These historical-baseline scoreboards do not establish same-GPU causal speedups.
- No kernel source edits, GitHub writes, sanitizer, or external baseline reruns were performed by this validation task. GPUs0–4 were released after completion.
