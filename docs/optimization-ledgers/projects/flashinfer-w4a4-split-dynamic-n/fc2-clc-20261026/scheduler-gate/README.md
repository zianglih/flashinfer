# Independent FC2 scheduler exactness gate

Passed 64 control and 128 candidate changing-data/routing replays. Control was clean `0def601d`; candidate was the frozen composed A plus independent FC2 scheduler patch `2d1a8e5dc7e548a023d15fa58f80f586f5e2c561519ed5a6cbd4bd6ab1eaa0d0`. All pinned source files and patch hashes remained unchanged. Full collection hashes are in `collection.json`; verified assertions are in `validation.json`.

- Standard NVFP4, per-token NVFP4, MXFP8, and MXFP4x8; both independent FC1/FC2 scheduler choices.
- PDL off/on, with the intended weight-prefetch contract observed.
- N16/N128 and one/two CTA groups across four configurations; live work exceeds resident capacity.
- Balanced, skewed, empty, and reactivated routes with changed inputs and route weights.
- Zero-tolerance within-source comparisons and identical output-byte SHA256 across sources.

The initial MX control helper used the stale `w8a8` spelling and was rejected before core execution. The helper was corrected to `mxfp8`, and only the MX configurations were rerun. No production source changed. The failed helper attempt is retained in the raw collection.

This is a focused gate, not a sanitizer run, exhaustive geometry cross-product, or native autotuning performance claim.
