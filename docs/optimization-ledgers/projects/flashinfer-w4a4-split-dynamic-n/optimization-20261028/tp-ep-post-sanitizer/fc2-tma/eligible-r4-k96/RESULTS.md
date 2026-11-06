# Rejected common-STMatrix cleanup

R4 passed all 256 paired exact comparisons against measured R3, but increased static instruction counts in 48 of 128 kernels (up to 40 instructions) and registers in 44 kernels (up to 18 registers). Uniform-register spill/fill counts did not grow. The instruction/resource gate rejected this cleanup; no R4 performance trials were launched.

The final candidate restores measured R3 GPU implementation and retains only the redundant host output_rows alias removal and required formatting. Raw source, compile artifacts and rejection evidence remain under this directory and its immutable remote counterpart. See rejection-analysis.json for source-bound kernel records.
