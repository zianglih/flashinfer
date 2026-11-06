# Control112 + universal scale-copy ordering

The complete fixed-tactic comparison supports retaining this as spill removal
and simpler independent scale-copy ordering, with broadly neutral end-to-end
performance. It does not establish a broad speedup: affected-cell aggregate is
+0.163%, while unchanged W4A16 moves +0.145% in the same campaign.

| Scope | Decode 4–64 | Middle 128–512 | Prefill 4096–16384 | All shown affected cells |
|---|---:|---:|---:|---:|
| EP | +0.066% | +0.073% | +0.693% | +0.239% |
| TP | +0.098% | +0.009% | +0.106% | +0.076% |

- All **15 exact tests passed**, with no skip/failure/error: seven existing
  cases and eight local M512 cases, covering four formats and CLC on/off.
- All **15 jobs, 468 cells, 187,200 strict CUPTI samples** passed source, cache,
  actual-tactic, route and timing audits. The shown 396 cells omit tokens 1–2;
  308 affected cells remain after excluding W4A16 from aggregates.
- All **854 loaded-kernel observations passed** the unchanged-compiler runtime
  guard. All **430 gathered-kernel observations** report zero local bytes,
  including one/two CTA groups and route tiles 16/32/64/128/256. These are compile
  observations across repeated processes, not 430 unique kernel variants.
- The clearest cell is K3 EP8 per-token 16K, **+8.867%**, with 0.011% control
  phase spread and 0.868% candidate spread. The most negative affected cell is
  N3U EP8 MXFP4x8 16K, **−1.515%**, but control phases vary 6.832% versus 1.015%
  for the candidate; do not interpret that cell as a resolved code regression.
- No sanitizer was run. The separately planned native-tactic follow-up was
  paused before any measurement, so these numbers contain no retuning benefit.

The measured source was the single unstaged kernel in
`flashinfer-fc1-gather-composed-review`, based on clean `fb66a27e`: +17/−9 lines,
kernel SHA256 `0d44e4d71465b29a565995febdad42ef168060d1ae2858df5b2611ca998f70ee`.
It was subsequently retained as commit
`7106faf3082f63f3c94a4dc04b7fd0a77388f209` with that exact kernel hash. Later
metadata experiments in the review workspace are not part of this evidence.
Patch SHA256 `37d5ef817e11ca2e4214bc9c65e241b4c8bf2e9d892261151ed6757c98330ed5`.
Both arms use identical original frozen winners; control is clean fb66, not
retained PR #7290 d35. C3 B300, `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2,
GPUs 4/6/7, same-GPU C-A-A-C, cold L2, 100 CUPTI samples per phase, no autotune
traversal, swap-AB unfused, NVFP4 input quantizer included. All GPU lanes finished
and were confirmed idle before being released.

Evidence:

- [All raw cell medians and phase spreads](report/cells.csv)
- [Complete summary](report/summary.json)
- [Exact tests and runtime guard summary](report/validation-summary.json)
- [EP heatmap](plots/composed-vs-clean-gather-ep.png)
- [TP heatmap](plots/composed-vs-clean-gather-tp.png)
- [Protocol and reproduction commands](README.md)
- Immutable `evidence.tar.gz`: SHA256
  `c9af9a151ec7b4524e666129076c706f0793d16cf068c31dec720dbfaba91c87`,
  996 files, 3,146,864 bytes. Remote controls remain in persistent storage under
  `optimization-next-20261029/composed-full/perf/` for subsequent explicit reuse.

Historical residual comparisons are separate artifacts:
`d35-residual-cells.csv` and `external-baseline-cells.csv`. The latter reverified
88 original raw files and 660 comparisons with no routing or quantization
contract mismatch. These historical comparisons are not the fresh causal
fb66-versus-composed experiment; most old measurements use different GPUs.
