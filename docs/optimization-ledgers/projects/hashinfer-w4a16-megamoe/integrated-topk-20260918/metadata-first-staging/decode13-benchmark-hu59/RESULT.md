# Metadata-first staging P1 performance result

Status: rejected for performance; no promotion or broad qualification. Owner and independent exact-output/source/closure audits pass.

Fresh hu59 d01/A1 baseline versus metadata-first3cd/P1. Same boot/software, EP8/H7168/I2048/E256/K8, public forward, O3/AUTO4, 3 warmups, 100 cold-L2 CUPTI CUDA-graph rank-MAX samples per row. A1 was measured in the preceding serial static-ID pair; no hu15 timing is used. All samples, including first-sample outliers, are preserved.

Decode 4–512 geometric speedup: **0.94992011×**, 0/8 wins. All 13 rows are slower. This protocol adds a mandatory payload publication; the benchmark does not isolate that cost from scheduling changes or serial drift.

| Tokens | d01 baseline µs | 3cd P1 µs | Speedup | MAD before/after µs | Tactic |
|---:|---:|---:|---:|---:|:---|
| 1 | 65.6805 | 75.8880 | 0.865493× | 0.7355 / 0.9280 | N64 epi |
| 2 | 84.7690 | 92.0965 | 0.920437× | 1.0235 / 0.7995 | N64 epi |
| 4 | 94.7040 | 103.0725 | 0.918810× | 0.6550 / 0.8315 | N64 epi |
| 8 | 120.8970 | 123.5205 | 0.978761× | 1.0080 / 0.8965 | N64 epi |
| 16 | 134.5290 | 142.3690 | 0.944932× | 0.9600 / 0.8320 | N64 epi |
| 32 | 159.7930 | 166.8495 | 0.957707× | 0.6880 / 0.9120 | N64 epi |
| 64 | 182.9625 | 191.0895 | 0.957470× | 0.7035 / 1.0720 | N64 epi |
| 128 | 184.9770 | 198.2255 | 0.933165× | 0.8320 / 0.9125 | N64 epi |
| 256 | 191.0255 | 200.1460 | 0.954431× | 0.7205 / 0.8805 | N64 epi |
| 512 | 195.5375 | 204.6900 | 0.955286× | 0.9915 / 0.8475 | N64 epi |
| 4096 | 464.0205 | 474.1160 | 0.978707× | 2.7530 / 3.2320 | N128 dispatch |
| 8192 | 797.7025 | 810.8860 | 0.983742× | 26.0970 / 22.3200 | N128 dispatch |
| 16384 | 1530.8020 | 1539.4850 | 0.994360× | 49.9690 / 94.1760 | N128 dispatch |

All 13 tactics match on all 8 ranks. All 104 cross-arm outputs are finite and bit-exact, and each candidate output repeats exactly. The candidate frozen 104 files and prior baseline source were rehashed. All candidate supervisor/torchrun/rank process groups closed, with empty GPUs.

The original 342,565,358-byte gzip remains remotely sealed (SHA `5ad0508480ad3d6f782f6b4d7b5aa4bd118db25d896f03a349e01908b2e5e5fa`). Complete local original-member bytes are verified using a 604,872-byte compact bundle and 8 exact-SHA-matching cached rank output files: 165 members total. This is not a local original-gzip-byte verification.

Evidence: [comparison with all quarters and rank tactics](comparison.json), [seal](seal.json), [full member assembly](collected/assembly-verification.json), [runtime review](independent-runtime-review.json), [independent terminal audit](independent-file-timing-audit.json).

No sanitizer, full numerical suite, extra timing repetition, source edit, push or promotion was performed after this result.
