# Shared SF/payload coordinates: rejected

Four Gather4 issuer warps reuse the token IDs loaded for scale-factor copies through a compile-time XOR ownership permutation. This preserves bank-conflict-free 4-byte SF stores, four payload issuers, the existing static payload issue loop, SF full-N duplication for two-CTA MMA, and all pipeline/barrier/FC2 behavior. It adds ownership arithmetic and coordinate liveness. No tuning axis or model/dtype-specific policy was added.

**Decision: reject.** The 8-case screen is mixed and its full-chain geometric mean is negative. A small V3 EP gain does not justify the added ownership logic, while K3 EP and per-token TP regress. The large N3U EP loss has substantial phase/clock drift and is not a precise isolated source-effect estimate. No source changes are retained.

## Source and gates

- Control: retained `475cae6b28a536e24aa8da2ed488d0f00fb5305b` source, materialized and hashed against all 514 bound files. The remote Git parent differs; source hashes are authoritative. This campaign is not relabeled as a later head comparison.
- Candidate kernel SHA256: `dac7f44c8203c364a4bb0b2f945f5508ca1f4d97df35405582b9380a1be46812`.
- Candidate patch SHA256: `7ef957625147f370697511557b04d31c1386614fd1140c1dc743018800555216`.
- Geometry proof: 3,006 combinations, 526,752 payload row/K pairs and 6,112,512 SF row/block pairs. Ownership, bank mapping and linear eligibility equivalence are checked; this is not an async runtime proof.
- 23 bit-exact tests passed; 44 generated kernels have zero STACK/LOCAL/LDL/STL. All 21 paired FC2 cubins are unchanged. Earlier revisions that spilled were not timed. See `GATE_RESULTS.md` and `codegen-summary.json`.
- Timed runtime guards: 64 observations, zero driver-reported local bytes, source/register budget/normal compilation options verified. Driver attributes alone do not prove every benchmark cubin has zero stack; the separate 44-cubin gate provides the inspected codegen coverage.

## Method

B300 on `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2.1, CuTe DSL 4.8.0, driver 595.58.03. GPUs 5 and 7 run independent lanes; each case is control/candidate/candidate/control on the same physical GPU. Every scope has 100 strict CUPTI cold-L2 CUDA-Graph samples after 10 warmups, no fallback, no native retune and no cache winner selection. Tactics are explicit geometry probes selected before measurement, not replacements for the published native-winner results. Persistent native/CuTe caches remain enabled; diagnostic compilation options are absent during timing.

Inputs use the public DeepSeek benchmark creation path, seed 42 and routing bias scale 0.01. Source manifests, actual route IDs/weights, activation/SF hashes, shape/tactic and GPU UUID are checked across phases. GEMM weight tensors are seeded consistently but are not individually byte-hashed; the route-facts weights hash is a routing-weights hash. NVFP4 full-chain scopes include input quantization and per-token uses the benchmark 4over6 recipe.

Runner scopes isolate the GEMM chain under balanced synthetic routes, actual saved routes and dense full-tile stress. `runner_full_tiles` deliberately routes all tokens to the first top-k local experts and can exceed actual EP rank work; it is diagnostic stress and excluded from aggregate summaries. `full_actual` uses the public full chain and actual routes. All samples, including drift, are retained.

Percent change is `(geomean(control phase medians) / geomean(candidate phase medians) - 1) * 100`; positive favors candidate. Spread is the max/min difference between each arm’s two phase medians.

## Full-chain results

| Geometry probe | Control us | Candidate us | Change | Control spread | Candidate spread |
|---|---:|---:|---:|---:|---:|
| ep-v3-w4a4-wide | 246.754 | 244.962 | +0.731% | 0.052% | 0.026% |
| ep-v41-mxfp8 | 595.324 | 595.164 | +0.027% | 0.121% | 0.239% |
| ep-k3-w4a4 | 484.359 | 492.459 | -1.645% | 0.906% | 0.335% |
| ep-n3u-mxfp4x8-wide | 363.159 | 375.184 | -3.205% | 3.150% | 2.025% |
| tp-v3-mxfp8 | 442.756 | 443.611 | -0.193% | 0.094% | 0.126% |
| tp-v41-per-token | 530.916 | 534.028 | -0.583% | 0.084% | 0.087% |
| ep-k3-decode-two-cta-k8 | 79.072 | 79.337 | -0.333% | 0.324% | 0.263% |
| tp-n3u-decode-two-cta-k8 | 83.273 | 83.233 | +0.048% | 0.172% | 0.077% |

Geometry-screen geometric means: overall -0.651%, prefill -0.820%, decode -0.143%. These are not full-model scoreboards.

## All measured scopes

| Case | Scope | Control us | Candidate us | Change | C spread | A spread |
|---|---|---:|---:|---:|---:|---:|
| ep-v3-w4a4-wide | runner_balanced | 251.714 | 251.930 | -0.086% | 0.077% | 0.019% |
| ep-v3-w4a4-wide | runner_actual | 260.738 | 259.922 | +0.314% | 0.147% | 0.012% |
| ep-v3-w4a4-wide | runner_full_tiles | 925.303 | 898.791 | +2.950% | 0.031% | 0.032% |
| ep-v3-w4a4-wide | full_actual | 246.754 | 244.962 | +0.731% | 0.052% | 0.026% |
| ep-v41-mxfp8 | runner_balanced | 595.516 | 596.165 | -0.109% | 0.175% | 0.038% |
| ep-v41-mxfp8 | runner_actual | 594.861 | 594.668 | +0.032% | 0.197% | 0.024% |
| ep-v41-mxfp8 | runner_full_tiles | 678.863 | 674.000 | +0.722% | 3.386% | 0.791% |
| ep-v41-mxfp8 | full_actual | 595.324 | 595.164 | +0.027% | 0.121% | 0.239% |
| ep-k3-w4a4 | runner_balanced | 506.691 | 514.004 | -1.423% | 0.133% | 0.044% |
| ep-k3-w4a4 | runner_actual | 468.963 | 475.500 | -1.375% | 0.068% | 0.064% |
| ep-k3-w4a4 | runner_full_tiles | 2438.515 | 2488.194 | -1.997% | 1.361% | 0.030% |
| ep-k3-w4a4 | full_actual | 484.359 | 492.459 | -1.645% | 0.906% | 0.335% |
| ep-n3u-mxfp4x8-wide | runner_balanced | 351.299 | 351.706 | -0.116% | 0.055% | 0.059% |
| ep-n3u-mxfp4x8-wide | runner_actual | 360.011 | 357.186 | +0.791% | 0.102% | 0.018% |
| ep-n3u-mxfp4x8-wide | runner_full_tiles | 1703.585 | 1720.499 | -0.983% | 1.442% | 1.264% |
| ep-n3u-mxfp4x8-wide | full_actual | 363.159 | 375.184 | -3.205% | 3.150% | 2.025% |
| tp-v3-mxfp8 | runner_balanced | 424.595 | 424.619 | -0.006% | 0.060% | 0.034% |
| tp-v3-mxfp8 | runner_actual | 435.091 | 435.147 | -0.013% | 0.088% | 0.033% |
| tp-v3-mxfp8 | runner_full_tiles | 309.050 | 310.098 | -0.338% | 0.047% | 0.186% |
| tp-v3-mxfp8 | full_actual | 442.756 | 443.611 | -0.193% | 0.094% | 0.126% |
| tp-v41-per-token | runner_balanced | 492.683 | 497.100 | -0.888% | 0.049% | 0.080% |
| tp-v41-per-token | runner_actual | 504.732 | 509.412 | -0.919% | 0.035% | 0.088% |
| tp-v41-per-token | runner_full_tiles | 304.314 | 301.290 | +1.004% | 0.037% | 0.048% |
| tp-v41-per-token | full_actual | 530.916 | 534.028 | -0.583% | 0.084% | 0.087% |
| ep-k3-decode-two-cta-k8 | runner_balanced | 345.915 | 345.355 | +0.162% | 0.107% | 0.274% |
| ep-k3-decode-two-cta-k8 | runner_actual | 77.384 | 77.008 | +0.488% | 0.103% | 0.043% |
| ep-k3-decode-two-cta-k8 | full_actual | 79.072 | 79.337 | -0.333% | 0.324% | 0.263% |
| tp-n3u-decode-two-cta-k8 | runner_balanced | 91.705 | 91.577 | +0.140% | 0.262% | 0.192% |
| tp-n3u-decode-two-cta-k8 | runner_actual | 84.008 | 83.944 | +0.076% | 0.172% | 0.019% |
| tp-n3u-decode-two-cta-k8 | full_actual | 83.273 | 83.233 | +0.048% | 0.172% | 0.077% |

## Telemetry and interpretation

Read-only NVML sampling at 10 ms records SM/memory clocks, power, temperature and event reasons with CUPTI timestamps. The reported scope envelope is bracketed by CPU launch timestamps in the CUPTI clock domain, not exact GPU kernel boundaries. NVML values can be coarse or stale. Several prefill phases observe software power-cap reason mask 4 and differing SM clocks; this can reflect candidate utilization as well as external conditions. No clock setting, sample filtering or clock normalization was performed.

V3 EP is a small stable gain (+0.73% with phase spreads below 0.06%). Per-token V41F TP loses 0.58% with phase spreads below 0.09% and reported 2032 MHz/mask 0 throughout. K3 EP loses 1.64% but its control phase spread is 0.91%. N3U EP loses 3.21% with 3.15%/2.03% phase spreads and a 2032-to-1545 MHz regime difference; treat this magnitude as drift-sensitive. Decode differences are small relative to phase variation. Added indexing is therefore not justified by robust broad gains even without interpreting the largest negative as purely source-caused.

## Complete evidence

- `summary.json`: all 30 case/scope rows, CAAC medians, per-phase quartiles, route facts and clock envelopes.
- `runtime-guards.json`: all 64 normal-build observations.
- `screen-evidence/`: all 32 phase receipts and 12,000 raw samples, source/input/runtime guards and clock logs; every file in `MANIFEST.json` verified.
- Screen archive: 208 files, 4,952,030 bytes, SHA256 `2ab626a2d20ecbaa3c10e8a12bf47543ddf73086e8a2c89657257b968784a566`.
- Gate archive: 147 files, 2,854,113 bytes, SHA256 `1e1fe1a8fc27d52cb16a72b0686b46b1a66b1355aa9440323a7df007337d1733`.
- `cases.json`, `lane-plan.json`, `local-source.json`, `candidate.patch`, launch/fetch/analyze helpers preserve the exact comparison.
- GPU 5 UUID `GPU-e6225ab4-a550-1aa4-dd51-687033fb4ad1`; GPU 7 UUID `GPU-7bda223d-cb19-0578-d9d3-e925a359254b`. Both lanes released.
- No sanitizer, commit or push for this experiment. Immutable remote sources and evidence are preserved.
