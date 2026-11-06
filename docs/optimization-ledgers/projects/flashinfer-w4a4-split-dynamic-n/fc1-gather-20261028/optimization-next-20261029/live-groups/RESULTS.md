# Live-group Gather4 experiment — reject

No source was committed or pushed. Keep retained475 unchanged. This experiment passes correctness and generated-code gates but regresses all six measured prefill cases; its two decode cases are effectively neutral.

- Source: retained `475cae6b28a536e24aa8da2ed488d0f00fb5305b`, one unstaged file originally in `flashinfer-fc1-gather-live-groups-review` (now retired; its separate row-outer successor is `flashinfer-fc1-gather-row-outer-review`). Patch SHA `8e245181072ee512db8da95df1a2eb46c8828d93bb7841c169ecdcee7f731104`.
- Design: lane-held route IDs outside K; four issuers broadcast coordinates with four SHFLs per runtime live-group iteration. Gather4 bytes are bounded by rounded live rows. SF transport, barriers/quorums, storage, release/publication, PDL, tactics and FC2 are unchanged. No shape/dtype heuristics or extra tuning axes.
- Gates: 2,976 ownership combinations;23 exact cases per source;44 paired generated kernels, all zero local storage/LDL/STL;21 FC2 cubins byte-identical. See `GATE_RESULTS.md` and raw gate archive. No sanitizer.
- Screen: GPU7 B300, CUDA13.2.1, CuTeDSL4.8.0, image `nvcr.io/nvidia/pytorch:26.05-py3`; source-bound fixed tactics, no search. Every case uses C-A-A-C,100 strict-CUPTI cold-L2 CUDA-Graph samples per scope per phase,10 warmups. NVFP4 full-chain includes input quantization, per-token uses the benchmark recipe. Source and route hashes, runtime register guards, and persistent caches retained.
- Complete audit:32 phases,30 case/scope rows,12,000 samples,64 executable register guards with zero local bytes. GPU UUID `GPU-7bda223d-cb19-0578-d9d3-e925a359254b`. All source/route/input/tactic identities match within each four-phase comparison. Timer-source SHA `c8fee53c767a27781ecf5671d971d4b9a324e19386c8d0c26cd5ac611890c1e6`.
- All results are retained without sample filtering or clock normalization. Positive percentages mean candidate faster: `(geomean(control phase medians) / geomean(candidate phase medians) - 1) * 100`. Repeat spread is `max/min-1` within each source.

## Actual full chain

T8192 for prefill, T8 for decode. N128/N256 K3 EP are separate fixed-tactic diagnostics, not two independently sampled model workloads. Prefill geometric mean −7.07%; decode geometric mean +0.0003%. These are bounded-screen summaries, not the complete benchmark scoreboard.

| Case | Retained µs | Candidate µs | Change | Control spread | Candidate spread |
|---|---:|---:|---:|---:|---:|
| k3-ep-w4a4-n128 | 486.340 | 526.548 | -7.636% | 0.079% | 0.195% |
| k3-ep-w4a4-n256 | 517.499 | 529.948 | -2.349% | 0.456% | 0.124% |
| k3-tp-per-token | 1249.770 | 1253.425 | -0.292% | 0.074% | 0.063% |
| n3u-ep-w4a4 | 416.550 | 440.379 | -5.411% | 1.039% | 0.055% |
| n3u-ep-mxfp8 | 547.890 | 634.953 | -13.712% | 0.627% | 3.896% |
| n3u-tp-mxfp4x8 | 700.531 | 798.454 | -12.264% | 1.100% | 0.205% |
| k3-ep-decode | 79.896 | 79.753 | +0.180% | 0.100% | 0.180% |
| n3u-tp-decode | 84.752 | 84.904 | -0.179% | 0.038% | 0.169% |

## All scopes

`runner_balanced` uses the unchanged production profile hook. `runner_actual` preserves the actual saved routes with identical other runner inputs. `runner_full_tiles` is synthetic stress: all tokens route to the first top-k local experts, filling tiles; in EP this may substantially increase rank load. It is excluded from full-chain summaries and any scoreboard.

| Case | Scope | Retained µs | Candidate µs | Change | Control spread | Candidate spread | C-A-A-C last/first-quartile change |
|---|---|---:|---:|---:|---:|---:|---|
| k3-ep-w4a4-n128 | runner_balanced | 506.251 | 540.052 | -6.259% | 0.225% | 0.035% | +0.13%, +0.04%, +0.04%, +1.21% |
| k3-ep-w4a4-n128 | runner_actual | 468.091 | 512.698 | -8.701% | 0.072% | 0.498% | +0.32%, +2.50%, +2.33%, +1.23% |
| k3-ep-w4a4-n128 | runner_full_tiles | 2438.838 | 2818.377 | -13.467% | 1.321% | 1.636% | +8.11%, +3.29%, +3.01%, +8.08% |
| k3-ep-w4a4-n128 | full_actual | 486.340 | 526.548 | -7.636% | 0.079% | 0.195% | +0.74%, +2.16%, +1.99%, +0.99% |
| k3-ep-w4a4-n256 | runner_balanced | 496.700 | 515.636 | -3.672% | 0.029% | 0.013% | +0.06%, +0.05%, +0.04%, -0.07% |
| k3-ep-w4a4-n256 | runner_actual | 505.547 | 517.212 | -2.255% | 0.352% | 0.015% | -0.01%, -0.03%, -0.08%, +0.43% |
| k3-ep-w4a4-n256 | runner_full_tiles | 2709.884 | 2569.860 | +5.449% | 0.150% | 0.082% | -0.01%, +0.36%, +0.49%, -0.13% |
| k3-ep-w4a4-n256 | full_actual | 517.499 | 529.948 | -2.349% | 0.456% | 0.124% | -0.07%, -0.06%, -0.33%, +0.32% |
| k3-tp-per-token | runner_balanced | 1151.817 | 1207.418 | -4.605% | 0.075% | 0.003% | -0.08%, +0.11%, -0.05%, -0.05% |
| k3-tp-per-token | runner_actual | 1223.362 | 1226.242 | -0.235% | 0.004% | 0.033% | -0.03%, -0.07%, +0.01%, +0.01% |
| k3-tp-per-token | runner_full_tiles | 1011.872 | 1033.672 | -2.109% | 0.046% | 0.015% | -0.04%, +0.01%, -0.02%, +0.04% |
| k3-tp-per-token | full_actual | 1249.770 | 1253.425 | -0.292% | 0.074% | 0.063% | -0.14%, +0.10%, +0.09%, -0.03% |
| n3u-ep-w4a4 | runner_balanced | 382.227 | 406.707 | -6.019% | 0.008% | 0.047% | +0.01%, -0.06%, -0.02%, -0.01% |
| n3u-ep-w4a4 | runner_actual | 405.475 | 430.699 | -5.857% | 0.016% | 0.034% | +0.03%, +0.02%, -0.04%, -0.01% |
| n3u-ep-w4a4 | runner_full_tiles | 2396.569 | 2556.252 | -6.247% | 0.227% | 0.053% | +1.13%, +0.16%, +0.16%, +1.35% |
| n3u-ep-w4a4 | full_actual | 416.550 | 440.379 | -5.411% | 1.039% | 0.055% | -0.05%, +0.09%, -0.04%, -0.95% |
| n3u-ep-mxfp8 | runner_balanced | 508.359 | 572.996 | -11.281% | 4.068% | 2.823% | +5.48%, +8.70%, +6.13%, +5.10% |
| n3u-ep-mxfp8 | runner_actual | 541.571 | 616.690 | -12.181% | 0.444% | 1.883% | +4.27%, +5.38%, +3.94%, +4.07% |
| n3u-ep-mxfp8 | runner_full_tiles | 3576.869 | 4071.703 | -12.153% | 0.400% | 1.874% | +6.88%, +8.35%, +6.03%, +10.40% |
| n3u-ep-mxfp8 | full_actual | 547.890 | 634.953 | -13.712% | 0.627% | 3.896% | +5.19%, -4.26%, +3.19%, +0.44% |
| n3u-tp-mxfp4x8 | runner_balanced | 672.691 | 762.342 | -11.760% | 0.482% | 0.088% | +2.46%, +0.39%, +0.12%, +3.21% |
| n3u-tp-mxfp4x8 | runner_actual | 706.230 | 797.854 | -11.484% | 3.045% | 0.130% | +2.99%, +1.71%, +0.79%, +3.40% |
| n3u-tp-mxfp4x8 | runner_full_tiles | 633.985 | 731.982 | -13.388% | 0.760% | 0.085% | -0.90%, -0.31%, +0.31%, +0.64% |
| n3u-tp-mxfp4x8 | full_actual | 700.531 | 798.454 | -12.264% | 1.100% | 0.205% | +3.90%, +3.04%, +0.07%, +1.98% |
| k3-ep-decode | runner_balanced | 357.131 | 359.218 | -0.581% | 0.121% | 0.036% | +0.19%, +0.06%, -1.14%, -0.03% |
| k3-ep-decode | runner_actual | 78.633 | 78.448 | +0.235% | 0.264% | 0.124% | +0.29%, -0.12%, -0.49%, +0.12% |
| k3-ep-decode | full_actual | 79.896 | 79.753 | +0.180% | 0.100% | 0.180% | +0.44%, +0.16%, -0.28%, -0.32% |
| n3u-tp-decode | runner_balanced | 92.040 | 91.913 | +0.139% | 0.018% | 0.192% | +0.24%, -0.45%, +0.59%, +0.03% |
| n3u-tp-decode | runner_actual | 85.416 | 85.497 | -0.094% | 0.057% | 0.131% | +0.19%, +0.11%, +0.11%, +0.30% |
| n3u-tp-decode | full_actual | 84.752 | 84.904 | -0.179% | 0.038% | 0.169% | +0.08%, -0.15%, +0.08%, +0.30% |

## Gathered payload geometry

The following counts are source-derived row volume summed over FC1 expert token tiles, before multiplying channel/K tiles. SF work is unchanged. Retained dead rows use descriptor-OOB coordinates, so these counts mainly describe zero-fill/shared-destination work and TMA issue/completion bytes, not an equivalent reduction in HBM activation reads. They are not causal performance proof.

| Case | Actual local routes | Retained physical rows | Candidate rounded rows | Payload reduction |
|---|---:|---:|---:|---:|
| k3-ep-w4a4-n128 | 16464 | 23680 | 18144 | +23.38% |
| k3-ep-w4a4-n256 | 16464 | 28672 | 18144 | +36.72% |
| k3-tp-per-token | 131072 | 231168 | 138208 | +40.21% |
| n3u-ep-w4a4 | 22996 | 27136 | 24000 | +11.56% |
| n3u-ep-mxfp8 | 22996 | 27136 | 24000 | +11.56% |
| n3u-tp-mxfp4x8 | 180224 | 212992 | 188224 | +11.63% |
| k3-ep-decode | 18 | 288 | 288 | +0.00% |
| n3u-tp-decode | 176 | 2496 | 2496 | +0.00% |

## Clock telemetry and limits

A separate read-only NVML process sampled at10ms. The table shows samples within the CPU launch-envelope of each actual-chain scope in CUPTI timestamp units; it is not a per-kernel clock trace. Sampling may be coarse/stale and the envelope also includes cold-L2 preparation and synchronization. Telemetry was not used to select or normalize samples.

| Case | Phase | SM MHz counts | Reason-mask counts | Temperature °C |
|---|---|---|---|---|
| k3-ep-w4a4-n128 | 0 control | {'1740': 5, '1965': 1} | {'4': 6} | [45, 46] |
| k3-ep-w4a4-n128 | 1 candidate | {'1965': 3, '2017': 3} | {'4': 4, '0': 2} | [43, 47] |
| k3-ep-w4a4-n128 | 2 candidate | {'1995': 6} | {'4': 6} | [47, 48] |
| k3-ep-w4a4-n128 | 3 control | {'1740': 4, '1965': 2} | {'4': 6} | [47, 48] |
| k3-ep-w4a4-n256 | 0 control | {'2032': 6} | {'0': 6} | [45, 46] |
| k3-ep-w4a4-n256 | 1 candidate | {'2017': 4, '2025': 3} | {'4': 7} | [43, 48] |
| k3-ep-w4a4-n256 | 2 candidate | {'2010': 7} | {'4': 7} | [47, 47] |
| k3-ep-w4a4-n256 | 3 control | {'2032': 6} | {'0': 6} | [47, 47] |
| k3-tp-per-token | 0 control | {'2032': 13} | {'0': 13} | [42, 42] |
| k3-tp-per-token | 1 candidate | {'2032': 14} | {'0': 14} | [42, 42] |
| k3-tp-per-token | 2 candidate | {'2032': 14} | {'0': 14} | [41, 43] |
| k3-tp-per-token | 3 control | {'2032': 13} | {'0': 13} | [40, 42] |
| n3u-ep-w4a4 | 0 control | {'2032': 5} | {'0': 5} | [40, 40] |
| n3u-ep-w4a4 | 1 candidate | {'2017': 5} | {'4': 5} | [47, 47] |
| n3u-ep-w4a4 | 2 candidate | {'2025': 6} | {'4': 6} | [46, 47] |
| n3u-ep-w4a4 | 3 control | {'1980': 6} | {'4': 6} | [47, 47] |
| n3u-ep-mxfp8 | 0 control | {'1275': 6} | {'4': 6} | [49, 49] |
| n3u-ep-mxfp8 | 1 candidate | {'1537': 6, '1545': 2} | {'4': 8} | [49, 50] |
| n3u-ep-mxfp8 | 2 candidate | {'1537': 7} | {'4': 7} | [50, 50] |
| n3u-ep-mxfp8 | 3 control | {'1275': 1, '1267': 5} | {'4': 6} | [49, 49] |
| n3u-tp-mxfp4x8 | 0 control | {'1972': 4, '1995': 4} | {'4': 8} | [44, 45] |
| n3u-tp-mxfp4x8 | 1 candidate | {'2017': 2, '2032': 7} | {'0': 9} | [45, 45] |
| n3u-tp-mxfp4x8 | 2 candidate | {'2032': 9} | {'4': 9} | [43, 43] |
| n3u-tp-mxfp4x8 | 3 control | {'1965': 8} | {'4': 8} | [45, 45] |
| k3-ep-decode | 0 control | {'2032': 2} | {'0': 2} | [36, 36] |
| k3-ep-decode | 1 candidate | {'2032': 2} | {'0': 2} | [34, 34] |
| k3-ep-decode | 2 candidate | {'2032': 1} | {'0': 1} | [34, 34] |
| k3-ep-decode | 3 control | {'2032': 1} | {'0': 1} | [35, 35] |
| n3u-tp-decode | 0 control | {'2032': 2} | {'0': 2} | [33, 33] |
| n3u-tp-decode | 1 candidate | {'2032': 2} | {'0': 2} | [33, 33] |
| n3u-tp-decode | 2 candidate | {'2032': 2} | {'0': 2} | [33, 33] |
| n3u-tp-decode | 3 control | {'2032': 2} | {'0': 2} | [34, 34] |

Mask4 is NVML software power cap. Several prefill scopes encounter it, and N3U MX shows sizable intra-phase ramps. Power limiting may reflect changed utilization as well as external variation; it is not automatically an unrelated noise source. The screen therefore does not establish an iso-clock percentage or isolate a single instruction as causal. Candidate is slower even while reported clocks are higher for N3U EP MXFP8; K3 TP and decode remain at2032MHz/mask0. No clock or power setting was changed.

## Interpretation

- Static wide-tile code size shrinks, but runtime SHFL/loop/address control is introduced into every K stage. Negative results are consistent with that recurring issue cost outweighing avoided payload work. This screen measures the combined patch and cannot isolate those costs individually.
- N256 synthetic full-tile stress improves5.45% while N128 stress regresses13.47%; avoiding dead rows is not a sufficient predictor of the outcome. The actual N256 chain still regresses2.35%.
- The one/two-bank lane design is correct and spill-free, but it is not a worthwhile general replacement for retained static Gather4. Do not retain, widen, or port based only on reduced payload counts. W4 direct-TMA/no-SF experiments remain independent.
- A two-bank `group // 8` lowers to additional quotient/remainder state. Unsigned indexing may simplify arithmetic, but it does not address all the costs and was not mixed into this measured source.

## Evidence

- `screen-evidence/MANIFEST.json` verifies209 files. Compressed screen archive SHA `069a0520079ad48cc155a48ac63d05b7f104b653c102078cba88e9672c67f473` (5,179,859 bytes).
- `summary.json`: every row, four phase medians and quartiles, full route histograms, and telemetry envelopes. `runtime-guards.json`:64 executable observations. `screen-evidence/screen/`: all12,000 raw samples, source receipts, commands, logs and clock JSONL.
- `gate-evidence/`: exact gates, generated-code proof, paired PTX/SASS; archive SHA `bc40fd2c264f599c36ef082e39146f5ecb335551da9871cf0a805e16de6d300b`.
- Reproduce analysis: `python3 fc1-gather-20261028/optimization-next-20261029/live-groups/analyze_screen.py`. Frozen source and all remote raw artifacts remain in persistent storage under `optimization-next-20261029/live-groups`.
- GPU7 released after screen completion; no further source edits or GPU runs are planned for this candidate.
