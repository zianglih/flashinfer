# Seeded-uniform synthetic routing native AUTO diagnostic

Control is retained `1e69d0a39`; candidate changes only swap-AB blockscaled synthetic route generation. Each arm performs a fresh native search, then uses its own saved winner for matched C-A-A-C timing. All public passes have 100 cold-L2 CUPTI samples; NV native tuning remains eager and MX native tuning remains graph-based. No tactic overrides or new tactics.

|N3U EP8 case|Tokens|Control µs|Candidate µs|Speedup|Control drift|Candidate spread|
|---|---:|---:|---:|---:|---:|---:|
|CuteDSL MXFP4x8|4|37.488|38.064|-1.513%|-0.083%|0.166%|
|CuteDSL PER-TOKEN|4096|320.498|321.345|-0.264%|+0.110%|0.130%|
|CuteDSL W4A4|4096|218.481|219.106|-0.285%|-0.307%|0.220%|

## CuteDSL MXFP4x8 T4
Actual local assignments/active experts: 10/10; balanced profile: 64/64; seeded-uniform profile: 11/10.

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
      8,
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
      "us": 37.50449999999999
    },
    {
      "name": "candidate-auto",
      "us": 38.321
    },
    {
      "name": "c0",
      "us": 37.504000000000005
    },
    {
      "name": "a1",
      "us": 38.032999999999994
    },
    {
      "name": "a2",
      "us": 38.096000000000004
    },
    {
      "name": "c3",
      "us": 37.473
    }
  ]
}
```

## CuteDSL PER-TOKEN T4096
Actual local assignments/active experts: 11180/64; balanced profile: 11418/64; seeded-uniform profile: 11232/64.

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
      8,
      4
    ],
    false
  ],
  "raw_phase_medians_us": [
    {
      "name": "control-auto",
      "us": 319.138
    },
    {
      "name": "candidate-auto",
      "us": 320.5135
    },
    {
      "name": "c0",
      "us": 320.3215
    },
    {
      "name": "a1",
      "us": 321.553
    },
    {
      "name": "a2",
      "us": 321.137
    },
    {
      "name": "c3",
      "us": 320.67400000000004
    }
  ]
}
```

## CuteDSL W4A4 T4096
Actual local assignments/active experts: 11180/64; balanced profile: 11418/64; seeded-uniform profile: 11232/64.

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
      8,
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
      "us": 218.3375
    },
    {
      "name": "candidate-auto",
      "us": 218.19349999999997
    },
    {
      "name": "c0",
      "us": 218.818
    },
    {
      "name": "a1",
      "us": 218.8655
    },
    {
      "name": "a2",
      "us": 219.34599999999998
    },
    {
      "name": "c3",
      "us": 218.1455
    }
  ]
}
```

All18 public measurements use100 fresh CUPTI samples. Gates/source/config/observer hashes and the independent gate-integrity sidecar are verified. The complete gate and raw result artifacts are retained alongside this summary.
