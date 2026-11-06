# Bulk-drain disposition

Rejected after bounded exact coverage and repeated fixed-native C–A–A–C timing. No source retained. The change is numerically sound in the tested scope, but the added entry/tail work has no convincing broad repeatable gain.

| Case | First prefill bracket C/A | Retention bracket C/A |
|---|---:|---:|
| decode-v3-cute-dsl-per-token | — | 0.999890× |
| decode-v41-flash-cute-dsl-w4a8 | — | 0.999904× |
| decode-kimi-k3-cute-dsl-mxfp8 | — | 0.999723× |
| decode-nemo3-ultra-cutedsl | — | 0.999417× |
| prefill-v3-cutedsl | 1.001755× | 1.000837× |
| prefill-v3-cute-dsl-mxfp8 | 1.018712× | 0.991455× |
| prefill-kimi-k3-cutedsl | 1.004297× | 1.016927× |
| prefill-nemo3-ultra-cutedsl | 1.006377× | 0.999118× |

Ratio above 1 favors the candidate. Decode guards were neutral (largest paired latency increase about 0.06%). The three inactive guard kernels are byte-identical across both sources. All 15 inactive T128 configurations are supported by the source-derived constructor/constexpr proof.

V3 MXFP8 reversed paired direction and its adjacent comparisons disagree. K3 showed a second-bracket gain, but candidate drift was −2.07%; its first bracket had opposite adjacent directions. Nemo’s initial gain did not repeat. Process-boundary telemetry was captured for every retention leg; it cannot establish clocks during the timed samples.

Validation: 48 initial static exact replays plus 24 CLC/inline replays; 16 initial performance legs (1,600 samples) plus 32 retention legs (3,200 samples). Final independent audit verified all 344 inputs, source/cache/route/dispatch bindings, actual compiler artifacts, unchanged resource plans and zero stack/local spills. No AUTO search or new tactics.

Measured source remained the frozen 0b7 checkout plus the exact d02 benchmark bytes. Local review was at d02 with the identical kernel patch. Cleanup removes only the rejected local/remote candidate source trees; no recovery archive is created. Patch, manifests, helpers, tensor bundle, logs, raw samples, compiler evidence, persistent caches and external symlink targets remain. See cleanup-local.json and cleanup-remote.json.
