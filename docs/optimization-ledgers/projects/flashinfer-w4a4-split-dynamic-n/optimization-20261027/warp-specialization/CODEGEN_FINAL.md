# Final r2 runtime and generated-code audit

Frozen kernel `e14519f9`, source config `62da0622`, final gate manifest `c8146221`. Production source is unchanged during measurement.

The final gate passed 144 source-paired public graph replays, 28 existing accuracy tests, 96 preparation byte replays, six unchanged default quantizer contracts, and 110 routed quantizer replays. The earlier physical-SF-padding poison proof passed 64 public replays with 112 hooks. No sanitizer was run.

All 72 final candidate binaries have 256 threads, zero stack/local spill bytes, no scalar SFB `cp.async` or SASS `LDGSTS`, and no `SETMAXNREG`. Operand/accumulator stage counts and TMEM column allocations are unchanged for the paired tactics.

CLC + PDL representatives (control → final candidate); counts are static instruction sites, not executed counts or timing.

| Config / format | N | FC | Registers | Scalar cp.async | SYNCS | MEMBAR |
|---|---:|---:|---:|---:|---:|---:|
| 0 / NVFP4 | 16 | 1 | 83 → 75 | 4 → 0 | 131 → 122 | 4 → 3 |
| 0 / NVFP4 | 16 | 2 | 74 → 70 | 40 → 0 | 145 → 129 | 4 → 3 |
| 1 / NVFP4 per-token | 32 | 1 | 112 → 110 | 4 → 0 | 151 → 142 | 6 → 3 |
| 1 / NVFP4 per-token | 32 | 2 | 92 → 86 | 8 → 0 | 137 → 149 | 6 → 3 |
| 2 / MXFP8 | 64 | 1 | 91 → 82 | 2 → 0 | 149 → 133 | 5 → 3 |
| 2 / MXFP8 | 64 | 2 | 78 → 78 | 4 → 0 | 121 → 161 | 4 → 3 |
| 3 / MXFP4x8 | 16 | 1 | 86 → 79 | 2 → 0 | 175 → 158 | 9 → 3 |
| 3 / MXFP4x8 | 16 | 2 | 78 → 70 | 4 → 0 | 145 → 181 | 6 → 3 |
| 4 / NVFP4 | 128 | 1 | 87 → 72 | 0 → 0 | 104 → 112 | 3 → 3 |
| 4 / NVFP4 | 128 | 2 | 104 → 94 | 0 → 0 | 166 → 186 | 5 → 5 |
| 5 / NVFP4 per-token | 256 | 1 | 92 → 90 | 0 → 0 | 78 → 85 | 3 → 3 |
| 5 / NVFP4 per-token | 256 | 2 | 158 → 160 | 0 → 0 | 127 → 158 | 11 → 11 |
| 6 / MXFP8 | 256 | 1 | 92 → 87 | 0 → 0 | 100 → 108 | 3 → 3 |
| 6 / MXFP8 | 256 | 2 | 114 → 112 | 0 → 0 | 134 → 130 | 11 → 11 |
| 7 / MXFP4x8 | 128 | 1 | 76 → 74 | 0 → 0 | 85 → 92 | 3 → 3 |
| 7 / MXFP4x8 | 128 | 2 | 96 → 96 | 0 → 0 | 118 → 113 | 5 → 5 |
| 8 / NVFP4 M512 | 16 | 1 | 88 → 85 | 4 → 0 | 121 → 117 | 6 → 3 |
| 8 / NVFP4 M512 | 16 | 2 | 78 → 72 | 8 → 0 | 137 → 149 | 6 → 3 |

The dedicated producer roles remove scalar scale-factor copies and their proxy fences, but each independent issuer has its own pipeline wait/announce sites. `SYNCS` totals therefore vary by specialization; these results do not establish a universal synchronization-instruction reduction. Epilogue CTA barriers and UMMA release sites remain unchanged. The installed CuTe 4.8 expected-byte producer acquisition adds no per-stage full-CTA join.

R2 also removes the redundant MMA startup dependency wait; MMA waits at exit before releasing its resources. Activation and epilogue roles wait before consuming predecessor data. The paired replay gate includes PDL disabled and enabled, static and CLC scheduling, one/two CTA, narrow/wide N, empty/returned routes and the M512 two-channel case.

Full code/resource records and hashes: `final-evidence/r2/codegen-summary-final.json`. Per-specialization PTX, CUBIN, SASS and resource reports remain in the evidence archive. Performance is evaluated separately by fresh native AUTO and frozen C-A-A-C measurements.
