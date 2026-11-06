# Narrow FC2 bulk-store experiment

Parent 0c; two-file unstaged candidate. Reuse existing stmatrix/bulk-copy output for every supported BF16/FP16 unfused scatter geometry. Filter supported slabs by actual allocated token extent, then retain capacity-based operand-stage fitting. Use ceil-div slab count so logical N16 consumes its physical N32 slab. No model thresholds, no replacement for operand TMA, no fused-path changes.

Admission compares 45 initialized-byte cases with clean0c: all three formats, N16/32/64 and unchanged N128, BF16/FP16, per-token scales, K384/2304 tails, zero output and untouched padded rows. Native fixed N16 V41 T32/128/512 C1/A1/A2/C2 follows a passing gate. All evidence and scripts stay outside the PR.
