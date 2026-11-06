# Actual-routing native AUTO diagnostic

Control is retained `1e69d0a39`; candidate changes only the call-scoped profiling input hook. Each arm performs a fresh native search, then uses its own saved winner for matched C-A-A-C timing. All public passes have 100 cold-L2 CUPTI samples; NV native tuning remains eager and MX native tuning remains graph-based. No tactic overrides or new tactics.

|N3U EP8 case|Tokens|Control µs|Candidate µs|Speedup|Control drift|Candidate spread|
|---|---:|---:|---:|---:|---:|---:|
|CuteDSL MXFP4x8|4|37.888|37.888|-0.001%|+0.000%|0.001%|
|CuteDSL PER-TOKEN|4096|320.210|310.738|+3.048%|+0.010%|0.021%|
|CuteDSL W4A4|4096|236.610|219.218|+7.934%|-0.121%|0.161%|

## CuteDSL MXFP4x8 T4
Actual local assignments/active experts: 10/10; balanced profile: 64/64.

```json
{
  "control_tactic": [
    16,
    [
      [
        128,
        16
      ],
      [
        1,
        1
      ],
      false
    ],
    [
      [
        128,
        16
      ],
      [
        1,
        1
      ],
      false
    ],
    [
      4,
      8
    ],
    true
  ],
  "candidate_tactic": [
    16,
    [
      [
        128,
        16
      ],
      [
        1,
        1
      ],
      false
    ],
    [
      [
        128,
        16
      ],
      [
        1,
        1
      ],
      false
    ],
    [
      4,
      8
    ],
    true
  ],
  "raw_phase_medians_us": [
    {
      "name": "control-auto",
      "us": 37.888
    },
    {
      "name": "candidate-auto",
      "us": 38.0805
    },
    {
      "name": "c0",
      "us": 37.888
    },
    {
      "name": "a1",
      "us": 37.888
    },
    {
      "name": "a2",
      "us": 37.8885
    },
    {
      "name": "c3",
      "us": 37.888
    }
  ]
}
```

## CuteDSL PER-TOKEN T4096
Actual local assignments/active experts: 11180/64; balanced profile: 11418/64.

```json
{
  "control_tactic": [
    128,
    [
      [
        256,
        128
      ],
      [
        2,
        1
      ],
      false
    ],
    [
      [
        256,
        128
      ],
      [
        2,
        1
      ],
      false
    ],
    [
      4,
      4
    ],
    false
  ],
  "candidate_tactic": [
    256,
    [
      [
        256,
        256
      ],
      [
        2,
        1
      ],
      false
    ],
    [
      [
        256,
        256
      ],
      [
        2,
        1
      ],
      false
    ],
    [
      4,
      4
    ],
    true
  ],
  "raw_phase_medians_us": [
    {
      "name": "control-auto",
      "us": 319.186
    },
    {
      "name": "candidate-auto",
      "us": 312.2265
    },
    {
      "name": "c0",
      "us": 320.1945
    },
    {
      "name": "a1",
      "us": 310.77
    },
    {
      "name": "a2",
      "us": 310.706
    },
    {
      "name": "c3",
      "us": 320.2265
    }
  ]
}
```

## CuteDSL W4A4 T4096
Actual local assignments/active experts: 11180/64; balanced profile: 11418/64.

```json
{
  "control_tactic": [
    256,
    [
      [
        128,
        256
      ],
      [
        1,
        1
      ],
      false
    ],
    [
      [
        256,
        256
      ],
      [
        2,
        1
      ],
      false
    ],
    [
      4,
      4
    ],
    false
  ],
  "candidate_tactic": [
    128,
    [
      [
        256,
        128
      ],
      [
        2,
        1
      ],
      false
    ],
    [
      [
        256,
        128
      ],
      [
        2,
        1
      ],
      false
    ],
    [
      4,
      4
    ],
    false
  ],
  "raw_phase_medians_us": [
    {
      "name": "control-auto",
      "us": 235.746
    },
    {
      "name": "candidate-auto",
      "us": 218.978
    },
    {
      "name": "c0",
      "us": 236.7535
    },
    {
      "name": "a1",
      "us": 219.0415
    },
    {
      "name": "a2",
      "us": 219.394
    },
    {
      "name": "c3",
      "us": 236.466
    }
  ]
}
```

The raw outer-wrapper `complete=false` field is a bookkeeping defect: the unchanged observer calls `sys.exit(main())`, causing successful `SystemExit(0)` to bypass the wrapper success assignment. Completion is established from native process returncode 0, native results complete/exit_code 0, full admitted-profile counts, all source/observer hashes and all route/sample/cache checks. Raw proofs and initial validator receipts are preserved; completed native AUTO was not rerun.
