# Narrow FC2 bulk-store experiment

Parent 0c; two-file unstaged candidate. Reuse existing stmatrix/bulk-copy output for every supported BF16/FP16 unfused scatter geometry. Add a native16-column slab and filter supported slabs by logical route extent, then retain capacity-based operand-stage fitting. N16 loads only16 live TMEM columns; its existing physical N32 accumulator allocation is unchanged. Use ceil-div slab count. No model thresholds, no replacement for operand TMA, no fused-path changes.

Admission compares 45 initialized-byte cases with clean0c: all three formats, N16/32/64 and unchanged N128, BF16/FP16, per-token scales, K384/2304 tails, zero output and untouched padded rows. Native fixed N16 V41 T32/128/512 C1/A1/A2/C2 follows a passing gate. All evidence and scripts stay outside the PR.
