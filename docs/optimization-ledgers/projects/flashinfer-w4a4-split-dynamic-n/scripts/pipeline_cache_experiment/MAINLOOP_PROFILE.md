# FC1 mainloop profile after stage/cache investigation

All three variants in this batch remain unretained. Production source was not edited. The earlier composed wide-K/stage handoff is separate and unchanged.

## Scope and immutable inputs

- Candidate: `7829fc00dc7121341cc40cd4190660507e006490`; frozen `pipeline_trial/baseline_core.py` and `baseline_utils.py`.
- Native `bench_moe_deepseek.py` NVFP4 inputs, seed 42, top-k 8, 32 local experts, hidden 7168, intermediate 2048. Route tile 256; FC1 and FC2 tactic `((256,256),(2,1),False)`.
- c1 `fi-w4a4-dyn-n-1024`, B200 GPU 1, image `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2, CuTe DSL 4.7.1. No baseline primary rerun and no shared native JIT changes.
- Ordinary phase timing: identical native routing and captured phase inputs; output plus output-SF byte equality before each arm; 10 warmups / 100 samples, cold-L2 CUDA graphs with CUPTI. These isolated phases are not full-pipeline retention evidence.
- iKET and NCU durations are diagnostic only. Instrumentation and replay perturb execution.

## NCU evidence

`results/pipeline-fc1-n256-stalls-01.ncu-rep`, `-raw.csv`, and `-sass.csv` contain the actual T16384 FC1 profile. The kernel uses 90 registers/thread (96 allocated), 195584 bytes dynamic shared memory, 1024-byte stack, and reports zero executed register-spill local reads/writes. Tensor utilization is 33.56% of elapsed peak; scheduler issue activity is 28.53% of active cycles; DRAM bandwidth is 1.926 TB/s. The profiled duration, 349.696 us, is not the ordinary phase timing.

Most long-scoreboard samples are idle epilogue warps waiting for accumulator completion, not proof that global SF loads are the principal bottleneck:

| SASS PC | Observation |
|---|---|
| `0x7ad67be46f50` | 5061 long-scoreboard samples in accumulator-wait `NANOSLEEP` |
| `0x7ad67be441d0` | 2068 samples branching into that accumulator wait |
| `0x7ad67be42b60` | 1525 samples around producer SF-stage reuse wait |
| `0x7ad67be43880` | 1795 samples on Gather4 shared-address calculation following SF `LDGSTS` |
| `0x7ad67be45e40` | 534 samples around MMA local SF-ready wait |

The address-calculation stall may involve register reuse following asynchronous SF copies, but this profile alone does not establish causality. No register-allocation workaround was retained.

## iKET evidence

The installed public wheel exposes `cutlass.cute.experimental.iket`. The task-local wrapper enables `cute.compile(..., options="iket")` only for `pipeline_trial.instrumented_core`; production and baseline compilation remain unchanged. Markers sample the first two CTA clusters only. Instrumented output and SF bytes matched the control in both the tracker pass and the profiling pass.

The compressed raw trace is `results/pipeline-iket-fc1-n256-01.trace.json.gz`; the uncompressed remote trace is `logs/pipeline-iket-fc1-n256-01/iket_pid_0x204de.trace.json`. `results/pipeline-iket-fc1-n256-01-summary.json` contains every sampled role and CTA. `analyze_iket.py` summarizes the last of six instrumented launches.

Representative means from the leader CTA, 476 K stages over 17 persistent output tiles:

| Range | Warp 0 | Other producer warps |
|---|---:|---:|
| A/SFA TMA issue region | 131.8 ns | 25.7–26.8 ns (branch/no-op span) |
| SF copy issue | 94.6 ns | 68.5–69.2 ns |
| Gather4 issue | 118.9 ns | 136.3–139.9 ns |
| SF-stage reuse wait | 95.6 ns | 177.7–193.9 ns |
| TMA-stage reuse wait | 55.4 ns | 53.0–54.2 ns |

Leader MMA means: local SF-ready wait 90.1 ns; relay-empty wait 52.1 ns; relay arrival region 40.9 ns; peer-SF-ready wait 38.2 ns; TMA-ready wait 38.8 ns; SF S2T issue 52.0 ns; four UMMA issues 47.7 ns. These ranges include marker overhead and must not be summed into an uninstrumented kernel model. The peer MMA warp naturally waits longer for SF because it has no leader-only MMA work.

This suggested producer imbalance and an opportunity to publish SF completion earlier. The ordinary timings below did not support retaining either mechanism.

## Exact-checked ordinary phase screens

Raw per-sample data, exact-check log lines, captured input metadata, expert counts, and valid route-row counts are in the correspondingly named JSON/log files under `results/`.

| Arm / file | Tokens | Control us | Variant us | Decision |
|---|---:|---:|---:|---|
| `gather3`, `pipeline-producer-balance-native-01` | 128 | 108.3840 | 107.2800 | unretained |
| `gather3`, same file | 16384 | 327.3280 | 323.6800 | 1.1% improvement; insufficient evidence to retain |
| `weightslate`, same file | 128 | 108.3840 | 110.2720 | unretained |
| `weightslate`, same file | 16384 | 327.3280 | 326.3200 | neutral; unretained |
| `sfcommitfirst`, `pipeline-sfcommitfirst-native-01` | 128 | 108.5120 | 108.5440 | neutral; unretained |
| `sfcommitfirst`, same file | 16384 | 326.1930 | 329.2165 | 0.9% slower; rejected |

- `gather3`: warp 0 keeps A/SFA TMA and its SF copies; the other three producer warps issue all activation Gather4 operations in a 12/10/10 split. All four TMA-barrier arrivals and the total transaction bytes remain unchanged. Metadata arrays grow to hold the larger per-warp row set.
- `weightslate`: the original four Gather4 producer assignments remain; warp 0 issues A/SFA after Gather4. No extra stage, scratch, or barrier.
- `sfcommitfirst`: only `ab.producer_commit` moves immediately after SF copies and before Gather4. This lets local SF completion and cluster relay advance independently of B TMA issue; the MMA still waits on the original TMA barrier before using operands.

No reverse-order confirmation, broader dtype/per-token sweep, sanitizer, or full-MoE screen was run for these rejected/unretained arms. Testing stopped after this bounded batch so the parent could run the primary combined screen. GPUs 1 and 4 were released.

## Reproduction

Run from the remote candidate checkout. Source files are deployed individually with the task-local `sync.py`; never sync a partial checkout.

```bash
CUDA_VISIBLE_DEVICES=1 PYTHONPATH=. ../.venv/bin/python \
  ../scripts/pipeline_cache_experiment/probe_native.py \
  --repo . --expected-head 7829fc00dc7121341cc40cd4190660507e006490 \
  --tokens 128,16384 --phases fc1 \
  --tactic '[256,[[256,256],[2,1],false],[[256,256],[2,1],false]]' \
  --variants baseline,gather3,weightslate \
  --output ../logs/<new-name>.json

CUDA_VISIBLE_DEVICES=1 PYTHONPATH=. ../.venv/bin/run-iket \
  --output-dir ../logs/<new-iket-name> --log-level info \
  profile --postprocess json --max-ts-cnt-per-warp 32768 -- \
  env DKG_IKET_INSTRUMENTATION_METHOD=NativeDump \
  ../.venv/bin/python ../scripts/pipeline_cache_experiment/probe_iket.py \
  --repo . --expected-head 7829fc00dc7121341cc40cd4190660507e006490 \
  --tokens 16384 --phases fc1 --variants instrumented --profile \
  --tactic '[256,[[256,256],[2,1],false],[[256,256],[2,1],false]]' \
  --output ../logs/<new-iket-name>.json
```

Untried follow-up, explicitly outside this batch: one elected MMA lane per CTA could perform a count-32 relay arrival, preserving both CTA-local waits and fences. That is distinct from the previously rejected SF-scratch transform experiment. The parent owns any follow-up on that mechanism.
