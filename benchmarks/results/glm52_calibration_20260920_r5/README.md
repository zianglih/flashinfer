# GLM-5.2 routed-MoE calibration results

[中文](README_zh.md)

**FINAL: 60/60 jobs, 110/110 complete paired groups; 200 samples per arm/group, 44,000 performance samples.** The eight-job correctness phase's 192 CUDA-event samples are diagnostic and excluded from performance.

Independent per-path expert-math/reduction-contract and requested graph checks pass at unchanged `atol=rtol=0.01`. Native cross-pair outcomes remain 8 PASS / 244 FAIL; per-path acceptance does not establish cross-backend equivalence.

## Results and complete raw evidence

[All 110 paired groups](PAIRED_TABLES.md) · [Strict original summary](summary/summary.md) · [Unrounded JSON](summary/summary.json) · [CSV](summary/paired_latency.csv) · [All 60 raw logs and tactics](RAW_LOGS.md) · [Figure/metric SHAs](figures/figure_manifest.json)

The table describes observed coordinates within each phase/EP/communication setting; ranges are not confidence intervals, and no cross-group speedup is pooled. Negative Δ means lower Mega latency.

Across all 110 coordinates: Mega latency is lower at 96, higher at 14; 9 reverse direction between repeats. These are observed direction counts, not a pooled gain across workloads.

| Phase | EP | Split comm | Groups | Mega lower/higher/equal | Mega latency Δ range % | Repeat sign reversals |
|---|---:|---|---:|---:|---:|---:|
| core | 4 | alltoall | 14 | 2/12/0 | -4.4553 to +7.9806 | 7 |
| core | 4 | allgather | 14 | 14/0/0 | -19.0825 to -1.9930 | 0 |
| core | 4 | allreduce | 14 | 14/0/0 | -20.8357 to -2.3433 | 0 |
| core | 8 | alltoall | 14 | 14/0/0 | -12.5557 to -4.7531 | 0 |
| core | 8 | allgather | 14 | 14/0/0 | -38.0766 to -18.2153 | 0 |
| core | 8 | allreduce | 14 | 14/0/0 | -37.2434 to -22.2058 | 0 |
| auto | 4 | allgather | 3 | 3/0/0 | -21.3732 to -7.6770 | 0 |
| auto | 8 | allgather | 3 | 3/0/0 | -34.4618 to -25.6725 | 0 |
| routing | 4 | allgather | 3 | 2/1/0 | -17.7735 to +1.3186 | 1 |
| routing | 4 | allreduce | 3 | 3/0/0 | -17.3226 to -2.3685 | 0 |
| routing | 8 | allgather | 3 | 3/0/0 | -28.8034 to -13.2262 | 0 |
| routing | 8 | allreduce | 3 | 3/0/0 | -34.3117 to -19.2901 | 0 |
| prefill | 4 | allgather | 2 | 1/1/0 | -5.0665 to +4.6656 | 0 |
| prefill | 4 | allreduce | 2 | 2/0/0 | -7.8798 to -1.2987 | 1 |
| prefill | 8 | allgather | 2 | 2/0/0 | -10.3969 to -4.3755 | 0 |
| prefill | 8 | allreduce | 2 | 2/0/0 | -12.3896 to -6.3116 | 0 |

**Eager prefill: Mega latency is lower at 7/8 points and higher at 1/8. Higher-latency points: EP4/allgather N16384: +4.6656%.** These large-N points use default Mega knobs, not AUTO.


## AUTO / routing controls and cross-invocation drift

Compare to default core at the same EP/communication/capacity/N, retaining both arms. AUTO's Split control uses the same algorithm; its cross-invocation drift limits attribution to tuning alone. Routing rows change both arms to precomputed routing. These are not within-process causal ablations; gains are not averaged across rows.

| Control | EP | Comm | N | Mega vs default Δ% | Split control vs default Δ% |
|---|---:|---|---:|---:|---:|
| auto | 4 | allgather | 16 | -12.7923 | +0.1331 |
| auto | 4 | allgather | 128 | -5.6955 | -4.5247 |
| auto | 4 | allgather | 1024 | -7.1098 | -4.4034 |
| auto | 8 | allgather | 16 | -7.1986 | -9.1015 |
| auto | 8 | allgather | 128 | -8.6653 | +5.3641 |
| auto | 8 | allgather | 1024 | -6.5257 | -11.6814 |
| routing | 4 | allgather | 16 | -2.2177 | -5.4137 |
| routing | 4 | allgather | 128 | +0.0990 | -6.0927 |
| routing | 4 | allgather | 1024 | -1.1488 | -2.7223 |
| routing | 4 | allreduce | 16 | -3.4812 | -3.1141 |
| routing | 4 | allreduce | 128 | -1.6914 | -4.9675 |
| routing | 4 | allreduce | 1024 | +0.2529 | -2.5806 |
| routing | 8 | allgather | 16 | -3.2090 | -12.9619 |
| routing | 8 | allgather | 128 | -1.6691 | -10.5414 |
| routing | 8 | allgather | 1024 | -1.5242 | -14.3505 |
| routing | 8 | allreduce | 16 | -3.4240 | -9.7911 |
| routing | 8 | allreduce | 128 | -2.9139 | -6.4211 |
| routing | 8 | allreduce | 1024 | -3.0251 | -5.6118 |

![EP4](figures/core-latency-ep4.png)

![EP8](figures/core-latency-ep8.png)

## Metric and limitations

- For each arm, `latency_us = 1000 × median(r1.samples_ms + r2.samples_ms)`: 100+100 untrimmed rank-MAX samples. Speedup is Split/Mega; signed change is `100×(Mega/Split−1)`. EP/communication/capacity/N/knobs/routing/graph settings remain separate; Mega observations are never reused across communications.
- Figures select 84 core groups: default knobs, routing included, CUDA graph, CUPTI, cold L2. Six auto groups use independent tuning, 12 routing groups are precomputed controls, and eight prefill groups are eager N4096/16384. All 110 groups remain in the full tables.
- Synthetic H6144/I2048/E256/K8/group1 routed-MoE with random inputs, not checkpoint replay; attention/shared expert/router GEMM/MTP are excluded. N counts global token rows, not requests. Latencies are not serving throughput, TPOT or interactivity and do not prove the cause of the serving gap.
- Two additional untimed poisoned-output graph replays are checked, not every timed replay; cuBLASLt and the documented NCCL primitives remain trusted boundaries. Raw r5 input tensors were not captured. Two repeats do not establish statistical significance; sign reversals remain visible.
- Tuning coverage: the [fixed-source / 16-serving-log review](proofs/serving-autotune-coverage-review.md) confirms Split startup tuning, but ordinary EAGLE explicitly skips the extra EXTEND pass; dedicated large-prefill tuning is unproven. Serving Mega uses its separate None path, not auto. r5 tunes Split at each invocation's maximum N; Mega AUTO covers graph N16/128/1024 only, while eager large-N remains default. Do not call prefill Mega autotuned or attribute serving behavior to this control.
- Original r3/d1 strict FAIL outcomes are unchanged. Their full tensor diagnosis is published separately and is not duplicated here. Cache archival and node cleanup are separate workflows; this bundle makes no archival or cleanup claim.

## Environment, source and reproduction

- Benchmark `bd8391858db504c8997e704c7952f4d48ccab591`; runtime/kernel `ad0a5e5e78e57070ec7c582efe733cb55cd8839f`; lmsysorg/sglang:nightly-dev-cu13-20260918-20518d85.
- NVIDIA B300, EP4/EP8; Torch `2.13.0+cu130`, CUDA `13.0`, CuTe `4.7.1`, CUPTI `13.2.0` / `13.2.86`, loaded NCCL `2.29.7`.
- [Exact argv/env/source/runtime](evidence/runs/glm52-calibration-20260920-r5/provenance.json) · [60-job plan](evidence/runs/glm52-calibration-20260920-r5/plan.json) · [Correctness seal](evidence/runs/glm52-calibration-20260920-r5/gate-receipt.json) · [Completion](evidence/runs/glm52-calibration-20260920-r5/exit.json).
- [12 setup receipts](environment/verification.json) · [Actual 12-test component gate](component-gate/verification.json) · [Unmodified proof index](PROOFS.md) · [Copy manifest](copy-manifest.json) · [Complete bundle hashes](bundle-manifest.json).

From this directory, use an existing Python environment with Matplotlib for CPU-only reproduction; output paths must be new.

```bash
python3 -B tools/summarize_calibration.py --transfer evidence --dispatch dispatch --output recomputed-summary
python3 -B tools/plot_calibration_core.py --summary recomputed-summary/summary.json --dispatch dispatch --output recomputed-figures
python3 -B tools/check_calibration_raw_arithmetic.py --summary recomputed-summary/summary.json --output recomputed-raw-arithmetic.json
```

Original absolute JSON paths and historical review snapshot names remain unchanged as provenance; clickable navigation uses bundle-relative paths. Raw files, sources, helpers and receipts are byte-copied and rehashed. Assembly completion is not independent final-review or GitHub-publication approval.
