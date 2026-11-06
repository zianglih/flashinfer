# Final retained-source qualification

Benchmark/publication head: `61249e0bbd40dd2c6e583e4e48ff95e055a3c7f8`. This file reports completed bounded qualification; it does not relabel historical full tests or sanitizer runs as final-head tests.

## Exact source binding

```json
{
  "complete": true,
  "head": "61249e0bbd40dd2c6e583e4e48ff95e055a3c7f8",
  "source_sha256": {
    "flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py": "c9b6948d8f7645d5076d3aa06d1d32b43b99846eb36749f83e5262d56959aa38",
    "flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py": "8acbdcf47b61cbe6256ff21023a4d15e78b0cf6c1b8ffa0d6f9469afb806af17"
  },
  "sanitizer": false,
  "scope": "Focused exact and generated-code gates, with independently bound source hashes. Historical broad tests remain labeled by their tested commits."
}
```

## Audited raw receipt fields

`optimization-20261028/tp-small-gemm-round/static-grid/composed/qualification.json` · SHA256 `101fc1634ede2032f6a18b22dec43b6b37d313dca5fd3387371521a297bdfc94` (qualification fields only)

```json
{
  "complete": true,
  "retained_head": "61249e0bbd40dd2c6e583e4e48ff95e055a3c7f8",
  "control_head": "d7e5ea1c67e6d5f011377e340811ffc377a41763",
  "changed_paths": [
    "flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py"
  ],
  "kernel_sha256": "c9b6948d8f7645d5076d3aa06d1d32b43b99846eb36749f83e5262d56959aa38",
  "patch_sha256": "a15762dcb0602d3973f557129a22e9fb4c75017289b3382273dd3335d69d1626",
  "source_receipt_sha256": "0db74fa955fc9b388210a47811f4828b79d8e84f8d0d30419eaed3656f8170c3",
  "gate_archive_sha256": "909c32058f6f8ab5c9aef4046445f19d0520ce66ea68d85d7cb7ab88054b499c",
  "gate_files_verified": 174,
  "source_files_per_arm": 348,
  "composed_exact_replays_per_source": 16,
  "composed_gemm_pairs": 16,
  "composed_combine_pairs": 2,
  "actual_cuda_traces": 8,
  "sanitizer": false,
  "device_raw_code_identical": true,
  "precommit_sha256": "87bd1c345e4ae6dd22c74b419eba5c052e7d4f1ad45e4add9eba2627621ef694",
  "canonical_precommit_sha256": "87bd1c345e4ae6dd22c74b419eba5c052e7d4f1ad45e4add9eba2627621ef694"
}
```

`optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/evidence/GATE.json` · SHA256 `1321a83c215ef83516c5459f953c075e06460ba9094eed10016e405e0a40eed3` (qualification fields only)

```json
{
  "complete": true,
  "source_sha256": "0293e7781b5bba93acf989dd87da20d144e8dc8b9e32b0ef10ee4a91e429268e",
  "config_sha256": "1074ffac5e59768a51b02cde5839bfc69e7469d9a90c98d2b1ffc4e11dc037b3",
  "reuse_control_sha256": "a354c723088c2ac1c896790ee0b47a04dc75358dbf84aee3ef2261c1ae462ad7",
  "analyses": {
    "main": "4a21a0ea18bcd58b79a2f5f94557b0370ba2577c7d181aeff333d1262c6a86d3",
    "supplement": "54cf7cf934dc42f80685e8df38ebbefa6450335fb3b6118d568002ba0328097c"
  },
  "exact_replays": 96,
  "gemm_pairs": 48,
  "combine_pairs": 10,
  "zero_local_stack": true,
  "sanitizer": false,
  "timing": false
}
```

`optimization-20261028/tp-small-gemm-round/producers/r2/evidence/GATE.json` · SHA256 `22dfa197be9a908e61da7879858036525ea22f0c0f6cf18e373671e49b68e575` (qualification fields only)

```json
{
  "complete": true,
  "base": "1054743780dda2919c1424124c1e3258248b8c19",
  "source_sha256": "fb879c3b3cb75c5e5769da359d940a79a2ca5a8410d559299e69fb1235c094b1",
  "kernel_sha256": "7932107248fa69ae0e843896d5931430d987be2ad4571fd15f77b1505238a5aa",
  "analysis_sha256": {
    "analysis.json": "2e54fa891688e183af1482d020a7191f454a6464a899176a65a418de36972768",
    "one-cta/analysis.json": "5128b98dcaab0e1922ee8bc2f78a43fc998285fddf696f07f70844d245706f04"
  },
  "exact_replays": 112,
  "gemm_pairs": 56,
  "one_cta_pairs": 32,
  "two_cta_identical_pairs": 24,
  "combine_pairs": 10,
  "one_cta_non_nop_delta_range": [
    -42,
    -10
  ],
  "one_cta_register_delta_range": [
    -12,
    2
  ],
  "zero_local_stack": true,
  "uniform_spill_fill_unchanged": true,
  "boundary": "Storage-bit exact public-wrapper source comparison, static/CLC, PDLoff/on, four blockscaled formats. No sanitizer. Static counts are not dynamic instruction totals; SDK rank reads can increase."
}
```

## Executed gate commands

These are the recorded commands against immutable experiment source/config snapshots. Closed source checkouts were removed after retention; their source commit, exact patch, hashes, helpers and raw results are preserved in the project ledger. Native compilation caches were retained. No sanitizer was launched.

```json
[
  {
    "receipt": "optimization-20261028/tp-small-gemm-round/static-grid/composed/gpu-evidence/lane7/t4/candidate/receipt.json",
    "sha256": "a1cfa0bf04d7d2f2af9014485684961d075157e7fcf9b6cbbed76b0b8b0417ad",
    "command": [
      "/data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python",
      "-u",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/static-grid/composed/probe_pair.py",
      "--output",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/static-grid/composed/lane7/t4/candidate/result.json",
      "--role",
      "candidate",
      "--config-ids",
      "0,1,2,3",
      "--intermediate",
      "256",
      "--hidden-size",
      "384",
      "--tokens",
      "4",
      "--reference",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/static-grid/composed/lane7/t4/control/result.json"
    ],
    "complete": true,
    "returncode": 0
  },
  {
    "receipt": "optimization-20261028/tp-small-gemm-round/static-grid/composed/gpu-evidence/lane7/t4/control/receipt.json",
    "sha256": "48efb97decd22bfc743aa3360e1f301e5997b6d83731571da08e5c4b987ff067",
    "command": [
      "/data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python",
      "-u",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/static-grid/composed/probe_pair.py",
      "--output",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/static-grid/composed/lane7/t4/control/result.json",
      "--role",
      "control",
      "--config-ids",
      "0,1,2,3",
      "--intermediate",
      "256",
      "--hidden-size",
      "384",
      "--tokens",
      "4"
    ],
    "complete": true,
    "returncode": 0
  },
  {
    "receipt": "optimization-20261028/tp-small-gemm-round/static-grid/composed/gpu-evidence/lane7/driver.json",
    "sha256": "3e2fe9e0db71e5c0511a6d5aa28e7cb51446ca214ba3143ca7e5ecfb9ce85830",
    "command": [
      "/data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python",
      "-u",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/static-grid/composed/run_gate.py",
      "--config",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/static-grid/composed/gate-config.json",
      "--gpu",
      "7",
      "--role",
      "control",
      "--config-ids",
      "0,1,2,3",
      "--intermediate",
      "256",
      "--tokens",
      "4",
      "--output-root",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/static-grid/composed/lane7"
    ],
    "returncode": 0
  },
  {
    "receipt": "optimization-20261028/tp-small-gemm-round/static-grid/composed/gpu-evidence/lane7/driver.json",
    "sha256": "3e2fe9e0db71e5c0511a6d5aa28e7cb51446ca214ba3143ca7e5ecfb9ce85830",
    "command": [
      "/data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python",
      "-u",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/static-grid/composed/run_gate.py",
      "--config",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/static-grid/composed/gate-config.json",
      "--gpu",
      "7",
      "--role",
      "candidate",
      "--config-ids",
      "0,1,2,3",
      "--intermediate",
      "256",
      "--tokens",
      "4",
      "--output-root",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/static-grid/composed/lane7",
      "--reference",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/static-grid/composed/lane7/t4/control/result.json"
    ],
    "returncode": 0
  }
]
```

```json
[
  {
    "receipt": "optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/evidence/lane3/i384/candidate/receipt.json",
    "sha256": "3d40fbe866a7fb975caf967470fc323c1aa20f7bbd98ae92c282a1dc4515646e",
    "command": [
      "/data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python",
      "-u",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/probe_pair.py",
      "--output",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/lane3/i384/candidate/result.json",
      "--role",
      "candidate",
      "--config-ids",
      "0,1",
      "--intermediate",
      "384",
      "--hidden-size",
      "384",
      "--reference",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-params-r1/lane3/i384/control/result.json"
    ],
    "complete": true,
    "returncode": 0
  },
  {
    "receipt": "optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/evidence/lane3/i384/control/receipt.json",
    "sha256": "40d5ddd5d52652fc761496d61a51a69d3ed7f2dd26fc1de009e9179084b3ad79",
    "command": [
      "/data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python",
      "-u",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-params-r1/probe_pair.py",
      "--output",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-params-r1/lane3/i384/control/result.json",
      "--role",
      "control",
      "--config-ids",
      "0,1",
      "--intermediate",
      "384",
      "--hidden-size",
      "384"
    ],
    "complete": true,
    "returncode": 0
  },
  {
    "receipt": "optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/evidence/lane4/i384/candidate/receipt.json",
    "sha256": "22d220b4ef8ea95e9849fc7169e142964b9fb2b1275b5168ed735759711fbcfa",
    "command": [
      "/data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python",
      "-u",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/probe_pair.py",
      "--output",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/lane4/i384/candidate/result.json",
      "--role",
      "candidate",
      "--config-ids",
      "6,7",
      "--intermediate",
      "384",
      "--hidden-size",
      "384",
      "--reference",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-params-r1/lane4/i384/control/result.json"
    ],
    "complete": true,
    "returncode": 0
  },
  {
    "receipt": "optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/evidence/lane4/i384/control/receipt.json",
    "sha256": "66dba6c2812fc6f9a405caaab22ff7a27aa6fb705be67efd6e618b797fdd14a8",
    "command": [
      "/data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python",
      "-u",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-params-r1/probe_pair.py",
      "--output",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-params-r1/lane4/i384/control/result.json",
      "--role",
      "control",
      "--config-ids",
      "6,7",
      "--intermediate",
      "384",
      "--hidden-size",
      "384"
    ],
    "complete": true,
    "returncode": 0
  },
  {
    "receipt": "optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/evidence/supplement/lane3/i384/candidate/receipt.json",
    "sha256": "6c44d5328623efad711a9b91286445a63ec87a670a412f0930a7cf9fb775d65e",
    "command": [
      "/data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python",
      "-u",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/supplement/probe_pair.py",
      "--output",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/supplement/lane3/i384/candidate/result.json",
      "--role",
      "candidate",
      "--config-ids",
      "4",
      "--intermediate",
      "384",
      "--hidden-size",
      "384",
      "--reference",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-params-r1/supplement/lane3/i384/control/result.json"
    ],
    "complete": true,
    "returncode": 0
  },
  {
    "receipt": "optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/evidence/supplement/lane3/i384/control/receipt.json",
    "sha256": "404131291064e0bc52b796fd401ee0ca93b53bc1abedf9173206be9b25449729",
    "command": [
      "/data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python",
      "-u",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-params-r1/supplement/probe_pair.py",
      "--output",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-params-r1/supplement/lane3/i384/control/result.json",
      "--role",
      "control",
      "--config-ids",
      "4",
      "--intermediate",
      "384",
      "--hidden-size",
      "384"
    ],
    "complete": true,
    "returncode": 0
  },
  {
    "receipt": "optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/evidence/supplement/lane4/i384/candidate/receipt.json",
    "sha256": "b9d4e7225229287769c50105cf5440e33d204e1f2b6519915bb3ff07af3c7270",
    "command": [
      "/data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python",
      "-u",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/supplement/probe_pair.py",
      "--output",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/supplement/lane4/i384/candidate/result.json",
      "--role",
      "candidate",
      "--config-ids",
      "5",
      "--intermediate",
      "384",
      "--hidden-size",
      "384",
      "--reference",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-params-r1/supplement/lane4/i384/control/result.json"
    ],
    "complete": true,
    "returncode": 0
  },
  {
    "receipt": "optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/evidence/supplement/lane4/i384/control/receipt.json",
    "sha256": "9b26c93f910bfcb7a75601e572c4d7d7260a0463ea00818f90d4311931421741",
    "command": [
      "/data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python",
      "-u",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-params-r1/supplement/probe_pair.py",
      "--output",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-params-r1/supplement/lane4/i384/control/result.json",
      "--role",
      "control",
      "--config-ids",
      "5",
      "--intermediate",
      "384",
      "--hidden-size",
      "384"
    ],
    "complete": true,
    "returncode": 0
  },
  {
    "receipt": "optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/evidence/lane3/driver.json",
    "sha256": "d21a41b7f134ec7cdbf3dcb5d2fdec6d6072de9e98211e6519b0d6e0ec4ac921",
    "command": [
      "/data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python",
      "-u",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/run_gate.py",
      "--config",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/gate-config.json",
      "--gpu",
      "3",
      "--role",
      "candidate",
      "--config-ids",
      "0,1",
      "--intermediate",
      "384",
      "--output-root",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/lane3",
      "--reference",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-params-r1/lane3/i384/control/result.json"
    ],
    "returncode": 0
  },
  {
    "receipt": "optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/evidence/lane3/driver.json",
    "sha256": "d21a41b7f134ec7cdbf3dcb5d2fdec6d6072de9e98211e6519b0d6e0ec4ac921",
    "command": [
      "/data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python",
      "-u",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/supplement/run_gate.py",
      "--config",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/supplement/gate-config.json",
      "--gpu",
      "3",
      "--role",
      "candidate",
      "--config-ids",
      "4",
      "--intermediate",
      "384",
      "--output-root",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/supplement/lane3",
      "--reference",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-params-r1/supplement/lane3/i384/control/result.json"
    ],
    "returncode": 0
  },
  {
    "receipt": "optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/evidence/lane4/driver.json",
    "sha256": "e44d0f876c15c3f330caf1778cd68b6438fbd75a3a57c146691b96df9bc04c11",
    "command": [
      "/data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python",
      "-u",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/run_gate.py",
      "--config",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/gate-config.json",
      "--gpu",
      "4",
      "--role",
      "candidate",
      "--config-ids",
      "6,7",
      "--intermediate",
      "384",
      "--output-root",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/lane4",
      "--reference",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-params-r1/lane4/i384/control/result.json"
    ],
    "returncode": 0
  },
  {
    "receipt": "optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/evidence/lane4/driver.json",
    "sha256": "e44d0f876c15c3f330caf1778cd68b6438fbd75a3a57c146691b96df9bc04c11",
    "command": [
      "/data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python",
      "-u",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/supplement/run_gate.py",
      "--config",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/supplement/gate-config.json",
      "--gpu",
      "4",
      "--role",
      "candidate",
      "--config-ids",
      "5",
      "--intermediate",
      "384",
      "--output-root",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/supplement/lane4",
      "--reference",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-params-r1/supplement/lane4/i384/control/result.json"
    ],
    "returncode": 0
  },
  {
    "receipt": "optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/evidence/supplement/lane3/driver.json",
    "sha256": "eb67cbce38c122b839be30fa6bb2c139e7e2e713beddc63b1aad2d70f80f888c",
    "command": [
      "/data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python",
      "-u",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/supplement/run_gate.py",
      "--config",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/supplement/gate-config.json",
      "--gpu",
      "3",
      "--role",
      "candidate",
      "--config-ids",
      "4",
      "--intermediate",
      "384",
      "--output-root",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/supplement/lane3",
      "--reference",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-params-r1/supplement/lane3/i384/control/result.json"
    ],
    "returncode": 0
  },
  {
    "receipt": "optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/evidence/supplement/lane4/driver.json",
    "sha256": "072be95d7fa8e101b15f89d4b405f2be30f105b62f8dfff9bbe08eff1749e795",
    "command": [
      "/data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python",
      "-u",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/supplement/run_gate.py",
      "--config",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/supplement/gate-config.json",
      "--gpu",
      "4",
      "--role",
      "candidate",
      "--config-ids",
      "5",
      "--intermediate",
      "384",
      "--output-root",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/supplement/lane4",
      "--reference",
      "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/producers/sf-params-r1/supplement/lane4/i384/control/result.json"
    ],
    "returncode": 0
  }
]
```

## Historical qualification

Earlier105474378 integer MMA-K passed24 exact changing-route comparisons and12 identical GEMM PTX/instruction/resource pairs; six matched combine specializations agreed. The broader handoff gate passed160 exact replays/80 identical PTX pairs, with two equivalent uniform-register renames. Existing MX uniform spill/fill counts did not grow. Final constant selection was separately proven equivalent.

At640877340, W4A16 passed18 exact cases/136 graph replays/four old/new-layout API tests and26 identical cleanup PTX/cubin/SASS/resource pairs. At83dfef8a6,95 pytest+11 Linux cache tests and memcheck/synccheck/racecheck each128 replays/64 GEMMs passed; assembled TMEM guards were verified. No sanitizer or broad pytest rerun qualifies the present iteration.

[Previous commands and source-bound results](https://raw.githubusercontent.com/zianglih/flashinfer/e041cd48bc576fa3353069fd936eb73ab86503f2/pr7290/2026-10-28/105474378/validation/commands-and-results.md). The PR retains the earlier manual sanitizer section unchanged. Those results remain bound to their original source commits.
