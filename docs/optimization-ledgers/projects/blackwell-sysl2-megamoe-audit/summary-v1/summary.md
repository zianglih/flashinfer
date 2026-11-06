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

## dispatch-last — EP4

Decode T4–512 geometric speedup: **0.997432×**.

| Global tokens | Baseline µs | Candidate µs | Speedup | Tactic changed |
|---:|---:|---:|---:|:---:|
| 1 | 68.864000 | 72.832000 | 0.945518× | False |
| 2 | 86.481000 | 95.937000 | 0.901435× | False |
| 4 | 119.312500 | 120.193000 | 0.992674× | True |
| 8 | 154.465500 | 155.857000 | 0.991072× | True |
| 16 | 208.865500 | 202.337000 | 1.032265× | False |
| 32 | 265.218000 | 262.290000 | 1.011163× | False |
| 64 | 300.850500 | 304.466500 | 0.988123× | False |
| 128 | 323.027500 | 330.194500 | 0.978295× | False |
| 256 | 331.298500 | 338.466000 | 0.978824× | False |
| 512 | 351.203000 | 348.337500 | 1.008226× | False |
| 4096 | 816.823500 | 819.191500 | 0.997109× | False |
| 8192 | 1523.596500 | 1469.549000 | 1.036778× | False |
| 16384 | 2915.853000 | 2904.770000 | 1.003815× | False |

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

## local-pool-last — EP4

Decode T4–512 geometric speedup: **0.992124×**.

| Global tokens | Baseline µs | Candidate µs | Speedup | Tactic changed |
|---:|---:|---:|---:|:---:|
| 1 | 68.864000 | 66.881000 | 1.029650× | False |
| 2 | 86.481000 | 100.721000 | 0.858619× | True |
| 4 | 119.312500 | 124.449000 | 0.958726× | False |
| 8 | 154.465500 | 155.361500 | 0.994233× | True |
| 16 | 208.865500 | 204.641500 | 1.020641× | False |
| 32 | 265.218000 | 270.994000 | 0.978686× | False |
| 64 | 300.850500 | 301.249500 | 0.998676× | False |
| 128 | 323.027500 | 331.074000 | 0.975696× | False |
| 256 | 331.298500 | 333.827000 | 0.992426× | False |
| 512 | 351.203000 | 344.483000 | 1.019507× | False |
| 4096 | 816.823500 | 792.998000 | 1.030045× | False |
| 8192 | 1523.596500 | 1449.597000 | 1.051048× | False |
| 16384 | 2915.853000 | 2911.291000 | 1.001567× | True |

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

## dispatch-last — EP8

Decode T4–512 geometric speedup: **1.024326×**.

| Global tokens | Baseline µs | Candidate µs | Speedup | Tactic changed |
|---:|---:|---:|---:|:---:|
| 1 | 76.752500 | 75.616500 | 1.015023× | True |
| 2 | 88.593000 | 96.193000 | 0.920992× | False |
| 4 | 107.232500 | 101.169000 | 1.059934× | True |
| 8 | 123.553000 | 125.521000 | 0.984321× | False |
| 16 | 140.385500 | 134.481500 | 1.043902× | False |
| 32 | 167.521000 | 165.633000 | 1.011399× | False |
| 64 | 194.401000 | 190.305000 | 1.021523× | False |
| 128 | 193.841500 | 192.802000 | 1.005392× | False |
| 256 | 200.978000 | 198.370000 | 1.013147× | False |
| 512 | 210.946000 | 199.489500 | 1.057429× | True |
| 4096 | 463.620500 | 474.484000 | 0.977105× | False |
| 8192 | 776.822000 | 787.945000 | 0.985884× | False |
| 16384 | 1509.195500 | 1505.547500 | 1.002423× | False |

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

## local-pool-last — EP8

Decode T4–512 geometric speedup: **1.001678×**.

| Global tokens | Baseline µs | Candidate µs | Speedup | Tactic changed |
|---:|---:|---:|---:|:---:|
| 1 | 76.752500 | 68.896500 | 1.114026× | True |
| 2 | 88.593000 | 92.961000 | 0.953013× | False |
| 4 | 107.232500 | 106.609000 | 1.005848× | False |
| 8 | 123.553000 | 129.009000 | 0.957708× | True |
| 16 | 140.385500 | 144.785000 | 0.969614× | False |
| 32 | 167.521000 | 171.761500 | 0.975312× | False |
| 64 | 194.401000 | 191.857000 | 1.013260× | False |
| 128 | 193.841500 | 193.698000 | 1.000741× | False |
| 256 | 200.978000 | 195.105500 | 1.030099× | True |
| 512 | 210.946000 | 198.050000 | 1.065115× | True |
| 4096 | 463.620500 | 475.236500 | 0.975557× | False |
| 8192 | 776.822000 | 799.542000 | 0.971584× | False |
| 16384 | 1509.195500 | 1510.690000 | 0.999011× | True |

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

### dispatch-last/ep4

```json
[{"global_tokens":1,"samples_ms":[15.950281,0.085569,0.070913,0.067905,0.070753,0.076256,0.072289,0.071648,0.072161,0.069377,0.070337,0.07504,0.070945,0.074688,0.070881,0.069024,0.074433,0.073312,0.072289,0.074592,0.071809,0.072193,0.073312,0.072352,0.072641,0.073952,0.071808,0.072256,0.074657,0.071489,0.070721,0.072289,0.071904,0.06912,0.071712,0.107105,0.075969,0.071105,0.074241,0.073953,0.073537,0.073216,0.072449,0.072,0.072545,0.073024,0.073952,0.072864,0.078496,0.072449,0.071521,0.072865,0.07248,0.071553,0.073056,0.104993,0.074721,0.072257,0.07424,0.073345,0.072417,0.075937,0.072641,0.071553,0.073025,0.07184,0.075297,0.073792,0.074561,0.075328,0.074881,0.076033,0.077761,0.071489,0.073153,0.073633,0.072929,0.070944,0.072257,0.073217,0.0728,0.073761,0.073729,0.078401,0.07008,0.070464,0.070112,0.071008,0.074081,0.074944,0.074017,0.073825,0.073824,0.071712,0.071265,0.072512,0.072673,0.074593,0.072417,0.073152]},{"global_tokens":2,"samples_ms":[2.938831,0.120066,0.097313,0.0936,0.089664,0.098017,0.091872,0.092065,0.091617,0.090337,0.094656,0.101441,0.089152,0.091713,0.099425,0.095009,0.09376,0.091553,0.094112,0.09616,0.096161,0.093953,0.097536,0.092001,0.093441,0.092384,0.093056,0.096385,0.093568,0.100608,0.092481,0.095681,0.095584,0.092609,0.105249,0.100416,0.093089,0.095553,0.094208,0.09808,0.093345,0.09696,0.092161,0.105729,0.098944,0.098368,0.098049,0.094656,0.097248,0.095713,0.103777,0.090945,0.105345,0.098305,0.096832,0.095937,0.100225,0.095105,0.095041,0.097249,0.093312,0.095841,0.092608,0.09248,0.096225,0.098753,0.097728,0.094465,0.101568,0.09584,0.102785,0.094817,0.096768,0.097569,0.091905,0.094688,0.092033,0.095937,0.096224,0.095905,0.095009,0.097088,0.1,0.102081,0.097089,0.096288,0.100033,0.095521,0.100576,0.097121,0.096,0.094784,0.104897,0.096,0.094432,0.096513,0.097505,0.100192,0.094721,0.105441]},{"global_tokens":4,"samples_ms":[5.646116,0.119425,0.117536,0.117089,0.117473,0.116288,0.114977,0.116865,0.116865,0.117281,0.117121,0.117217,0.118209,0.118529,0.121089,0.121249,0.119841,0.119776,0.116033,0.116001,0.11872,0.120449,0.11696,0.115201,0.117856,0.119168,0.117761,0.119105,0.120161,0.117441,0.118913,0.118817,0.118208,0.118881,0.121025,0.120385,0.118177,0.123425,0.119713,0.120064,0.117985,0.124704,0.116545,0.120513,0.120768,0.121729,0.129569,0.122177,0.123392,0.120225,0.122624,0.126497,0.123809,0.120481,0.119905,0.121217,0.123457,0.121889,0.120929,0.121089,0.120225,0.120257,0.121696,0.119393,0.119361,0.122913,0.1232,0.121312,0.123041,0.123808,0.130433,0.344259,0.120128,0.120097,0.120577,0.117441,0.120641,0.119904,0.118753,0.115681,0.123745,0.121409,0.117857,0.120353,0.123298,0.120161,0.116705,0.119873,0.122433,0.122785,0.123073,0.124,0.118465,0.136962,0.128001,0.124481,0.121985,0.124449,0.123457,0.119489]},{"global_tokens":8,"samples_ms":[18.33888,0.150593,0.15645,0.155169,0.154017,0.155873,0.155778,0.155873,0.155201,0.161345,0.154658,0.155041,0.156129,0.157665,0.16189,0.155233,0.155297,0.156321,0.158018,0.158402,0.156129,0.156449,0.155873,0.155586,0.155522,0.156481,0.158081,0.156098,0.155906,0.156001,0.155233,0.155585,0.155778,0.156321,0.160609,0.154786,0.156353,0.156066,0.155105,0.155809,0.156001,0.155714,0.156482,0.156577,0.156353,0.156258,0.154113,0.156417,0.155937,0.154818,0.155938,0.154913,0.155457,0.155713,0.15405,0.15389,0.156449,0.154593,0.154145,0.155042,0.158081,0.153537,0.154497,0.155873,0.154658,0.155361,0.155841,0.157313,0.155617,0.154849,0.157249,0.157217,0.157921,0.157122,0.154785,0.153857,0.155521,0.155682,0.154658,0.154497,0.155489,0.154562,0.158498,0.157441,0.156257,0.161569,0.155778,0.15485,0.156769,0.152705,0.153858,0.15485,0.154465,0.160417,0.157153,0.153186,0.155906,0.231618,0.157249,0.155873]},{"global_tokens":16,"samples_ms":[1.446701,0.195169,0.196865,0.199586,0.195746,0.19677,0.197026,0.197857,0.196289,0.19725,0.198306,0.19869,0.199329,0.198529,0.197538,0.198977,0.201058,0.199746,0.198337,0.198818,0.198242,0.199074,0.201218,0.200034,0.201506,0.200962,0.201953,0.200098,0.203586,0.200993,0.200289,0.202561,0.202305,0.204097,0.200162,0.199362,0.203074,0.202402,0.201634,0.202305,0.203106,0.203074,0.206242,0.205697,0.20365,0.202178,0.206402,0.203713,0.204386,0.203362,0.201314,0.203138,0.204769,0.205058,0.203746,0.203233,0.20285,0.201922,0.203106,0.201922,0.203202,0.203297,0.203202,0.204994,0.203777,0.203682,0.203937,0.20125,0.202818,0.203105,0.202753,0.202018,0.202242,0.202369,0.201378,0.203906,0.201313,0.20269,0.200161,0.20301,0.20045,0.202434,0.202754,0.204161,0.202146,0.202305,0.20349,0.204738,0.203233,0.203714,0.20445,0.206754,0.205314,0.201985,0.202785,0.201474,0.203202,0.204514,0.203841,0.202081]},{"global_tokens":32,"samples_ms":[3.997881,0.259874,0.259042,0.260994,0.260867,0.262466,0.261379,0.280291,0.259651,0.262306,0.26205,0.256835,0.263107,0.261314,0.260386,0.258754,0.261698,0.263074,0.262466,0.273346,0.262211,0.26141,0.262114,0.26077,0.261634,0.259458,0.263106,0.264227,0.261571,0.263778,0.26365,0.259298,0.264482,0.263362,0.262595,0.260002,0.263106,0.263938,0.271426,0.262723,0.263074,0.260482,0.260035,0.262563,0.261602,0.26429,0.266755,0.261123,0.261154,0.263458,0.262274,0.264482,0.269475,0.26189,0.263394,0.262787,0.262146,0.260066,0.269506,0.26157,0.262018,0.25949,0.260002,0.261602,0.262754,0.268514,0.264322,0.264386,0.260803,0.262403,0.264322,0.262883,0.264546,0.261186,0.262498,0.263011,0.261827,0.259651,0.259523,0.260258,0.263715,0.26157,0.263522,0.266211,0.26509,0.262146,0.261186,0.259937,0.260515,0.263778,0.266083,0.263906,0.266147,0.265539,0.260674,0.260675,0.261634,0.263234,0.264354,0.260802]},{"global_tokens":64,"samples_ms":[14.474753,0.306786,0.303011,0.308835,0.304322,0.306147,0.305827,0.306723,0.306211,0.302851,0.304163,0.304962,0.302883,0.303459,0.312834,0.301731,0.303555,0.42509,0.306755,0.300994,0.296451,0.302786,0.301635,0.303971,0.30269,0.303523,0.305123,0.30237,0.303171,0.304963,0.305475,0.310627,0.304099,0.303331,0.302947,0.304771,0.305442,0.303427,0.306243,0.306595,0.308003,0.308131,0.30333,0.304579,0.303778,0.300643,0.305282,0.303043,0.306083,0.304898,0.306947,0.307138,0.304547,0.304611,0.302978,0.303747,0.305506,0.304099,0.303747,0.30365,0.302467,0.309282,0.301539,0.302626,0.303362,0.303203,0.309379,0.309155,0.303362,0.304515,0.305315,0.298946,0.306179,0.307234,0.305603,0.304099,0.304323,0.305283,0.303586,0.305251,0.302947,0.304899,0.303203,0.305123,0.305763,0.306083,0.30317,0.303555,0.305891,0.304995,0.303843,0.306114,0.301859,0.302114,0.303427,0.304418,0.307394,0.306851,0.305059,0.301667]},{"global_tokens":128,"samples_ms":[6.536174,0.331235,0.326403,0.326787,0.327522,0.327234,0.326947,0.32413,0.323556,0.325443,0.327427,0.327042,0.325634,0.32733,0.326978,0.331394,0.32813,0.32797,0.326338,0.326786,0.325122,0.32682,0.327682,0.328578,0.324995,0.328259,0.32605,0.329859,0.33069,0.327267,0.330018,0.330851,0.35933,0.332354,0.330882,0.331458,0.331554,0.32957,0.331298,0.329122,0.329634,0.329698,0.332898,0.334722,0.330818,0.330914,0.32922,0.331618,0.327971,0.331426,0.335586,0.332226,0.335138,0.330178,0.332098,0.332482,0.32989,0.333443,0.332514,0.333315,0.330468,0.331266,0.329026,0.334018,0.333218,0.331554,0.330211,0.32733,0.32637,0.329634,0.331716,0.330914,0.331554,0.331842,0.33133,0.329154,0.330018,0.32973,0.332514,0.32986,0.328962,0.331363,0.331874,0.329346,0.328834,0.329634,0.332098,0.33517,0.332322,0.33405,0.331554,0.330754,0.330178,0.331875,0.332611,0.332963,0.330339,0.32941,0.32909,0.336482]},{"global_tokens":256,"samples_ms":[8.947903,0.336642,0.336514,0.33741,0.336162,0.336931,0.336131,0.344803,0.337571,0.337027,0.337955,0.33725,0.336674,0.338243,0.335427,0.337378,0.33837,0.337154,0.335426,0.338466,0.338178,0.337186,0.337026,0.338722,0.343522,0.338146,0.335874,0.338851,0.341027,0.339747,0.344323,0.340131,0.347235,0.338339,0.335938,0.339714,0.339938,0.340322,0.338978,0.339554,0.336354,0.33789,0.340067,0.338787,0.336834,0.337058,0.338467,0.340962,0.343907,0.337986,0.339747,0.340802,0.33277,0.338466,0.341378,0.338338,0.340802,0.339458,0.334818,0.335522,0.343811,0.336898,0.33917,0.335714,0.337603,0.339714,0.339939,0.338979,0.339043,0.337027,0.339523,0.334082,0.340898,0.335619,0.339586,0.339458,0.33965,0.33757,0.34573,0.338338,0.340194,0.339715,0.341922,0.338723,0.339203,0.337091,0.340323,0.33549,0.340675,0.337026,0.338594,0.337154,0.338594,0.338178,0.34381,0.338306,0.33837,0.338818,0.339683,0.337827]},{"global_tokens":512,"samples_ms":[6.577563,0.352513,0.351555,0.34813,0.346626,0.34525,0.345474,0.344226,0.347106,0.349442,0.34733,0.348226,0.347682,0.34797,0.347841,0.348898,0.346019,0.346402,0.345666,0.346434,0.34765,0.349922,0.349473,0.34941,0.348609,0.349058,0.348195,0.34618,0.348898,0.34733,0.345411,0.349474,0.347394,0.347651,0.346722,0.346211,0.349763,0.347651,0.357666,0.34813,0.348514,0.348995,0.346338,0.347171,0.347106,0.34909,0.349378,0.348417,0.349506,0.348514,0.350434,0.348162,0.34813,0.346114,0.349251,0.350242,0.347137,0.349763,0.34877,0.34813,0.348515,0.347779,0.349793,0.349442,0.347875,0.346658,0.347587,0.347779,0.349507,0.35149,0.349827,0.348643,0.348802,0.347683,0.347874,0.352323,0.348707,0.346626,0.348771,0.348131,0.350339,0.350306,0.347715,0.349956,0.349603,0.348258,0.347331,0.346242,0.349346,0.350116,0.349027,0.351042,0.348162,0.348899,0.350018,0.349218,0.350274,0.347458,0.349827,0.347684]},{"global_tokens":4096,"samples_ms":[6.814272,0.786916,0.785672,0.787655,0.789608,0.779015,0.787271,0.7834,0.790375,0.783624,0.791237,0.784517,0.789608,0.789798,0.793092,0.790312,0.786565,0.793,0.785511,0.790757,0.795365,0.784647,0.785093,0.792805,0.810982,0.782215,0.795045,0.787556,0.795048,0.791141,0.790244,0.77652,0.784391,0.785735,0.789605,0.776262,0.7906,0.794309,0.789,0.787271,0.793287,0.794152,0.809415,0.828005,0.832264,0.823653,0.826312,0.821508,0.820264,0.825158,0.816741,0.825959,0.813189,0.82116,0.825061,0.820616,0.820709,0.816039,0.818343,0.816805,0.816392,0.829096,0.817639,0.825224,0.821736,0.826919,0.824295,0.825032,0.820552,0.8338,0.82468,0.8282,0.82004,0.813287,0.84116,0.84084,0.832392,0.8354,0.840488,0.844296,0.839112,0.83892,0.840005,0.838437,0.831781,0.847528,0.859112,0.857413,0.866694,0.862725,0.845192,0.858152,0.853096,0.851881,0.854664,0.860585,0.852808,0.855941,0.84788,0.869285]},{"global_tokens":8192,"samples_ms":[10.958883,1.338061,1.336619,1.337901,1.351756,1.346348,1.346252,1.349548,1.346252,1.352876,1.346668,1.346252,1.340556,1.341356,1.354604,1.353868,1.345228,1.361484,1.34654,1.353964,1.344204,1.3451,1.349516,1.355276,1.347628,1.356972,1.351788,1.363756,1.359212,1.365676,1.358252,1.366476,1.35502,1.370349,1.445485,1.46331,1.439021,1.434157,1.435693,1.467181,1.469485,1.466957,1.46971,1.471149,1.471789,1.469613,1.473005,1.471181,1.469197,1.458573,1.46283,1.463726,1.461678,1.460718,1.463373,1.467437,1.453805,1.552718,1.563886,1.559918,1.554958,1.564238,1.557742,1.565806,1.531405,1.550893,1.534574,1.551886,1.543342,1.537133,1.529678,1.545838,1.539982,1.54555,1.54267,1.548429,1.575598,1.563918,1.56683,1.578255,1.563438,1.571214,1.581934,1.58107,1.563598,1.57947,1.569102,1.571726,1.574895,1.572431,1.550574,1.549294,1.551886,1.537486,1.544206,1.54747,1.548237,1.556589,1.537197,1.54699]},{"global_tokens":16384,"samples_ms":[24.796341,2.470031,2.477618,2.472179,2.478383,2.479282,2.470258,2.472654,2.484975,2.493938,2.524339,2.494131,2.508914,2.526387,2.721233,2.707288,2.701017,2.717584,2.697684,2.682937,2.694128,2.679184,2.683056,2.674451,2.698772,2.82162,2.861242,2.857873,2.875985,2.883761,2.914609,2.920027,2.914033,2.919158,2.91861,2.908946,2.905266,2.922002,2.918257,2.912849,2.915761,2.926321,2.917457,2.926802,2.91253,2.901874,2.903921,2.916338,2.906705,2.908177,2.910267,2.899377,2.904274,2.901393,2.905586,2.912177,2.906289,2.919889,2.901265,2.888305,2.881873,2.881298,2.91909,2.914929,2.911793,2.926545,2.920401,2.915378,2.924626,2.921137,2.929297,2.918609,2.918065,2.907921,2.934002,2.917362,2.937714,2.936305,2.924753,2.916881,2.916786,2.939602,2.92053,2.915442,2.912529,2.90847,2.917499,2.893403,2.893137,2.890961,2.885681,2.885201,2.908433,2.888241,2.883729,2.884593,2.882001,2.881906,2.896721,2.890641]}]
```

### local-pool-last/ep4

```json
[{"global_tokens":1,"samples_ms":[4.157907,0.079201,0.067936,0.068096,0.067937,0.066304,0.156993,0.069376,0.065057,0.065569,0.066624,0.067073,0.065792,0.065729,0.066848,0.067968,0.066336,0.066273,0.065953,0.066304,0.06512,0.065184,0.066656,0.064929,0.064832,0.068896,0.064544,0.066561,0.065345,0.065312,0.067456,0.065888,0.068033,0.066816,0.067328,0.068801,0.104257,0.067872,0.06544,0.067329,0.068096,0.065601,0.064512,0.067585,0.066881,0.066561,0.066977,0.068672,0.072,0.066208,0.066913,0.067009,0.06672,0.067552,0.067329,0.064321,0.067777,0.068864,0.066912,0.066752,0.068129,0.068865,0.066432,0.067648,0.066368,0.068768,0.066529,0.066017,0.066208,0.065825,0.067392,0.06848,0.066881,0.066112,0.068224,0.064897,0.067968,0.074465,0.067361,0.068128,0.066784,0.068257,0.069376,0.080577,0.070656,0.06608,0.065665,0.066624,0.065569,0.068321,0.065664,0.065408,0.066432,0.066304,0.066177,0.066881,0.065729,0.066976,0.06864,0.067809]},{"global_tokens":2,"samples_ms":[6.259244,0.096128,0.099905,0.102208,0.099488,0.097697,0.099873,0.096801,0.095456,0.097281,0.099073,0.097185,0.0976,0.098497,0.096097,0.097089,0.098305,0.09888,0.101377,0.099713,0.098336,0.099585,0.098048,0.099776,0.100417,0.100865,0.098401,0.099521,0.097024,0.106657,0.099808,0.098945,0.098113,0.097153,0.098689,0.097825,0.099872,0.097793,0.101696,0.100193,0.100897,0.098529,0.099777,0.100864,0.100192,0.103617,0.101344,0.100065,0.101376,0.098336,0.100961,0.101248,0.099905,0.100833,0.09936,0.100961,0.10112,0.098337,0.100609,0.100512,0.101793,0.105216,0.101217,0.101089,0.100384,0.101345,0.101184,0.10176,0.100993,0.10384,0.099969,0.09888,0.100833,0.102721,0.101185,0.109057,0.101216,0.099905,0.101345,0.101409,0.107073,0.102528,0.101825,0.103264,0.101888,0.098337,0.103744,0.102689,0.101568,0.100929,0.105761,0.102369,0.101313,0.101056,0.101408,0.100225,0.10144,0.101217,0.101473,0.102145]},{"global_tokens":4,"samples_ms":[17.013755,0.128929,0.120961,0.120097,0.130689,0.123072,0.121441,0.122689,0.122722,0.122689,0.123136,0.124097,0.124674,0.123009,0.120418,0.121281,0.122976,0.121472,0.121409,0.122433,0.120801,0.119489,0.121889,0.119841,0.121889,0.123264,0.123201,0.12237,0.121601,0.123809,0.124417,0.122817,0.122113,0.122753,0.124864,0.123265,0.123041,0.12416,0.124034,0.12669,0.128482,0.124994,0.121217,0.127585,0.154626,0.122945,0.124353,0.125504,0.124833,0.125249,0.123905,0.122849,0.124993,0.131809,0.126113,0.125792,0.126689,0.125441,0.127616,0.124513,0.123681,0.128257,0.125697,0.124577,0.126625,0.124641,0.127009,0.126946,0.122978,0.125441,0.125985,0.124481,0.125985,0.124993,0.124225,0.126305,0.125857,0.127265,0.125761,0.126593,0.123489,0.122593,0.126337,0.125921,0.123617,0.125153,0.268675,0.124481,0.125761,0.124993,0.125281,0.122657,0.123425,0.122338,0.130369,0.123457,0.125984,0.127681,0.128833,0.123425]},{"global_tokens":8,"samples_ms":[3.321473,0.157505,0.154498,0.153025,0.153762,0.152769,0.154498,0.320163,0.164226,0.153378,0.151617,0.154402,0.152449,0.155394,0.154305,0.153634,0.154017,0.158402,0.153153,0.15917,0.153377,0.158913,0.154625,0.154306,0.156609,0.319875,0.168674,0.154306,0.154562,0.153378,0.151553,0.153442,0.155521,0.158241,0.154401,0.153633,0.156706,0.154241,0.15581,0.156225,0.157026,0.154786,0.155746,0.154209,0.156385,0.158369,0.156513,0.155554,0.156194,0.155297,0.155041,0.154721,0.155457,0.157058,0.161634,0.158114,0.160386,0.154913,0.156258,0.156929,0.153633,0.155329,0.155362,0.157089,0.153186,0.151489,0.15357,0.156417,0.158209,0.154273,0.15757,0.154369,0.157473,0.155777,0.156674,0.157921,0.156865,0.154146,0.157217,0.154465,0.156098,0.155201,0.155361,0.15981,0.156193,0.156194,0.154625,0.15341,0.155777,0.156098,0.156001,0.157954,0.155361,0.154145,0.154818,0.154753,0.155713,0.15389,0.15485,0.15245]},{"global_tokens":16,"samples_ms":[10.005814,0.210626,0.201154,0.204353,0.201793,0.206753,0.210273,0.202338,0.204193,0.202241,0.204321,0.203041,0.203105,0.204098,0.202561,0.206465,0.200513,0.204193,0.204097,0.204898,0.202913,0.202561,0.204352,0.203041,0.204801,0.203969,0.207169,0.207681,0.200513,0.205665,0.207649,0.204609,0.201825,0.203841,0.204449,0.203617,0.202817,0.205696,0.204481,0.202945,0.204642,0.206145,0.206209,0.203649,0.208609,0.207713,0.206017,0.205025,0.205633,0.205953,0.206178,0.426724,0.215618,0.206369,0.206433,0.206689,0.204066,0.206529,0.204641,0.204385,0.208545,0.207649,0.208065,0.207074,0.204353,0.204514,0.202561,0.207233,0.204449,0.202434,0.205698,0.20381,0.202881,0.207554,0.201761,0.20605,0.204066,0.206369,0.201986,0.207874,0.205537,0.204321,0.20861,0.205857,0.206209,0.203394,0.207329,0.202786,0.205698,0.207361,0.203138,0.205793,0.205857,0.205633,0.202881,0.203874,0.201633,0.203234,0.206146,0.205985]},{"global_tokens":32,"samples_ms":[23.993398,0.270819,0.272002,0.268002,0.267106,0.266435,0.266626,0.274914,0.270915,0.269571,0.26877,0.272899,0.269571,0.27053,0.269698,0.270594,0.270882,0.27165,0.273667,0.271107,0.27149,0.273794,0.269507,0.271938,0.27101,0.268386,0.276611,0.27149,0.446948,0.26909,0.268002,0.272482,0.270082,0.271491,0.278403,0.27053,0.270082,0.272866,0.26765,0.27037,0.268707,0.270594,0.268802,0.267906,0.271171,0.271939,0.27293,0.270787,0.271203,0.269026,0.270627,0.27229,0.270146,0.269026,0.272098,0.271075,0.276162,0.27261,0.273763,0.272642,0.270978,0.273122,0.273987,0.268355,0.274818,0.272035,0.272098,0.272546,0.272067,0.268835,0.271874,0.270818,0.269091,0.270114,0.270018,0.268547,0.269379,0.272258,0.273155,0.272771,0.272003,0.269826,0.271331,0.269603,0.272034,0.27133,0.273186,0.26973,0.272098,0.268547,0.269986,0.270754,0.273123,0.269411,0.272163,0.271554,0.272451,0.269154,0.270658,0.269698]},{"global_tokens":64,"samples_ms":[5.91969,0.299682,0.300994,0.306306,0.300418,0.299266,0.297601,0.298465,0.298178,0.299329,0.29789,0.29741,0.300129,0.294978,0.296642,0.299266,0.302145,0.300353,0.30125,0.300737,0.296002,0.300354,0.300258,0.298658,0.301505,0.301282,0.302114,0.302467,0.301121,0.299234,0.301154,0.301633,0.300513,0.301762,0.299906,0.300545,0.299841,0.298915,0.300354,0.303746,0.302114,0.302114,0.303106,0.303554,0.301858,0.303714,0.30189,0.302818,0.299714,0.303458,0.29901,0.302402,0.30205,0.303201,0.302306,0.302274,0.301057,0.300994,0.303555,0.303139,0.30093,0.300546,0.301826,0.302529,0.302753,0.301283,0.301281,0.299394,0.303298,0.301249,0.301313,0.300226,0.300322,0.299873,0.304642,0.302305,0.301249,0.30221,0.299842,0.304738,0.301569,0.29997,0.302722,0.30045,0.30301,0.299394,0.302179,0.30221,0.300834,0.302402,0.303778,0.300449,0.302371,0.300226,0.298242,0.301378,0.302562,0.302946,0.303042,0.300546]},{"global_tokens":128,"samples_ms":[9.598051,0.331746,0.328418,0.325986,0.324386,0.329571,0.326562,0.328994,0.330435,0.327139,0.328642,0.328355,0.330434,0.330658,0.331394,0.329763,0.331715,0.340386,0.331234,0.328706,0.333826,0.324099,0.332866,0.331682,0.336002,0.332066,0.330178,0.333346,0.329986,0.33261,0.329698,0.33485,0.33213,0.332386,0.331394,0.328546,0.328674,0.329538,0.33181,0.330594,0.330274,0.331298,0.331778,0.33261,0.330786,0.329026,0.329762,0.333858,0.332962,0.331618,0.333922,0.334562,0.330626,0.331906,0.331266,0.33261,0.333474,0.33277,0.323554,0.334082,0.331714,0.333218,0.330595,0.32909,0.332514,0.33085,0.332354,0.331746,0.332578,0.331106,0.331554,0.331682,0.330083,0.330434,0.331042,0.330819,0.328866,0.330946,0.333155,0.328963,0.328547,0.332483,0.329026,0.328962,0.328866,0.330083,0.33133,0.333378,0.329635,0.32909,0.328066,0.328898,0.331874,0.333187,0.328034,0.330723,0.334115,0.332866,0.331522,0.330179]},{"global_tokens":256,"samples_ms":[9.645747,0.340867,0.332355,0.335043,0.332483,0.333091,0.331267,0.331587,0.330915,0.331779,0.332419,0.332547,0.334499,0.334019,0.334019,0.330851,0.331075,0.332675,0.333923,0.333891,0.333443,0.333699,0.349507,0.330467,0.33517,0.335651,0.340611,0.334627,0.331939,0.333507,0.332228,0.332995,0.331555,0.333955,0.331811,0.332035,0.332355,0.333411,0.332739,0.331555,0.332035,0.329891,0.33306,0.340931,0.333603,0.334883,0.335523,0.334595,0.333635,0.334755,0.334499,0.336483,0.335684,0.334819,0.334179,0.332515,0.334019,0.333442,0.336098,0.333922,0.334531,0.334659,0.331491,0.338786,0.334787,0.334819,0.343075,0.333955,0.334979,0.332484,0.333763,0.335267,0.333315,0.334627,0.329603,0.333283,0.332387,0.332195,0.334531,0.332291,0.334339,0.334852,0.333347,0.333283,0.335907,0.334404,0.332995,0.332707,0.334275,0.333955,0.335651,0.333347,0.333411,0.333155,0.335331,0.335427,0.332451,0.335875,0.335491,0.334019]},{"global_tokens":512,"samples_ms":[2.073842,0.35258,0.344451,0.347171,0.346179,0.344899,0.344611,0.345379,0.341795,0.344451,0.346308,0.344419,0.343746,0.346979,0.342467,0.344035,0.343139,0.344899,0.343491,0.344227,0.35226,0.345667,0.348068,0.346339,0.344995,0.341955,0.343779,0.344515,0.341155,0.345987,0.360163,0.351683,0.347683,0.343971,0.345123,0.342787,0.344579,0.397987,0.346211,0.343427,0.344899,0.344899,0.342755,0.343715,0.343171,0.344228,0.348995,0.34365,0.343716,0.346211,0.345763,0.34861,0.361347,0.345315,0.342755,0.343555,0.344067,0.346179,0.344515,0.346659,0.345315,0.34445,0.344771,0.344227,0.343331,0.345538,0.345026,0.345186,0.350691,0.343554,0.341955,0.343555,0.344963,0.344579,0.341795,0.343842,0.343747,0.342979,0.342787,0.342402,0.345444,0.345028,0.344003,0.344994,0.342723,0.343747,0.344483,0.344483,0.343587,0.342467,0.344291,0.342883,0.343778,0.343204,0.344164,0.393988,0.344708,0.344195,0.342882,0.344803]},{"global_tokens":4096,"samples_ms":[10.426172,0.780007,0.783047,0.792326,0.789252,0.782727,0.785063,0.783015,0.788519,0.789575,0.780263,0.779656,0.787462,0.782247,0.78887,0.787496,0.791431,0.782151,0.787496,0.788359,0.797128,0.790471,0.787687,0.787911,0.789863,0.794406,0.783431,0.787911,0.787528,0.782663,0.780999,0.783655,0.780775,0.779015,0.792902,0.791335,0.782855,0.783109,0.799048,0.788231,0.788487,0.782503,0.804935,0.796584,0.792391,0.793862,0.801544,0.789799,0.794054,0.796872,0.799592,0.794662,0.788326,0.790951,0.790181,0.793094,0.794309,0.797927,0.790696,0.798408,0.783943,0.791047,0.795143,0.790087,0.792839,0.794888,0.796231,0.789095,0.791143,0.797096,0.79431,0.814472,0.820616,0.826792,0.842023,0.822087,0.820743,0.825799,0.82596,0.821415,0.84068,0.864071,0.852808,0.838984,0.837767,0.834536,0.849575,0.858216,0.838471,0.835176,0.837895,0.832935,0.834535,0.844712,0.830407,0.8394,0.839111,0.842215,0.837287,0.837256]},{"global_tokens":8192,"samples_ms":[6.903625,1.347436,1.339756,1.338252,1.33582,1.348141,1.33774,1.341772,1.346316,1.349352,1.339275,1.339372,1.344458,1.343688,1.342792,1.356426,1.334091,1.356621,1.334028,1.349292,1.352904,1.354604,1.343882,1.350793,1.34574,1.342088,1.348716,1.358794,1.35937,1.347564,1.349516,1.35294,1.38241,1.38017,1.37313,1.378315,1.37649,1.385962,1.396266,1.388811,1.439178,1.439241,1.432364,1.441197,1.442505,1.438028,1.432489,1.440844,1.457261,1.448425,1.45054,1.453453,1.45214,1.448654,1.454313,1.46046,1.4483,1.450797,1.463304,1.452941,1.462184,1.463049,1.459337,1.473356,1.472329,1.555598,1.560585,1.557033,1.612878,1.68958,1.558861,1.548174,1.528686,1.540718,1.547662,1.532109,1.542254,1.55659,1.539341,1.546286,1.542702,1.541997,1.562445,1.542861,1.536173,1.544462,1.535981,1.537741,1.542477,1.539021,1.563949,1.56667,1.579309,1.571469,1.584654,1.583693,1.549229,1.566606,1.568685,1.570318]},{"global_tokens":16384,"samples_ms":[50.322216,2.481719,2.478102,2.470935,2.479414,2.485719,2.484727,2.477302,2.478934,2.471255,2.487159,2.493175,2.479638,2.612024,2.612984,2.609464,2.638328,2.782073,2.755312,2.763056,2.753561,2.754256,2.744272,2.726607,2.725721,2.734041,2.721593,2.738681,2.886235,2.915802,2.913946,2.910491,2.928507,2.920507,2.915834,2.914747,2.914427,2.916122,2.915162,2.925371,2.914011,2.912827,2.912251,2.913403,2.931963,2.932699,2.941691,2.936442,2.934748,2.94537,2.936732,2.931835,2.937819,2.931131,2.905627,2.91257,2.913051,2.918907,2.916346,2.91065,2.916475,2.912507,2.916794,2.911163,2.911963,2.917563,2.910938,2.907451,2.903738,2.914555,2.904603,2.915163,2.905114,2.911483,2.934683,2.939675,2.948443,2.946747,2.937531,2.943195,2.944923,2.912314,2.911419,2.916475,2.907931,2.900378,2.912315,4.100517,2.90505,2.900923,2.906234,2.915995,2.900603,2.862106,2.855706,2.840122,2.865146,2.882843,2.881306,2.874586]}]
```

### baseline/ep8

```json
[{"global_tokens":1,"samples_ms":[27.364317,0.080321,0.075041,0.070208,0.074561,0.070689,0.072736,0.075393,0.074113,0.073281,0.077985,0.072481,0.075489,0.074688,0.075136,0.076065,0.07664,0.075393,0.082785,0.077184,0.076385,0.077728,0.090433,0.076544,0.078241,0.079457,0.076577,0.074369,0.07472,0.076993,0.07648,0.07504,0.076353,0.078048,0.07648,0.077633,0.077408,0.080001,0.076512,0.079681,0.076481,0.076608,0.073057,0.077697,0.076449,0.078209,0.076545,0.077857,0.075904,0.075777,0.086336,0.078049,0.076257,0.075424,0.078017,0.076928,0.077665,0.07728,0.074817,0.078081,0.077217,0.079009,0.077952,0.076353,0.078144,0.074304,0.077057,0.08464,0.076225,0.07776,0.077088,0.077217,0.074881,0.077665,0.07632,0.074049,0.079937,0.076513,0.076513,0.077824,0.075489,0.075264,0.07824,0.077953,0.077856,0.076833,0.079168,0.075393,0.075777,0.077441,0.075009,0.077153,0.072353,0.078688,0.076672,0.087168,0.077825,0.078113,0.084544,0.078113]},{"global_tokens":2,"samples_ms":[9.415019,0.085185,0.083265,0.086593,0.082849,0.083553,0.084512,0.08285,0.082561,0.082848,0.082305,0.079936,0.086977,0.086945,0.084416,0.083777,0.085409,0.083457,0.083554,0.084769,0.082945,0.085409,0.085921,0.087297,0.086625,0.085825,0.084481,0.086689,0.086657,0.085249,0.086369,0.084577,0.086145,0.087361,0.086433,0.08736,0.088065,0.086529,0.089282,0.087265,0.089473,0.08829,0.087457,0.096161,0.089217,0.091169,0.091393,0.088928,0.092417,0.088609,0.088225,0.089376,0.090018,0.089921,0.088801,0.091266,0.090369,0.090338,0.088641,0.091905,0.088577,0.090306,0.091489,0.092033,0.088545,0.087361,0.090241,0.091457,0.08989,0.08736,0.091841,0.090337,0.088321,0.090113,0.089921,0.087265,0.090369,0.089441,0.090497,0.090817,0.089089,0.08928,0.087936,0.091041,0.090369,0.092545,0.090081,0.091201,0.090721,0.091136,0.099937,0.090945,0.090049,0.090049,0.089025,0.087488,0.090561,0.088993,0.089633,0.088065]},{"global_tokens":4,"samples_ms":[9.519342,0.102784,0.103873,0.099873,0.101761,0.109121,0.10384,0.102113,0.101761,0.102945,0.101889,0.101313,0.100257,0.102528,0.099713,0.100608,0.102401,0.100705,0.102305,0.102881,0.101824,0.103169,0.103233,0.103105,0.101953,0.109824,0.100481,0.101889,0.104705,0.102337,0.104609,0.105441,0.104801,0.102849,0.104577,0.103169,0.102369,0.104929,0.106209,0.101632,0.103329,0.104289,0.10496,0.104929,0.105152,0.105249,0.106657,0.105217,0.110049,0.107457,0.106656,0.103809,0.107008,0.107745,0.107777,0.114786,0.107873,0.109569,0.109793,0.107649,0.110113,0.107969,0.110017,0.109953,0.108641,0.106433,0.108961,0.108672,0.108097,0.109217,0.108865,0.107873,0.109089,0.109312,0.118721,0.106816,0.108353,0.109377,0.107745,0.109761,0.108449,0.108033,0.109313,0.109729,0.1096,0.110177,0.109953,0.107777,0.110945,0.109441,0.11088,0.108353,0.108865,0.110913,0.109121,0.110465,0.108385,0.109729,0.109985,0.108097]},{"global_tokens":8,"samples_ms":[41.327824,0.146882,0.119617,0.116738,0.116929,0.120417,0.119265,0.119778,0.118465,0.117473,0.119105,0.119457,0.118112,0.119618,0.117793,0.117633,0.119713,0.120129,0.120001,0.119585,0.120641,0.117793,0.118881,0.120225,0.122177,0.119489,0.124578,0.121441,0.121025,0.120674,0.122401,0.123457,0.122274,0.130018,0.123361,0.121857,0.124929,0.127137,0.123904,0.124065,0.123489,0.127778,0.126114,0.125154,0.128289,0.124513,0.126466,0.124513,0.124673,0.123042,0.123617,0.124449,0.125377,0.12381,0.124385,0.12653,0.121985,0.124384,0.124162,0.125281,0.125409,0.123937,0.123938,0.123457,0.126465,0.125377,0.122082,0.121761,0.122625,0.122081,0.124481,0.123297,0.124193,0.125441,0.12608,0.126721,0.123009,0.134529,0.123682,0.124513,0.123425,0.133762,0.123681,0.122881,0.122529,0.12573,0.125857,0.125857,0.123905,0.121633,0.124738,0.121185,0.124225,0.124641,0.122946,0.127298,0.124161,0.122721,0.12461,0.123296]},{"global_tokens":16,"samples_ms":[42.402826,0.133025,0.13869,0.138369,0.140769,0.137794,0.138081,0.148482,0.140929,0.160354,0.138433,0.137857,0.14013,0.137953,0.139137,0.137186,0.137889,0.13885,0.139489,0.135361,0.140258,0.138817,0.13949,0.138017,0.138337,0.140098,0.141537,0.13933,0.139105,0.138689,0.13981,0.139809,0.139457,0.14237,0.140321,0.140737,0.141409,0.142626,0.141121,0.141537,0.139553,0.140033,0.14477,0.140897,0.155138,0.139201,0.147106,0.139521,0.140034,0.140354,0.165762,0.142401,0.144929,0.13997,0.139746,0.138881,0.139137,0.139234,0.139425,0.143426,0.141665,0.139202,0.141217,0.141249,0.141569,0.141345,0.141633,0.138369,0.142434,0.144034,0.142401,0.140418,0.143745,0.13917,0.140961,0.140994,0.141697,0.139073,0.13965,0.140769,0.152034,0.140353,0.141954,0.143074,0.140002,0.140769,0.141378,0.140225,0.140865,0.140194,0.141249,0.138977,0.141633,0.141698,0.140417,0.144962,0.142145,0.14045,0.14093,0.149378]},{"global_tokens":32,"samples_ms":[16.058891,0.210178,0.163778,0.188962,0.165282,0.164002,0.164065,0.168353,0.164162,0.164354,0.161601,0.164033,0.16365,0.163234,0.165057,0.163073,0.162561,0.164834,0.164322,0.164321,0.164545,0.164898,0.164513,0.164417,0.165249,0.165442,0.162913,0.164801,0.168993,0.165762,0.166593,0.167009,0.167426,0.164129,0.165313,0.167457,0.167938,0.165248,0.167681,0.16669,0.168482,0.164257,0.166753,0.169634,0.169633,0.16957,0.168833,0.168801,0.169473,0.16701,0.16685,0.167457,0.173922,0.168609,0.169377,0.169442,0.167394,0.169377,0.167745,0.16797,0.169633,0.167073,0.170338,0.168034,0.167585,0.170722,0.169377,0.167713,0.16813,0.170466,0.167681,0.169185,0.167425,0.167201,0.168961,0.168449,0.167937,0.168417,0.164226,0.168482,0.168865,0.167714,0.174913,0.171458,0.173538,0.168321,0.170273,0.170018,0.16653,0.177281,0.168034,0.170977,0.166497,0.172066,0.167586,0.166593,0.166338,0.16653,0.167265,0.165218]},{"global_tokens":64,"samples_ms":[39.286024,0.20173,0.190338,0.189441,0.191362,0.190401,0.19325,0.190946,0.192066,0.191713,0.19293,0.193602,0.193953,0.194561,0.194721,0.194721,0.195393,0.196161,0.194049,0.193793,0.194177,0.193665,0.197025,0.199585,0.194049,0.196513,0.196225,0.196769,0.198657,0.197985,0.190273,0.201185,0.190913,0.194113,0.193409,0.193793,0.195265,0.193153,0.193537,0.194529,0.194433,0.192033,0.193921,0.193857,0.195105,0.196225,0.194401,0.193217,0.196289,0.192257,0.193793,0.194401,0.193921,0.195425,0.194273,0.194369,0.193985,0.194881,0.194017,0.197793,0.194113,0.195777,0.194658,0.194081,0.196129,0.202081,0.194241,0.194529,0.194721,0.19421,0.195873,0.193473,0.239617,0.191233,0.192225,0.193185,0.195041,0.195489,0.195489,0.194081,0.199329,0.194849,0.210305,0.195489,0.233793,0.241378,0.193826,0.195681,0.192802,0.193186,0.192226,0.197058,0.193858,0.193826,0.196065,0.195938,0.222178,0.195745,0.195905,0.210113]},{"global_tokens":128,"samples_ms":[27.273399,0.188162,0.186146,0.185729,0.186626,0.189409,0.187457,0.186689,0.186433,0.189666,0.187554,0.186305,0.185826,0.186785,0.189153,0.188417,0.191105,0.190401,0.189089,0.187776,0.187873,0.191745,0.188609,0.189441,0.190177,0.191553,0.190274,0.191586,0.192673,0.192257,0.191649,0.192995,0.191137,0.192321,0.194241,0.193794,0.195137,0.196001,0.19389,0.203074,0.194946,0.196385,0.194049,0.193825,0.194433,0.193633,0.194145,0.193601,0.194305,0.194274,0.193761,0.193954,0.19357,0.193185,0.194945,0.199489,0.19469,0.195905,0.194274,0.198529,0.204227,0.194146,0.195714,0.193858,0.194753,0.194786,0.194561,0.19421,0.194178,0.192738,0.19549,0.197665,0.192065,0.194913,0.195297,0.195169,0.193793,0.194306,0.194018,0.19181,0.193985,0.192481,0.196098,0.194434,0.193474,0.192961,0.194177,0.193697,0.196193,0.194657,0.19613,0.216738,0.195777,0.190913,0.199842,0.194977,0.194402,0.19565,0.193634,0.195361]},{"global_tokens":256,"samples_ms":[18.995316,0.199842,0.19501,0.194466,0.194722,0.193954,0.193697,0.19517,0.195714,0.195746,0.196577,0.19581,0.195778,0.20557,0.196866,0.196865,0.506693,0.197634,0.200802,0.199266,0.194209,0.19645,0.198338,0.195458,0.199906,0.199106,0.199554,0.196034,0.197314,0.199106,0.196994,0.210178,0.199874,0.198402,0.201506,0.19933,0.19901,0.197859,0.20045,0.199938,0.202146,0.199873,0.20541,0.199362,0.200802,0.205986,0.202018,0.204514,0.200642,0.202946,0.212546,0.202306,0.204066,0.203586,0.20333,0.199905,0.202913,0.20349,0.203202,0.199234,0.202466,0.200257,0.20173,0.202178,0.200706,0.19997,0.201921,0.204001,0.202594,0.201826,0.204162,0.20509,0.201282,0.205218,0.202913,0.239746,0.201857,0.20205,0.203266,0.20141,0.200706,0.201122,0.204162,0.204258,0.202849,0.19981,0.21277,0.20189,0.204226,0.203138,0.200066,0.202978,0.200834,0.20381,0.21021,0.19917,0.201954,0.203681,0.202755,0.200098]},{"global_tokens":512,"samples_ms":[43.123653,0.290947,0.215202,0.210882,0.210753,0.212674,0.212578,0.209154,0.210946,0.211137,0.212578,0.205442,0.212642,0.211299,0.207585,0.21133,0.21597,0.206913,0.21149,0.210434,0.211906,0.210114,0.212002,0.209858,0.211298,0.212834,0.209282,0.210242,0.212386,0.21133,0.21245,0.212162,0.211426,0.209793,0.209794,0.21037,0.211906,0.210946,0.21085,0.210721,0.209154,0.210946,0.21005,0.22125,0.212226,0.21149,0.211106,0.210338,0.210786,0.211074,0.209283,0.206914,0.207714,0.213282,0.212674,0.212162,0.20925,0.21021,0.209634,0.220738,0.213026,0.212259,0.210817,0.212034,0.213378,0.213698,0.210657,0.211233,0.21005,0.21101,0.212194,0.21053,0.209923,0.213346,0.211586,0.207458,0.212514,0.209985,0.210242,0.21549,0.209538,0.212642,0.210913,0.209699,0.209762,0.210274,0.214018,0.20989,0.210497,0.212353,0.207522,0.202081,0.209346,0.209026,0.210626,0.211489,0.210626,0.211906,0.208577,0.208579]},{"global_tokens":4096,"samples_ms":[30.566813,0.461412,0.45962,0.464357,0.458277,0.454372,0.456356,0.4625,0.457092,0.462725,0.457284,0.456996,0.45818,0.465573,0.46586,0.457252,0.45754,0.45818,0.453892,0.466628,0.46282,0.463332,0.460581,0.460068,0.4689,0.468452,0.464101,0.461988,0.468036,0.465285,0.462821,0.460548,0.45514,0.463685,0.4761,0.46218,0.461637,0.457445,0.464037,0.465092,0.46842,0.457668,0.464868,0.460004,0.464068,0.462245,0.467204,0.456804,0.466276,0.471621,0.46858,0.460069,0.466565,0.462692,0.473412,0.458885,0.46922,0.471908,0.464484,0.460452,0.460068,0.456228,0.458213,0.46186,0.461093,0.46714,0.46234,0.453923,0.461124,0.457796,0.463748,0.463716,0.466565,0.458436,0.46426,0.461861,0.46282,0.463588,0.463653,0.459908,0.468452,0.469892,0.467429,0.462084,0.461124,0.467973,0.469892,0.46615,0.476901,0.474373,0.473092,0.473061,0.480166,0.472069,0.472068,0.468932,0.467716,0.472453,0.47002,0.473572]},{"global_tokens":8192,"samples_ms":[19.972982,0.770119,0.756454,0.769126,0.771846,0.770662,0.770598,0.77415,0.76439,0.770342,0.782599,0.766918,0.768326,0.767623,0.780646,0.764359,0.767943,0.776678,0.783942,0.764774,0.772901,0.779174,0.769863,0.765158,0.764998,0.770854,0.782502,0.772742,0.766022,0.771302,0.765926,0.76807,0.773254,0.770534,0.769574,0.772262,0.778214,0.776742,0.763718,0.762566,0.770918,0.772102,0.776423,0.763717,0.769798,0.767559,0.773063,0.758886,0.77351,0.778278,0.760774,0.76903,0.768454,0.76967,0.784582,0.78391,0.77159,0.77479,0.78199,0.776902,0.781638,0.773702,0.774854,0.78119,0.784902,0.789382,0.788774,0.874695,0.78999,0.795975,0.801255,0.801831,0.797766,0.803558,0.803943,0.794983,0.807047,0.812902,0.808422,0.811815,0.821286,0.827526,0.813639,0.812006,0.816455,0.817511,0.816998,0.816167,0.816903,0.814438,0.815655,0.819303,0.820934,0.809991,0.818535,0.817862,0.816743,0.824806,0.823558,0.822343]},{"global_tokens":16384,"samples_ms":[32.572661,1.376171,1.363178,1.367531,1.361834,1.372107,1.370443,1.373131,1.377931,1.365867,1.376331,1.379371,1.379915,1.373451,1.377611,1.367659,1.383147,1.380587,1.371115,1.369739,1.370603,1.378538,1.406059,1.400139,1.400939,1.394251,1.389867,1.397675,1.415564,1.452588,1.476908,1.487212,1.475051,1.479787,1.513068,1.512012,1.506508,1.498668,1.498315,1.496268,1.498705,1.502572,1.497516,1.496396,1.492108,1.50366,1.49822,1.496619,1.503532,1.500172,1.506188,1.509196,1.509195,1.523756,1.515308,1.508333,1.528716,1.516556,1.567308,1.559724,1.553132,1.552172,1.55614,1.579852,1.558124,1.554124,1.564748,1.561964,1.552396,1.549293,1.557036,1.559596,1.555052,1.548653,1.532204,1.520748,1.530636,1.532779,1.532427,1.590253,1.576492,1.5931,1.584684,1.586509,1.587372,1.57598,1.580876,1.590957,1.589325,1.596332,1.590829,1.598765,1.591692,1.580204,1.586732,1.584109,1.58974,1.550668,1.547308,1.552812]}]
```

### dispatch-normal-r1/ep8

```json
[{"global_tokens":1,"samples_ms":[24.262268,0.076161,0.071265,0.069889,0.07456,0.071072,0.0704,0.074592,0.069089,0.069665,0.069536,0.070529,0.070081,0.068737,0.068545,0.072705,0.070432,0.071457,0.076257,0.069601,0.070688,0.068256,0.075232,0.070785,0.070945,0.070817,0.071648,0.070273,0.072384,0.070433,0.073249,0.071232,0.070848,0.069441,0.073345,0.072737,0.070688,0.070496,0.071552,0.072641,0.072384,0.075712,0.072738,0.070529,0.072961,0.071105,0.069345,0.070976,0.073857,0.069696,0.072641,0.072929,0.07184,0.074752,0.074688,0.072609,0.072896,0.07216,0.072353,0.073344,0.071489,0.071264,0.071777,0.070433,0.072928,0.071296,0.072001,0.070688,0.071617,0.071936,0.072289,0.070017,0.072833,0.072674,0.07328,0.072257,0.074017,0.072064,0.073409,0.070913,0.073665,0.073665,0.07488,0.075713,0.070208,0.072576,0.072737,0.072992,0.073377,0.072929,0.073024,0.073889,0.069824,0.073281,0.074113,0.074049,0.072769,0.072384,0.073729,0.071105]},{"global_tokens":2,"samples_ms":[22.481969,0.083681,0.086689,0.084193,0.082944,0.08496,0.084449,0.082977,0.083072,0.084193,0.08288,0.08608,0.084065,0.083328,0.084289,0.084256,0.088897,0.084257,0.084065,0.08448,0.085697,0.084865,0.086113,0.084289,0.084961,0.085377,0.084833,0.08608,0.086753,0.086176,0.087201,0.088289,0.084097,0.084833,0.086176,0.086145,0.084193,0.084705,0.086849,0.086528,0.084289,0.088289,0.087809,0.087745,0.086816,0.088449,0.087232,0.089537,0.090465,0.087361,0.087873,0.087393,0.089665,0.088769,0.088769,0.090113,0.090657,0.089184,0.089921,0.08928,0.090464,0.086977,0.090017,0.090049,0.088865,0.088642,0.090433,0.091521,0.088801,0.091553,0.090112,0.09072,0.089665,0.092736,0.089696,0.091297,0.0928,0.091392,0.091393,0.092833,0.092321,0.090881,0.089217,0.092673,0.092065,0.09264,0.089697,0.091841,0.092321,0.090337,0.092576,0.088737,0.090273,0.088416,0.090368,0.087361,0.091392,0.091905,0.091105,0.088832]},{"global_tokens":4,"samples_ms":[22.930324,0.109569,0.102976,0.101505,0.102177,0.103553,0.101857,0.102657,0.100258,0.098977,0.101025,0.101954,0.102785,0.101826,0.100513,0.102304,0.102177,0.101889,0.101185,0.099105,0.100545,0.103681,0.107361,0.101441,0.101217,0.102337,0.099648,0.105185,0.101473,0.099649,0.102848,0.102753,0.102177,0.100353,0.103105,0.102305,0.105153,0.102944,0.104385,0.103714,0.101889,0.103584,0.103713,0.103873,0.101569,0.102497,0.103009,0.104257,0.103009,0.102274,0.103073,0.103072,0.103905,0.102689,0.102721,0.103425,0.104834,0.104353,0.103457,0.108737,0.10557,0.105793,0.105922,0.10416,0.108193,0.105698,0.105537,0.108865,0.107648,0.108033,0.107041,0.106337,0.109249,0.10832,0.108482,0.108481,0.109665,0.110721,0.108929,0.109921,0.107137,0.118689,0.108257,0.109601,0.109216,0.108129,0.109761,0.109153,0.108353,0.105696,0.107041,0.108801,0.108096,0.109217,0.109473,0.109761,0.108417,0.108002,0.107393,0.111745]},{"global_tokens":8,"samples_ms":[13.968428,0.11853,0.115969,0.116929,0.115681,0.117025,0.117506,0.117281,0.11821,0.118081,0.118082,0.115872,0.115457,0.116033,0.118913,0.118593,0.117282,0.118817,0.118626,0.116257,0.118337,0.118753,0.119042,0.119425,0.120161,0.118913,0.120865,0.117474,0.119361,0.118786,0.120449,0.127457,0.120738,0.118721,0.120801,0.121537,0.120834,0.124513,0.12205,0.124769,0.12365,0.123553,0.125857,0.122274,0.128769,0.12221,0.120098,0.122274,0.126721,0.126722,0.125602,0.125665,0.124418,0.126049,0.125026,0.124481,0.122209,0.12349,0.122049,0.123169,0.124386,0.122561,0.126946,0.125249,0.123073,0.124257,0.123521,0.123809,0.128033,0.124256,0.123234,0.122562,0.123201,0.123841,0.12493,0.123009,0.122401,0.120673,0.124161,0.123617,0.124097,0.124897,0.122081,0.124514,0.124417,0.12288,0.123521,0.123841,0.127969,0.131617,0.124482,0.122977,0.122497,0.122242,0.123521,0.12352,0.124289,0.125185,0.123617,0.123585]},{"global_tokens":16,"samples_ms":[28.608572,0.143297,0.140673,0.138017,0.140226,0.139586,0.140065,0.145633,0.140353,0.141569,0.143233,0.142113,0.142081,0.137538,0.142305,0.140866,0.143649,0.140065,0.143009,0.140929,0.142465,0.142274,0.144257,0.14128,0.143746,0.144321,0.144609,0.144545,0.145697,0.143009,0.143969,0.143649,0.150657,0.146337,0.145473,0.146529,0.146176,0.145409,0.146594,0.14493,0.147457,0.144994,0.148418,0.143393,0.145537,0.144801,0.146657,0.144929,0.146497,0.157793,0.146209,0.143937,0.15005,0.146209,0.148257,0.148354,0.146273,0.14845,0.147265,0.146689,0.147489,0.146338,0.148385,0.147777,0.148386,0.147361,0.147553,0.146369,0.149793,0.148545,0.146465,0.145281,0.147041,0.145729,0.146273,0.144833,0.146465,0.145089,0.147169,0.143618,0.14909,0.14797,0.14704,0.145825,0.147105,0.14669,0.153474,0.145698,0.145505,0.146817,0.148417,0.146209,0.148801,0.146433,0.148129,0.147745,0.149217,0.146113,0.146113,0.148993]},{"global_tokens":32,"samples_ms":[49.954226,0.173762,0.169858,0.166273,0.167009,0.165505,0.165122,0.164226,0.164354,0.163938,0.164866,0.165601,0.165058,0.166146,0.165729,0.166913,0.167842,0.167554,0.16765,0.168577,0.167106,0.16685,0.171522,0.167138,0.16717,0.168514,0.169538,0.168193,0.177026,0.169346,0.168513,0.17005,0.169857,0.170498,0.167265,0.168354,0.169314,0.170369,0.168802,0.170274,0.160705,0.170113,0.169122,0.17053,0.170722,0.168034,0.172034,0.171362,0.170529,0.170945,0.172769,0.171554,0.171842,0.173729,0.173345,0.179842,0.169634,0.171329,0.174658,0.170946,0.172674,0.17037,0.171457,0.170657,0.172866,0.170657,0.16941,0.170018,0.171586,0.170786,0.17949,0.170657,0.168738,0.168897,0.168642,0.170626,0.170241,0.17229,0.169538,0.170497,0.168673,0.168449,0.167297,0.170241,0.17005,0.168545,0.17005,0.170721,0.169027,0.170242,0.171042,0.173761,0.172129,0.172834,0.171201,0.173761,0.169281,0.172993,0.169634,0.171842]},{"global_tokens":64,"samples_ms":[14.869936,0.249666,0.191362,0.192354,0.19533,0.194144,0.189345,0.18957,0.188578,0.192194,0.193537,0.1912,0.194242,0.189888,0.190722,0.19584,0.191329,0.192546,0.192449,0.198946,0.202274,0.218594,0.199298,0.202209,0.199106,0.199969,0.196962,0.197185,0.198817,0.199938,0.200769,0.199203,0.206178,0.197538,0.202273,0.211457,0.203234,0.200386,0.19741,0.198146,0.200225,0.202913,0.203874,0.195938,0.201345,0.203393,0.196418,0.210561,0.199457,0.203938,0.202529,0.200352,0.201537,0.19936,0.211809,0.203874,0.19613,0.216194,0.198242,0.199169,0.199585,0.196834,0.204161,0.198177,0.199874,0.195553,0.204258,0.203137,0.206689,0.205698,0.202497,0.203105,0.196545,0.203777,0.197537,0.200737,0.207201,0.200449,0.196097,0.201474,0.196385,0.199746,0.195265,0.198753,0.197345,0.196257,0.211265,0.201377,0.203041,0.196866,0.19677,0.202561,0.202913,0.204898,0.20029,0.200897,0.201121,0.198177,0.197441,0.199553]},{"global_tokens":128,"samples_ms":[23.876168,0.198785,0.197121,0.199042,0.197921,0.196289,0.198209,0.199937,0.198977,0.21069,0.19933,0.200962,0.200577,0.221569,0.203233,0.201666,0.202881,0.203617,0.202305,0.213538,0.201857,0.200513,0.201858,0.199681,0.203137,0.202081,0.201921,0.200641,0.203041,0.210017,0.201153,0.203297,0.202913,0.203105,0.202145,0.201409,0.245089,0.201153,0.202593,0.205314,0.204449,0.202657,0.204225,0.202721,0.201025,0.203073,0.201249,0.201825,0.202593,0.212322,0.20365,0.201985,0.200737,0.201505,0.203521,0.203713,0.202113,0.202241,0.197121,0.200577,0.201537,0.201633,0.202369,0.200769,0.201377,0.200769,0.197633,0.201569,0.202401,0.208418,0.202465,0.202017,0.202337,0.203426,0.201697,0.200609,0.197345,0.200321,0.199041,0.212673,0.200514,0.199297,0.204001,0.200833,0.20205,0.203201,0.207457,0.199905,0.200354,0.209697,0.204993,0.202338,0.200962,0.202337,0.201121,0.198562,0.204258,0.202113,0.203457,0.202369]},{"global_tokens":256,"samples_ms":[15.556826,0.20253,0.194881,0.193538,0.19357,0.193282,0.192481,0.192929,0.194689,0.194081,0.196642,0.194273,0.197986,0.192098,0.195266,0.196802,0.194178,0.194562,0.194593,0.194498,0.204034,0.19293,0.193633,0.19565,0.196833,0.197122,0.197186,0.19853,0.196129,0.196418,0.199682,0.196226,0.198946,0.199042,0.201281,0.19965,0.197794,0.19917,0.198977,0.201474,0.199809,0.19933,0.200962,0.201058,0.202689,0.202946,0.19933,0.20829,0.200418,0.200225,0.200834,0.198721,0.199554,0.202849,0.216578,0.198818,0.201697,0.20877,0.199298,0.199682,0.19949,0.19757,0.197665,0.198466,0.201122,0.202529,0.199778,0.204034,0.201825,0.201538,0.200514,0.19885,0.19997,0.20525,0.196706,0.199298,0.200098,0.20029,0.202722,0.198466,0.204642,0.203458,0.203233,0.205154,0.200033,0.201026,0.201058,0.20013,0.200257,0.197953,0.200962,0.20173,0.200578,0.201121,0.208322,0.199969,0.204386,0.202242,0.202593,0.202818]},{"global_tokens":512,"samples_ms":[17.795484,0.202432,0.194945,0.196353,0.203137,0.198657,0.206177,0.195905,0.195681,0.197377,0.199712,0.194561,0.198241,0.201729,0.197313,0.198785,0.197825,0.196289,0.197218,0.19629,0.198689,0.197217,0.196673,0.199649,0.200706,0.199393,0.194752,0.201825,0.198242,0.199329,0.199874,0.198946,0.203361,0.198561,0.210914,0.202209,0.201473,0.199906,0.201985,0.197378,0.200385,0.198849,0.201602,0.199009,0.200449,0.201953,0.204001,0.200865,0.198209,0.205185,0.199713,0.202082,0.203362,0.19933,0.201442,0.200898,0.198306,0.203682,0.200097,0.200897,0.199329,0.201601,0.199969,0.197473,0.198306,0.199553,0.203362,0.200866,0.198914,0.202785,0.200354,0.206913,0.20109,0.196257,0.199777,0.197922,0.196705,0.200001,0.19725,0.199041,0.197474,0.19677,0.20381,0.200001,0.202626,0.199938,0.203138,0.19853,0.198849,0.19677,0.19821,0.201249,0.253986,0.201761,0.200193,0.195906,0.197537,0.200194,0.203074,0.200065]},{"global_tokens":4096,"samples_ms":[45.791776,0.466723,0.456419,0.460835,0.463683,0.458531,0.465155,0.462083,0.466435,0.463971,0.465059,0.463075,0.471875,0.465475,0.489603,0.463619,0.470787,0.468387,0.467683,0.456195,0.470307,0.468932,0.476899,0.478755,0.471363,0.473475,0.468771,0.465571,0.470531,0.465698,0.475715,0.480227,0.470339,0.469891,0.474723,0.479075,0.477699,0.476227,0.469859,0.465059,0.470562,0.467075,0.465443,0.460579,0.470179,0.470339,0.471747,0.469635,0.469027,0.464451,0.472067,0.468323,0.465186,0.469795,0.473955,0.468419,0.468835,0.475683,0.470691,0.467747,0.477412,0.473283,0.469059,0.467907,0.467715,0.462626,0.471843,0.482947,0.47101,0.463907,0.466723,0.469475,0.467747,0.478339,0.474947,0.474371,0.469282,0.470723,0.479555,0.473379,0.466947,0.470499,0.466083,0.473827,0.470626,0.469059,0.477379,0.468994,0.475363,0.475907,0.475075,0.458147,0.47037,0.478723,0.483075,0.470626,0.483299,0.468483,0.463459,0.468995]},{"global_tokens":8192,"samples_ms":[16.308547,0.759847,0.754086,0.75911,0.760999,0.759718,0.761414,0.761605,0.758248,0.760872,0.776101,0.764901,0.767909,0.766503,0.761637,0.797351,0.765509,0.761989,0.768135,0.761032,0.767365,0.767431,0.765221,0.760167,0.761319,0.767397,0.769831,0.764423,0.761638,0.764613,0.756358,0.757478,0.790887,0.758791,0.761992,0.758151,0.763047,0.7602,0.753768,0.757481,0.766055,0.756453,0.7578,0.757831,0.762535,0.752904,0.765831,0.75652,0.799912,0.79223,0.777768,0.797702,0.787751,0.787461,0.791079,0.791655,0.807655,0.784233,0.787301,0.791207,0.789927,0.782856,0.785095,0.776647,0.775814,0.778502,0.794662,0.782758,0.783816,0.781798,0.783781,0.78887,0.788038,0.79335,0.801192,0.798311,0.79527,0.790921,0.796358,0.785193,0.801702,0.796486,0.791109,0.78996,0.805446,0.798182,0.809189,0.819718,0.80999,0.811429,0.824838,0.813829,0.816198,0.812006,0.819557,0.81479,0.817926,0.833349,0.816422,0.814821]},{"global_tokens":16384,"samples_ms":[34.604499,1.366348,1.368296,1.354092,1.355179,1.368553,1.359021,1.368266,1.3562,1.369961,1.358989,1.357836,1.363948,1.360653,1.367181,1.36209,1.367117,1.369034,1.365066,1.353324,1.36062,1.365515,1.364684,1.357448,1.374957,1.364969,1.495405,1.505996,1.508747,1.508556,1.500653,1.485963,1.489067,1.490794,1.492618,1.498026,1.483306,1.491531,1.483979,1.480651,1.499179,1.486826,1.487402,1.49265,1.518285,1.552877,1.556683,1.546061,1.561934,1.536461,1.555211,1.520461,1.540906,1.547179,1.53217,1.543627,1.531978,1.530251,1.538893,1.540875,1.527917,1.553518,1.566605,1.596875,1.611275,1.600172,1.593676,1.602091,1.600491,1.591435,1.602156,1.597099,1.598187,1.592267,1.603979,1.589419,1.601035,1.598379,1.601003,1.607019,1.595243,1.59758,1.581483,1.602219,1.594284,1.604811,1.608363,1.576619,1.554795,1.564107,1.559275,1.567211,1.566059,1.561994,1.565163,1.557131,1.567947,1.97787,1.568459,1.556842]}]
```

### dispatch-last/ep8

```json
[{"global_tokens":1,"samples_ms":[71.986533,0.078112,0.072737,0.070656,0.072768,0.069632,0.073216,0.074816,0.069664,0.071041,0.071489,0.072737,0.071649,0.072096,0.072577,0.07264,0.073536,0.071872,0.07392,0.073953,0.070784,0.073985,0.079937,0.075616,0.072832,0.074048,0.074112,0.074977,0.073889,0.074017,0.073601,0.075617,0.075425,0.075168,0.072704,0.075584,0.075041,0.080769,0.074465,0.075297,0.075488,0.077056,0.074304,0.074592,0.076769,0.076225,0.075457,0.076129,0.074976,0.073984,0.07424,0.07472,0.074273,0.073537,0.075168,0.076961,0.075969,0.077504,0.073376,0.076129,0.078753,0.078305,0.076449,0.080576,0.07968,0.077472,0.085024,0.077185,0.079585,0.079393,0.076448,0.080416,0.076385,0.078816,0.076513,0.075521,0.075617,0.079072,0.119841,0.086625,0.079937,0.078432,0.076864,0.07568,0.078625,0.074849,0.077793,0.076096,0.076448,0.07552,0.078464,0.078816,0.07616,0.079265,0.077409,0.098368,0.079936,0.077185,0.075809,0.078145]},{"global_tokens":2,"samples_ms":[32.750129,0.096961,0.092801,0.092001,0.090369,0.090113,0.091553,0.090305,0.091009,0.091041,0.091297,0.091809,0.089697,0.091553,0.090721,0.090881,0.090433,0.091234,0.099905,0.090497,0.091457,0.090337,0.092865,0.090465,0.092417,0.092001,0.092929,0.092033,0.090753,0.092929,0.095712,0.093025,0.093985,0.09469,0.134082,0.094113,0.093505,0.091138,0.09677,0.092577,0.094305,0.096097,0.096865,0.095105,0.094881,0.100673,0.094561,0.095489,0.096609,0.094721,0.097057,0.09709,0.096256,0.094753,0.094658,0.104992,0.096769,0.096225,0.097377,0.096737,0.096257,0.096705,0.096001,0.096161,0.097761,0.094113,0.098913,0.097473,0.097857,0.099233,0.10349,0.096705,0.098881,0.098241,0.101185,0.097634,0.099233,0.097377,0.097281,0.097633,0.099745,0.098881,0.096833,0.096353,0.097825,0.096032,0.098753,0.098529,0.095809,0.098305,0.098721,0.097248,0.098049,0.102913,0.098241,0.096482,0.097601,0.097696,0.095905,0.099393]},{"global_tokens":4,"samples_ms":[27.777028,0.103361,0.098881,0.096993,0.09904,0.097441,0.097825,0.104033,0.094304,0.098336,0.100833,0.096769,0.099201,0.095456,0.097665,0.097345,0.097217,0.096705,0.096609,0.096929,0.098113,0.097345,0.096832,0.097697,0.098017,0.097761,0.097377,0.094816,0.098593,0.098689,0.098401,0.099393,0.099777,0.09888,0.099008,0.098849,0.09952,0.100033,0.099938,0.1008,0.098561,0.102433,0.103649,0.101057,0.101825,0.101825,0.101985,0.103969,0.101249,0.102338,0.098401,0.098721,0.099905,0.103489,0.100962,0.102433,0.100545,0.101793,0.101089,0.101249,0.103297,0.104353,0.103681,0.101505,0.103841,0.100385,0.098881,0.098945,0.103105,0.104641,0.101793,0.103777,0.10384,0.10208,0.103105,0.102432,0.101569,0.103393,0.101985,0.102209,0.101889,0.100513,0.101313,0.102401,0.105921,0.104353,0.103969,0.102273,0.102241,0.101025,0.103489,0.106305,0.105761,0.104417,0.10576,0.102624,0.103425,0.10272,0.102017,0.103169]},{"global_tokens":8,"samples_ms":[32.928816,0.132769,0.121985,0.123298,0.135233,0.127233,0.124161,0.121922,0.124673,0.124833,0.128258,0.124544,0.128673,0.124513,0.12765,0.125633,0.123105,0.124385,0.126913,0.125985,0.124929,0.121634,0.123777,0.122273,0.127969,0.123617,0.129377,0.123905,0.127905,0.132161,0.123554,0.123361,0.127137,0.123297,0.125025,0.126754,0.127361,0.124898,0.127682,0.123682,0.132129,0.126401,0.135329,0.124257,0.124226,0.127649,0.127074,0.127649,0.124001,0.126946,0.128514,0.124194,0.125889,0.125473,0.127073,0.136129,0.124641,0.124354,0.131073,0.122209,0.123041,0.126561,0.125825,0.125089,0.127937,0.125729,0.122209,0.126881,0.126817,0.124641,0.127233,0.121954,0.122913,0.127169,0.125729,0.125377,0.126113,0.128609,0.130178,0.127425,0.124578,0.359715,0.133377,0.126497,0.132033,0.123489,0.125569,0.124385,0.124866,0.125281,0.121824,0.124033,0.121601,0.124226,0.126369,0.125025,0.123681,0.126625,0.124898,0.125345]},{"global_tokens":16,"samples_ms":[39.023059,0.141345,0.132129,0.131232,0.133921,0.13245,0.134592,0.129985,0.131904,0.137921,0.133281,0.130753,0.132737,0.129953,0.132129,0.1312,0.134786,0.132321,0.134593,0.134945,0.134945,0.131873,0.132993,0.132801,0.133249,0.134305,0.138753,0.131073,0.134658,0.135009,0.134497,0.134241,0.134978,0.131489,0.133729,0.132481,0.139393,0.137217,0.174786,0.132961,0.135169,0.133825,0.138048,0.134529,0.134465,0.142145,0.134177,0.134785,0.134305,0.132449,0.134721,0.134657,0.134209,0.132833,0.134177,0.133953,0.135329,0.138753,0.134273,0.133281,0.137217,0.137121,0.133153,0.132385,0.135905,0.135329,0.139298,0.137153,0.132737,0.134242,0.13293,0.131618,0.135681,0.134466,0.136354,0.130593,0.136897,0.137441,0.135714,0.134593,0.132961,0.137889,0.142241,0.134626,0.134241,0.130721,0.135233,0.137441,0.138978,0.135873,0.136097,0.136417,0.136002,0.133409,0.135905,0.133409,0.136609,0.131841,0.134657,0.132801]},{"global_tokens":32,"samples_ms":[33.722105,0.16765,0.164578,0.16445,0.16269,0.163809,0.164449,0.162594,0.163585,0.161729,0.163265,0.161122,0.166273,0.164737,0.166113,0.165121,0.160289,0.164929,0.164289,0.163073,0.165793,0.168033,0.166753,0.165281,0.162721,0.167009,0.165313,0.168833,0.167969,0.167873,0.166753,0.167106,0.165601,0.173601,0.166113,0.163105,0.167201,0.167745,0.167073,0.167809,0.167265,0.168577,0.166497,0.167201,0.168129,0.168833,0.167426,0.163905,0.164609,0.164257,0.173761,0.168257,0.166561,0.165825,0.165153,0.167809,0.164513,0.167009,0.165665,0.163777,0.167233,0.165313,0.163201,0.168033,0.163489,0.174145,0.164353,0.164193,0.165217,0.164929,0.169153,0.162945,0.166946,0.164866,0.161954,0.163682,0.164866,0.164961,0.163617,0.164769,0.172417,0.16317,0.165538,0.165921,0.16925,0.167297,0.166882,0.167265,0.163586,0.165121,0.163841,0.166434,0.164834,0.165026,0.166401,0.165697,0.164257,0.166689,0.165826,0.167617]},{"global_tokens":64,"samples_ms":[45.428227,0.192289,0.188225,0.18749,0.190018,0.188481,0.188545,0.187137,0.18765,0.183266,0.18813,0.187585,0.187585,0.186305,0.188514,0.18781,0.188097,0.187841,0.192834,0.186658,0.188705,0.187361,0.187137,0.188385,0.188194,0.186881,0.188897,0.189313,0.19261,0.189281,0.185825,0.190433,0.188226,0.189922,0.187201,0.189217,0.186946,0.19181,0.189569,0.189281,0.188545,0.192162,0.188962,0.189985,0.188002,0.19101,0.188417,0.188865,0.189058,0.188962,0.190817,0.189249,0.19165,0.18829,0.190402,0.191777,0.187234,0.192865,0.190945,0.19325,0.191266,0.189985,0.194497,0.192161,0.193346,0.190049,0.189601,0.191298,0.190241,0.192129,0.193633,0.192642,0.192866,0.198657,0.192034,0.195138,0.193441,0.191425,0.193281,0.195554,0.191233,0.192066,0.192194,0.193218,0.192321,0.194305,0.194306,0.194561,0.191105,0.191394,0.192833,0.190018,0.191265,0.191586,0.193794,0.190369,0.193634,0.191202,0.190721,0.192481]},{"global_tokens":128,"samples_ms":[30.06688,0.196226,0.190242,0.193442,0.190913,0.190849,0.19117,0.19197,0.190497,0.19133,0.191681,0.191777,0.192225,0.191522,0.190882,0.190785,0.189313,0.192802,0.188897,0.187841,0.190274,0.191105,0.189922,0.188929,0.19133,0.191841,0.185602,0.193986,0.194305,0.191746,0.188994,0.192355,0.191745,0.190818,0.193794,0.193537,0.192514,0.193922,0.194465,0.194178,0.195586,0.190401,0.188834,0.191617,0.192513,0.19517,0.192802,0.194049,0.194241,0.193537,0.196833,0.193985,0.196193,0.194913,0.192354,0.196546,0.195073,0.19101,0.196161,0.190915,0.193666,0.192322,0.192129,0.192386,0.191874,0.192129,0.193857,0.195298,0.194657,0.19357,0.192386,0.192226,0.193826,0.193538,0.193921,0.19309,0.194401,0.193921,0.193698,0.192834,0.192353,0.194018,0.194209,0.19389,0.189826,0.194305,0.193953,0.193602,0.193122,0.192257,0.192354,0.191169,0.193345,0.190658,0.194754,0.19341,0.193442,0.202882,0.192898,0.195394]},{"global_tokens":256,"samples_ms":[33.672134,0.194337,0.193379,0.196162,0.194882,0.198434,0.192738,0.191202,0.194755,0.195938,0.195267,0.194497,0.195235,0.194594,0.196322,0.193634,0.193698,0.194851,0.197314,0.19453,0.194306,0.195074,0.196418,0.192706,0.197474,0.19629,0.19677,0.198434,0.197314,0.209602,0.19565,0.196866,0.197698,0.196898,0.19853,0.199906,0.199458,0.20141,0.19789,0.198146,0.197826,0.200098,0.199298,0.19741,0.198306,0.19933,0.198305,0.201761,0.196738,0.199138,0.198914,0.197187,0.197858,0.199682,0.198306,0.199426,0.198466,0.198818,0.198274,0.200002,0.207201,0.199714,0.196482,0.199074,0.197346,0.199875,0.198018,0.199267,0.201346,0.200386,0.196322,0.196706,0.199042,0.197922,0.20045,0.199106,0.200738,0.204513,0.197666,0.198754,0.205762,0.201218,0.201858,0.20061,0.201283,0.202083,0.198242,0.198179,0.201442,0.201026,0.200002,0.201666,0.199074,0.210818,0.19885,0.199971,0.202178,0.202179,0.20061,0.199042]},{"global_tokens":512,"samples_ms":[56.812779,0.196161,0.193474,0.195203,0.197826,0.194818,0.195682,0.195425,0.195586,0.195266,0.196418,0.197633,0.192482,0.197346,0.201762,0.19613,0.196642,0.198338,0.196386,0.196194,0.198018,0.19805,0.194658,0.199938,0.19933,0.198849,0.195074,0.194562,0.198882,0.197857,0.200194,0.199394,0.201762,0.200226,0.200706,0.19773,0.19901,0.19933,0.201346,0.198658,0.198914,0.199363,0.200866,0.198242,0.203074,0.200482,0.20141,0.201347,0.201154,0.20061,0.203938,0.199298,0.200194,0.200354,0.197314,0.200962,0.198818,0.19821,0.200546,0.199745,0.202978,0.201826,0.207394,0.200578,0.204898,0.202114,0.200674,0.199363,0.202402,0.19821,0.20141,0.200706,0.199202,0.199041,0.201794,0.199585,0.204194,0.201218,0.200514,0.198978,0.201507,0.202306,0.203969,0.20061,0.201186,0.19773,0.202338,0.201122,0.199586,0.199234,0.200258,0.199138,0.201794,0.200834,0.19997,0.207746,0.19613,0.19853,0.208482,0.198306]},{"global_tokens":4096,"samples_ms":[25.432587,0.476931,0.4665,0.469891,0.46522,0.470116,0.470404,0.469636,0.46874,0.469188,0.475236,0.465571,0.491396,0.471396,0.4793,0.472771,0.47098,0.471299,0.465956,0.472292,0.47098,0.471139,0.46106,0.472003,0.473444,0.477635,0.471876,0.468612,0.471364,0.469572,0.477348,0.468803,0.476227,0.47498,0.476483,0.468292,0.480707,0.470756,0.468611,0.476228,0.480803,0.469796,0.4793,0.47306,0.468259,0.472515,0.471172,0.472867,0.4753,0.466627,0.488196,0.476867,0.474436,0.464707,0.469412,0.473604,0.47578,0.480228,0.473316,0.46506,0.508708,0.476868,0.461923,0.474244,0.477028,0.478628,0.470916,0.479203,0.473956,0.475525,0.4753,0.481636,0.481252,0.474948,0.473219,0.481348,0.485059,0.484516,0.474052,0.478243,0.48474,0.475684,0.47594,0.475428,0.481284,0.486756,0.479363,0.474532,0.469763,0.475972,0.48282,0.473188,0.475204,0.487236,0.480932,0.482531,0.478019,0.47946,0.471875,0.477764]},{"global_tokens":8192,"samples_ms":[43.000732,0.789162,0.779913,0.782794,0.774505,0.795432,0.780777,0.809482,0.786185,0.775657,0.774089,0.784201,0.777705,0.782249,0.778857,0.777161,0.779018,0.781673,0.770537,0.790056,0.782249,0.773065,0.772233,0.777577,0.776426,0.782217,0.79233,0.767593,0.791434,0.773289,0.776393,0.758089,0.766729,0.77185,0.779049,0.771272,0.769001,0.774569,0.793705,0.76817,0.774025,0.769545,0.766376,0.781961,0.776297,0.785065,0.788201,0.787689,0.786058,0.782857,0.78465,0.781737,0.782729,0.773385,0.775306,0.773161,0.786378,0.781513,0.800074,0.781002,0.793961,0.817929,0.80769,0.816362,0.815466,0.82241,0.812073,0.826793,0.809801,0.813738,0.822601,0.811049,0.811018,0.816458,0.817002,0.81985,0.814666,0.830826,0.81409,0.837831,0.828361,0.82769,0.821066,0.811786,0.819145,0.828074,0.813194,0.820521,0.820714,0.834954,0.824746,0.81665,0.823274,0.821322,0.821482,0.82817,0.815978,0.820906,0.817609,0.823498]},{"global_tokens":16384,"samples_ms":[53.566674,1.372967,1.365193,1.363817,1.357293,1.368937,1.3506,1.359437,1.366413,1.369898,1.37153,1.365322,1.379886,1.364109,1.364938,1.365705,1.362857,1.385166,1.379691,1.370349,1.366573,1.36177,1.378381,1.373514,1.376813,1.373418,1.404714,1.421518,1.438894,1.44699,1.432746,1.507946,1.492713,1.509419,1.494641,1.486859,1.499403,1.4947,1.498411,1.505227,1.501424,1.499755,1.490347,1.489259,1.494059,1.490827,1.530443,1.493451,1.498667,1.501067,1.512269,1.514155,1.503404,1.505868,1.514731,1.517486,1.515695,1.508459,1.503692,1.492943,1.512236,1.537227,1.543563,1.526316,1.518417,1.536875,1.521868,1.536491,1.518475,1.52462,1.531244,1.527467,1.528913,1.526956,1.526097,1.533004,1.52222,1.529164,1.517681,1.513137,1.503051,1.53774,1.564977,1.55646,1.560465,1.653293,1.558955,1.566988,1.549106,1.537452,1.546545,1.539915,1.53902,1.531726,1.556844,1.528203,1.549169,1.561837,1.54312,1.551628]}]
```

### local-pool-last/ep8

```json
[{"global_tokens":1,"samples_ms":[25.759579,0.065537,0.066817,0.066017,0.064608,0.070976,0.065536,0.064864,0.064001,0.063745,0.063744,0.06288,0.064384,0.073248,0.070272,0.066369,0.064193,0.066113,0.066336,0.065632,0.067329,0.066721,0.065537,0.068737,0.066817,0.066049,0.067424,0.068993,0.067969,0.065505,0.068353,0.065921,0.067424,0.069121,0.068705,0.068385,0.068992,0.071521,0.069441,0.070753,0.075937,0.069536,0.069281,0.068576,0.068353,0.068736,0.067201,0.068897,0.069313,0.070529,0.065985,0.068864,0.068288,0.067265,0.072449,0.068449,0.072257,0.07136,0.072993,0.069888,0.070048,0.070433,0.070816,0.070977,0.068896,0.06976,0.070689,0.069216,0.069312,0.070976,0.072512,0.070113,0.071232,0.069408,0.067936,0.068385,0.069889,0.069825,0.072193,0.068448,0.070113,0.0824,0.068321,0.068769,0.068865,0.069217,0.069089,0.07296,0.070305,0.067905,0.069248,0.071361,0.077985,0.069056,0.069985,0.069024,0.068545,0.068353,0.068865,0.068961]},{"global_tokens":2,"samples_ms":[20.340665,0.090497,0.088865,0.089024,0.090561,0.089601,0.089249,0.08992,0.08832,0.320675,0.086209,0.089984,0.088257,0.087553,0.089889,0.089793,0.090881,0.092097,0.091328,0.093088,0.091233,0.090112,0.094336,0.092513,0.092544,0.092,0.092641,0.091744,0.08912,0.089761,0.090241,0.090144,0.091265,0.093537,0.093024,0.097921,0.091201,0.090625,0.09232,0.091585,0.090849,0.094753,0.094817,0.09008,0.09344,0.093729,0.093792,0.089217,0.091169,0.093857,0.095425,0.093345,0.095488,0.096224,0.095041,0.097793,0.094657,0.095649,0.094592,0.095681,0.096481,0.088128,0.093697,0.094817,0.091392,0.092609,0.093888,0.093985,0.091457,0.095456,0.09232,0.092993,0.092864,0.094273,0.093281,0.093632,0.093217,0.094337,0.094305,0.094337,0.096608,0.09488,0.093057,0.09392,0.091424,0.092929,0.0936,0.103041,0.092033,0.090528,0.089761,0.093633,0.095073,0.093632,0.092193,0.09184,0.093601,0.094241,0.095488,0.093121]},{"global_tokens":4,"samples_ms":[40.219368,0.102144,0.101249,0.102112,0.103714,0.104801,0.105249,0.102945,0.105217,0.104353,0.102689,0.104865,0.103169,0.103936,0.107234,0.102497,0.106465,0.105729,0.105569,0.10496,0.106305,0.106497,0.109217,0.106432,0.106465,0.106561,0.104993,0.107297,0.105217,0.106464,0.106785,0.1064,0.111105,0.106657,0.115712,0.108289,0.107297,0.110912,0.107425,0.109281,0.105761,0.108257,0.10864,0.105856,0.107809,0.10656,0.105409,0.108097,0.10736,0.107521,0.10685,0.106081,0.108385,0.108576,0.105857,0.108417,0.104801,0.102624,0.103905,0.109217,0.10768,0.105377,0.107009,0.106913,0.108418,0.104896,0.108385,0.106017,0.108001,0.108993,0.107809,0.106114,0.104256,0.104993,0.106177,0.106145,0.106209,0.107553,0.109633,0.106784,0.105473,0.104097,0.105889,0.108193,0.107745,0.106753,0.108225,0.108961,0.108033,0.108513,0.109601,0.104193,0.105665,0.107777,0.107136,0.107841,0.106689,0.109409,0.107712,0.108738]},{"global_tokens":8,"samples_ms":[28.125113,0.130914,0.122465,0.13981,0.123105,0.122082,0.124609,0.123426,0.121473,0.125442,0.122241,0.123362,0.135297,0.122786,0.121793,0.121793,0.12493,0.122593,0.123714,0.123906,0.124322,0.122241,0.124002,0.123777,0.128002,0.127137,0.123746,0.12973,0.125793,0.124706,0.127298,0.126881,0.126689,0.12781,0.126786,0.125282,0.125633,0.128257,0.128769,0.127265,0.128865,0.126626,0.128193,0.126402,0.129697,0.127489,0.131138,0.129185,0.129954,0.129857,0.130754,0.128321,0.130369,0.125858,0.129282,0.127586,0.129697,0.127874,0.127169,0.128033,0.129473,0.131713,0.131074,0.130657,0.132802,0.133057,0.129345,0.12749,0.131329,0.13197,0.129442,0.131489,0.131522,0.131105,0.127938,0.140738,0.130849,0.129153,0.129378,0.13229,0.134914,0.132545,0.132001,0.13053,0.128801,0.129346,0.132385,0.13053,0.130018,0.130625,0.13053,0.128513,0.141154,0.132737,0.130849,0.131617,0.133698,0.133281,0.133058,0.130401]},{"global_tokens":16,"samples_ms":[30.464099,0.142305,0.140257,0.136866,0.139266,0.138273,0.137985,0.137473,0.140321,0.139074,0.140578,0.138209,0.141089,0.139969,0.141634,0.142113,0.142305,0.139649,0.139521,0.140994,0.139394,0.14157,0.143521,0.140897,0.14237,0.140322,0.173025,0.14253,0.142913,0.136769,0.142209,0.140866,0.142274,0.142626,0.146593,0.151745,0.143778,0.140481,0.143457,0.141665,0.145954,0.144257,0.144929,0.142913,0.145121,0.143297,0.144769,0.143234,0.145186,0.144737,0.146753,0.146818,0.143938,0.143553,0.14541,0.143713,0.147105,0.144513,0.145666,0.144801,0.144929,0.144609,0.145442,0.157474,0.146593,0.147074,0.147426,0.143969,0.146177,0.142626,0.147745,0.152865,0.147426,0.148865,0.148001,0.147617,0.145698,0.146178,0.145153,0.147618,0.147842,0.146977,0.148193,0.151362,0.150753,0.145601,0.149313,0.148098,0.148257,0.149506,0.147489,0.149185,0.147393,0.148482,0.147458,0.150369,0.147681,0.14925,0.142817,0.147713]},{"global_tokens":32,"samples_ms":[62.242818,0.168386,0.168577,0.166978,0.165185,0.166658,0.164769,0.165761,0.165602,0.167586,0.168578,0.166146,0.170306,0.166689,0.174625,0.163649,0.166082,0.166306,0.171873,0.166593,0.166338,0.169538,0.177345,0.168194,0.170177,0.167841,0.168481,0.169505,0.168801,0.170465,0.171649,0.169313,0.169441,0.169217,0.17005,0.169954,0.17085,0.204769,0.169313,0.169249,0.171586,0.169761,0.172738,0.171553,0.189762,0.170146,0.17197,0.172482,0.179617,0.171234,0.17069,0.172065,0.172513,0.172162,0.176674,0.173474,0.17117,0.17197,0.17549,0.174465,0.174209,0.176226,0.17325,0.172162,0.173986,0.17373,0.173154,0.173826,0.172642,0.173762,0.170306,0.173922,0.172418,0.17277,0.176386,0.171105,0.172417,0.170369,0.17165,0.17117,0.172578,0.180545,0.172194,0.173602,0.17405,0.173123,0.174978,0.172034,0.17357,0.170466,0.173442,0.174145,0.174305,0.173025,0.173634,0.17709,0.171073,0.170657,0.173858,0.17341]},{"global_tokens":64,"samples_ms":[36.198381,0.200674,0.188258,0.182338,0.192417,0.185986,0.189249,0.186465,0.19517,0.189218,0.18861,0.19085,0.189474,0.188929,0.190562,0.196578,0.190497,0.189089,0.187713,0.188833,0.191393,0.191681,0.187745,0.189921,0.191074,0.192033,0.19085,0.192354,0.18781,0.191394,0.19069,0.187202,0.194177,0.193921,0.190497,0.190593,0.191105,0.193633,0.192801,0.191201,0.190369,0.191873,0.188642,0.198946,0.193282,0.192386,0.192482,0.193634,0.190337,0.189857,0.194017,0.189441,0.194145,0.253059,0.194561,0.189889,0.190657,0.191841,0.192577,0.192737,0.192321,0.192449,0.193506,0.203554,0.19373,0.190817,0.189217,0.193569,0.194241,0.192577,0.192961,0.193473,0.189153,0.193345,0.191329,0.19117,0.19213,0.194978,0.193921,0.19261,0.193121,0.195297,0.192257,0.192321,0.190625,0.191105,0.191553,0.193377,0.190594,0.193922,0.192642,0.191938,0.192066,0.191458,0.193697,0.191617,0.191585,0.190945,0.192545,0.192801]},{"global_tokens":128,"samples_ms":[48.119704,0.207715,0.184385,0.186785,0.18573,0.18749,0.186018,0.186562,0.186178,0.185954,0.187617,0.186114,0.18781,0.18781,0.186689,0.188961,0.189186,0.189218,0.189794,0.186146,0.188386,0.18829,0.187714,0.552934,0.188834,0.190721,0.192642,0.190337,0.191298,0.192866,0.192865,0.19117,0.19325,0.191969,0.191489,0.193122,0.193825,0.190497,0.193409,0.20285,0.194082,0.194626,0.193825,0.193634,0.194498,0.198082,0.194594,0.194786,0.194369,0.194946,0.195266,0.195073,0.19437,0.192354,0.192642,0.194242,0.194114,0.19613,0.193986,0.192994,0.192802,0.19213,0.19245,0.195521,0.192802,0.18717,0.193762,0.194049,0.193026,0.194433,0.195907,0.197314,0.193826,0.195746,0.195522,0.196099,0.195073,0.193315,0.193473,0.197346,0.197377,0.196707,0.192449,0.19645,0.19773,0.194017,0.194978,0.196034,0.192962,0.196866,0.19629,0.194178,0.194338,0.21629,0.194274,0.20717,0.195361,0.196354,0.195585,0.192993]},{"global_tokens":256,"samples_ms":[35.113352,0.196803,0.192897,0.195523,0.197473,0.191618,0.191458,0.192578,0.195073,0.203618,0.191106,0.194657,0.193122,0.195138,0.191874,0.193538,0.194658,0.193443,0.192514,0.193633,0.194018,0.193409,0.194594,0.192706,0.194882,0.195202,0.19437,0.194146,0.194114,0.19453,0.193057,0.194339,0.197026,0.195969,0.194337,0.194626,0.193666,0.193538,0.195361,0.194306,0.197314,0.19533,0.194529,0.193826,0.194881,0.19133,0.190626,0.197282,0.194177,0.194722,0.196481,0.195298,0.194755,0.197186,0.196674,0.19965,0.194785,0.194978,0.196546,0.197282,0.195714,0.196546,0.194786,0.194818,0.196546,0.197602,0.196642,0.195746,0.195553,0.197506,0.19453,0.195266,0.194625,0.195138,0.196737,0.196866,0.195362,0.198402,0.195714,0.195522,0.194082,0.195553,0.196546,0.197505,0.19517,0.194753,0.189474,0.206146,0.196706,0.196034,0.193986,0.195905,0.197314,0.19341,0.198497,0.19533,0.198402,0.195298,0.19517,0.193794]},{"global_tokens":512,"samples_ms":[12.487218,0.192034,0.190946,0.190786,0.191938,0.19101,0.190914,0.193922,0.190882,0.191683,0.193473,0.19181,0.193601,0.194818,0.19549,0.192642,0.194306,0.195042,0.192386,0.198018,0.19565,0.193794,0.19517,0.195489,0.19389,0.194498,0.195074,0.196418,0.195458,0.199042,0.19741,0.198305,0.196194,0.196833,0.19677,0.200866,0.196417,0.195682,0.199777,0.195714,0.19773,0.197314,0.19549,0.200258,0.197025,0.199137,0.197474,0.198082,0.197378,0.19821,0.199203,0.199746,0.198017,0.199554,0.198689,0.197634,0.197922,0.201635,0.197218,0.200418,0.20205,0.198307,0.198242,0.199778,0.197858,0.198914,0.202242,0.197186,0.20237,0.200706,0.200066,0.201954,0.205571,0.198882,0.202466,0.203266,0.20173,0.200706,0.202306,0.196482,0.200738,0.199267,0.199843,0.20429,0.201346,0.19981,0.200417,0.199042,0.200354,0.200674,0.19549,0.19981,0.197666,0.199777,0.201826,0.199362,0.199906,0.199713,0.198402,0.200258]},{"global_tokens":4096,"samples_ms":[30.599907,0.476196,0.474405,0.464068,0.474597,0.475109,0.467845,0.473156,0.463044,0.470149,0.475268,0.47674,0.469157,0.482213,0.477221,0.476901,0.470181,0.476293,0.474245,0.474757,0.47866,0.480773,0.473413,0.475653,0.485638,0.472485,0.464357,0.476677,0.471908,0.468261,0.465957,0.481061,0.469861,0.469829,0.470853,0.477669,0.483237,0.471109,0.471013,0.477541,0.475908,0.472293,0.482373,0.485349,0.476421,0.471045,0.475813,0.473733,0.477413,0.476612,0.486757,0.4649,0.474853,0.470565,0.470181,0.472933,0.471589,0.470725,0.475205,0.469605,0.468229,0.472677,0.488549,0.479524,0.474597,0.479941,0.475397,0.472358,0.475204,0.476485,0.475717,0.475748,0.473348,0.478917,0.481989,0.478981,0.485957,0.476069,0.487461,0.473029,0.474981,0.474725,0.476228,0.466853,0.478469,0.477125,0.473574,0.477381,0.481413,0.469893,0.480005,0.485541,0.475397,0.473829,0.477157,0.471173,0.486021,0.477445,0.480581,0.467525]},{"global_tokens":8192,"samples_ms":[35.724292,0.778438,0.76791,0.771749,0.761061,0.771014,0.773829,0.775718,0.767109,0.773318,0.765031,0.765605,0.770757,0.773574,0.780357,0.781478,0.763368,0.771557,0.768422,0.782437,0.77271,0.76855,0.777157,0.77207,0.783462,0.776806,0.772261,0.775845,0.772134,0.771429,0.768965,0.780646,0.772997,0.772102,0.767974,0.776583,0.771366,0.776005,0.77844,0.773029,0.760646,0.792198,0.787046,0.799462,0.799622,0.793221,0.793958,0.786693,0.795526,0.809478,0.802118,0.798117,0.795174,0.797094,0.810949,0.81527,0.816134,0.806599,0.814438,0.804648,0.822822,0.816742,0.81319,0.818694,0.816262,0.823974,0.808326,0.815366,0.821862,0.827942,0.827942,0.811366,0.818534,0.817638,0.81703,0.814153,0.811206,0.824198,0.822088,0.817062,0.825574,0.81015,0.816805,0.806246,0.823526,0.808517,0.80775,0.81255,0.806982,0.810184,0.806854,0.805062,0.800904,0.817094,0.81799,1.122888,0.831878,0.811718,0.812198,0.835782]},{"global_tokens":16384,"samples_ms":[41.806516,1.370473,1.370897,1.371792,1.37032,1.380112,1.37368,1.380784,1.382192,1.38696,1.381489,1.380976,1.379056,1.38744,1.389777,1.37544,1.38824,1.389264,1.379568,1.37864,1.377584,1.376624,1.382992,1.3908,1.382704,1.388913,1.456177,1.460721,1.450576,1.458801,1.474866,1.478321,1.471569,1.475025,1.506994,1.512272,1.518834,1.51144,1.496978,1.510578,1.51557,1.507666,1.510866,1.506642,1.507442,1.515922,1.509138,1.501874,1.512754,1.510802,1.509906,1.517682,1.511569,1.524018,1.52549,1.523186,1.537138,1.514226,1.536658,1.505778,1.50869,1.518161,1.513969,1.509714,1.525714,1.51045,1.506578,1.522962,1.515762,1.515122,1.50933,1.52693,1.507857,1.515794,1.515123,1.506161,1.518129,1.511602,1.517202,1.52661,1.54261,1.528433,1.518161,1.541266,1.531826,1.554994,1.576402,1.582866,1.596083,1.591155,1.590962,1.589554,1.589843,1.595251,1.583123,1.601683,1.594962,1.599187,1.594194,1.610515]}]
```
