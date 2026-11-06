# N3U TP8 W4A4 16384-token profile notes

Control822, frozen shared-CLC-off winner: FC1 M128/N256/one CTA, FC2 M256/N256/two CTA. FC1 carries a dedicated128-thread Gather4 warpgroup; FC2 regular TMA. Raw source-bound CUPTI medians and route fingerprints are in native-components.json. NCU is diagnostic replay, not retention timing.

All512 experts remain local under TP8. Hidden2048, per-rank intermediate640, top22, ReLU2. The actual histogram has360448 live routes across1667 N256 tiles; FC1 has5 channel tiles,8335 work items. Legal MMA N16 rounding costs1.0742% columns.

Full FC2 slabs use Ld16x256 -> scaling/BF16 conversion -> stmatrix.trans -> TMA; no TMEM scratch transpose. Depending on the compiled32/64 slab, only2.29%/4.85% live rows use SIMT tails. New Rubin FC2 64-token MOVM/TMEM transpose could only replace the separate tail/nonbulk ownership and is not a broad prefill candidate without further evidence.

Current FP32 FC1 shares Rubin's multi-round in-place TMEM transpose structure. Direct LD.RED is invalid under its four-token-per-TMEM-row mapping; old shared-FP32 transpose was slower. Rubin serial max.xorsign.abs does not beat existing compiler-fused FMNMX3 count, and the previous balanced tree was explicitly reverted for complexity. None is reopened here.

The first NCU attempt ended in argparse due to a helper selector typo before GPU work; preserved in attempt1-failure.json/remote fc1/. Correct existing selectors are --backends cutedsl --profile-backend cute-dsl. Retry output uses fc1-retry1/. Production source, compiler flags, cache winners and route generation unchanged.
