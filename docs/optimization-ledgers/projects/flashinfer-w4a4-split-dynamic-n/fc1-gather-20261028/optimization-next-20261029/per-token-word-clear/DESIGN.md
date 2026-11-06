# Vectorized inactive SF clearing

Isolate aligned 1/2/4-byte SF zero stores with the original retained CTA width/grid policy. R1 paired-width is rejected after sparse decode and precise-recipe regressions; R2 only partly recovered decode and regressed N3U TP16K. This candidate removes the 7 host-width lines. No new dtype/model/tactic branch, synchronization, register budget or quantization arithmetic. The compile-time gcd of padded row SF columns selects a safe store width. Existing canonical layouts have contiguous aligned 4-byte SF atoms; linear layout uses 1/2/4-byte row alignment.

Local base6c6515f2, remote controlled pair22ffe662; the only intervening retained change is W4 gather issue order. Remote source hashes freeze all514 files. Source-identity will be verified again before any composition or retention. Persistent C++/CuTe caches remain intact. GPU6 exact/layout/codegen qualification precedes GPU0 same-protocol performance.
