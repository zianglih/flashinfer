# FlashInfer PR #4366: W4A4/W4A16 performance comparisons

This document extracts the original CuTe DSL W4A4, W4A16, and TRTLLM latency and throughput columns from every performance table in [flashinfer-ai/flashinfer#4366](https://github.com/flashinfer-ai/flashinfer/pull/4366). It presents direct W4A16-versus-W4A4 and W4A16-versus-TRTLLM comparisons, plus combined speedup and slowdown views of best default W4A4, best per-token 4-over-6 W4A4, and a common W4A16 series from the default runs.

## Source and benchmark scope

- PR head and validated head: `d684167f69d124bfcaf725ad69d485f39ae9605b`
- Live PR body retrieved: 2026-08-13 (America/Los_Angeles)
- Hardware: 8x NVIDIA B200 devbox; each reported arm uses GPU 0
- Software: driver 580.126.09, CUDA 13.2, PyTorch 2.13.0+cu132, CuTe DSL 4.7.0, FlashInfer 0.6.18, and CUPTI 13.2.0
- Workload: DeepSeek-V3 MoE, hidden size 7168, intermediate size 2048, 256 experts, top-k 8, TP=1
- EP setup: `--ep 8` is a single-process compute-shard simulation with 32 local experts; it does not measure eight distributed ranks or inter-rank communication
- Timing: CUDA graphs enabled with CUPTI hardware-activity timing; all four arms use deterministic two-stage finalize via `--no-fused-finalize`
- Scope here: the first comparison retains the published CuTe DSL W4A4 and W4A16 columns; the second retains W4A16 and TRTLLM; the combined comparisons select the lower-latency W4A4 candidate from CuTe DSL W4A4 and TRTLLM within each activation contract while sharing the default-run W4A16 series. CUTLASS is intentionally omitted.

The PR body's existing `Speedup` columns compare each CuTe DSL mode against CUTLASS or TRTLLM. They do not provide a direct W4A16-versus-W4A4 comparison, so that speedup is derived below. The W4A16-versus-TRTLLM sections preserve the PR body's published W4A16 speedup values.

The added speedup is calculated from the printed latency values:

`W4A16 vs W4A4 speedup = W4A4 ms / W4A16 ms`

A value above `1.0x` means W4A16 is faster; below `1.0x` means W4A4 is faster. Raw milliseconds and TFLOPS are transcribed at the PR body's published precision. The speedup is therefore approximate and is calculated from timings rounded to 0.001 ms; it can differ slightly from a ratio inferred from the separately rounded TFLOPS columns.

## 4-over-6 per-token activation contract

These tables use `--use-per-token-activation`, enable the 4-over-6 environment, exclude timed initial activation quantization, and use deterministic two-stage finalize. This contract changes W4A4's activation path; W4A16 consumes BF16 directly but is reported in the same paired benchmark.

### Output-side router weights

| Tokens | W4A4 (ms) | W4A4 (TFLOPS) | W4A16 (ms) | W4A16 (TFLOPS) | W4A16 vs W4A4 speedup |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 16 | 0.096 | 14.7 | 0.082 | 17.2 | 1.171x |
| 32 | 0.131 | 21.5 | 0.116 | 24.3 | 1.129x |
| 64 | 0.167 | 33.8 | 0.151 | 37.4 | 1.106x |
| 128 | 0.170 | 66.1 | 0.155 | 72.9 | 1.097x |
| 256 | 0.181 | 124.9 | 0.163 | 138.6 | 1.110x |
| 512 | 0.185 | 244.3 | 0.166 | 272.5 | 1.114x |
| 1024 | 0.195 | 463.6 | 0.187 | 482.5 | 1.043x |
| 2048 | 0.216 | 833.6 | 0.232 | 778.9 | 0.931x |
| 4096 | 0.280 | 1286.4 | 0.351 | 1028.9 | 0.798x |

### Input-side router weights

| Tokens | W4A4 (ms) | W4A4 (TFLOPS) | W4A16 (ms) | W4A16 (TFLOPS) | W4A16 vs W4A4 speedup |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 16 | 0.095 | 14.8 | 0.082 | 17.1 | 1.159x |
| 32 | 0.131 | 21.5 | 0.116 | 24.4 | 1.129x |
| 64 | 0.167 | 33.7 | 0.150 | 37.5 | 1.113x |
| 128 | 0.171 | 66.0 | 0.155 | 72.8 | 1.103x |
| 256 | 0.181 | 124.8 | 0.163 | 138.2 | 1.110x |
| 512 | 0.185 | 243.8 | 0.166 | 271.9 | 1.114x |
| 1024 | 0.194 | 464.8 | 0.187 | 482.0 | 1.037x |
| 2048 | 0.215 | 840.7 | 0.231 | 780.3 | 0.931x |
| 4096 | 0.278 | 1297.6 | 0.366 | 986.8 | 0.760x |

## Default activation contract

These tables disable the 4-over-6 environment, omit `--use-per-token-activation`, and use deterministic two-stage finalize.

### Output-side router weights

| Tokens | W4A4 (ms) | W4A4 (TFLOPS) | W4A16 (ms) | W4A16 (TFLOPS) | W4A16 vs W4A4 speedup |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 16 | 0.083 | 16.9 | 0.081 | 17.4 | 1.025x |
| 32 | 0.114 | 24.6 | 0.116 | 24.2 | 0.983x |
| 64 | 0.150 | 37.7 | 0.151 | 37.4 | 0.993x |
| 128 | 0.153 | 73.9 | 0.154 | 73.3 | 0.994x |
| 256 | 0.161 | 139.8 | 0.162 | 139.0 | 0.994x |
| 512 | 0.163 | 276.4 | 0.168 | 269.1 | 0.970x |
| 1024 | 0.166 | 543.3 | 0.187 | 482.0 | 0.888x |
| 2048 | 0.176 | 1023.6 | 0.232 | 776.0 | 0.759x |
| 4096 | 0.219 | 1650.7 | 0.360 | 1001.9 | 0.608x |

### Input-side router weights

| Tokens | W4A4 (ms) | W4A4 (TFLOPS) | W4A16 (ms) | W4A16 (TFLOPS) | W4A16 vs W4A4 speedup |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 16 | 0.083 | 17.0 | 0.081 | 17.3 | 1.025x |
| 32 | 0.114 | 24.7 | 0.116 | 24.4 | 0.983x |
| 64 | 0.149 | 37.8 | 0.150 | 37.7 | 0.993x |
| 128 | 0.152 | 73.9 | 0.154 | 73.1 | 0.987x |
| 256 | 0.161 | 140.1 | 0.162 | 138.8 | 0.994x |
| 512 | 0.163 | 277.0 | 0.169 | 267.3 | 0.964x |
| 1024 | 0.165 | 545.4 | 0.187 | 481.1 | 0.882x |
| 2048 | 0.174 | 1037.2 | 0.232 | 778.0 | 0.750x |
| 4096 | 0.210 | 1714.8 | 0.351 | 1028.6 | 0.598x |

## W4A16 vs TRTLLM

The published comparison uses:

`W4A16 vs TRTLLM speedup = TRTLLM ms / W4A16 ms`

A value above `1.0x` means W4A16 is faster; below `1.0x` means TRTLLM is faster. The speedup values below are transcribed directly from the PR body rather than recomputed from the displayed milliseconds. They use the benchmark's underlying timings, while the raw latency columns are printed only to 0.001 ms, so a ratio calculated from the displayed values can differ slightly.

### 4-over-6 per-token activation contract

#### Output-side router weights

| Tokens | W4A16 (ms) | W4A16 (TFLOPS) | TRTLLM (ms) | TRTLLM (TFLOPS) | Published W4A16 vs TRTLLM speedup |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 16 | 0.082 | 17.2 | 0.083 | 17.0 | 1.01x |
| 32 | 0.116 | 24.3 | 0.111 | 25.4 | 0.96x |
| 64 | 0.151 | 37.4 | 0.146 | 38.7 | 0.97x |
| 128 | 0.155 | 72.9 | 0.150 | 75.1 | 0.97x |
| 256 | 0.163 | 138.6 | 0.160 | 140.8 | 0.98x |
| 512 | 0.166 | 272.5 | 0.170 | 265.4 | 1.03x |
| 1024 | 0.187 | 482.5 | 0.320 | 281.7 | 1.71x |
| 2048 | 0.232 | 778.9 | 0.323 | 558.0 | 1.40x |
| 4096 | 0.351 | 1028.9 | 0.334 | 1080.4 | 0.95x |

#### Input-side router weights

| Tokens | W4A16 (ms) | W4A16 (TFLOPS) | TRTLLM (ms) | TRTLLM (TFLOPS) | Published W4A16 vs TRTLLM speedup |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 16 | 0.082 | 17.1 | 0.083 | 17.1 | 1.00x |
| 32 | 0.116 | 24.4 | 0.111 | 25.4 | 0.96x |
| 64 | 0.150 | 37.5 | 0.144 | 39.0 | 0.96x |
| 128 | 0.155 | 72.8 | 0.150 | 75.1 | 0.97x |
| 256 | 0.163 | 138.2 | 0.160 | 141.1 | 0.98x |
| 512 | 0.166 | 271.9 | 0.170 | 264.9 | 1.03x |
| 1024 | 0.187 | 482.0 | 0.321 | 281.0 | 1.72x |
| 2048 | 0.231 | 780.3 | 0.325 | 554.3 | 1.41x |
| 4096 | 0.366 | 986.8 | 0.334 | 1081.4 | 0.91x |

### Default activation contract

#### Output-side router weights

| Tokens | W4A16 (ms) | W4A16 (TFLOPS) | TRTLLM (ms) | TRTLLM (TFLOPS) | Published W4A16 vs TRTLLM speedup |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 16 | 0.081 | 17.4 | 0.074 | 18.9 | 0.92x |
| 32 | 0.116 | 24.2 | 0.104 | 27.2 | 0.89x |
| 64 | 0.151 | 37.4 | 0.139 | 40.6 | 0.92x |
| 128 | 0.154 | 73.3 | 0.142 | 79.2 | 0.93x |
| 256 | 0.162 | 139.0 | 0.151 | 148.9 | 0.93x |
| 512 | 0.168 | 269.1 | 0.161 | 280.3 | 0.96x |
| 1024 | 0.187 | 482.0 | 0.306 | 295.1 | 1.63x |
| 2048 | 0.232 | 776.0 | 0.300 | 600.7 | 1.29x |
| 4096 | 0.360 | 1001.9 | 0.301 | 1196.7 | 0.84x |

#### Input-side router weights

| Tokens | W4A16 (ms) | W4A16 (TFLOPS) | TRTLLM (ms) | TRTLLM (TFLOPS) | Published W4A16 vs TRTLLM speedup |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 16 | 0.081 | 17.3 | 0.074 | 19.0 | 0.91x |
| 32 | 0.116 | 24.4 | 0.104 | 27.1 | 0.90x |
| 64 | 0.150 | 37.7 | 0.138 | 40.9 | 0.92x |
| 128 | 0.154 | 73.1 | 0.142 | 79.1 | 0.92x |
| 256 | 0.162 | 138.8 | 0.152 | 148.3 | 0.94x |
| 512 | 0.169 | 267.3 | 0.161 | 280.7 | 0.95x |
| 1024 | 0.187 | 481.1 | 0.307 | 294.0 | 1.64x |
| 2048 | 0.232 | 778.0 | 0.303 | 594.5 | 1.31x |
| 4096 | 0.351 | 1028.6 | 0.302 | 1192.8 | 0.86x |

## Combined best W4A4, per-token 4-over-6, and common W4A16

For each retained token count, both W4A4 series select the lower displayed latency between CuTe DSL W4A4 and TRTLLM within their respective activation contracts. The backend identity is omitted from the tables; in every arm, TRTLLM is selected from 16 through 512 tokens and CuTe DSL W4A4 from 1024 through 4096 tokens.

The common W4A16 series is always taken from the default, non-4-over-6 run for the matching router-weight placement.

`W4A16 vs best W4A4 speedup = best W4A4 ms / W4A16 ms`

`per-token 4-over-6 vs W4A4 speedup = best W4A4 ms / best W4A4 per-token 4-over-6 ms`

`W4A16 vs best W4A4 per-token 4-over-6 speedup = best W4A4 per-token 4-over-6 ms / W4A16 ms`

For each speedup, a value above `1.0x` means the first-named configuration is faster. Selection and speedups use the displayed 0.001 ms values. Each best-W4A4 series is an oracle per-row composite, not a measured runtime dispatcher or a single backend configuration.

### Output-side router weights

| Tokens | Best W4A4 (ms) | Best W4A4 per-token 4-over-6 (ms) | W4A16 (ms) | W4A16 vs best W4A4 speedup | Per-token 4-over-6 vs W4A4 speedup | W4A16 vs best W4A4 per-token 4-over-6 speedup |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 16 | 0.074 | 0.083 | 0.081 | 0.914x | 0.892x | 1.025x |
| 32 | 0.104 | 0.111 | 0.116 | 0.897x | 0.937x | 0.957x |
| 64 | 0.139 | 0.146 | 0.151 | 0.921x | 0.952x | 0.967x |
| 128 | 0.142 | 0.150 | 0.154 | 0.922x | 0.947x | 0.974x |
| 256 | 0.151 | 0.160 | 0.162 | 0.932x | 0.944x | 0.988x |
| 512 | 0.161 | 0.170 | 0.168 | 0.958x | 0.947x | 1.012x |
| 1024 | 0.166 | 0.195 | 0.187 | 0.888x | 0.851x | 1.043x |
| 2048 | 0.176 | 0.216 | 0.232 | 0.759x | 0.815x | 0.931x |
| 4096 | 0.219 | 0.280 | 0.360 | 0.608x | 0.782x | 0.778x |

### Input-side router weights

| Tokens | Best W4A4 (ms) | Best W4A4 per-token 4-over-6 (ms) | W4A16 (ms) | W4A16 vs best W4A4 speedup | Per-token 4-over-6 vs W4A4 speedup | W4A16 vs best W4A4 per-token 4-over-6 speedup |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 16 | 0.074 | 0.083 | 0.081 | 0.914x | 0.892x | 1.025x |
| 32 | 0.104 | 0.111 | 0.116 | 0.897x | 0.937x | 0.957x |
| 64 | 0.138 | 0.144 | 0.150 | 0.920x | 0.958x | 0.960x |
| 128 | 0.142 | 0.150 | 0.154 | 0.922x | 0.947x | 0.974x |
| 256 | 0.152 | 0.160 | 0.162 | 0.938x | 0.950x | 0.988x |
| 512 | 0.161 | 0.170 | 0.169 | 0.953x | 0.947x | 1.006x |
| 1024 | 0.165 | 0.194 | 0.187 | 0.882x | 0.851x | 1.037x |
| 2048 | 0.174 | 0.215 | 0.232 | 0.750x | 0.809x | 0.927x |
| 4096 | 0.210 | 0.278 | 0.351 | 0.598x | 0.755x | 0.792x |

## Combined comparison expressed as slowdown

These tables use the same selected W4A4 series and common default-run W4A16 series as the preceding combined comparison, but express each comparison as a signed percentage slowdown:

`candidate slowdown vs reference = (candidate ms / reference ms - 1) × 100%`

A positive value means the first-named configuration is slower than the reference; a negative value means it is faster.

### Output-side router weights

| Tokens | Best W4A4 (ms) | Best W4A4 per-token 4-over-6 (ms) | W4A16 (ms) | W4A16 slowdown vs best W4A4 | Per-token 4-over-6 W4A4 slowdown vs W4A4 | W4A16 slowdown vs best W4A4 per-token 4-over-6 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 16 | 0.074 | 0.083 | 0.081 | +9.46% | +12.16% | -2.41% |
| 32 | 0.104 | 0.111 | 0.116 | +11.54% | +6.73% | +4.50% |
| 64 | 0.139 | 0.146 | 0.151 | +8.63% | +5.04% | +3.42% |
| 128 | 0.142 | 0.150 | 0.154 | +8.45% | +5.63% | +2.67% |
| 256 | 0.151 | 0.160 | 0.162 | +7.28% | +5.96% | +1.25% |
| 512 | 0.161 | 0.170 | 0.168 | +4.35% | +5.59% | -1.18% |
| 1024 | 0.166 | 0.195 | 0.187 | +12.65% | +17.47% | -4.10% |
| 2048 | 0.176 | 0.216 | 0.232 | +31.82% | +22.73% | +7.41% |
| 4096 | 0.219 | 0.280 | 0.360 | +64.38% | +27.85% | +28.57% |

### Input-side router weights

| Tokens | Best W4A4 (ms) | Best W4A4 per-token 4-over-6 (ms) | W4A16 (ms) | W4A16 slowdown vs best W4A4 | Per-token 4-over-6 W4A4 slowdown vs W4A4 | W4A16 slowdown vs best W4A4 per-token 4-over-6 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 16 | 0.074 | 0.083 | 0.081 | +9.46% | +12.16% | -2.41% |
| 32 | 0.104 | 0.111 | 0.116 | +11.54% | +6.73% | +4.50% |
| 64 | 0.138 | 0.144 | 0.150 | +8.70% | +4.35% | +4.17% |
| 128 | 0.142 | 0.150 | 0.154 | +8.45% | +5.63% | +2.67% |
| 256 | 0.152 | 0.160 | 0.162 | +6.58% | +5.26% | +1.25% |
| 512 | 0.161 | 0.170 | 0.169 | +4.97% | +5.59% | -0.59% |
| 1024 | 0.165 | 0.194 | 0.187 | +13.33% | +17.58% | -3.61% |
| 2048 | 0.174 | 0.215 | 0.232 | +33.33% | +23.56% | +7.91% |
| 4096 | 0.210 | 0.278 | 0.351 | +67.14% | +32.38% | +26.26% |

## Reading the result

- Under the 4-over-6 per-token contract, W4A16 is faster at every retained size from 16 through 1024 tokens in both router-weight placements. W4A4 becomes faster at 2048 and 4096 tokens.
- Under the default activation contract, most retained small-token results are near parity. W4A16 has only a small published latency lead at 16 tokens in either placement; W4A4's lead grows materially from 1024 through 4096 tokens.
- Against TRTLLM, W4A16's clearest wins are at 1024 and 2048 tokens in all four arms: `1.63–1.72x` at 1024 and `1.29–1.41x` at 2048. TRTLLM is faster again at 4096 tokens and generally leads below 512 tokens; the 4-over-6 arms show a small W4A16 lead at 512 tokens.
- In the combined view, the common default-run W4A16 series never beats best default W4A4 at a retained size. Best per-token 4-over-6 W4A4 is also slower than best default W4A4 at every retained size. W4A16 beats best per-token 4-over-6 W4A4 only at 16, 512, and 1024 tokens, by `1.006–1.043x` across the two placements.
- Expressed as slowdown, W4A16 is `4.35–67.14%` slower than best default W4A4. Per-token 4-over-6 W4A4 is `4.35–32.38%` slower than default W4A4. Against per-token 4-over-6 W4A4, W4A16 ranges from `4.10%` faster to `28.57%` slower.
- These are direct comparisons within each published arm. They do not compare input-side against output-side placement, and they do not establish distributed EP performance.
