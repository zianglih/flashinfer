# Complete benchmark result tables

Source latency tables round to 0.001 ms. All latency values below preserve that display precision. Speedups use matching unrounded capture JSON when available; otherwise they are approximate ratios of the printed values. Each run identifies its source, and speedups display two decimal places. Per-token aggregate speedup is the median of each run's BF16/W4A16 latency ratio, not a ratio of medians. Speedup > 1 means CuTe DSL W4A16 is faster than TRTLLM BF16.
