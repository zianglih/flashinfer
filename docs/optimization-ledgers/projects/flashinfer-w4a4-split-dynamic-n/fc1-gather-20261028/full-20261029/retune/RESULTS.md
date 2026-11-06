# Existing-tactic prefill retune

Same clean `fb66a27e` kernel with original frozen d35 winners versus native retuned winners. This measures tactic selection benefit, not a source-code optimization. No tactic axis or source change was introduced.

Two public token buckets (4096, 16384), existing 320 admitted tactics each, same-GPU old/new/new/old replay. 100 strict CUPTI cold-L2 graph samples per cell and phase; input quantizer included. Routes match prior full campaign; each arm’s cache and winners remained frozen during replay.

| Shape | Tokens | Old winner (us) | Native winner (us) | Retune speedup | Old/native phase spread |
|---|---:|---:|---:|---:|---:|
| nemo3-ultra EP8 | 4096 | 285.241 | 246.097 | +15.906% | 0.050% / 0.130% |
| nemo3-ultra EP8 | 16384 | 750.067 | 615.498 | +21.863% | 0.017% / 0.008% |
| v3 EP8 | 4096 | 203.177 | 203.234 | -0.028% | 0.166% / 0.063% |
| v3 EP8 | 16384 | 560.837 | 525.652 | +6.694% | 0.097% / 0.012% |

N3U 4K selects FC1 M256/two CTA instead of M128/one CTA and K steps 8 instead of 4. N3U 16K selects FC1 M512 instead of M256; FC2 is unchanged. V3 4K retains the identical tactic; V3 16K selects route N128 instead of N256 and FC1 M512 instead of M256. These are already-admitted choices that increase gathered-activation reuse.

| Shape | Native process wall | cute.compile API wall | Profiling excluding nested compile | Other context wall |
|---|---:|---:|---:|---:|
| ep-nemo3-ultra-nvfp4 | 192.48s | 161.44s | 12.27s | 5.03s |
| ep-v3-nvfp4 | 160.18s | 133.05s | 10.16s | 3.90s |

Each search made 115 `cute.compile` API calls and 642 native profiling calls. Compile includes SDK-cache work and runtime resource checks; profiling exclusive time still includes warmup, graph capture, waits, and timing machinery. It is not pure GPU execution time. Persistent compilation caches were retained.

Fresh managed winners are archived under `evidence/runs/<job>/cache-native/` for later replay. Raw samples, source/guard receipts, nested wall telemetry, and exact commands are under `evidence/runs/`. Both source and helper hashes are recorded.

Archive SHA256: `9a411345a65916fdf823d4dcb27107ab75b1bb22a99488b440d29436fb87b555`. The abandoned default 20-bucket searches are separate remote diagnostics under `optimization-next-20261029/retune`; final evidence is under `retune-prefill`.
