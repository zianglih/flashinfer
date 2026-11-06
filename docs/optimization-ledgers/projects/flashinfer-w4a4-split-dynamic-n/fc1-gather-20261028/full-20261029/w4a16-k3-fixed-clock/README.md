# K3 EP prefill: fixed-clock diagnostic

This is a diagnostic1500MHz SM-clock regime, not stock-clock retention or PR-table data. It isolates clock variation from source behavior on exclusiveGPU6 (`GPU-55563f08-7de4-1809-b469-968e568fa223`).1500MHz is supported and below the observed1567MHz droop; memory stays3996MHz, and no power limit or other GPU setting changes.

Oldfb66 prepare versus retained475-equivalent W4 Gather4 source, identical frozen winners/routes, same strict CUPTI cold-L2 CUDA graph benchmark,10warmups/100samples per phase, C-A-A-C. The capture observer runs after activity collection ends and is AST-equivalent to the original timing function once removed. Separate read-only NVML sampling confirms every timing-window sample at1500MHz, event mask0, memory3996MHz.

| Tokens | C1 µs | A1 µs | A2 µs | C2 µs | Candidate speedup | Control spread | Candidate spread |
|---:|---:|---:|---:|---:|---:|---:|---:|
|4096|612.9625|635.3940|635.6325|610.9780|−3.70%|0.325%|0.038%|
|8192|1073.0915|1092.9475|1095.0430|1072.4040|−1.94%|0.064%|0.192%|

FC1 accounts for the residual cost:4K old366µs versus gather405µs, with20.8µs prepare removed;8K old662µs versus gather714µs, with39.0µs prepare removed. FC2 and combine are effectively unchanged. This corroborates a smaller genuine FC1 gap after suppressing the7–10% stock-clock phase drift; it does not justify replacing the existing public stock-clock measurements.

Restoration: `nvidia-smi --reset-gpu-clocks` ran successfully in `finally`. The recorded post-reset state has no compute processes, memory3996MHz, default/applicationSM2032MHz and an idling225MHz current clock; a subsequent status query observes120MHz/0MiB/0%GPU utilization. Automatic clock behavior is restored. OnlyGPU6 was modified.

Attempt1 (`w4a16-k3-fixed-clock` remote) failed before benchmark execution because the runpy capture wrapper received interpreter argv. The finally path restored clocks successfully and the GPU was idle. Attempt2 (`w4a16-k3-fixed-clock-r2` remote) fixes only that local diagnostic argv composition and completes all four phases. `evidence/` contains attempt2; failed attempt1 remains remotely preserved. No kernel, tactic, source contract, repository or PR change was made.

Reproduce analysis with `python3 analyze.py`. `analysis.json` includes all phase medians, per-quartile means, stage medians, and observed clocks. `evidence/clock-receipt.json` proves initial exclusive ownership, supported/current/default clocks, the exact scoped lock/reset commands, and restored state. All raw100sample arrays, CUPTI stage traces, source hashes, cache manifests and NVML samples are preserved.
