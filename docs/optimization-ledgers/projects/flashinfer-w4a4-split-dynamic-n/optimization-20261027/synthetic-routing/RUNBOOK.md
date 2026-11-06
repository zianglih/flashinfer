# Seeded-uniform routing experiment

Rejected after the three-cell screen; no broad run or production change. W4A4 T4096 was−0.285%, per-token T4096−0.264%, and MXFP4x8 T4−1.513%. All18 phases/1800 CUPTI samples passed validation. GPUs1/2/5 are idle and released. [Full results and selected tactics](harness/RESULTS.md).

- **Base:** clean `1e69d0a391fd926d21a35388cacf2df3c1c22baf`; rejected candidate had only two unstaged initializer/configuration files. Patch SHA256 `ef52e932454d125d70452690ce479a0fe15faefc1cb190ea2d7d00ad80ae40cf`. Owned candidate source copies are removed after source/hash/no-consumer proof; evidence and caches remain.
- **Policy:** private device generator seed515, FP32 global scores and unique top-k IDs; swap-AB blockscaled only. Legacy/Rubin and W4A16 policy is preserved. No serving-input dependency, new tactics, cache axis, forced local work, or seed search.
- **Sources/caches:** independent remote control/candidate checkouts under `/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261027/synthetic-routing`; nine verified persistent native artifact links per source, private CuTe namespaces. Full source manifests and native-cache receipts are in `harness/gate-evidence/harness/`.
- **Environment:** existing C3 `fi-moe-nvfp4-port-1026`, CUDA13.2, CuTe4.8, PyTorch2.12 NVIDIA26.05, private CUPTI overlay. Frozen observer SHA256 `a09d15e086c866653aa95f3529e28ecbdceee8aea0b1de68f18cdfd280c852b0` requires100 CUPTI samples and saved native-winner hits; both timer fallbacks are fatal.
- **Measurements:** GPU1 N3U W4A4 T4096; GPU2 N3U per-token T4096; GPU5 N3U MXFP4x8 T4. Fresh control/candidate native selection caches; NV native eager and MX native graph timing stay unchanged. Public frozen measurements use10 warmups/100 cold-L2 CUPTI samples, same routes/weights, unfused finalize; NV includes input quantization. No historical timings are reused.
- **Instrumentation:** wrapper records actual/synthetic/prepared route hashes and cold-batch references outside timing. Candidate profile hashes must match the independent route gate. Both arms must admit the exact same native tactics for every profile shape.

## Completed gates

`route_gate.py` passed352 profiles: four models × four formats ×22 native buckets, including all13 published token rows. It checks all EP offsets, global ID range/uniqueness, local histogram conservation, determinism, global CPU/CUDA RNG isolation, and all existing route-tile allocation bounds. No zero-local synthesized profile was observed at tokens≥4 on any checked rank. Tiny1/2-token zero cases remain in the raw receipt without intervention.

One synchronized untimed maximum-profile observation measured allocator peak deltas83.44MiB for K3 and60.56MiB for N3U at16384 tokens, versus the analytical visible-tensor sums60MiB/37.5MiB. These include top-k allocation behavior and are setup observations, not steady benchmark timings. Observed setup wall times were approximately1.00ms/0.44ms respectively.

`api_gate.py` passed eight format/API cases (functional/wrapper), with24 cache-key identity checks and16 cold-batch identity checks. Warm captured calls did not profile, outputs matched the warm eager result bitwise, and original inputs were unchanged. This is one admissible tactic per bucket only for the gate; the three benchmarks use the full native search. Nonzero-offset/zero-route coverage above is route-generation/allocation coverage, not a new GPU-kernel correctness claim.

Early gate archive: `harness/gate-evidence-transfer.tar.gz`, SHA256 `0405f589c371269f5db4e677936c1a26e7e1b55ed8bc05af6e4d397f244804ac` (21 files). Final archive: `harness/evidence-transfer.tar.gz`, SHA256 `870e1095c5bf9c5e931bad90233a1631303fb66c52677ab0a61daaaebfa9db16` (98 files). An initial sidecar pins the route/API gate outputs, source config, runner, wrapper and launch receipt while all three workers were still in control AUTO. Its generated watcher failed with a Python syntax error before monitoring; that error and initial pin are preserved. The replacement watcher ran after all workers completed and verified every artifact still matched the original pin. There is no continuous-monitoring claim for the uncovered interval. Running benchmark source, observer, runner bytes and receipts were left unchanged.

## Commands

Run local transport only through the managed HAI CLI:

```bash
command -v h  # /usr/local/bin/h
python3 swap-ab-exact-20261027/remote.py optimization-20261027/synthetic-routing/harness/status_remote.py
```

Exact launched commands, source/config hashes, native winner caches, per-profile routing proofs and raw samples are stored in the local final archive and remote run receipts. The local helper scripts preserve the same environment and public `benchmarks/bench_moe_deepseek.py` arguments as the prior controlled campaign. `harness/summarize.py` verified every sample median, saved winner, matched workload, and all43 native profile admission pairs; independent audit is recorded separately.
