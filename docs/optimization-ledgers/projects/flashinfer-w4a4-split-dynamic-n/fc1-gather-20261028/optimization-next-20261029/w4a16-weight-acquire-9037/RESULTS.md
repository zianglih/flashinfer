# W4A16 weight producer acquire cleanup

**Recommendation: retain for instruction sanity, without a speedup claim.** The change removes14lines and2–13static instructions per captured kernel, including one branch and1–2redundant barrier try-waits. The bounded screen is effectively flat on decode and slightly negative/noisy on prefill; the two largest unclear losses shrink in separate repeats and do not demonstrate a consistent~2% regression. Parent approved retention on this basis; integration/push is handled by the parent.

- Base: `9037f6d46fcb45eac04be04c182104336c8b1e7c`; candidate kernel SHA256 `de042712ac4fcab0f14eb5f870824416f65dce15e2243198b28ffb4226ac0d58`.
- Source: only initial/end-K weight-pipeline peeks and the cached token argument are removed. Direct `producer_acquire` still waits for the requested empty phase. Count/reset, weight/scale copies, dequant peeks, PDL, stage publication, scheduling and terminal drains are unchanged.
- Local review: `flashinfer-w4a16-weight-acquire-review`,14deletions unstaged. All514guarded source files equal the measured source. Scoped pre-commit (including mypy and Ruff) passed without changing source bytes.

## Qualification

-33existing W4A16 accuracy cases passed,0failed/skipped. Source-bound test receipt and complete output are in `qualification-evidence/qualification/exact/`.
-Four frozen native tactic pairs compiled in both arms, FC1+FC2:16kernels, unchanged launch register allocation, zero local storage and no LDL/STL. TMA/MMA instruction counts unchanged. Captured kernels were not launched in this codegen diagnostic.
-Full original16-cell screen:4models×EP/TP×tokens8/4096, then a separately preserved2-cell repeat. Total40complete C-A-A-C phases,7,200strictCUPTI samples,40runtime guard receipts and144loaded kernels; all guards pass and all reported local storage is zero.
-Same frozen routes/tactics, public functional API, no fused finalize,10warmups/100cold-L2 CUDA Graph samples per phase. Legitimate cached default tactics are preserved. No retune, clock/power changes or sanitizer.
-Each cell uses `100*((C1+C2)/(A1+A2)-1)`, the arithmetic mean of each arm's two phase medians, matching the earlier W4 CAAC convention. Cross-cell summaries use the geometric mean of these ratios. All four phase medians and quartiles remain in JSON.

## Original16-cell screen

| Model/topology | Tokens | Control µs | Candidate µs | Change | Control repeat spread | Candidate repeat spread |
|---|---:|---:|---:|---:|---:|---:|
| K3 EP | 8 | 84.424 | 83.992 | +0.514% | 0.209% | 0.057% |
| K3 EP | 4096 | 528.145 | 535.827 | -1.434% | 0.291% | 3.179% |
| N3U EP | 8 | 51.153 | 51.136 | +0.033% | 0.064% | 0.125% |
| N3U EP | 4096 | 391.265 | 391.075 | +0.049% | 0.221% | 0.148% |
| V3 EP | 8 | 68.072 | 68.192 | -0.176% | 0.259% | 0.048% |
| V3 EP | 4096 | 279.666 | 278.362 | +0.468% | 0.080% | 0.063% |
| V41F EP | 8 | 50.904 | 51.112 | -0.407% | 0.094% | 0.219% |
| V41F EP | 4096 | 433.851 | 433.227 | +0.144% | 0.255% | 0.174% |
| K3 TP | 8 | 87.689 | 87.648 | +0.046% | 0.018% | 0.111% |
| K3 TP | 4096 | 702.331 | 707.219 | -0.691% | 1.734% | 2.961% |
| N3U TP | 8 | 66.072 | 66.192 | -0.181% | 0.120% | 0.048% |
| N3U TP | 4096 | 546.499 | 548.034 | -0.280% | 0.035% | 0.281% |
| V3 TP | 8 | 57.168 | 56.960 | +0.365% | 0.057% | 0.112% |
| V3 TP | 4096 | 481.243 | 480.435 | +0.168% | 0.117% | 0.167% |
| V41F TP | 8 | 63.776 | 63.808 | -0.050% | 0.002% | 0.099% |
| V41F TP | 4096 | 559.403 | 570.371 | -1.923% | 0.232% | 1.299% |

Original screen geometric means: decode **+0.018%**, prefill **-0.440%**, all **-0.212%**. These rows are retained unchanged.

## Separate repeat of unclear cells

| Case | Original change | Repeat change | Repeat C/A spread |
|---|---:|---:|---:|
| ep-kimi-k3-w4a16 T4096 | -1.434% | -0.190% | 3.511% / 4.028% |
| tp-v41-flash-w4a16 T4096 | -1.923% | -0.568% | 0.082% / 2.914% |

Both original and repeat prefill phases have substantial later-quartile growth in FC1 and FC2. Coarse NVML snapshots mostly remain2032MHz/reason0; occasional power-cap reasons are recorded. This does not establish a clock explanation or identical effective clocks. Timing is not precise enough to attribute these small aggregate differences solely to the removed instructions. Repeats are separate evidence, not substitutions or selected winners.

## Generated code

| Case | Phase | Before non-NOP | After | Delta | Registers |
|---|---|---:|---:|---:|---:|
| ep-kimi-k3-w4a16 T4096 | FC1 | 1943 | 1931 | -12 | 96 |
| ep-kimi-k3-w4a16 T4096 | FC2 | 1566 | 1553 | -13 | 128 |
| ep-v41-flash-w4a16 T4096 | FC1 | 1747 | 1735 | -12 | 96 |
| ep-v41-flash-w4a16 T4096 | FC2 | 1562 | 1549 | -13 | 128 |
| tp-nemo3-ultra-w4a16 T16384 | FC1 | 1768 | 1757 | -11 | 96 |
| tp-nemo3-ultra-w4a16 T16384 | FC2 | 1608 | 1595 | -13 | 128 |
| tp-v3-w4a16 T8 | FC1 | 1614 | 1602 | -12 | 96 |
| tp-v3-w4a16 T8 | FC2 | 1415 | 1413 | -2 | 128 |

Generated-code effects are counted for the complete function; no assertion that all other warps are byte-identical.

## Evidence and preserved failures

- `screen.csv`, `perf-summary.json`, `telemetry-summary.json`, `drift-analysis.json`: complete original16cells, all medians/quartiles and observed clocks.
- `repeat.csv`, `repeat-summary.json`, `repeat-drift-analysis.json`: separate2cell repetition.
- `codegen-analysis.json`, `final-source-equivalence.json`, `screen-engine-proof.json`, `precommit-receipt.json`: source/resource/method binding.
- Codegen archive `349d0d4be90dbb20189e477c420de19961736de903dd2e9106a95f1b987be28b` (91verifiedfiles). Full qualification archive `4aa1091cb3c7eab36263a83f849fc34bf17d504a2de625cb7dab1c9423e52935` (423verifiedfiles). Repeat archive `3c376513aab2ab6c24b15093622519093b0844fb74d3db28fc00ac5be07a8a27` (84verifiedfiles).
- Original codegen helper wrongly rejected a valid cached default `-1`; it stopped before the affected control compilation and was corrected in `retry-r1`.
- Initial timing helper expected an obsolete `dequant` field in the guard-policy receipt. Both control phases passed the actual guards, then failed this schema check. They are preserved and excluded; `screen-r1` restarts allCAACphases with the exact9037guard-loop AST.
- Oversized transport payload/archive attempts are preserved; final full evidence was fetched in bounded chunks with archive and semantic-file SHA verification.
