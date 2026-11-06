# Bounded repeat of all flagged prefill cells

Repeated all eleven pilot T16384 cells whose absolute control drift or candidate spread exceeded 1%, including positive and negative results. This is a separate diagnostic: the original 80-cell pilot, its aggregates, and all original raw samples remain unchanged.

The repeat used unchanged retained `1e69d0a39` and frozen r2 sources, the original strict observer, the same per-arm native winner cache entries, identical routing, no AUTO, and fresh C-A-A-C with 10 warmups and 100 cold-L2 CUDA-graph CUPTI samples per phase. Source/config/cache identities were checked before and after every phase. Clock, temperature, power, and GPU identity were recorded at each phase boundary. All 28 phases and 4,400 samples passed; no source or tactic changes were made.

Two cells now have both within-arm differences below 1%: K3 MXFP4x8 +1.743% and N3U W4A4 −0.167%. The other nine still exceed the drift threshold, including V41F MXFP4x8 −2.838% with −5.052% control drift and K3 MXFP8 −2.114% with −5.548% control drift and −3.667% candidate spread. These repeats do not establish a stable large prefill regression. They also do not justify replacing unfavorable pilot rows or claiming the large positive N3U MXFP4x8 repeat as a stable gain.

[All original/repeated results](table.md) retain the drift columns. `audit_results.py` recomputes all eleven ratios directly from raw samples, validates exact flagged-cell coverage and saved winner identity, and writes `results.json`. All values compare swap-AB source variants, not TRTLLM or non-swap backends.

The archive is `transfer.tar.gz`, SHA256 `d7c779de47f3d8a3a5ea2abf879896636f3f1025589aae825026bda654b23a70`, containing 113 files. All six assigned GPUs (1, 2, 3, 5, 6, 7) were confirmed idle and released after completion. This closes the planned bounded repeat; additional validation is a separate decision.
