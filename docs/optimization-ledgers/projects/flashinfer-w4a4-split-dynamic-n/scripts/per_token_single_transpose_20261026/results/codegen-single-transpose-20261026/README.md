# Single-transpose codegen evidence

Four public profiler runs on c3 B300 GPU7, using exactly the saved V41-Flash per-token control tactics from the native public benchmark: token32/N16 and token4096/N128. Each source has its own verified DSL namespace; only unchanged native C++ inputs reuse the persistent cache. Public per-token recipe and input quantization remain enabled; no fallback AUTO compilation is permitted. These are codegen diagnostics, not timing measurements.

| Tokens | FC1 registers | FC1 SASS LDTM | FC1 SASS STTM | FC1 SASS SHFL |
|---:|---:|---:|---:|---:|
| 32 | 110 → 100 | 12 → 7 | 6 → 3 | 0 → 16 |
| 4096 | 107 → 96 | 12 → 7 | 6 → 3 | 0 → 16 |

Both FC1 tactics preserve dynamic shared memory and one CTA/SM, with zero local memory or SASS local load/store sites. FC2 PTX and cubins are byte-identical for both tactics. The FC1 SASS contains the native up/gate TMEM loads, sixteen scale shuffles, componentwise activation, and one surviving TMEM transpose; the control has two pre-activation transposes. Counts are static instruction sites, not dynamic instruction counts.

Runtime image is `nvcr.io/nvidia/pytorch:26.05-py3` (CUDA13.2); generated PTX reports the bundled CUDA13.3 NVVM producer. Complete PTX, cubins, SASS, source receipts, exact public commands, replayed tactics and compiler/resource metadata are retained beside this report.
