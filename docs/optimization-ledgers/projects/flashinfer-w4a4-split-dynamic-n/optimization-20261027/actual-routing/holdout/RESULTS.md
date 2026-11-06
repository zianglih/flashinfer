# Result: reject unconditional actual-input profiling

The shape-keyed tuner can retain an unsuitable winner after an EP rank's
zero-local-work warmup. The bounded counterexample was decisive; no concentrated
or additional-seed holdout was launched.

| N3U EP8 PER-TOKEN4096 real workload | C0 | A1 | A2 | C3 | Geometric mean |
|---|---:|---:|---:|---:|---:|
| Winner selected from real warmup | 310.722 us | — | — | 310.754 us | 310.737999 us |
| Winner selected from zero-local warmup | — | 354.0185 us | 354.1140 us | — | 354.066247 us |

Zero-local winner: **-12.237328% speedup, +13.943659% latency** against the
real-trained winner. Control drift was +0.010299%; candidate spread was
0.026976%. The four frozen passes contain 400 CUPTI samples and identical
11,180 local routes across 64 local experts, including input quantization.

Native AUTO kept the unchanged 360-tactic catalog and exactly the same 320
admitted tactics for the 4096-token geometry. Only the matching bucket was
retuned, using valid unique top-K IDs that all target remote experts; the other
19 native cache entries were byte-identical. No winner was forced.

- Real-trained: route N256; both GEMMs channel M256 / two CTAs / K4; shared CLC on.
- Zero-local-trained: route N256; FC1 M256 / two CTAs / K8; FC2 M128 / one CTA / K4;
  shared CLC off.
- Both replay arms execute the same candidate source: retained `1e69d0a39` plus
  the two-file actual-input profiling hook. No kernel-code difference exists
  between the replay arms.
- Native NV profiling remains eager event timing; final public replay remains
  cold-L2 CUDA-graph CUPTI with 10 warmups and 100 samples/pass. Event fallback
  is forbidden. Per-token 4over6 MSE/256/error-fast-math and disabled base FP4
  fast math remain unchanged.

The original balanced-profile winner was not remeasured in this holdout, and
there is no claim of a new paired comparison against it. The observed loss
against the naturally selected real-workload winner suffices to reject the
unconditional policy; earlier seed-specific gains are not a general retention
justification.

`independent-audit.json` verifies five successful phases / 500 samples including
AUTO's diagnostic public timing, route and cache identities, all medians and
formulas, the single native profile and unchanged other entries. Archive:
38 files, SHA256
`97f4a79cd34863ec623e7cdff544adac15c25f732c596341631906720434949d`.

The first frozen invocation failed before GPU work because the wrapper did not
add the observer's sibling helper directory to `sys.path`. V2 adds that path;
its sibling-import and SystemExit(None/0/1) checks pass. The successful AUTO and
its cache were preserved and hash-verified, and a new replay receipt holds all
four successful frozen passes. Both versions and the failure log remain in
`evidence/`; no failed run is presented as a timing result.

The rejected local review clone and remote candidate source copy were removed
after expected HEAD, exact two-file patch, independent Git metadata, no
untracked files and no active consumers were verified. The measured clean
1e69 control source, both persistent compile caches, helper scripts, patch and
all evidence remain. Cleanup receipts are under `../artifacts/`.
