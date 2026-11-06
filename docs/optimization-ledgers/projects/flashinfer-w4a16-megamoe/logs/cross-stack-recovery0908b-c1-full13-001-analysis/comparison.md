# Complete fresh C1 catalog16 comparison

Each completed stack passes the saved-source/result audit: **52 raw values, 208 split records, 208 compiled records, 104 actual auto winners and thirteen complete 16-candidate rankings**. Both use exact source `250553779d5278c66794abef19696df40297d0767336e2782836298fc0a9074b`, identical benchmark helpers and two transform groups. All 18 per-arm provenance hashes validate. No 512-thread or historical timing row is substituted.

CUDA 13.0 auto is slower than CUDA 13.2 auto in all thirteen rows. The largest gaps are T1 (+27.12%) and T32 (+25.72%); T4096 is +10.29%. Actual Mega choices differ in nine rows, so this is a whole-auto comparison across different stacks and nodes. Percentages below are `(13.0 / 13.2 - 1) × 100`.

| T | 13.0 auto split ms | 13.0 auto Mega ms | 13.0 actual choice | 13.2 auto split ms | 13.2 auto Mega ms | 13.2 actual choice | Mega gap |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 0.082289 | 0.112289 | M256/N64, C2, F4, reuse | 0.084720 | 0.088336 | M128/N64, C1, F8, reuse | +27.12% |
| 2 | 0.122689 | 0.122753 | M256/N64, C2, F4, epi | 0.101584 | 0.118321 | M256/N64, C2, F8, reuse | +3.75% |
| 4 | 0.173569 | 0.153057 | M128/N64, C2, F8, epi | 0.145120 | 0.129025 | M128/N64, C1, F8, reuse | +18.63% |
| 8 | 0.196993 | 0.173489 | M256/N64, C2, F8, epi | 0.151409 | 0.157473 | M128/N64, C2, F4, epi | +10.17% |
| 16 | 0.220851 | 0.188258 | M128/N64, C2, F4, epi | 0.182240 | 0.165105 | M128/N64, C2, F8, epi | +14.02% |
| 32 | 0.256355 | 0.237585 | M128/N64, C2, F8, reuse | 0.204113 | 0.188978 | M256/N64, C2, F8, epi | +25.72% |
| 64 | 0.279601 | 0.261347 | M256/N64, C2, F4, epi | 0.209105 | 0.240770 | M256/N64, C2, F4, epi | +8.55% |
| 128 | 0.304003 | 0.250226 | M256/N64, C2, F4, epi | 0.235698 | 0.220081 | M256/N64, C2, F4, epi | +13.70% |
| 256 | 0.314354 | 0.267250 | M256/N64, C2, F4, epi | 0.232258 | 0.227921 | M128/N64, C2, F4, epi | +17.26% |
| 512 | 0.304435 | 0.271986 | M256/N64, C2, F4, epi | 0.236818 | 0.228514 | M256/N64, C2, F8, epi | +19.02% |
| 1024 | 0.305234 | 0.290002 | M256/N64, C2, F8, epi | 0.260738 | 0.251970 | M256/N64, C2, F8, epi | +15.09% |
| 2048 | 0.371795 | 0.356835 | M256/N128, C2, F8, epi | 0.351186 | 0.335859 | M256/N128, C2, F8, reuse | +6.25% |
| 4096 | 0.561238 | 0.546835 | M256/N128, C2, F4, reuse | 0.550483 | 0.495827 | M256/N128, C2, F4, reuse | +10.29% |

Actual Mega choices match only at T64, T128, T1024 and T4096. No C1 geometry wins on CUDA 13.0; C1 wins T1 and T4 on CUDA 13.2. Full sixteen-choice counts, including zero winners, are retained in JSON.

| T | 13.0 fixed split / Mega ms | 13.0 auto vs fixed Mega | 13.0 split spread | 13.2 fixed split / Mega ms | 13.2 auto vs fixed Mega | 13.2 split spread |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 0.095729 / 0.105441 | +6.49% | 16.33% | 0.075681 / 0.081633 | +8.21% | 11.94% |
| 2 | 0.123569 / 0.132449 | -7.32% | 0.72% | 0.101712 / 0.118193 | +0.11% | 0.13% |
| 4 | 0.163537 / 0.154209 | -0.75% | 6.13% | 0.137649 / 0.137361 | -6.07% | 5.43% |
| 8 | 0.199953 / 0.171874 | +0.94% | 1.50% | 0.160449 / 0.161793 | -2.67% | 5.97% |
| 16 | 0.219250 / 0.199138 | -5.46% | 0.73% | 0.179874 / 0.181265 | -8.92% | 1.32% |
| 32 | 0.252034 / 0.233186 | +1.89% | 1.71% | 0.204978 / 0.210705 | -10.31% | 0.42% |
| 64 | 0.280546 / 0.282466 | -7.48% | 0.34% | 0.222801 / 0.235954 | +2.04% | 6.55% |
| 128 | 0.294977 / 0.261906 | -4.46% | 3.06% | 0.234961 / 0.242594 | -9.28% | 0.31% |
| 256 | 0.313891 / 0.279362 | -4.34% | 0.15% | 0.241905 / 0.250626 | -9.06% | 4.15% |
| 512 | 0.303826 / 0.283138 | -3.94% | 0.20% | 0.241041 / 0.251922 | -9.29% | 1.78% |
| 1024 | 0.315987 / 0.296849 | -2.31% | 3.52% | 0.262401 / 0.268962 | -6.32% | 0.64% |
| 2048 | 0.377218 / 0.359139 | -0.64% | 1.46% | 0.355106 / 0.336435 | -0.17% | 1.12% |
| 4096 | 0.571620 / 0.541907 | +0.91% | 1.85% | 0.555268 / 0.522484 | -5.10% | 0.87% |

Split selections change in 23/104 within-stack rank/shape pairs on CUDA 13.0 and 40/104 on CUDA 13.2. Across stacks, 81/104 fixed-process pairs and 79/104 auto-process pairs differ. All input shapes and other selector metadata match; all original pairs remain in JSON. Split spread is observed process movement, not a confidence interval.

On CUDA 13.0, auto regresses against its own fixed Mega at T1 (+6.49%), T8 (+0.94%), T32 (+1.89%) and T4096 (+0.91%). Its strongest apparent improvements are T64 (−7.48%) and T2 (−7.32%). These are single-process comparisons with independent split retuning, not a promotion or repeatability decision.

| Stack | Node / image | Torch runtime | Torch distribution metadata | Toolkit / DSL native compiler | Mapped NVSHMEM / NCCL |
| --- | --- | --- | --- | --- | --- |
| cuda130 | hu-pdx-119 / `nvcr.io/nvidia/pytorch:25.11-py3` | `2.10.0a0+b558c986e8.nv25.11` | `2.10.0a0+b558c986e8.nv25.11` | 13.0 / DSLCudaVersion(major=12, minor=9) | 3.4.5 / 2.28.8 |
| cuda132 | hu-pdx-88 / `nvcr.io/nvidia/pytorch:26.05-py3` | `2.12.0a0+5aff3928d8.nv26.05` | `2.12.0a0+5aff3928d8.nv26.5.50603568` | 13.2 / DSLCudaVersion(major=13, minor=3) | 3.6.5 / 2.30.4 |

Both use DSL 4.7.1. CUDA 13.0 imports native cu12 compiler 12.9 with the direct-decode gate false, selecting fallback; CUDA 13.2 imports cu13 compiler 13.3 with that gate true, selecting direct decode. Native extension hashes, interpreter paths, actual compiled source and rank resources are retained per record. Torch runtime and distribution metadata are separate fields.

The new CUDA 13.0 auto map (SHA `c51f9760deed64e9c403f262a7d79acd99f65c318326214b6766ce1656e0368c`) matches its control native/CUPTI map; all eight PID/start-time/argv identities are stable during each capture. CUDA 13.2 has a matched auto map but no fresh fixed-control map. Both auto processes map CUPTI; two distinct CUPTI binaries are mapped on 13.2, which does not establish binding ownership.

The benchmark remains 100-iteration CUPTI, CUDA graph, cold L2 and three warmups, with no fallback warning or NCU cleanup flag. Host ranking scores remain separate from these GPU timing rows. Final ten cache-capacity entries do not replace thirteen actual selections. Current cache-directory/process liveness is outside this CPU audit.

Different selected tactics, compiler/decoder behavior, Torch, libraries, image and node prevent causal attribution. Input shapes are equal but input-byte identity across Torch versions is not established here. No statistical confidence, later-row minimum, repeated-run conclusion or cubin/register audit is inferred.

Reproduce from the effort root:

```bash
python3 -B candidates/cuda130_recovery_0908b/performance/audit_fresh_full13.py \
  --output logs/cross-stack-recovery0908b-c1-full13-001-analysis
```
