# Decode geometry experiment

Frozen production: d9074cb6e9e934d387e358a069e90ddf084f5ef7. Task-local copies only.

- baseline: production unified one/two-CTA core.
- small: permit physical M256 at route N16/32/64 with allocated N>=64 (B rows>=32 per CTA); dynamic MMA N still align16(live routes).
- overlap: independently dedicate four epilogue warps for every geometry.
- All variants preserve the 128-row minimum SFB storage and existing per-CTA 128-channel epilogue.

GPU0 only. Pair byte-exact raw FC2, quantized FC1, and per-token FC1 including partial route tiles and sentinel output/SF guard storage before sparse phase timings. No production source changes or native retention claims.

Final evidence: [RESULTS.md](RESULTS.md); complete raw logs are in `../../artifacts/decode-geometry-experiment/`. Retained production policy: small-N FC2 and nonmixed FC1 overlap; no small2 tactics. 306 paired overlap1 exact cases passed.
