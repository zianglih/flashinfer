# FC1 release-limit screen: recommend retention

The general FC1 ownership policy is supported by this bounded screen: the two affected frozen native winners improve **+4.923% (N3U EP4096)** and **+1.767% (N3U TP4096)**. The two unchanged controls are within repeat variation. Keep the complete four-row result below, including the negative MXFP8 row. Independent peer audit passed (`independent-peer-audit.json`); no commit/push was performed by this experiment owner.

## Source and scope

- Base: `6be4971b2dc3720f168510d09190e6519da38e2c`.
- Unstaged review: `flashinfer-swap-ab-fc1-release-review`, one file `flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py`, **17 additions / 10 deletions**.
- Candidate SHA256: `f41712327504ba6bc4c1c2c28aeb7d38536fa0d59400f9c977ddf2eb2f041e4a`.
- Full-index patch SHA256: `e65f35e6e4dbff3b6ab4785ccf7eb1738827c86f93b890d2e9486d360f538816` (`../fc1-release-limit-6be/candidate-full-index.patch`).
- Resolve one private maximum release width: capacity/2 for the variable-slab activation epilogue, 64 columns for the existing bulk epilogue. Feed it to actual accumulator storage and both automatic K-planning helpers. The existing preserve-overlap predicate is unchanged. No epilogue-body, public API, tactic, barrier, PDL or W4A16 change.
- This corrects the earlier proposal: FC2 False still preserves overlap through the bulk-output arm of `_select_k_steps`. The corrected helper retains FC2's limit in **both** actual setup and automatic K selection.
- All 514 source hashes were frozen and checked in both arms; only this kernel differs. Current frozen native winners acquire new eligibility at only the two N3U W4A4 points. Both use explicit FC1 K8, so their measured K geometry is unchanged. Future automatic-K configurations can choose differently and must report resolved K/stage geometry.

## Complete paired timings

Positive means candidate faster, `100 * (sqrt(C1*C2/(A1*A2)) - 1)`. Values are medians of 100 strict CUPTI samples per phase. CAAC is serialized on one physical GPU per job; C/A repeats remain visible.

|Model / mode|Tokens|Format|C1 µs|A1 µs|A2 µs|C2 µs|Speedup|C spread|A spread|
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
|N3U EP8|4096|W4A4|232.050|221.266|221.378|232.387|+4.923%|0.145%|0.051%|
|N3U TP8|4096|W4A4|384.306|377.443|377.538|384.018|+1.767%|0.075%|0.025%|
|K3 TP8|8192|PER-TOKEN|1026.633|1026.697|1026.329|1026.729|+0.016%|0.009%|0.036%|
|V3 TP8|8192|MXFP8|737.412|739.013|737.284|736.341|-0.172%|0.145%|0.234%|

The affected-pair geomean is **+3.333%**. The unchanged-control geomean is **−0.078%**; do not call that a meaningful slowdown or speedup. The unweighted four-cell geomean is +1.613%, which is a screen statistic, not a full-matrix performance claim.

CUPTI completion-frontier accounting attributes the N3U gains to FC1: **−11.088 µs EP** and **−6.640 µs TP** of exposed FC1 extension. FC2 moves +0.144 / −0.023 µs. These are completion-frontier extensions accounting for overlap, not sums of overlapping kernel durations. `evidence/components.json` preserves all stages and both controls.

## Qualification and limits

- Actual-source CPU proof: 4,704 FC2 capacity/eligibility cases, 21,150 K-selection requests, and 24,870 actual storage/output states are identical. All six kernel-legal operand/scale combinations, legal M/N tiles, both K steps, native K/alignment variants, CLC and fitting explicit stage budgets are covered. Metadata depths are a finite sample with a separate algebraic equivalence proof. The naive global widening changes 170 FC2 K choices; the corrected implementation changes none.
- Scoped pre-commit (including mypy/ruff), syntax, and diff checks pass. Formatting left the measured kernel hash unchanged.
- **39 existing exact cases per arm**, plus **4 candidate explicit-overlap=True cases**, pass. The extra four force repeated work tiles and both accumulator phases at the newly admitted 96-column span, for one/two CTA and M512 virtual-channel ownership, ordinary/per-token output. Current legal K4/K8 layouts newly admit 96, not128 columns.
- Preliminary automatic-K/explicit-depth gate: all **13 FC2 PTXs byte-identical**, 11 CUBINs byte-identical. The other two only rename descriptor register pairs UR16:17 and UR18:19 at 12 operands; order, control words and resources match. It includes the 128-stage CLC metadata counterexample. No FC2 kernel launches in this preliminary diagnostic.
- Paired exact gate: 76 kernel pairs; all **37 FC2 PTXs byte-identical**, 36 CUBINs byte-identical, the remaining pair has the same validated descriptor-register rename. All 212 qualification prelaunch resource guards pass.
- No new spill sites. Two unchanged synthetic M512/N128/K8 MX-activation FC1 cases already have STACK168 and 21 LDL/21 STL sites in both arms. The ten newly eligible FC1 captures increase static instructions by1,643–3,595 (and4–7 branches) because the existing cyclic epilogue is selected; this remains a useful future simplification target. All FC2 qualification captures have zero stack/local.
- Performance: all 16 runtime guard receipts / 32 loaded MoE kernels pass, all runtime LOCAL bytes are zero, and normal compiler options are unchanged. All 1,600 raw sample arrays, routes, fixed tactics, source hashes and derived ratios were independently recomputed by `audit_raw.py`.
- Stock clocks were untouched. All 64 timing quartiles have NVML samples. N3U and K3 quartile medians are2032MHz; V3 MXFP8 varies1987–2032MHz. Its−0.172% result is inside the0.234% candidate repeat spread. No cells were discarded.
- This is a four-cell screen, not a fresh full matrix; no sanitizer. It is independent of the native-FC1 epilogue prototype. If composed with another retained change, qualify the composed source and recompare affected winners.

## Reproduction and evidence

C3 `fi-gather-6be-1029`, namespace `ziangli`, B300 SM103, GPUs1/2. Image `nvcr.io/nvidia/pytorch:26.05-py3`, AMD64 digest `sha256:ca73b4795f0d3ae27e9cd81b1b1f7fc6c0a129f7d51a359d2326e95af48a3d`; driver595.91.07, CUDA13.2.78, CuTe DSL4.8.0, Python3.12.3. Runtime details: `../devbox-recovery-6be/environment.json`.

The benchmark uses public `benchmarks/bench_moe_deepseek.py`, unfused swap-AB, cold-L2 CUDA graphs,10 warmups,100 strict CUPTI samples, no AUTO, and input quantization for the NVFP4 family. `evidence/perf-config.json` and each job receipt contain exact commands, frozen winner cache manifests, environment, physical GPU UUIDs and all source hashes. The CAAC engine's AST matches the earlier accepted engine except descriptive strings (`engine-equivalence.json`). Persistent native/CuTe compilation caches and the canonical whole-data symlink were retained.

- Full timings: `evidence/{cells.csv,table.md,summary.json,components.json}`.
- Raw audit: `raw-audit.json`; all source/tactic/route/sample/guard checks pass.
- Raw timing archive: `gate-evidence.tar.gz`, SHA256 `c6ecd3bbee90d4f7add71bfe022bc2ae248c4f01ef3e4e2bd2b2edef7ac2f9a9`;121 files hash-verified.
- Qualification: `../fc1-release-limit-6be/evidence/{qualification-summary.json,fc2-identity.json,codegen-comparison.json}` and `qualification-local-audit.json`.
- Qualification archive SHA256 `fe208f81e575439e2d9e2a51fc455d464351860d9c7a07d8c1a18fad7c73686d`;1,108 files hash-verified.
- Corrected proposal and CPU rationale: `../fc2-prefix-cache-d9/FC1_ONLY_PROPOSAL.md`; actual source proof: `../fc1-release-limit-6be/audit_actual_source.py`.
