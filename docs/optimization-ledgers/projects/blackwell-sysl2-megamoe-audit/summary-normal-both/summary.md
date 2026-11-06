# SysL2 cache-hint benchmark

PR11 native full-forward cold-L2 graph CUPTI; rankMAX then untrimmed median.

Baseline was run once per topology and reused. No correctness checks were run, as requested. Single-baseline timing remains sensitive to drift; AUTO tactic changes are shown. The existing local L2 flush does not prove SysL2 invalidation.

## dispatch-normal-r1 — EP4

Decode T4–512 geometric speedup: **1.003091×**.

| Global tokens | Baseline µs | Candidate µs | Speedup | Tactic changed |
|---:|---:|---:|---:|:---:|
| 1 | 68.864000 | 80.225000 | 0.858386× | True |
| 2 | 86.481000 | 94.145000 | 0.918594× | False |
| 4 | 119.312500 | 122.161000 | 0.976682× | False |
| 8 | 154.465500 | 150.273000 | 1.027899× | True |
| 16 | 208.865500 | 210.081000 | 0.994214× | False |
| 32 | 265.218000 | 257.842000 | 1.028607× | False |
| 64 | 300.850500 | 292.770500 | 1.027598× | True |
| 128 | 323.027500 | 321.507500 | 1.004728× | False |
| 256 | 331.298500 | 338.419000 | 0.978960× | True |
| 512 | 351.203000 | 355.554500 | 0.987761× | False |
| 4096 | 816.823500 | 815.960000 | 1.001058× | False |
| 8192 | 1523.596500 | 1482.062000 | 1.028025× | False |
| 16384 | 2915.853000 | 2898.147000 | 1.006109× | True |

Exact winning tactics:

```json
[
  {
    "global_tokens": 1,
    "baseline_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 512,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        64,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "epi_warps",
      "use_2cta_instrs": true
    },
    "candidate_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 1024,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        64,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "epi_warps",
      "use_2cta_instrs": true
    }
  },
  {
    "global_tokens": 2,
    "baseline_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 1024,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        64,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "epi_warps",
      "use_2cta_instrs": true
    },
    "candidate_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 1024,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        64,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "epi_warps",
      "use_2cta_instrs": true
    }
  },
  {
    "global_tokens": 4,
    "baseline_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 512,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        64,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "epi_warps",
      "use_2cta_instrs": true
    },
    "candidate_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 512,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        64,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "epi_warps",
      "use_2cta_instrs": true
    }
  },
  {
    "global_tokens": 8,
    "baseline_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 1024,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        64,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "epi_warps",
      "use_2cta_instrs": true
    },
    "candidate_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 512,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        64,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "epi_warps",
      "use_2cta_instrs": true
    }
  },
  {
    "global_tokens": 16,
    "baseline_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 1024,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        64,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "epi_warps",
      "use_2cta_instrs": true
    },
    "candidate_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 1024,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        64,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "epi_warps",
      "use_2cta_instrs": true
    }
  },
  {
    "global_tokens": 32,
    "baseline_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 1024,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        64,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "epi_warps",
      "use_2cta_instrs": true
    },
    "candidate_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 1024,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        64,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "epi_warps",
      "use_2cta_instrs": true
    }
  },
  {
    "global_tokens": 64,
    "baseline_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 1024,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        64,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "epi_warps",
      "use_2cta_instrs": true
    },
    "candidate_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 512,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        64,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "epi_warps",
      "use_2cta_instrs": true
    }
  },
  {
    "global_tokens": 128,
    "baseline_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 1024,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        64,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "epi_warps",
      "use_2cta_instrs": true
    },
    "candidate_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 1024,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        64,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "epi_warps",
      "use_2cta_instrs": true
    }
  },
  {
    "global_tokens": 256,
    "baseline_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 1024,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        64,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "epi_warps",
      "use_2cta_instrs": true
    },
    "candidate_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 512,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        64,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "epi_warps",
      "use_2cta_instrs": true
    }
  },
  {
    "global_tokens": 512,
    "baseline_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 1024,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        64,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "epi_warps",
      "use_2cta_instrs": true
    },
    "candidate_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 1024,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        64,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "epi_warps",
      "use_2cta_instrs": true
    }
  },
  {
    "global_tokens": 4096,
    "baseline_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 1024,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        128,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "reuse_dispatch_warps",
      "use_2cta_instrs": true
    },
    "candidate_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 1024,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        128,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "reuse_dispatch_warps",
      "use_2cta_instrs": true
    }
  },
  {
    "global_tokens": 8192,
    "baseline_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 1024,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        128,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "reuse_dispatch_warps",
      "use_2cta_instrs": true
    },
    "candidate_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 1024,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        128,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "reuse_dispatch_warps",
      "use_2cta_instrs": true
    }
  },
  {
    "global_tokens": 16384,
    "baseline_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 512,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        128,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "reuse_dispatch_warps",
      "use_2cta_instrs": true
    },
    "candidate_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 1024,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        128,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "reuse_dispatch_warps",
      "use_2cta_instrs": true
    }
  }
]
```

## dispatch-normal-r1 — EP8

Decode T4–512 geometric speedup: **0.996702×**.

| Global tokens | Baseline µs | Candidate µs | Speedup | Tactic changed |
|---:|---:|---:|---:|:---:|
| 1 | 76.752500 | 72.208500 | 1.062929× | True |
| 2 | 88.593000 | 88.432500 | 1.001815× | True |
| 4 | 107.232500 | 104.032500 | 1.030760× | False |
| 8 | 123.553000 | 122.928500 | 1.005080× | False |
| 16 | 140.385500 | 146.144500 | 0.960594× | False |
| 32 | 167.521000 | 170.050000 | 0.985128× | False |
| 64 | 194.401000 | 199.569000 | 0.974104× | False |
| 128 | 193.841500 | 202.033500 | 0.959452× | False |
| 256 | 200.978000 | 199.682000 | 1.006490× | False |
| 512 | 210.946000 | 199.745000 | 1.056076× | True |
| 4096 | 463.620500 | 469.827000 | 0.986790× | False |
| 8192 | 776.822000 | 782.278000 | 0.993025× | False |
| 16384 | 1509.195500 | 1537.677000 | 0.981478× | True |

Exact winning tactics:

```json
[
  {
    "global_tokens": 1,
    "baseline_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 1024,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        128,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "epi_warps",
      "use_2cta_instrs": true
    },
    "candidate_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 512,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        64,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "epi_warps",
      "use_2cta_instrs": true
    }
  },
  {
    "global_tokens": 2,
    "baseline_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 512,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        64,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "epi_warps",
      "use_2cta_instrs": true
    },
    "candidate_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 1024,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        64,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "epi_warps",
      "use_2cta_instrs": true
    }
  },
  {
    "global_tokens": 4,
    "baseline_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 512,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        64,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "epi_warps",
      "use_2cta_instrs": true
    },
    "candidate_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 512,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        64,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "epi_warps",
      "use_2cta_instrs": true
    }
  },
  {
    "global_tokens": 8,
    "baseline_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 512,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        64,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "epi_warps",
      "use_2cta_instrs": true
    },
    "candidate_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 512,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        64,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "epi_warps",
      "use_2cta_instrs": true
    }
  },
  {
    "global_tokens": 16,
    "baseline_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 512,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        64,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "epi_warps",
      "use_2cta_instrs": true
    },
    "candidate_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 512,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        64,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "epi_warps",
      "use_2cta_instrs": true
    }
  },
  {
    "global_tokens": 32,
    "baseline_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 512,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        64,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "epi_warps",
      "use_2cta_instrs": true
    },
    "candidate_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 512,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        64,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "epi_warps",
      "use_2cta_instrs": true
    }
  },
  {
    "global_tokens": 64,
    "baseline_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 1024,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        64,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "epi_warps",
      "use_2cta_instrs": true
    },
    "candidate_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 1024,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        64,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "epi_warps",
      "use_2cta_instrs": true
    }
  },
  {
    "global_tokens": 128,
    "baseline_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 512,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        64,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "epi_warps",
      "use_2cta_instrs": true
    },
    "candidate_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 512,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        64,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "epi_warps",
      "use_2cta_instrs": true
    }
  },
  {
    "global_tokens": 256,
    "baseline_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 512,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        64,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "epi_warps",
      "use_2cta_instrs": true
    },
    "candidate_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 512,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        64,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "epi_warps",
      "use_2cta_instrs": true
    }
  },
  {
    "global_tokens": 512,
    "baseline_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 512,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        64,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "epi_warps",
      "use_2cta_instrs": true
    },
    "candidate_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 1024,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        64,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "epi_warps",
      "use_2cta_instrs": true
    }
  },
  {
    "global_tokens": 4096,
    "baseline_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 1024,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        128,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "reuse_dispatch_warps",
      "use_2cta_instrs": true
    },
    "candidate_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 1024,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        128,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "reuse_dispatch_warps",
      "use_2cta_instrs": true
    }
  },
  {
    "global_tokens": 8192,
    "baseline_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 1024,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        128,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "reuse_dispatch_warps",
      "use_2cta_instrs": true
    },
    "candidate_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 1024,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        128,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "reuse_dispatch_warps",
      "use_2cta_instrs": true
    }
  },
  {
    "global_tokens": 16384,
    "baseline_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 1024,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        128,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "reuse_dispatch_warps",
      "use_2cta_instrs": true
    },
    "candidate_tactic": {
      "cluster_shape_mnk": [
        2,
        1,
        1
      ],
      "epi_flag_batch": [
        2,
        4
      ],
      "flag_batch": 4,
      "group_hint": 512,
      "in_kernel_fc2_reduce": false,
      "load_balance_mode": "atomic_counter",
      "mma_tiler_mnk": [
        256,
        128,
        256
      ],
      "num_sched_stages": 2,
      "token_back_mode": "reuse_dispatch_warps",
      "use_2cta_instrs": true
    }
  }
]
```

## Complete raw samples

All samples are milliseconds; none are trimmed. Full fixtures, rank tactics and provenance are in `raw-evidence.json`.

### baseline/ep4

```json
[{"global_tokens":1,"samples_ms":[8.740843,0.074049,0.0704,0.075264,0.076097,0.069953,0.068192,0.061312,0.067841,0.065473,0.072064,0.071648,0.072544,0.067553,0.067776,0.068928,0.072704,0.065921,0.066273,0.068736,0.068576,0.070304,0.068545,0.067521,0.069249,0.07472,0.069472,0.069985,0.066817,0.067232,0.067456,0.068417,0.068353,0.069569,0.0736,0.068864,0.068,0.068193,0.066529,0.069504,0.073472,0.065473,0.068993,0.066976,0.068384,0.082177,0.067393,0.067136,0.069088,0.06928,0.068545,0.068864,0.069889,0.068896,0.068417,0.068449,0.069281,0.071648,0.066561,0.069025,0.072993,0.068768,0.070752,0.070176,0.068673,0.067584,0.070112,0.074016,0.073696,0.073409,0.073856,0.063745,0.068609,0.070817,0.072288,0.068736,0.067904,0.068513,0.068481,0.06976,0.068864,0.067009,0.069505,0.067329,0.068032,0.070625,0.068449,0.069281,0.073249,0.070625,0.072929,0.068129,0.06688,0.069728,0.067232,0.066881,0.074561,0.067521,0.069664,0.067264]},{"global_tokens":2,"samples_ms":[7.871335,0.097601,0.08512,0.085312,0.085761,0.085441,0.087296,0.091233,0.089217,0.090433,0.093472,0.092129,0.094401,0.088513,0.086433,0.093218,0.092417,0.087777,0.088417,0.089249,0.091264,0.094177,0.093825,0.093281,0.094048,0.093185,0.089089,0.095009,0.08736,0.088769,0.088225,0.088576,0.093249,0.086241,0.085121,0.0864,0.08736,0.084577,0.087585,0.089665,0.093568,0.085185,0.087201,0.090368,0.087424,0.089793,0.088193,0.087776,0.084064,0.082944,0.085153,0.084161,0.085601,0.083809,0.08352,0.085377,0.087744,0.083873,0.085089,0.084897,0.084385,0.084321,0.083297,0.083297,0.084865,0.085089,0.083617,0.084321,0.085761,0.089473,0.085089,0.084768,0.084545,0.084449,0.086401,0.084673,0.092641,0.08544,0.084289,0.085793,0.085505,0.086369,0.084993,0.085409,0.088417,0.085313,0.090113,0.084288,0.088961,0.089921,0.086209,0.087042,0.087201,0.084129,0.086881,0.084416,0.086657,0.084161,0.086529,0.084065]},{"global_tokens":4,"samples_ms":[11.982192,0.117025,0.118433,0.120353,0.110913,0.121729,0.114432,0.118241,0.116833,0.117985,0.114624,0.121409,0.117633,0.115681,0.120289,0.118816,0.119233,0.116033,0.119233,0.119392,0.116225,0.119424,0.123265,0.118592,0.120577,0.119456,0.118113,0.115264,0.118753,0.117088,0.120385,0.116993,0.118529,0.120704,0.116577,0.117761,0.119937,0.120833,0.117857,0.120833,0.118657,0.115105,0.115361,0.121281,0.118433,0.120513,0.119681,0.121409,0.122561,0.117601,0.120449,0.123393,0.121345,0.117952,0.121952,0.121632,0.120385,0.119841,0.124097,0.117345,0.115777,0.114337,0.120448,0.119521,0.121281,0.116545,0.116801,0.121088,0.117889,0.127488,0.121249,0.118017,0.119489,0.123105,0.116513,0.121985,0.118497,0.121089,0.120129,0.116993,0.120705,0.120001,0.118944,0.116289,0.118593,0.117153,0.117313,0.11584,0.117825,0.120897,0.121089,0.117377,0.121185,0.121057,0.117345,0.123201,0.120577,0.121633,0.120481,0.119489]},{"global_tokens":8,"samples_ms":[2.607314,0.156033,0.152961,0.15133,0.157409,0.15213,0.156769,0.152674,0.156289,0.15405,0.151234,0.151777,0.152674,0.152001,0.152609,0.152417,0.156802,0.151649,0.153121,0.152898,0.151842,0.148993,0.151393,0.153153,0.157538,0.153569,0.153697,0.154273,0.154273,0.154658,0.160321,0.153538,0.153921,0.149442,0.150625,0.153889,0.168066,0.151681,0.154178,0.155137,0.150273,0.156129,0.155201,0.154402,0.15277,0.150818,0.159425,0.153634,0.158721,0.151649,0.153921,0.154337,0.154594,0.153185,0.158722,0.156737,0.159522,0.153089,0.15501,0.154497,0.161378,0.156226,0.161825,0.16125,0.160898,0.160514,0.162433,0.154849,0.153121,0.154466,0.160738,0.155841,0.159777,0.164322,0.160673,0.15501,0.160801,0.155682,0.154913,0.155777,0.153761,0.154465,0.161473,0.164801,0.153537,0.156737,0.155073,0.154817,0.154082,0.156417,0.153442,0.155489,0.155361,0.153537,0.151938,0.155234,0.154145,0.153922,0.161217,0.15389]},{"global_tokens":16,"samples_ms":[3.757212,0.202209,0.20781,0.205025,0.20205,0.205889,0.202625,0.20509,0.20413,0.206241,0.207201,0.203458,0.204833,0.207586,0.20461,0.218049,0.204258,0.20637,0.206274,0.209217,0.209154,0.206593,0.208097,0.205474,0.210626,0.209249,0.208898,0.210242,0.214274,0.209794,0.208834,0.205057,0.20845,0.210881,0.209569,0.209186,0.210529,0.211457,0.211426,0.209537,0.209922,0.211362,0.211873,0.210498,0.20813,0.209633,0.210081,0.210914,0.208033,0.208674,0.209633,0.208705,0.207266,0.21133,0.209473,0.210498,0.211105,0.207106,0.20973,0.208161,0.206946,0.209922,0.208929,0.207777,0.207586,0.208897,0.207682,0.207714,0.207681,0.207169,0.210178,0.208321,0.208417,0.20877,0.20957,0.21261,0.206658,0.209217,0.209345,0.204834,0.212097,0.208098,0.20973,0.207233,0.209538,0.211298,0.210146,0.207714,0.206913,0.208097,0.20925,0.209826,0.210625,0.210914,0.208258,0.210689,0.211842,0.208577,0.208001,0.213986]},{"global_tokens":32,"samples_ms":[17.420837,0.267266,0.27213,0.477219,0.273891,0.264803,0.267522,0.263491,0.265858,0.263715,0.264578,0.265314,0.262754,1.459726,0.264322,0.263427,0.267202,0.265987,0.266914,0.265314,0.26141,0.273506,0.272194,0.266114,0.264163,0.263395,0.265795,0.265186,0.275779,0.266242,0.264835,0.264642,0.266307,0.261986,0.262594,0.26189,0.264289,0.279043,0.266659,0.268482,0.264001,0.265218,0.265091,0.266946,0.265634,0.26477,0.263523,0.265922,0.264643,0.26749,0.268771,0.265122,0.268067,0.265826,0.265955,0.264386,0.264035,0.265218,0.265987,0.261634,0.264227,0.265634,0.260738,0.26509,0.263491,0.266914,0.267971,0.26493,0.265795,0.26365,0.26189,0.264417,0.262979,0.263714,0.266115,0.262946,0.262722,0.265314,0.26573,0.265698,0.264675,0.266498,0.266466,0.265698,0.264227,0.267234,0.261539,0.263842,0.264931,0.263266,0.264195,0.265314,0.264579,0.266114,0.269603,0.265249,0.261506,0.267554,0.265091,0.264674]},{"global_tokens":64,"samples_ms":[6.703042,0.30093,0.300099,0.294243,0.296899,0.298562,0.298883,0.297955,0.298755,0.297027,0.300771,0.299683,0.298787,0.301507,0.298307,0.310019,0.300195,0.297252,0.303235,0.302595,0.300291,0.299523,0.300675,0.299683,0.300003,0.303459,0.304259,0.302499,0.301028,0.300963,0.29981,0.29773,0.302275,0.302947,0.302787,0.299299,0.302275,0.302755,0.299651,0.30365,0.304035,0.300739,0.305026,0.303043,0.297123,0.298723,0.301443,0.300771,0.301379,0.303235,0.300003,0.304419,0.301507,0.299491,0.305987,0.303138,0.302884,0.303203,0.302532,0.303746,0.302338,0.303427,0.301155,0.298371,0.303203,0.300931,0.303203,0.304323,0.298723,0.302755,0.298531,0.305123,0.303074,0.301603,0.302852,0.302083,0.303363,0.299907,0.303107,0.303971,0.300323,0.296323,0.301475,0.300419,0.301411,0.295747,0.299076,0.295011,0.296003,0.294883,0.299555,0.301091,0.294691,0.295746,0.299108,0.295619,0.297731,0.297315,0.297027,0.300163]},{"global_tokens":128,"samples_ms":[10.862412,0.341858,0.321602,0.321667,0.317603,0.319939,0.320132,0.319875,0.318244,0.32141,0.321698,0.322594,0.321219,0.384739,0.329827,0.320067,0.322307,0.32717,0.322083,0.321347,0.322562,0.322306,0.322211,0.322243,0.323331,0.32173,0.324835,0.335587,0.326595,0.325826,0.324739,0.324899,0.321539,0.324034,0.324931,0.318979,0.32173,0.322562,0.324003,0.322467,0.32493,0.323234,0.320195,0.325347,0.324898,0.32429,0.322019,0.322691,0.320738,0.321858,0.322787,0.32381,0.322659,0.322915,0.32314,0.324547,0.321539,0.321954,0.321988,0.327683,0.323522,0.324259,0.327715,0.323619,0.324771,0.325923,0.322883,0.322979,0.323842,0.323618,0.322787,0.32445,0.323554,0.32445,0.323235,0.322755,0.32141,0.327267,0.324356,0.323971,0.322786,0.323747,0.325572,0.324611,0.322242,0.321923,0.321283,0.323106,0.324068,0.325539,0.322659,0.325954,0.323076,0.323299,0.323618,0.32125,0.320644,0.321539,0.321444,0.323266]},{"global_tokens":256,"samples_ms":[9.111323,0.328387,0.326243,0.337444,0.32698,0.326179,0.328931,0.326307,0.327907,0.327555,0.326915,0.327812,0.328739,0.325923,0.327908,0.330435,0.328708,0.326051,0.329604,0.329731,0.331651,0.330691,0.330019,0.330179,0.332291,0.329603,0.332036,0.331203,0.332068,0.330403,0.331427,0.332387,0.330979,0.333251,0.331747,0.329059,0.337507,0.685703,0.499013,0.370628,0.332675,0.336387,0.331715,0.343395,0.331171,0.331459,0.329763,0.329059,0.328452,0.33226,0.331108,0.330307,0.334307,0.329476,0.329027,0.331299,0.333155,0.330659,0.331524,0.335108,0.331203,0.332004,0.33066,0.333347,0.331043,0.332707,0.332099,0.330916,0.331938,0.33034,0.331235,0.337283,0.331298,0.338596,0.328996,0.330243,0.33194,0.332739,0.333411,0.330276,0.330372,0.32986,0.33677,0.331587,0.32842,0.331523,0.333572,0.331458,0.331875,0.332291,0.332931,0.330531,0.334083,0.331619,0.334243,0.334498,0.33194,0.333058,0.330979,0.333059]},{"global_tokens":512,"samples_ms":[8.386752,0.352995,0.347939,0.348674,0.349507,0.346531,0.353955,0.349922,0.351267,0.347874,0.348131,0.34781,0.350211,0.34669,0.512004,0.356771,0.348291,0.349986,0.348099,0.348579,0.348931,0.352003,0.35069,0.351715,0.349315,0.349506,0.351203,0.352067,0.349251,0.349731,0.350626,0.348707,0.34781,0.349123,0.351138,0.353987,0.348932,0.350627,0.354596,0.349507,0.351811,0.354244,0.350115,0.353283,0.351971,0.351299,0.352546,0.346179,0.351139,0.352195,0.353634,0.350595,0.352995,0.351395,0.351651,0.350338,0.350115,0.351683,0.34906,0.352579,0.349892,0.352387,0.353219,0.348291,0.348899,0.350212,0.352291,0.351203,0.351236,0.352706,0.351363,0.34845,0.350499,0.350787,0.358787,0.352578,0.358595,0.35309,0.354116,0.352547,0.353571,0.349379,0.351555,0.349282,0.352323,0.355907,0.351523,0.352514,0.352227,0.35325,0.352323,0.352835,0.35098,0.351523,0.356516,0.351171,0.348387,0.353188,0.350883,0.349635]},{"global_tokens":4096,"samples_ms":[14.753455,0.795303,0.790568,0.797512,0.793383,0.795015,0.793448,0.792808,0.787495,0.790184,0.79604,0.788456,0.792584,0.801832,0.792775,0.795144,0.788199,0.795016,0.784488,0.794632,0.802248,0.790696,0.796039,0.793672,0.79284,0.795079,0.794344,0.791528,0.789959,0.790407,0.78676,0.788967,0.80004,0.788167,0.796583,0.784296,0.789096,0.783495,0.785384,0.812744,0.808424,0.809576,0.816616,0.821096,0.811816,0.811848,0.816743,0.816904,0.809096,0.81188,0.815464,0.80884,0.836776,0.83108,0.833384,0.845128,0.834312,0.841576,0.835783,0.836936,0.835112,0.834536,0.829864,0.839976,0.816456,0.823944,0.835592,0.825542,0.822984,0.829032,0.82724,0.831912,0.823847,0.831944,0.819109,0.833992,0.83108,0.818664,0.827336,0.82948,0.820936,0.821032,0.826696,0.831752,0.848264,0.863465,0.853544,0.866696,0.861449,0.866312,0.868937,0.867976,0.86948,0.871688,0.859561,0.865128,0.884552,0.861257,0.859752,0.869032]},{"global_tokens":8192,"samples_ms":[9.720316,1.355049,1.342441,1.342665,1.337642,1.344553,1.352457,1.350344,1.347433,1.370733,1.339817,1.338121,1.351177,1.348201,1.345581,1.348009,1.345929,1.337513,1.334186,1.343594,1.349709,1.344137,1.347117,1.343821,1.341609,1.335625,1.344653,1.430025,1.439754,1.44241,1.445193,1.444714,1.438538,1.422985,1.425741,1.428398,1.436781,1.429102,1.416173,1.41675,1.435693,1.43275,1.425901,1.417805,1.408877,1.421837,1.420301,1.49227,1.521838,1.533839,1.530606,1.525711,1.525614,1.521706,1.525355,1.554095,1.554218,1.560591,1.569483,1.551403,1.566699,1.559823,1.560235,1.565611,1.568459,1.571695,1.568522,1.573711,1.567567,1.576208,1.571663,1.571407,1.571946,1.575055,1.561615,1.570991,1.56443,1.527726,1.541199,1.550987,1.537679,1.560043,1.547438,1.554666,1.542639,1.546794,1.537871,1.550091,1.555278,1.541359,1.552942,1.550638,1.538607,1.528718,1.53563,1.52049,1.544494,1.538735,1.532395,1.540879]},{"global_tokens":16384,"samples_ms":[6.548716,2.477048,2.482264,2.487865,2.494201,2.476823,2.487481,2.489784,2.483769,2.48204,2.487673,2.481945,2.479865,2.493113,2.490328,2.743291,2.759067,2.739067,2.725371,2.717691,2.704731,2.706235,2.715739,2.709338,2.714459,2.737371,2.895197,2.896188,2.8895,2.897724,2.924669,2.944861,2.915869,2.91862,2.92566,2.923037,2.926173,2.930909,2.929181,2.927613,2.923677,2.926333,2.928381,2.925789,2.9223,2.919484,2.925789,2.920829,2.915229,2.92246,2.927261,2.913597,2.918173,2.903581,2.914653,2.913533,2.907709,2.930237,2.917373,2.918557,2.919997,2.911772,2.914525,2.915837,2.919964,2.91942,2.920509,2.914013,2.925788,2.919516,2.924093,2.915229,2.917597,2.920796,2.913501,2.908733,2.911965,2.910236,2.920668,2.914333,2.916412,2.909405,2.932093,2.922653,2.916924,2.936349,2.9047,2.919133,2.921981,2.921245,2.917341,2.922205,2.921725,2.915933,2.913756,2.91478,2.915613,2.916221,2.926204,2.920445]}]
```

### dispatch-normal-r1/ep4

```json
[{"global_tokens":1,"samples_ms":[19.960151,0.071457,0.078912,0.075457,0.076032,0.077313,0.077057,0.078112,0.075777,0.074496,0.077121,0.076385,0.080224,0.079009,0.076769,0.077953,0.079201,0.076992,0.080161,0.078496,0.078177,0.079841,0.079296,0.082945,0.079489,0.078593,0.078017,0.078977,0.081313,0.079681,0.080225,0.079137,0.078369,0.089984,0.082913,0.078817,0.078144,0.080609,0.079232,0.080384,0.078977,0.082368,0.081505,0.078913,0.0808,0.081889,0.081025,0.079489,0.080513,0.081664,0.078305,0.081537,0.077984,0.081409,0.081825,0.081536,0.079617,0.104161,0.080225,0.091041,0.082049,0.08048,0.083201,0.080609,0.080416,0.083457,0.078945,0.079136,0.086561,0.089281,0.080384,0.080513,0.081441,0.085825,0.082081,0.078369,0.080641,0.081409,0.080608,0.081057,0.078209,0.080768,0.079361,0.080257,0.083232,0.079777,0.079104,0.079584,0.080193,0.081312,0.080897,0.080225,0.080352,0.080289,0.081313,0.080128,0.088449,0.080513,0.078112,0.080897]},{"global_tokens":2,"samples_ms":[8.51555,0.098017,0.092416,0.126369,0.107969,0.093025,0.092896,0.091264,0.092033,0.092385,0.092769,0.094337,0.092448,0.091936,0.091809,0.092833,0.095457,0.094177,0.09696,0.093025,0.095489,0.094145,0.094337,0.095201,0.093344,0.098977,0.095585,0.092737,0.096257,0.094432,0.094432,0.092513,0.091329,0.093921,0.094657,0.094016,0.093057,0.094016,0.094977,0.096097,0.093824,0.091617,0.093345,0.095232,0.096128,0.094752,0.095776,0.09264,0.094336,0.096096,0.095137,0.094209,0.092704,0.094465,0.095745,0.093248,0.093953,0.094561,0.094817,0.095937,0.093217,0.094145,0.092097,0.094081,0.093185,0.095968,0.094753,0.095361,0.090432,0.095328,0.092193,0.093505,0.094048,0.096224,0.095488,0.092481,0.092417,0.092833,0.094049,0.094592,0.093696,0.095137,0.096384,0.094273,0.096065,0.095489,0.095041,0.092417,0.092833,0.091617,0.092448,0.093792,0.09184,0.095521,0.092449,0.094401,0.093536,0.092256,0.095616,0.097089]},{"global_tokens":4,"samples_ms":[6.269497,0.120513,0.117985,0.118497,0.124065,0.117857,0.119105,0.118273,0.119137,0.122305,0.120289,0.119681,0.123778,0.118721,0.119074,0.119905,0.118658,0.121089,0.116961,0.117537,0.122753,0.118465,0.119265,0.122017,0.121537,0.120385,0.121121,0.122177,0.120289,0.121025,0.128098,0.121314,0.124576,0.118178,0.121345,0.124097,0.12301,0.120321,0.345283,0.140385,0.120961,0.121153,0.114337,0.121985,0.124609,0.122785,0.135137,0.121921,0.122145,0.120577,0.120449,0.120801,0.117409,0.120833,0.123169,0.124225,0.156322,0.134113,0.122689,0.123073,0.302179,0.133569,0.121697,0.121345,0.123201,0.123521,0.119681,0.135042,0.121281,0.13501,0.124129,0.125793,0.124865,0.125217,0.125217,0.122305,0.126977,0.123842,0.117538,0.123042,0.122402,0.122657,0.124642,0.127873,0.121985,0.120961,0.122785,0.130977,0.122977,0.122817,0.122145,0.124577,0.120194,0.123778,0.123073,0.120289,0.124961,0.122401,0.124577,0.119649]},{"global_tokens":8,"samples_ms":[4.521129,0.158241,0.151201,0.151073,0.149282,0.15181,0.149665,0.152609,0.180194,0.150881,0.154337,0.150946,0.151361,0.149377,0.151138,0.150849,0.150849,0.150529,0.151329,0.153666,0.150081,0.151041,0.150178,0.149953,0.150209,0.151841,0.148033,0.148833,0.150273,0.152194,0.149698,0.151233,0.149634,0.150722,0.149409,0.153921,0.149602,0.149313,0.148322,0.147777,0.151041,0.149825,0.149089,0.148161,0.148065,0.150369,0.150593,0.151842,0.149505,0.148609,0.148418,0.148354,0.148033,0.150466,0.149505,0.15165,0.150273,0.148992,0.150593,0.149409,0.150402,0.14797,0.150593,0.147713,0.149922,0.149569,0.148034,0.148066,0.148801,0.148769,0.149729,0.148673,0.150497,0.149505,0.150785,0.150369,0.148929,0.155682,0.147938,0.150145,0.151234,0.152002,0.150273,0.148482,0.150657,0.149538,0.149441,0.151521,0.150497,0.151489,0.149313,0.151649,0.152482,0.150945,0.149761,0.149761,0.152545,0.152417,0.148385,0.151905]},{"global_tokens":16,"samples_ms":[29.850313,0.221441,0.211522,0.209922,0.220418,0.207969,0.208321,0.216482,0.210561,0.209985,0.205505,0.208482,0.209889,0.211201,0.212194,0.210945,0.209985,0.208897,0.210529,0.211137,0.215713,0.210017,0.214689,0.205921,0.385762,0.213217,0.214433,0.205697,0.207074,0.205953,0.210882,0.208225,0.208993,0.211041,0.210562,0.211297,0.206977,0.211297,0.208738,0.209601,0.211233,0.207361,0.210082,0.20781,0.207745,0.207522,0.212418,0.209025,0.210433,0.210978,0.211105,0.210657,0.208161,0.208289,0.209921,0.208386,0.209857,0.207617,0.214081,0.208033,0.209058,0.210146,0.212193,0.210753,0.211777,0.21085,0.208769,0.208801,0.208769,0.212706,0.210145,0.210081,0.210113,0.212577,0.212257,0.209921,0.207458,0.212897,0.212033,0.208193,0.21197,0.207457,0.209089,0.207233,0.210306,0.211169,0.211169,0.208673,0.208929,0.209537,0.213282,0.210081,0.208674,0.210146,0.208129,0.209153,0.210882,0.210049,0.209377,0.211714]},{"global_tokens":32,"samples_ms":[11.115176,0.258658,0.267042,0.257347,0.25773,0.255522,0.269347,0.260291,0.257603,0.263522,0.257058,0.257506,0.259522,0.259458,0.259107,0.257538,0.257219,0.256258,0.25693,0.258594,0.257442,0.258083,0.258946,0.255938,0.256515,0.258146,0.256131,0.259138,0.258722,0.259875,0.258211,0.258306,0.259971,0.258946,0.25485,0.25853,0.256418,0.256483,0.255138,0.256674,0.357476,0.258402,0.257251,0.257603,0.256194,0.258915,0.258723,0.254466,0.259779,0.258883,0.259458,0.435141,0.257091,0.25917,0.257795,0.257378,0.257282,0.257667,0.25933,0.256131,0.253987,0.256835,0.258947,0.257411,0.258531,0.25549,0.259618,0.257826,0.25725,0.258658,0.257698,0.259459,0.260066,0.259043,0.256642,0.257539,0.258243,0.256994,0.25581,0.258978,0.258594,0.258307,0.263906,0.256035,0.25613,0.258178,0.258691,0.257186,0.258178,0.257059,0.256194,0.25517,0.258659,0.257858,0.258147,0.256802,0.257154,0.257635,0.258786,0.256482]},{"global_tokens":64,"samples_ms":[4.96212,0.303491,0.289027,0.293858,0.293667,0.291138,0.293187,0.29645,0.292739,0.292035,0.291235,0.294339,0.293346,0.291618,0.296867,0.293251,0.292515,0.29085,0.293763,0.294147,0.293154,0.292418,0.291874,0.292963,0.291971,0.290946,0.293379,0.290882,0.293283,0.29053,0.292131,0.293219,0.291299,0.29245,0.292675,0.293635,0.291138,0.291714,0.291619,0.29293,0.293987,0.291875,0.293347,0.29245,0.292963,0.291554,0.291971,0.295651,0.292899,0.294915,0.291395,0.292291,0.293379,0.290115,0.294371,0.293698,0.292802,0.292675,0.292163,0.291523,0.29021,0.294882,0.293347,0.293155,0.29117,0.291875,0.292898,0.293443,0.292067,0.289986,0.293506,0.290467,0.293794,0.300355,0.294498,0.292515,0.294498,0.293219,0.29197,0.289827,0.293442,0.294466,0.289954,0.291235,0.293603,0.292259,0.294019,0.289826,0.29261,0.293507,0.290242,0.293667,0.289986,0.292194,0.298979,0.292418,0.293187,0.29629,0.288674,0.293698]},{"global_tokens":128,"samples_ms":[2.892925,0.317635,0.317697,0.316546,0.316194,0.315426,0.316003,0.315394,0.317859,0.318946,0.31597,0.317955,0.318594,0.319203,0.319427,0.320003,0.319747,0.321059,0.319779,0.324161,0.321954,0.320195,0.32269,0.321187,0.319235,0.321474,0.318595,0.323651,0.322818,0.318499,0.320899,0.322435,0.324099,0.32077,0.323427,0.322915,0.319555,0.323619,0.321059,0.321283,0.322787,0.322691,0.321729,0.323107,0.320355,0.324995,0.323361,0.322275,0.321474,0.321281,0.326178,0.321762,0.320483,0.323427,0.320771,0.321219,0.32157,0.324034,0.323459,0.322914,0.322658,0.324066,0.320707,0.324642,0.32093,0.32141,0.322466,0.32205,0.319522,0.325154,0.320034,0.323395,0.322242,0.326465,0.32301,0.321826,0.32109,0.323202,0.323202,0.321507,0.321667,0.321508,0.324098,0.322018,0.325379,0.320099,0.321826,0.323234,0.322755,0.321283,0.324578,0.320739,0.319969,0.323491,0.322659,0.32109,0.318307,0.320387,0.318626,0.324514]},{"global_tokens":256,"samples_ms":[6.048443,0.338563,0.336803,0.334948,0.334947,0.334115,0.336355,0.335523,0.336355,0.336643,0.338755,0.336963,0.337059,0.337347,0.337827,0.338787,0.338371,0.339043,0.337732,0.340067,0.337379,0.339459,0.336195,0.358755,0.338627,0.338339,0.338627,0.337252,0.336227,0.338595,0.362371,0.337155,0.331043,0.338435,0.33837,0.338659,0.33962,0.340451,0.335907,0.337827,0.338403,0.337891,0.339907,0.338788,0.336004,0.349924,0.346691,0.338563,0.362755,0.341027,0.33642,0.336163,0.34138,0.338787,0.338179,0.335427,0.341571,0.338051,0.340803,0.350435,0.337283,0.338883,0.341411,0.338467,0.338019,0.340867,0.340355,0.337475,0.336868,0.336292,0.338019,0.338371,0.336355,0.338691,0.337123,0.339395,0.338147,0.339971,0.347395,0.33802,0.33786,0.336515,0.339556,0.338499,0.336835,0.335331,0.338115,0.336419,0.339268,0.335746,0.340452,0.338819,0.339171,0.340963,0.339843,0.340771,0.348611,0.341667,0.340868,0.339363]},{"global_tokens":512,"samples_ms":[6.344431,0.354723,0.353698,0.356867,0.351138,0.351586,0.350595,0.353699,0.350594,0.349571,0.355843,0.354947,0.357026,0.354338,0.368195,0.35325,0.353219,0.35565,0.353282,0.35341,0.351459,0.356131,0.372131,0.360611,0.354787,0.359042,0.353955,0.356066,0.352675,0.353186,0.358211,0.360515,0.354178,0.355459,0.355619,0.358723,0.354627,0.353475,0.354979,0.353154,0.354531,0.355651,0.354979,0.352963,0.354882,0.357283,0.357187,0.355842,0.355075,0.357218,0.356099,0.356131,0.353827,0.356611,0.354658,0.355907,0.355491,0.356706,0.357219,0.357794,0.356131,0.356994,0.353955,0.355107,0.355618,0.356611,0.352738,0.357283,0.357731,0.357731,0.360099,0.356963,0.351299,0.358018,0.356547,0.356451,0.354851,0.356323,0.355458,0.351875,0.354787,0.355202,0.358563,0.350915,0.356387,0.357026,0.354915,0.355907,0.353922,0.355395,0.356098,0.356034,0.356963,0.35565,0.360355,0.356386,0.354146,0.355459,0.354722,0.353379]},{"global_tokens":4096,"samples_ms":[7.422504,0.78836,0.78244,0.787943,0.788488,0.781127,0.788711,0.783016,0.782695,0.792167,0.78532,0.782247,0.791462,0.78324,0.786054,0.78391,0.789702,0.787944,0.785353,0.780136,0.789608,0.795912,0.78884,0.788648,0.783622,0.79255,0.785032,0.784232,0.789222,0.78708,0.789192,0.78647,0.795494,0.781191,0.806279,0.793383,0.792936,0.789544,0.795496,0.783559,0.791432,0.788712,0.798663,0.794407,0.800136,0.795016,0.811368,0.797959,0.832135,0.820679,0.828968,0.814408,0.821032,0.821736,0.822632,0.83284,0.823528,0.83268,0.830216,0.826056,0.835496,0.825352,0.820968,0.830153,0.819528,0.817512,0.818952,0.822792,0.806408,0.809928,0.828744,0.8202,0.829512,0.825448,0.828841,0.823752,0.828232,0.8266,0.825448,0.833768,0.860265,0.854312,0.851336,0.854408,0.860456,0.855657,0.851432,0.85316,0.861929,0.863016,0.849417,0.867208,0.853481,0.857384,0.84644,0.858121,0.855496,0.858953,0.85796,0.855464]},{"global_tokens":8192,"samples_ms":[11.484338,1.335755,1.349708,1.345037,1.35137,1.348203,1.342861,1.349292,1.341133,1.339212,1.339499,1.340842,1.337067,1.345803,1.340843,1.347883,1.351179,1.34785,1.341674,1.349099,1.353419,1.346155,1.354348,1.375083,1.382956,1.385228,1.434796,1.418029,1.431438,1.42443,1.413966,1.420591,1.418733,1.417166,1.471407,1.48427,1.481838,1.473198,1.483215,1.47339,1.482286,1.478127,1.470703,1.461966,1.478446,1.464174,1.459951,1.47691,1.457006,1.472302,1.463599,1.470127,1.472494,1.482318,1.480876,1.538223,1.537069,1.544943,1.526574,1.547279,1.543407,1.607376,1.60072,1.589392,1.603248,1.583919,1.595376,1.594095,1.592272,1.595184,1.596143,1.582733,1.566543,1.575215,1.579952,1.573231,1.575344,1.568656,1.578704,1.590032,1.571664,1.583823,1.577871,1.569872,1.574064,1.576047,1.578415,1.570572,1.575535,1.567344,1.57096,1.564623,1.568335,1.578063,1.544624,1.545423,1.542,1.538764,1.541357,1.54334]},{"global_tokens":16384,"samples_ms":[9.845057,2.470161,2.461364,2.467697,2.474612,2.471928,2.480216,2.471449,2.481716,2.473528,2.467604,2.471,2.479224,2.463992,2.475604,2.671834,2.658737,2.65845,2.653049,2.770266,2.788732,2.803259,2.804475,2.798098,2.792315,2.793075,2.780467,2.787443,2.790774,2.810204,2.909597,2.944499,2.944531,2.949971,2.940957,2.932596,2.928093,2.931315,2.933629,2.907389,2.889972,2.888189,2.889907,2.894621,2.904691,2.89942,2.900467,2.898067,2.904755,2.898963,2.900573,2.894908,2.894771,2.902195,2.906323,2.908307,2.890547,2.887539,2.897139,2.898579,2.905779,2.910164,2.908052,2.901459,2.904884,2.893428,2.904404,2.897751,2.904604,2.903092,2.903059,2.921853,2.903955,2.896444,2.900956,2.899357,2.894071,2.893468,2.901175,2.904764,2.8997,2.900083,2.897532,2.899891,2.894515,2.907923,2.893011,2.905267,2.901459,2.900669,2.898227,2.910067,2.900403,2.905021,2.900467,2.902739,2.900435,2.895123,2.892563,2.890492]}]
```

### baseline/ep8

```json
[{"global_tokens":1,"samples_ms":[27.364317,0.080321,0.075041,0.070208,0.074561,0.070689,0.072736,0.075393,0.074113,0.073281,0.077985,0.072481,0.075489,0.074688,0.075136,0.076065,0.07664,0.075393,0.082785,0.077184,0.076385,0.077728,0.090433,0.076544,0.078241,0.079457,0.076577,0.074369,0.07472,0.076993,0.07648,0.07504,0.076353,0.078048,0.07648,0.077633,0.077408,0.080001,0.076512,0.079681,0.076481,0.076608,0.073057,0.077697,0.076449,0.078209,0.076545,0.077857,0.075904,0.075777,0.086336,0.078049,0.076257,0.075424,0.078017,0.076928,0.077665,0.07728,0.074817,0.078081,0.077217,0.079009,0.077952,0.076353,0.078144,0.074304,0.077057,0.08464,0.076225,0.07776,0.077088,0.077217,0.074881,0.077665,0.07632,0.074049,0.079937,0.076513,0.076513,0.077824,0.075489,0.075264,0.07824,0.077953,0.077856,0.076833,0.079168,0.075393,0.075777,0.077441,0.075009,0.077153,0.072353,0.078688,0.076672,0.087168,0.077825,0.078113,0.084544,0.078113]},{"global_tokens":2,"samples_ms":[9.415019,0.085185,0.083265,0.086593,0.082849,0.083553,0.084512,0.08285,0.082561,0.082848,0.082305,0.079936,0.086977,0.086945,0.084416,0.083777,0.085409,0.083457,0.083554,0.084769,0.082945,0.085409,0.085921,0.087297,0.086625,0.085825,0.084481,0.086689,0.086657,0.085249,0.086369,0.084577,0.086145,0.087361,0.086433,0.08736,0.088065,0.086529,0.089282,0.087265,0.089473,0.08829,0.087457,0.096161,0.089217,0.091169,0.091393,0.088928,0.092417,0.088609,0.088225,0.089376,0.090018,0.089921,0.088801,0.091266,0.090369,0.090338,0.088641,0.091905,0.088577,0.090306,0.091489,0.092033,0.088545,0.087361,0.090241,0.091457,0.08989,0.08736,0.091841,0.090337,0.088321,0.090113,0.089921,0.087265,0.090369,0.089441,0.090497,0.090817,0.089089,0.08928,0.087936,0.091041,0.090369,0.092545,0.090081,0.091201,0.090721,0.091136,0.099937,0.090945,0.090049,0.090049,0.089025,0.087488,0.090561,0.088993,0.089633,0.088065]},{"global_tokens":4,"samples_ms":[9.519342,0.102784,0.103873,0.099873,0.101761,0.109121,0.10384,0.102113,0.101761,0.102945,0.101889,0.101313,0.100257,0.102528,0.099713,0.100608,0.102401,0.100705,0.102305,0.102881,0.101824,0.103169,0.103233,0.103105,0.101953,0.109824,0.100481,0.101889,0.104705,0.102337,0.104609,0.105441,0.104801,0.102849,0.104577,0.103169,0.102369,0.104929,0.106209,0.101632,0.103329,0.104289,0.10496,0.104929,0.105152,0.105249,0.106657,0.105217,0.110049,0.107457,0.106656,0.103809,0.107008,0.107745,0.107777,0.114786,0.107873,0.109569,0.109793,0.107649,0.110113,0.107969,0.110017,0.109953,0.108641,0.106433,0.108961,0.108672,0.108097,0.109217,0.108865,0.107873,0.109089,0.109312,0.118721,0.106816,0.108353,0.109377,0.107745,0.109761,0.108449,0.108033,0.109313,0.109729,0.1096,0.110177,0.109953,0.107777,0.110945,0.109441,0.11088,0.108353,0.108865,0.110913,0.109121,0.110465,0.108385,0.109729,0.109985,0.108097]},{"global_tokens":8,"samples_ms":[41.327824,0.146882,0.119617,0.116738,0.116929,0.120417,0.119265,0.119778,0.118465,0.117473,0.119105,0.119457,0.118112,0.119618,0.117793,0.117633,0.119713,0.120129,0.120001,0.119585,0.120641,0.117793,0.118881,0.120225,0.122177,0.119489,0.124578,0.121441,0.121025,0.120674,0.122401,0.123457,0.122274,0.130018,0.123361,0.121857,0.124929,0.127137,0.123904,0.124065,0.123489,0.127778,0.126114,0.125154,0.128289,0.124513,0.126466,0.124513,0.124673,0.123042,0.123617,0.124449,0.125377,0.12381,0.124385,0.12653,0.121985,0.124384,0.124162,0.125281,0.125409,0.123937,0.123938,0.123457,0.126465,0.125377,0.122082,0.121761,0.122625,0.122081,0.124481,0.123297,0.124193,0.125441,0.12608,0.126721,0.123009,0.134529,0.123682,0.124513,0.123425,0.133762,0.123681,0.122881,0.122529,0.12573,0.125857,0.125857,0.123905,0.121633,0.124738,0.121185,0.124225,0.124641,0.122946,0.127298,0.124161,0.122721,0.12461,0.123296]},{"global_tokens":16,"samples_ms":[42.402826,0.133025,0.13869,0.138369,0.140769,0.137794,0.138081,0.148482,0.140929,0.160354,0.138433,0.137857,0.14013,0.137953,0.139137,0.137186,0.137889,0.13885,0.139489,0.135361,0.140258,0.138817,0.13949,0.138017,0.138337,0.140098,0.141537,0.13933,0.139105,0.138689,0.13981,0.139809,0.139457,0.14237,0.140321,0.140737,0.141409,0.142626,0.141121,0.141537,0.139553,0.140033,0.14477,0.140897,0.155138,0.139201,0.147106,0.139521,0.140034,0.140354,0.165762,0.142401,0.144929,0.13997,0.139746,0.138881,0.139137,0.139234,0.139425,0.143426,0.141665,0.139202,0.141217,0.141249,0.141569,0.141345,0.141633,0.138369,0.142434,0.144034,0.142401,0.140418,0.143745,0.13917,0.140961,0.140994,0.141697,0.139073,0.13965,0.140769,0.152034,0.140353,0.141954,0.143074,0.140002,0.140769,0.141378,0.140225,0.140865,0.140194,0.141249,0.138977,0.141633,0.141698,0.140417,0.144962,0.142145,0.14045,0.14093,0.149378]},{"global_tokens":32,"samples_ms":[16.058891,0.210178,0.163778,0.188962,0.165282,0.164002,0.164065,0.168353,0.164162,0.164354,0.161601,0.164033,0.16365,0.163234,0.165057,0.163073,0.162561,0.164834,0.164322,0.164321,0.164545,0.164898,0.164513,0.164417,0.165249,0.165442,0.162913,0.164801,0.168993,0.165762,0.166593,0.167009,0.167426,0.164129,0.165313,0.167457,0.167938,0.165248,0.167681,0.16669,0.168482,0.164257,0.166753,0.169634,0.169633,0.16957,0.168833,0.168801,0.169473,0.16701,0.16685,0.167457,0.173922,0.168609,0.169377,0.169442,0.167394,0.169377,0.167745,0.16797,0.169633,0.167073,0.170338,0.168034,0.167585,0.170722,0.169377,0.167713,0.16813,0.170466,0.167681,0.169185,0.167425,0.167201,0.168961,0.168449,0.167937,0.168417,0.164226,0.168482,0.168865,0.167714,0.174913,0.171458,0.173538,0.168321,0.170273,0.170018,0.16653,0.177281,0.168034,0.170977,0.166497,0.172066,0.167586,0.166593,0.166338,0.16653,0.167265,0.165218]},{"global_tokens":64,"samples_ms":[39.286024,0.20173,0.190338,0.189441,0.191362,0.190401,0.19325,0.190946,0.192066,0.191713,0.19293,0.193602,0.193953,0.194561,0.194721,0.194721,0.195393,0.196161,0.194049,0.193793,0.194177,0.193665,0.197025,0.199585,0.194049,0.196513,0.196225,0.196769,0.198657,0.197985,0.190273,0.201185,0.190913,0.194113,0.193409,0.193793,0.195265,0.193153,0.193537,0.194529,0.194433,0.192033,0.193921,0.193857,0.195105,0.196225,0.194401,0.193217,0.196289,0.192257,0.193793,0.194401,0.193921,0.195425,0.194273,0.194369,0.193985,0.194881,0.194017,0.197793,0.194113,0.195777,0.194658,0.194081,0.196129,0.202081,0.194241,0.194529,0.194721,0.19421,0.195873,0.193473,0.239617,0.191233,0.192225,0.193185,0.195041,0.195489,0.195489,0.194081,0.199329,0.194849,0.210305,0.195489,0.233793,0.241378,0.193826,0.195681,0.192802,0.193186,0.192226,0.197058,0.193858,0.193826,0.196065,0.195938,0.222178,0.195745,0.195905,0.210113]},{"global_tokens":128,"samples_ms":[27.273399,0.188162,0.186146,0.185729,0.186626,0.189409,0.187457,0.186689,0.186433,0.189666,0.187554,0.186305,0.185826,0.186785,0.189153,0.188417,0.191105,0.190401,0.189089,0.187776,0.187873,0.191745,0.188609,0.189441,0.190177,0.191553,0.190274,0.191586,0.192673,0.192257,0.191649,0.192995,0.191137,0.192321,0.194241,0.193794,0.195137,0.196001,0.19389,0.203074,0.194946,0.196385,0.194049,0.193825,0.194433,0.193633,0.194145,0.193601,0.194305,0.194274,0.193761,0.193954,0.19357,0.193185,0.194945,0.199489,0.19469,0.195905,0.194274,0.198529,0.204227,0.194146,0.195714,0.193858,0.194753,0.194786,0.194561,0.19421,0.194178,0.192738,0.19549,0.197665,0.192065,0.194913,0.195297,0.195169,0.193793,0.194306,0.194018,0.19181,0.193985,0.192481,0.196098,0.194434,0.193474,0.192961,0.194177,0.193697,0.196193,0.194657,0.19613,0.216738,0.195777,0.190913,0.199842,0.194977,0.194402,0.19565,0.193634,0.195361]},{"global_tokens":256,"samples_ms":[18.995316,0.199842,0.19501,0.194466,0.194722,0.193954,0.193697,0.19517,0.195714,0.195746,0.196577,0.19581,0.195778,0.20557,0.196866,0.196865,0.506693,0.197634,0.200802,0.199266,0.194209,0.19645,0.198338,0.195458,0.199906,0.199106,0.199554,0.196034,0.197314,0.199106,0.196994,0.210178,0.199874,0.198402,0.201506,0.19933,0.19901,0.197859,0.20045,0.199938,0.202146,0.199873,0.20541,0.199362,0.200802,0.205986,0.202018,0.204514,0.200642,0.202946,0.212546,0.202306,0.204066,0.203586,0.20333,0.199905,0.202913,0.20349,0.203202,0.199234,0.202466,0.200257,0.20173,0.202178,0.200706,0.19997,0.201921,0.204001,0.202594,0.201826,0.204162,0.20509,0.201282,0.205218,0.202913,0.239746,0.201857,0.20205,0.203266,0.20141,0.200706,0.201122,0.204162,0.204258,0.202849,0.19981,0.21277,0.20189,0.204226,0.203138,0.200066,0.202978,0.200834,0.20381,0.21021,0.19917,0.201954,0.203681,0.202755,0.200098]},{"global_tokens":512,"samples_ms":[43.123653,0.290947,0.215202,0.210882,0.210753,0.212674,0.212578,0.209154,0.210946,0.211137,0.212578,0.205442,0.212642,0.211299,0.207585,0.21133,0.21597,0.206913,0.21149,0.210434,0.211906,0.210114,0.212002,0.209858,0.211298,0.212834,0.209282,0.210242,0.212386,0.21133,0.21245,0.212162,0.211426,0.209793,0.209794,0.21037,0.211906,0.210946,0.21085,0.210721,0.209154,0.210946,0.21005,0.22125,0.212226,0.21149,0.211106,0.210338,0.210786,0.211074,0.209283,0.206914,0.207714,0.213282,0.212674,0.212162,0.20925,0.21021,0.209634,0.220738,0.213026,0.212259,0.210817,0.212034,0.213378,0.213698,0.210657,0.211233,0.21005,0.21101,0.212194,0.21053,0.209923,0.213346,0.211586,0.207458,0.212514,0.209985,0.210242,0.21549,0.209538,0.212642,0.210913,0.209699,0.209762,0.210274,0.214018,0.20989,0.210497,0.212353,0.207522,0.202081,0.209346,0.209026,0.210626,0.211489,0.210626,0.211906,0.208577,0.208579]},{"global_tokens":4096,"samples_ms":[30.566813,0.461412,0.45962,0.464357,0.458277,0.454372,0.456356,0.4625,0.457092,0.462725,0.457284,0.456996,0.45818,0.465573,0.46586,0.457252,0.45754,0.45818,0.453892,0.466628,0.46282,0.463332,0.460581,0.460068,0.4689,0.468452,0.464101,0.461988,0.468036,0.465285,0.462821,0.460548,0.45514,0.463685,0.4761,0.46218,0.461637,0.457445,0.464037,0.465092,0.46842,0.457668,0.464868,0.460004,0.464068,0.462245,0.467204,0.456804,0.466276,0.471621,0.46858,0.460069,0.466565,0.462692,0.473412,0.458885,0.46922,0.471908,0.464484,0.460452,0.460068,0.456228,0.458213,0.46186,0.461093,0.46714,0.46234,0.453923,0.461124,0.457796,0.463748,0.463716,0.466565,0.458436,0.46426,0.461861,0.46282,0.463588,0.463653,0.459908,0.468452,0.469892,0.467429,0.462084,0.461124,0.467973,0.469892,0.46615,0.476901,0.474373,0.473092,0.473061,0.480166,0.472069,0.472068,0.468932,0.467716,0.472453,0.47002,0.473572]},{"global_tokens":8192,"samples_ms":[19.972982,0.770119,0.756454,0.769126,0.771846,0.770662,0.770598,0.77415,0.76439,0.770342,0.782599,0.766918,0.768326,0.767623,0.780646,0.764359,0.767943,0.776678,0.783942,0.764774,0.772901,0.779174,0.769863,0.765158,0.764998,0.770854,0.782502,0.772742,0.766022,0.771302,0.765926,0.76807,0.773254,0.770534,0.769574,0.772262,0.778214,0.776742,0.763718,0.762566,0.770918,0.772102,0.776423,0.763717,0.769798,0.767559,0.773063,0.758886,0.77351,0.778278,0.760774,0.76903,0.768454,0.76967,0.784582,0.78391,0.77159,0.77479,0.78199,0.776902,0.781638,0.773702,0.774854,0.78119,0.784902,0.789382,0.788774,0.874695,0.78999,0.795975,0.801255,0.801831,0.797766,0.803558,0.803943,0.794983,0.807047,0.812902,0.808422,0.811815,0.821286,0.827526,0.813639,0.812006,0.816455,0.817511,0.816998,0.816167,0.816903,0.814438,0.815655,0.819303,0.820934,0.809991,0.818535,0.817862,0.816743,0.824806,0.823558,0.822343]},{"global_tokens":16384,"samples_ms":[32.572661,1.376171,1.363178,1.367531,1.361834,1.372107,1.370443,1.373131,1.377931,1.365867,1.376331,1.379371,1.379915,1.373451,1.377611,1.367659,1.383147,1.380587,1.371115,1.369739,1.370603,1.378538,1.406059,1.400139,1.400939,1.394251,1.389867,1.397675,1.415564,1.452588,1.476908,1.487212,1.475051,1.479787,1.513068,1.512012,1.506508,1.498668,1.498315,1.496268,1.498705,1.502572,1.497516,1.496396,1.492108,1.50366,1.49822,1.496619,1.503532,1.500172,1.506188,1.509196,1.509195,1.523756,1.515308,1.508333,1.528716,1.516556,1.567308,1.559724,1.553132,1.552172,1.55614,1.579852,1.558124,1.554124,1.564748,1.561964,1.552396,1.549293,1.557036,1.559596,1.555052,1.548653,1.532204,1.520748,1.530636,1.532779,1.532427,1.590253,1.576492,1.5931,1.584684,1.586509,1.587372,1.57598,1.580876,1.590957,1.589325,1.596332,1.590829,1.598765,1.591692,1.580204,1.586732,1.584109,1.58974,1.550668,1.547308,1.552812]}]
```

### dispatch-normal-r1/ep8

```json
[{"global_tokens":1,"samples_ms":[24.262268,0.076161,0.071265,0.069889,0.07456,0.071072,0.0704,0.074592,0.069089,0.069665,0.069536,0.070529,0.070081,0.068737,0.068545,0.072705,0.070432,0.071457,0.076257,0.069601,0.070688,0.068256,0.075232,0.070785,0.070945,0.070817,0.071648,0.070273,0.072384,0.070433,0.073249,0.071232,0.070848,0.069441,0.073345,0.072737,0.070688,0.070496,0.071552,0.072641,0.072384,0.075712,0.072738,0.070529,0.072961,0.071105,0.069345,0.070976,0.073857,0.069696,0.072641,0.072929,0.07184,0.074752,0.074688,0.072609,0.072896,0.07216,0.072353,0.073344,0.071489,0.071264,0.071777,0.070433,0.072928,0.071296,0.072001,0.070688,0.071617,0.071936,0.072289,0.070017,0.072833,0.072674,0.07328,0.072257,0.074017,0.072064,0.073409,0.070913,0.073665,0.073665,0.07488,0.075713,0.070208,0.072576,0.072737,0.072992,0.073377,0.072929,0.073024,0.073889,0.069824,0.073281,0.074113,0.074049,0.072769,0.072384,0.073729,0.071105]},{"global_tokens":2,"samples_ms":[22.481969,0.083681,0.086689,0.084193,0.082944,0.08496,0.084449,0.082977,0.083072,0.084193,0.08288,0.08608,0.084065,0.083328,0.084289,0.084256,0.088897,0.084257,0.084065,0.08448,0.085697,0.084865,0.086113,0.084289,0.084961,0.085377,0.084833,0.08608,0.086753,0.086176,0.087201,0.088289,0.084097,0.084833,0.086176,0.086145,0.084193,0.084705,0.086849,0.086528,0.084289,0.088289,0.087809,0.087745,0.086816,0.088449,0.087232,0.089537,0.090465,0.087361,0.087873,0.087393,0.089665,0.088769,0.088769,0.090113,0.090657,0.089184,0.089921,0.08928,0.090464,0.086977,0.090017,0.090049,0.088865,0.088642,0.090433,0.091521,0.088801,0.091553,0.090112,0.09072,0.089665,0.092736,0.089696,0.091297,0.0928,0.091392,0.091393,0.092833,0.092321,0.090881,0.089217,0.092673,0.092065,0.09264,0.089697,0.091841,0.092321,0.090337,0.092576,0.088737,0.090273,0.088416,0.090368,0.087361,0.091392,0.091905,0.091105,0.088832]},{"global_tokens":4,"samples_ms":[22.930324,0.109569,0.102976,0.101505,0.102177,0.103553,0.101857,0.102657,0.100258,0.098977,0.101025,0.101954,0.102785,0.101826,0.100513,0.102304,0.102177,0.101889,0.101185,0.099105,0.100545,0.103681,0.107361,0.101441,0.101217,0.102337,0.099648,0.105185,0.101473,0.099649,0.102848,0.102753,0.102177,0.100353,0.103105,0.102305,0.105153,0.102944,0.104385,0.103714,0.101889,0.103584,0.103713,0.103873,0.101569,0.102497,0.103009,0.104257,0.103009,0.102274,0.103073,0.103072,0.103905,0.102689,0.102721,0.103425,0.104834,0.104353,0.103457,0.108737,0.10557,0.105793,0.105922,0.10416,0.108193,0.105698,0.105537,0.108865,0.107648,0.108033,0.107041,0.106337,0.109249,0.10832,0.108482,0.108481,0.109665,0.110721,0.108929,0.109921,0.107137,0.118689,0.108257,0.109601,0.109216,0.108129,0.109761,0.109153,0.108353,0.105696,0.107041,0.108801,0.108096,0.109217,0.109473,0.109761,0.108417,0.108002,0.107393,0.111745]},{"global_tokens":8,"samples_ms":[13.968428,0.11853,0.115969,0.116929,0.115681,0.117025,0.117506,0.117281,0.11821,0.118081,0.118082,0.115872,0.115457,0.116033,0.118913,0.118593,0.117282,0.118817,0.118626,0.116257,0.118337,0.118753,0.119042,0.119425,0.120161,0.118913,0.120865,0.117474,0.119361,0.118786,0.120449,0.127457,0.120738,0.118721,0.120801,0.121537,0.120834,0.124513,0.12205,0.124769,0.12365,0.123553,0.125857,0.122274,0.128769,0.12221,0.120098,0.122274,0.126721,0.126722,0.125602,0.125665,0.124418,0.126049,0.125026,0.124481,0.122209,0.12349,0.122049,0.123169,0.124386,0.122561,0.126946,0.125249,0.123073,0.124257,0.123521,0.123809,0.128033,0.124256,0.123234,0.122562,0.123201,0.123841,0.12493,0.123009,0.122401,0.120673,0.124161,0.123617,0.124097,0.124897,0.122081,0.124514,0.124417,0.12288,0.123521,0.123841,0.127969,0.131617,0.124482,0.122977,0.122497,0.122242,0.123521,0.12352,0.124289,0.125185,0.123617,0.123585]},{"global_tokens":16,"samples_ms":[28.608572,0.143297,0.140673,0.138017,0.140226,0.139586,0.140065,0.145633,0.140353,0.141569,0.143233,0.142113,0.142081,0.137538,0.142305,0.140866,0.143649,0.140065,0.143009,0.140929,0.142465,0.142274,0.144257,0.14128,0.143746,0.144321,0.144609,0.144545,0.145697,0.143009,0.143969,0.143649,0.150657,0.146337,0.145473,0.146529,0.146176,0.145409,0.146594,0.14493,0.147457,0.144994,0.148418,0.143393,0.145537,0.144801,0.146657,0.144929,0.146497,0.157793,0.146209,0.143937,0.15005,0.146209,0.148257,0.148354,0.146273,0.14845,0.147265,0.146689,0.147489,0.146338,0.148385,0.147777,0.148386,0.147361,0.147553,0.146369,0.149793,0.148545,0.146465,0.145281,0.147041,0.145729,0.146273,0.144833,0.146465,0.145089,0.147169,0.143618,0.14909,0.14797,0.14704,0.145825,0.147105,0.14669,0.153474,0.145698,0.145505,0.146817,0.148417,0.146209,0.148801,0.146433,0.148129,0.147745,0.149217,0.146113,0.146113,0.148993]},{"global_tokens":32,"samples_ms":[49.954226,0.173762,0.169858,0.166273,0.167009,0.165505,0.165122,0.164226,0.164354,0.163938,0.164866,0.165601,0.165058,0.166146,0.165729,0.166913,0.167842,0.167554,0.16765,0.168577,0.167106,0.16685,0.171522,0.167138,0.16717,0.168514,0.169538,0.168193,0.177026,0.169346,0.168513,0.17005,0.169857,0.170498,0.167265,0.168354,0.169314,0.170369,0.168802,0.170274,0.160705,0.170113,0.169122,0.17053,0.170722,0.168034,0.172034,0.171362,0.170529,0.170945,0.172769,0.171554,0.171842,0.173729,0.173345,0.179842,0.169634,0.171329,0.174658,0.170946,0.172674,0.17037,0.171457,0.170657,0.172866,0.170657,0.16941,0.170018,0.171586,0.170786,0.17949,0.170657,0.168738,0.168897,0.168642,0.170626,0.170241,0.17229,0.169538,0.170497,0.168673,0.168449,0.167297,0.170241,0.17005,0.168545,0.17005,0.170721,0.169027,0.170242,0.171042,0.173761,0.172129,0.172834,0.171201,0.173761,0.169281,0.172993,0.169634,0.171842]},{"global_tokens":64,"samples_ms":[14.869936,0.249666,0.191362,0.192354,0.19533,0.194144,0.189345,0.18957,0.188578,0.192194,0.193537,0.1912,0.194242,0.189888,0.190722,0.19584,0.191329,0.192546,0.192449,0.198946,0.202274,0.218594,0.199298,0.202209,0.199106,0.199969,0.196962,0.197185,0.198817,0.199938,0.200769,0.199203,0.206178,0.197538,0.202273,0.211457,0.203234,0.200386,0.19741,0.198146,0.200225,0.202913,0.203874,0.195938,0.201345,0.203393,0.196418,0.210561,0.199457,0.203938,0.202529,0.200352,0.201537,0.19936,0.211809,0.203874,0.19613,0.216194,0.198242,0.199169,0.199585,0.196834,0.204161,0.198177,0.199874,0.195553,0.204258,0.203137,0.206689,0.205698,0.202497,0.203105,0.196545,0.203777,0.197537,0.200737,0.207201,0.200449,0.196097,0.201474,0.196385,0.199746,0.195265,0.198753,0.197345,0.196257,0.211265,0.201377,0.203041,0.196866,0.19677,0.202561,0.202913,0.204898,0.20029,0.200897,0.201121,0.198177,0.197441,0.199553]},{"global_tokens":128,"samples_ms":[23.876168,0.198785,0.197121,0.199042,0.197921,0.196289,0.198209,0.199937,0.198977,0.21069,0.19933,0.200962,0.200577,0.221569,0.203233,0.201666,0.202881,0.203617,0.202305,0.213538,0.201857,0.200513,0.201858,0.199681,0.203137,0.202081,0.201921,0.200641,0.203041,0.210017,0.201153,0.203297,0.202913,0.203105,0.202145,0.201409,0.245089,0.201153,0.202593,0.205314,0.204449,0.202657,0.204225,0.202721,0.201025,0.203073,0.201249,0.201825,0.202593,0.212322,0.20365,0.201985,0.200737,0.201505,0.203521,0.203713,0.202113,0.202241,0.197121,0.200577,0.201537,0.201633,0.202369,0.200769,0.201377,0.200769,0.197633,0.201569,0.202401,0.208418,0.202465,0.202017,0.202337,0.203426,0.201697,0.200609,0.197345,0.200321,0.199041,0.212673,0.200514,0.199297,0.204001,0.200833,0.20205,0.203201,0.207457,0.199905,0.200354,0.209697,0.204993,0.202338,0.200962,0.202337,0.201121,0.198562,0.204258,0.202113,0.203457,0.202369]},{"global_tokens":256,"samples_ms":[15.556826,0.20253,0.194881,0.193538,0.19357,0.193282,0.192481,0.192929,0.194689,0.194081,0.196642,0.194273,0.197986,0.192098,0.195266,0.196802,0.194178,0.194562,0.194593,0.194498,0.204034,0.19293,0.193633,0.19565,0.196833,0.197122,0.197186,0.19853,0.196129,0.196418,0.199682,0.196226,0.198946,0.199042,0.201281,0.19965,0.197794,0.19917,0.198977,0.201474,0.199809,0.19933,0.200962,0.201058,0.202689,0.202946,0.19933,0.20829,0.200418,0.200225,0.200834,0.198721,0.199554,0.202849,0.216578,0.198818,0.201697,0.20877,0.199298,0.199682,0.19949,0.19757,0.197665,0.198466,0.201122,0.202529,0.199778,0.204034,0.201825,0.201538,0.200514,0.19885,0.19997,0.20525,0.196706,0.199298,0.200098,0.20029,0.202722,0.198466,0.204642,0.203458,0.203233,0.205154,0.200033,0.201026,0.201058,0.20013,0.200257,0.197953,0.200962,0.20173,0.200578,0.201121,0.208322,0.199969,0.204386,0.202242,0.202593,0.202818]},{"global_tokens":512,"samples_ms":[17.795484,0.202432,0.194945,0.196353,0.203137,0.198657,0.206177,0.195905,0.195681,0.197377,0.199712,0.194561,0.198241,0.201729,0.197313,0.198785,0.197825,0.196289,0.197218,0.19629,0.198689,0.197217,0.196673,0.199649,0.200706,0.199393,0.194752,0.201825,0.198242,0.199329,0.199874,0.198946,0.203361,0.198561,0.210914,0.202209,0.201473,0.199906,0.201985,0.197378,0.200385,0.198849,0.201602,0.199009,0.200449,0.201953,0.204001,0.200865,0.198209,0.205185,0.199713,0.202082,0.203362,0.19933,0.201442,0.200898,0.198306,0.203682,0.200097,0.200897,0.199329,0.201601,0.199969,0.197473,0.198306,0.199553,0.203362,0.200866,0.198914,0.202785,0.200354,0.206913,0.20109,0.196257,0.199777,0.197922,0.196705,0.200001,0.19725,0.199041,0.197474,0.19677,0.20381,0.200001,0.202626,0.199938,0.203138,0.19853,0.198849,0.19677,0.19821,0.201249,0.253986,0.201761,0.200193,0.195906,0.197537,0.200194,0.203074,0.200065]},{"global_tokens":4096,"samples_ms":[45.791776,0.466723,0.456419,0.460835,0.463683,0.458531,0.465155,0.462083,0.466435,0.463971,0.465059,0.463075,0.471875,0.465475,0.489603,0.463619,0.470787,0.468387,0.467683,0.456195,0.470307,0.468932,0.476899,0.478755,0.471363,0.473475,0.468771,0.465571,0.470531,0.465698,0.475715,0.480227,0.470339,0.469891,0.474723,0.479075,0.477699,0.476227,0.469859,0.465059,0.470562,0.467075,0.465443,0.460579,0.470179,0.470339,0.471747,0.469635,0.469027,0.464451,0.472067,0.468323,0.465186,0.469795,0.473955,0.468419,0.468835,0.475683,0.470691,0.467747,0.477412,0.473283,0.469059,0.467907,0.467715,0.462626,0.471843,0.482947,0.47101,0.463907,0.466723,0.469475,0.467747,0.478339,0.474947,0.474371,0.469282,0.470723,0.479555,0.473379,0.466947,0.470499,0.466083,0.473827,0.470626,0.469059,0.477379,0.468994,0.475363,0.475907,0.475075,0.458147,0.47037,0.478723,0.483075,0.470626,0.483299,0.468483,0.463459,0.468995]},{"global_tokens":8192,"samples_ms":[16.308547,0.759847,0.754086,0.75911,0.760999,0.759718,0.761414,0.761605,0.758248,0.760872,0.776101,0.764901,0.767909,0.766503,0.761637,0.797351,0.765509,0.761989,0.768135,0.761032,0.767365,0.767431,0.765221,0.760167,0.761319,0.767397,0.769831,0.764423,0.761638,0.764613,0.756358,0.757478,0.790887,0.758791,0.761992,0.758151,0.763047,0.7602,0.753768,0.757481,0.766055,0.756453,0.7578,0.757831,0.762535,0.752904,0.765831,0.75652,0.799912,0.79223,0.777768,0.797702,0.787751,0.787461,0.791079,0.791655,0.807655,0.784233,0.787301,0.791207,0.789927,0.782856,0.785095,0.776647,0.775814,0.778502,0.794662,0.782758,0.783816,0.781798,0.783781,0.78887,0.788038,0.79335,0.801192,0.798311,0.79527,0.790921,0.796358,0.785193,0.801702,0.796486,0.791109,0.78996,0.805446,0.798182,0.809189,0.819718,0.80999,0.811429,0.824838,0.813829,0.816198,0.812006,0.819557,0.81479,0.817926,0.833349,0.816422,0.814821]},{"global_tokens":16384,"samples_ms":[34.604499,1.366348,1.368296,1.354092,1.355179,1.368553,1.359021,1.368266,1.3562,1.369961,1.358989,1.357836,1.363948,1.360653,1.367181,1.36209,1.367117,1.369034,1.365066,1.353324,1.36062,1.365515,1.364684,1.357448,1.374957,1.364969,1.495405,1.505996,1.508747,1.508556,1.500653,1.485963,1.489067,1.490794,1.492618,1.498026,1.483306,1.491531,1.483979,1.480651,1.499179,1.486826,1.487402,1.49265,1.518285,1.552877,1.556683,1.546061,1.561934,1.536461,1.555211,1.520461,1.540906,1.547179,1.53217,1.543627,1.531978,1.530251,1.538893,1.540875,1.527917,1.553518,1.566605,1.596875,1.611275,1.600172,1.593676,1.602091,1.600491,1.591435,1.602156,1.597099,1.598187,1.592267,1.603979,1.589419,1.601035,1.598379,1.601003,1.607019,1.595243,1.59758,1.581483,1.602219,1.594284,1.604811,1.608363,1.576619,1.554795,1.564107,1.559275,1.567211,1.566059,1.561994,1.565163,1.557131,1.567947,1.97787,1.568459,1.556842]}]
```
