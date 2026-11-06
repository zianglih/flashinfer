# Aligned SF word-clear screen

Compare the retained22ffe control with only aligned SF hole clearing; original quantizer widths and grid policy stay unchanged. Seven cells: N3U TP8 at8/32/64/4096/16384 tokens, plus V3 EP8/TP8 at16384. The V3 controls cover the actual initial-linear K7168 stack increase observed in source-paired codegen.

Use GPU0 only, after the actual row_limits-hole qualification proves the1/2/4-byte stores. Reuse the strict100-CUPTI cold-L2 graph CAAC harness, frozen374 routes and winners, source hashes, all runtime guards, and read-only NVML. No retune, no clocks changes, no sanitizer. Initial quantization remains included. Small changes within repeat spread are inconclusive.

The earlier R2 screen did not emit wider stores because recast_ptr preserved byte alignment; it cannot qualify this aligned implementation.
