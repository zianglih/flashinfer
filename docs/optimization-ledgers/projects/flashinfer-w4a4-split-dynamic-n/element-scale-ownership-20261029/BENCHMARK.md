# Elements/scales ownership experiment: benchmark plan

Read-only preparation, 2026-10-29. No new harness, source changes, or GPU
launches were made. Paths below are relative to this project unless noted.

## Reuse these artifacts

Let `O = fc1-gather-20261028/optimization-next-20261029`.

| Purpose | Existing source |
|---|---|
| Paired fresh-process C-A-A-C driver | `O/static-sf-id-screen/run_perf.py` |
| Per-job analysis, repeats and CUPTI component timing | `O/static-sf-id-screen/analyze_perf.py`, `aggregate.py`, `audit_raw.py`, `components.py` |
| Native public API/timing observer | `O/retained-control128-full/evidence/observe_benchmark.py` |
| Quantization and backend-label contract | `O/retained-control128-full/evidence/arm_contracts.py` |
| Host telemetry | `O/retained-control128-full/evidence/nvml_clock_wrapper.py` |
| Swap-AB register guard and configurable adapter | `O/static-sf-id-screen/register_guard.py`, `guard_observer_adapter.py` |
| W4A16 zero-local-memory guard | `O/retained-w4-scale-dup-full/evidence/register_guard_w4.py` |
| Complete swap-AB jobs/frozen choices | `O/retained-control128-full/evidence/perf-config.json` |
| Complete W4A16 jobs/frozen choices | `O/retained-w4-scale-dup-full/evidence/perf-config.json` |

Use the actual **`evidence/perf-config.json`** files, not
`retained-control128-full/config-template.json`, which contains stale
source/observer/output paths. Both evidence configs still refer to historic
remote paths: rebind these to the new experiment's source snapshots and
local copied evidence. Do not execute an old deploy/launch script unchanged.

For every job `J`, the complete local frozen inputs are:

- `<campaign>/evidence/results/J/cache-candidate/`: native managed tactic
  cache, copied independently for the two arms.
- `<campaign>/evidence/results/J/1-candidate/results.json`: exact expected
  per-token keys, runners, tactics, route hashes and benchmark arguments.
- `<campaign>/evidence/results/J/receipt.json`: frozen cache manifest and
  source/timing receipts.

All **31 cache directories, 1,455 cache files, and 468 expected cells** were
checked locally against their receipts during this preparation. Latest
measurements are swap `b52e4e09` (364 cells) and W4 `1e4b127a` (104 cells).
Those provide frozen choices and historical context, **not fresh control
latencies** for this experiment: control must be the new retained PR head,
including subsequent reverts/cleanup.

The existing paired driver already supplies the relevant controls: fresh
processes in C-A-A-C order on one physical GPU per job; exact source/patch
hashes; no profiling or cache mutation; identical routes and tactics;
100 finite CUPTI samples; 10 warmups; CUDA Graph replay with cold L2;
no CUDA-event fallback; GPU UUID and clock/power telemetry. Its
`--w4a4-only`/`--w4a16-only` observer flags isolate each result even though
public `--backends cutedsl` selects both.

## Freeze this matrix

`benchmarks/bench_moe_deepseek.py` is the timed native script, through the
existing observer and public functional API. These are **single-GPU local
EP/TP shard shapes**, not distributed communication measurements.

| Model | EP arm | TP arm | Included modes |
|---|---|---|---|
| V3 | `--model v3 --ep 8 --tp 1` | `--model v3 --ep 1 --tp 8` | W4A4, per-token, W4A16, MXFP4x8, MXFP8 |
| V41F | `--model v41-flash --ep 4 --tp 1` | `--model v41-flash --ep 1 --tp 4` | EP: all five; TP: W4A4, per-token, W4A16 |
| K3 | `--model kimi-k3 --ep 8 --tp 1` | `--model kimi-k3 --ep 1 --tp 8` | W4A4, per-token, W4A16, MXFP4x8 |
| N3U | `--model nemo3-ultra --ep 8 --tp 1` | `--model nemo3-ultra --ep 1 --tp 8` | All five |

Preserve the existing exclusions: K3 MXFP8 for both topologies, and both
V41F TP MX modes. These have no qualifying external comparison in the
published supported-cell matrix. Do not silently add or time excluded
combinations or substitute a fused candidate. Swap-AB remains unfused.
No CUTLASS or TRTLLM timing is needed for this causal ownership comparison;
reuse their existing measurements only for the separate external scoreboard.

Native selectors/flags:

- W4A4: `--quant-family nvfp4 --backends cutedsl` plus observer
  `--w4a4-only`.
- W4A16: same native selector plus observer `--w4a16-only`.
- Per-token: `--quant-family nvfp4 --backends cute-dsl-per-token`.
- MX: `--quant-family mxfp --backends cute-dsl-w4a8,cute-dsl-mxfp8`;
  K3 uses only `cute-dsl-w4a8`.
- All: `--functional-api --swap-ab --no-fused-finalize --warmup 10
  --iters 100 --no-autotune --cache <frozen-arm-cache>`.
- NVFP4 family: add `--include-activation-quant`; W4A16 still consumes BF16
  directly, so it has no initial activation quantization operation.
- MX family: preserve the previous omission of initial activation
  quantization from timing.
- Preserve the native per-token recipe: fast FP4 quantization disabled,
  MSE 4over6, E4M3 maximum 256, 4over6 error fast math enabled. Standard W4A4
  and weights retain their standard recipe. `arm_contracts.py` records this
  distinction; do not globally impose the per-token recipe on all modes.

First screen: tokens **4, 64, 512, 4096, 16384** across all 36 included
model/topology/dtype combinations: **180 cells / 72,000 CUPTI samples** for
four phases. Keep all four models and both EP/TP in the screen.

If retained for full evaluation, use
**1,2,4,8,16,32,64,128,256,512,4096,8192,16384**: 31 jobs, **468 cells /
187,200 samples**, including 247 EP and 221 TP cells. Tokens 1/2 are run but
excluded from retention summaries and the plot, leaving 396 displayed cells.

## Parallel scheduling and comparison

Use eight independent GPU lanes when available: V3 EP/TP on lanes 0/1,
V41F EP/TP on 2/3, K3 EP/TP on 4/5, N3U EP/TP on 6/7. Within a lane, process
the existing W4A4, per-token, MX-family, and W4A16 jobs sequentially. Each job
must finish C-A-A-C on that same GPU before the lane takes another job;
never run another benchmark or correctness test on that GPU concurrently.
If fewer lanes are available, queue the same jobs without changing each
job's GPU inside its four phases. This preserves per-cell same-GPU pairing.

Do not retune initially. Require the recorded runner/key/tactic identities
to hit in both arms, with zero `profile_calls`, zero admitted tactics and
unchanged cache manifests. If a cache version/namespace no longer matches,
stop and resolve that exact compatibility issue using the recorded explicit
choices; do not silently fall back to defaults or AUTO.

Keep the **split campaign aggregation**, distinct from the recent MegaMoE
pooled-sample aggregation: take the median of each 100-sample phase, then
`before = sqrt(C1*C2)`, `after = sqrt(A1*A2)` and
`speedup = 100*(before/after - 1)`. Report per-cell C1/A1/A2/C2, repeat spreads,
model/dtype/topology breakdowns, and geomeans over tokens 4+ with decode
4–64, medium 128–512, and prefill 4096–16384 bands. CUPTI component spans can
diagnose FC1/FC2 changes but overlap under PDL and must not be summed into E2E.

## Minimal rebinding before launch

Reuse the existing driver/observer rather than creating another engine.
Refresh source and helper hashes, paths, job token subsets, and descriptive
scope strings. The existing guard maps contain old kernel hashes; validate
current static register policy and update only the source bindings needed
for that proof. Current retained source uses swap control/gather/epilogue
128/128/248, and W4 80/64/144 (with its two existing 96-register dequant
warpgroups). Preserve the loaded-kernel zero-local-memory check; do not use
the W4 campaign's stale swap adapter default 120/128/256.

Use [CACHE.md](CACHE.md): both arms share canonical immutable native assets
and native workspace, verified by byte-identical generated Ninja strings.
Keep kernel source snapshots and CuTe source keys distinct, keep native
cache/tactic cache concepts separate, and record native build times outside
timing. Do not import old source manifests containing deleted files into
new control/candidate receipts: regenerate their manifests at the exact
retained/candidate source snapshots while preserving the frozen tactics.
