# Adjacent-term 4over6 packing: rejected

The bounded isolated comparison rejects source `679c86cd`: **430.098 →509.571 µs**, **18.478% longer duration** / **−15.596% speedup**, despite lower static instructions and registers. Both candidate phases are slower than both fresh controls, with normal clocks. No broader screen, extra packing variant, profiling, recipe rescue, or production integration follows.

This is distinct from rejected `5f232629`: the existing one-candidate helper/API and both callers remain unchanged; only adjacent independent subtraction/square terms are packed. Each candidate retains its original16 scalar RN additions in the same order, with scalar abs forMAE. The source diff is12+/11−; scoped hooks, source graph and independent source/native reviews pass. Main remains retained c1ac.

## Exact/native gate

| Existing case | Non-NOP C/A | Registers C/A | LOCAL C/A | Occupancy capacity C/A |
|---|---:|---:|---:|---:|
| BF16 K640, MSE256 error-fast, precise base, group256/SFgroup256 |743 /711|61 /43|0 /0|16 /20|
| FP16 K1536, MAE448 error-fast |407 /394|64 /48|0 /0|10 /13|
| FP16 K80 strict-error folded-scale control |1430 /1430|64 /64|16 /16|32 /32|

Six paired-arm exact calls and24 changing-valid-row graph replays passed. The strict control's PTX/cubin/SASS are byte-identical, including its pre-existing LOCAL16. Affected PTX has16 adjacent packed subtractions,16 packed squares forMSE, and two separate16-add scalar RN chains. No error recurrence contracts into FMA or addsFTZ. MAE has one additional HFMA2 solely for zero materialization (`−RZ*RZ+0`), independently verified; it is not error contraction. K640 NOP count remains25 in both. Full13,245-file inventories and four unchanged release ELF/Ninja identities pass before/after.

These are resource capacity limits, not claims of measured residency. Isolated timing uses unchanged grid2368/block64; the lower register count does not imply a larger grid.

## Separate isolated CAAC

| Phase | Median (µs) |
|---|---:|
| 0-control | 430.323 |
| 1-candidate | 509.459 |
| 2-candidate | 509.683 |
| 3-control | 429.874 |

Geometric mean of the two phase medians per arm: control `430.098441408` µs, candidate `509.570987692` µs. Speedup `(C/A−1)×100 = -15.595971553%`. Repeat spreads: control `0.104449%`, candidate `0.043968%`. All400 CUPTI spans and16 clock quartiles replayed; **zero clock exceptions or missing quartiles**,2032MHz/reason0 throughout sampled windows.

The existing captured N3U TP8 T16384 FC1 payload is reused exactly: BF16 allocation491008×640,360448 live routed rows,426752 processed/padded rows, original valid-row/row-limit/group256 arguments, MSE256 error-fast with precise base math, PDLtrue. Input SHA `73a6ee6a9c49b0171d5f246785f488a70416445ae37f805f9edb9db1f8d75bb6`. The graph contains only the intermediate quantizer and has no predecessor/successor FC2. Every phase uses strict CUPTI100 samples/10 warmups/cold-L2; there is no event fallback, sample exclusion, retune or phase replacement.

Each arm first populates its distinct private quantizer cache using one untimed ordinary public call. Each timed process then uses the normal disk loader and verifies the actual native image/resource/configuration before measurement: control `ff00cf52`, candidate `598f9d00`. All defined output hashes match; unspecified inactive packed/per-row capacity is outside the existing comparison. The timer, replay, native recorder and NVML helper are byte-identical to the prior isolated diagnostic. No compiler-option change or forced compilation is used in timing. Source/cache postflight passes and GPU3 is0MiB/0%/noPIDs.

The result shows that restoring scalar ordered accumulation does **not** remove the intrinsic isolated slowdown from this alternative packing. It does not establish packed instruction latency or a unique scheduling cause. The prior cross-candidate42-cell screen and400-sample isolated CAAC remain unchanged and separate; no fresh whole-chain performance was collected here. The bounded pilot is not full recipe/shape coverage and does not promise NaN payload identity.

## Evidence

- `source-proof.json`, `candidate.patch`, `candidate.py`, `pre-commit.log`: exact unstaged source and inverse whole-module/ordered RN source proof.
- `qualification/evidence/`, `native-summary.json`: six exact/native captures,24 graph replays, unchanged strict image, compiler/resource/source/cache receipts. Qualification archive `8f9823e8955b08ebee664ae14e80d1fffaccd1b29fe08e920b181ce126061076`.
- `isolated/{evidence,summary.json,samples.json}`: all400 raw spans, fourphase medians, clocks, normal-cache native bindings, original captured input/argument hashes. Archive `b0c15a8c6eb041c1f63b526b5901b35348bd594de739d9597592444db39dcce1`; large input remains remote and hash-bound.
- Independent reviews: `../../audits/adjacent-4over6-error-source-peer.json`, `../../audits/adjacent-4over6-error-native-peer.json`; final raw peer/retirement receipts are additive.
