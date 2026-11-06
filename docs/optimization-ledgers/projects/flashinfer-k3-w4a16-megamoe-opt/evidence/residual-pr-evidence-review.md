# Residual-prefix evidence review for the final PR

Local review only. No source, PR body, README, benchmark or GPU changes. N32 remains a separate pending screen; the cancelled four-decoder experiment has no retention result.

## Main finding

The saved residual-prefix screen is **1.015400× versus BEFORE** and **1.018291× versus the native-tanh intermediate**, using the unweighted geometric mean of the 11 retained pointwise median ratios. This is +1.54% / +1.83% speedup, not an arithmetic mean or a claim about full-model throughput. T1/T2 are reported but excluded; T512 is included.
The 13-point report is ready: its medians match all original raw rank-MAX samples, the original and intermediate controls each have one fresh eight-rank AUTO run, and residual has one fixed-winner run with 100 untrimmed samples per point. The residual source differs from native only in the scheduler; all eight ranks retained the exact native winner. Across the11 retention points the BEFORE and native AUTO winners also agree; their only tactic differences are group_hint at excluded T1/T2.

## Honest interpretation

- Residual is 0.12% slower than BEFORE at T64 (322.195 vs321.811µs); do not say it wins every point against BEFORE.
- Residual medians are lower at all11 retained points against native, but T128/T512 improve only≈0.03%, and T64/T256≈0.2–0.3%. Treat these as effectively flat, not individually established speedups.
- The larger native-relative changes are T4≈5.79%, T16≈3.59%, T4096≈3.66% and T8192≈3.00%. Keep the complete table. Dense-point interquartile spreads are several percent, so one run per arm supports a modest measured gain, not a confidence claim or repeatability proof.
- Keep the earlier controls separate; do not replace these medians with the best historical T32 result or pool AUTO and fixed-winner policies. No new baseline is needed to publish the existing evidence.
- Native tanh alone was flat/slightly slower across the full retained set. The combined BEFORE→residual result does not establish that native tanh itself accelerated decode.
- Retention is an engineering decision supported by the measured modest gain and the exact gate; the report deliberately imposes no extra process-count threshold.

## Complete pointwise medians

| Global tokens | Retention | BEFORE AUTO µs | Native AUTO µs | Residual fixed µs | Residual / BEFORE speedup | Residual / native speedup |
|---:|:---:|---:|---:|---:|---:|---:|
| 1 | no | 84.1930 | 84.9770 | 81.6650 | 1.03096× | 1.04056× |
| 2 | no | 97.7445 | 93.8885 | 97.9370 | 0.99803× | 0.95866× |
| 4 | yes | 108.1610 | 113.7610 | 107.5370 | 1.00580× | 1.05788× |
| 8 | yes | 137.8255 | 136.7220 | 134.2410 | 1.02670× | 1.01848× |
| 16 | yes | 160.0815 | 158.3220 | 152.8335 | 1.04742× | 1.03591× |
| 32 | yes | 238.0665 | 235.4425 | 232.5145 | 1.02388× | 1.01259× |
| 64 | yes | 321.8110 | 323.1070 | 322.1950 | 0.99881× | 1.00283× |
| 128 | yes | 377.0445 | 376.1320 | 376.0195 | 1.00273× | 1.00030× |
| 256 | yes | 400.7560 | 400.8210 | 399.9715 | 1.00196× | 1.00212× |
| 512 | yes | 415.9410 | 411.9095 | 411.7795 | 1.01011× | 1.00032× |
| 4096 | yes | 593.6060 | 601.4455 | 580.1980 | 1.02311× | 1.03662× |
| 8192 | yes | 1069.0370 | 1086.7950 | 1055.1945 | 1.01312× | 1.02995× |
| 16384 | yes | 2089.7810 | 2067.6530 | 2055.3530 | 1.01675× | 1.00598× |

Speedup = comparator median / residual median. One process group per arm,100 samples at each point; no averaging of medians.

## Scope and numerical gate

Proposed concise scope wording: “Reuse the scheduler’s accumulated FC1 tile prefix to reconstruct group-boundary cursors, avoiding a redundant residual-expert walk when padding equals the token tile. Preserve the original fallback and all activation/decoder arithmetic.”
The optimization is a scheduler identity, not an activation approximation change. Its support condition is equal token padding/tile and positive static FC1 feature-block count; the old loop remains otherwise. Decoder groups, warp partition, register roles, deterministic combine and PDL/reduction controls are unchanged.
The focused exact gate **passed**: four logical parameter cases on EP2, four passes per rank, zero skips, existing `assert_w4a16_bits`, source unchanged. Cases cover N64/N128×static/atomic scheduling and existing uneven/skewed/empty/refill rounds. This is additional bounded scheduler qualification; do not present it as an EP8 released-K3 checkpoint test.

If residual is retained, the existing PR scope sentence “No ... scheduler changes are retained” is stale and must be rewritten. Keep the native-tanh instruction-oracle update separately described: the residual change does not require a reference or tolerance relaxation. The draft remains an experiment until the owner finishes N32 selection and rewrites the final implementation scope.

## Exact local evidence paths

- Full table/quartiles/tactics/raw contributions: `evidence/progressive-residual-v1.md` and `.json`.
- BEFORE: `runs/full-base-v2/{raw-records.json,run.json,summary.json,sweep-1.log,command.json,source-before.patch,source-manifest.json}`.
- Intermediate: same filenames in `runs/full-native-v2/`.
- Residual: same filenames plus `recorded-tactics.json` in `runs/residual-prefix-v1/`.
- Map/source transition: `queues/residual-prefix-v1/{recorded-tactics.json,source-change.json,exit.json}`.
- Exact gate: `correctness/residual-exact-v1/{exit.json,source-identity.json,source-tested.json,source-tested.patch}` and `ep2/{validation.json,test.log,command.json,junit/rank-0.xml,junit/rank-1.xml}`.
- Complete exact receipts archive: `evidence/residual-exact-v1-receipts.tar.gz`. The earlier `residual-exact-v1-truncated-transfer.tar.gz` is a retained failed transfer, not the authoritative archive.
- Performance source base is `a7103ae2a97f38f4dbbf410c32acc7c6fe99cab1` plus each saved patch; source commit alone does not identify these arms. Native epilogue SHA `8b4bf3915d0eb26fe8dca7d57bc11df218eeca3e6270e10c3d3cb12510bfa809`; residual scheduler SHA `01f0e21f395e3418e8d2bc27b6b75a48b4576e206aafa421344384102cafacd8`.

| Arm | Raw-records SHA256 | Full-source-patch SHA256 |
|---|---|---|
| full-base-v2 | `a281013f863f9f433d75cf038cbefc91533cb899550f877dd7ba2dd7cf587906` | `00849464f14439a3e02d654f31500cd2354422baaf996fc3e075eae3ace01b15` |
| full-native-v2 | `cbec32216abb87994c7586d24ece05a591adbc91c7c57b206ff3ff42ff28de10` | `9a8a972b5839c86a5ead2a592cd4d769dd11018f9fc76e6cfffa975c0bb569ae` |
| residual-prefix-v1 | `9bfb8c885a5bbd987eda3b4867c49c0c57aecf392a2fc82889d9db918da25e6b` | `db9b1714872c36b53a20bcfe43b71f69e377cb087dd44c3305ce3c2285c02f01` |

## Commands to preserve in PR evidence

These are the actual measured invocations, not requests to rerun them. Their environment is frozen in each run.json; container `nvcr.io/nvidia/pytorch:26.05-py3`, EP8 B300, CUDA13.2.1, Torch2.12.0a0+5aff3928d8.nv26.5.50603568, CuTe4.7.1, CUDA Python/bindings/CUPTI Python13.2.0, CUPTI13.2.86, NVSHMEM3.6.5/nvshmem4py0.3.1.

AUTO controls (same command, different saved source patch):
```sh
torchrun --master-addr=127.0.0.1 --master-port=29671 --nproc-per-node=8 /data/home/ziangli/flashinfer-k3-w4a16-megamoe-opt/flashinfer/benchmarks/bench_cute_dsl_moe_distributed.py --model kimi-k3 --mode benchmark --parallel-modes ep --num-gpus 8 --variants w4a16_megamoe --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --timing cupti --cuda-graph --precomputed-routing --no-fused-finalize --warmup 3 --iters 100 --log-timing-samples --megamoe-knobs auto
```

Residual uses the unchanged native benchmark through the fixed-map adapter. The `{}` CLI value is a bootstrap placeholder; the verified per-token map is the effective configuration. Do not relabel this command as an AUTO run. An independently reproducible public PR needs the frozen adapter/map alongside this command, or an explicitly distinguished reproduction procedure.
```sh
export K3_SOURCE_DIR=/data/home/ziangli/flashinfer-k3-w4a16-megamoe-opt/flashinfer
export K3_RECORDED_TACTICS=/data/home/ziangli/flashinfer-k3-w4a16-megamoe-opt/queues/residual-prefix-v1/recorded-tactics.json
torchrun --master-addr=127.0.0.1 --master-port=29671 --nproc-per-node=8 /data/home/ziangli/flashinfer-k3-w4a16-megamoe-opt/next-residual-prefix-v1/harness/native_entry.py --model kimi-k3 --mode benchmark --parallel-modes ep --num-gpus 8 --variants w4a16_megamoe --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --timing cupti --cuda-graph --precomputed-routing --no-fused-finalize --warmup 3 --iters 100 --log-timing-samples --megamoe-knobs '{}'
```

Focused exact command (full env and wrapper are retained with receipts):
```sh
/usr/bin/python3 -m torch.distributed.run --master-addr=127.0.0.1 --master-port=29681 --nproc-per-node=2 /data/home/ziangli/flashinfer-k3-w4a16-megamoe-opt/next-residual-exact-v1/helpers/pytest_entry.py --junit-dir /data/home/ziangli/flashinfer-k3-w4a16-megamoe-opt/correctness/residual-exact-v1/ep2/junit -- tests/moe_ep/test_moe_ep_nvfp4_cutedsl_mega_multirank.py::test_nvfp4_mega_uneven_sources_and_empty_refill -k prefix -q -ra -x --confcutdir=tests/moe_ep
```

Local report regeneration, using a new prefix (CPU only):
```sh
python3 -B runner/summarize_progressive.py --candidates residual-prefix-v1 --output evidence/residual-final-review
```

After a complete valid N32 result, use the current arm name (`n32-token-v3`) with the report helper. Label N32 as “fixed N32; all other native winner knobs unchanged,” retain both original/transformed map hashes, and judge it pointwise as an optional tactic. N32 does not include residual-prefix; if both are later combined, keep their evidence scopes distinct until the combined source is measured/qualified. The cancelled four-WG arm is excluded.
