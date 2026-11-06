# Retained default: full NCU, T1024 / N64 / direct epilogue

[Download all eight reports](../direct-epi-0910a-ncu-full-t1024-001-download.tar.gz) · [Raw/base metric CSVs](../direct-epi-0910a-ncu-full-t1024-001-csv.tar.gz) · [Per-rank PC ranking](../direct-epi-0910a-ncu-full-analysis/ranking/README.md)

Captured retained commit `8d7718c9a6c76e5722e1cf201395b0df538b081e`, exact source `eb036705ebe71f940bf567c94fdcb78020a5fdc21bdeb3e7ea361cc1d140a09d`, after rejecting and reversing the BAR1 trial. Source, native binaries and GPU idle closure passed. This is a profiling diagnostic; no new AUTO timing or baseline was run.

Setup: eight B300 GPUs on `hu-pdx-115`, explicit `nvcr.io/nvidia/pytorch:26.05-py3` (CUDA 13.2), driver 590.48.01, Nsight Compute 2026.1.1.0. Global 1024 source tokens means 128/rank; H7168/I2048/E256/top-k8. M256/N64/K256, cluster2, F4, epi flags2/4, schedulerS2, `atomic_counter`, `epi_warps`, two decode WGs/five total WGs. See [exact command](command.txt), [source binding](profile-binding.json), and [preflight](preflight.json).

Full set: `--set=full` with no custom metric filter. Each report has one Mega action, 2472 metric names, 14 rendered sections including Source Counters, and populated SM/SMSP/DRAM/LTS/L1TEX/GPU counters. The installed full set has 22 conditional/extended section definitions and an estimate of 7314 metrics; that generic inventory is distinct from actual report counts. Raw/base CSVs each have 2468 columns. All eight actions record 96 registers, 640 threads and 200064 dynamic shared bytes. Embedded project sources match the retained manifest.

Logged application pass IDs reached 40; report replay passes are 40 and PC aggregate passes are 2. These fields retain their separate meanings. PC drop/overflow counters are zero. Six C2C metrics were unavailable. Rank 3 has 23 PM-triage entries without aggregate values; all metric names and base hardware-family counts still match. See [coverage](full-report-verification/coverage.json) and [verification receipt](full-metrics-verification-completion.json).

Instrumented duration fields range 0.208096–64.954560ms, and rank 3 reports derived SM throughput 377.44%. These replay artifacts prevent using these values as AUTO latency or physical rates. Sample shares are sampled warp states, not elapsed stall fractions. Actual source/SASS attribution is recorded separately; unresolved PCs stay explicit.

All eight idle SM clocks 120 MHz, memory 3996 MHz and power limits 1100 W match the previous observed state; no settings changed. See [idle comparison](idle-state-comparison.json).

| Rank | Report | Bytes | SHA256 |
|---:|---|---:|---|
| 0 | [ep_w4a16_megamoe_t1024.rank0.ncu-rep](ep_w4a16_megamoe_t1024.rank0.ncu-rep) | 29,146,256 | `ad58f6d2e8a75aecfe04d917c3dc686da109d0a8f3fac32c842f1ca2b274c904` |
| 1 | [ep_w4a16_megamoe_t1024.rank1.ncu-rep](ep_w4a16_megamoe_t1024.rank1.ncu-rep) | 303,685,184 | `bcc62f7e52e6d73877fb5b501888825445d3636d32e7dd238029eec7d0c9fa38` |
| 2 | [ep_w4a16_megamoe_t1024.rank2.ncu-rep](ep_w4a16_megamoe_t1024.rank2.ncu-rep) | 40,249,460 | `fece31afb36ff688888617fdb1918284ca993e99ead04b0e790eeb06a9af66a2` |
| 3 | [ep_w4a16_megamoe_t1024.rank3.ncu-rep](ep_w4a16_megamoe_t1024.rank3.ncu-rep) | 15,738,727 | `5a3d7dcf36ae70f083830649d0c0a92a75bbc72227d5adf581a45910bcd85332` |
| 4 | [ep_w4a16_megamoe_t1024.rank4.ncu-rep](ep_w4a16_megamoe_t1024.rank4.ncu-rep) | 331,125,689 | `4b1bc2cbdcb3ecbed0adcbf1d44feac287c2125e508a68a581ddc24ea00be9b3` |
| 5 | [ep_w4a16_megamoe_t1024.rank5.ncu-rep](ep_w4a16_megamoe_t1024.rank5.ncu-rep) | 232,087,091 | `3c9330e6ad1cdd802dda64e4b0aedf2b97b84dd4407d180b597599bfd05b924c` |
| 6 | [ep_w4a16_megamoe_t1024.rank6.ncu-rep](ep_w4a16_megamoe_t1024.rank6.ncu-rep) | 124,610,795 | `f8e4f48cad9f96e4e655903df8ba44140fb9ca24ba1f7e262dc9f190f2e1217d` |
| 7 | [ep_w4a16_megamoe_t1024.rank7.ncu-rep](ep_w4a16_megamoe_t1024.rank7.ncu-rep) | 279,992,710 | `1bd6abd99c46b4ae0a5deb9cd230fb6daac88284b467817a7fc9919a7fa675a9` |

Raw archive: 36,594,582 bytes; SHA256 `5d4c542ad5ee62b81dc78f12fb055c421fa2c5e2abce5704a08e80c76a77f6fc`. It includes reports, commands, source/preflight/native inputs, tool inventory, hardware/idle snapshot, replay log and closure. Driver/DSL caches are excluded. This archive is immutable; CPU exports and analysis are adjacent artifacts.
