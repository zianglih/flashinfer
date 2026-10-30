# W4 transform cutoff publication

Retained commit: `c1ac8ce7341039db65195b99445fcdeb193cf226`. Fresh measurements used immutable `2b8eb9d8` plus the qualified `cbef9186` W4 kernel; the committed kernel is byte-identical. Earlier evidence retains its actual revisions and native-library cohorts.

- **Fresh causal result:** 39 primary C/A/A/C cells (15,600 samples) across V41F TP4, K3 TP8 and N3U TP8. The 33 cells excluding tokens1/2 give +0.159% GM: decode +0.422%, middle +0.339%, prefill −0.459%. All15 decode points improve; all8 negative retention cells remain. Retained as a general predicate simplification with the adverse prefill tradeoff, not a general throughput win.
- **Separate diagnostic:** two same-GPU A/C/C/A cells (800 samples). V41F TP4K reverses −2.368%→+1.445% with control drift. N3U TP16K stays adverse −0.891%/−0.966%, with variable clock/control trajectories. These rows are not pooled with or substituted for primary rows.
- **Full view:**39 fresh primary +429 exactly preserved prior candidate row dictionaries =468. Reuse consists of364 unchanged swap rows and65 W4 rows selecting unchanged aligned/all-live graphs under their actual recorded native tactics. Native equality evidence is representative, not an exhaustive recompilation. The detailed104-cell geometry/constexpr enumeration is in `source/publication-reuse-proof.json`.
- **Historical baseline:** full retained heatmaps reuse measured `326c4a79`, production-equivalent to `82254e20`. They are not fresh paired comparisons against2b8. The396 displayed cells have +0.304% historical GM and166 negative cells, all preserved. External TRTLLM/non-swap/pre-PR W4 denominator fields are unchanged. These historical red cells alone do not isolate a particular commit's regression.
- **Timing/resource evidence:**93,600 selected candidate samples (7,800 fresh/85,800 reused),1,136 loaded native function records with LOCAL0. Current mixed view has3,744 clock quartiles,90 exceptions and0 missing. Primary causal has55/624 exceptions, diagnostic14/32; no unavailable windows in either. Original historical evidence, including earlier missing windows, remains untouched and archived.
- **Native gate:**14 fresh exact calls plus6 matched retained controls,26 kernel pairs. No resource growth. Four K640 FC2s remove ULEA/USHF per stage and3 total non-NOP instructions; K320 removes2. Partial FC1 total counts remain unchanged; one-stage compare polarity changes are recorded. Aligned/all-live and Mega padded-K native specializations remain byte-identical where qualified. No extra distributed timing is needed for those unchanged Mega images.

## Environment and contract

Two B300 GPUs on an eight-B300 recovery node; `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2.1/compiler13.2.78, driver595.91.07, CuTe DSL4.8.0, CUPTI Python13.2.0/library13.2.86, PyTorch package `2.12.0a0+5aff3928d8.nv26.5.50603568`. Exact source, routing, frozen-choice, actual-default-resolution and release-library/Ninja guards are preserved. No retuning, event fallback, clock lock, sanitizer or sample filtering.

Each phase uses10 warmups and100 cold-L2 CUDA-graph CUPTI samples. Each arm uses the geometric mean of its two phase medians; speedup is100×(control/candidate−1). Kernel durations overlap under PDL; component extensions are reported separately. Repeat spreads are descriptive, not statistical confidence. Public commands and exact observer/wrapper arguments are in the body draft and raw phase receipts.

## Contents

- `tail-cutoff-causal/`: all39 primary rows, all phases/components/clocks and actual resource joins; `tail-cutoff-acca/` contains only the separate2-cell diagnostic.
- `report/`, `external/`, `plots/`:468 full rows, unchanged historical denominator fields, mixed provenance, four historical full heatmaps and one fresh33-cell causal heatmap. Tokens1/2 remain raw but are omitted from every plot.
- `completed-tables/`:15 unchanged-native-printer tables across16 groups, with468 CuTe records (39 fresh/429 reused) plus390 historical TRTLLM records. All54 original final-pass stdout suffixes reproduce byte-for-byte before family completion. Tables use final pass; heatmaps use two-pass aggregates. Older reused BF16 records predate strict per-record timer guards. Unsupported/missing cells remain N/A.
- `stdout/`:154 original logs (12 new primary CAAC logs plus142 inherited); no parsing/reconstruction. All8 diagnostic logs are retained in the separate raw evidence leaf.
- `source/`, `experiments/`, `audits/`, `runtime/`, `evidence/`:source integration, actual-tactic reuse proof, exact/native/raw/clock receipts, helper scripts, original records and runtime boundaries.
- `previous-paired-situ-publication/`:every member of the sealed prior publication preserved byte-identically, without embedding a nested archive. Earlier causal tables and GLM5 comparison remain unchanged.

The inactive review worktree and branch were retired only after exact source/patch/status checks. Canonical commit and remote publication are owned by the parent. This local publication does not modify the previous publication, baseline assets or GitHub. The XZ allowlist excludes draft body, preview archives and publisher transport files.
