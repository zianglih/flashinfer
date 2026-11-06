# K16 staged-reduction diagnostic

Baseline: PR7290 `0def601d6603df828ea39679b41ccbce64f7f09e`.
Experimental source is the independent `../flashinfer-scheduler-20261026/`
clone. Its four-file delta remains unstaged. Canonical and review sources are
untouched. The bounded GPU experiment uses GPU 7 on the c3 B300 devbox;
its source-private native cache is linked to the persistent control cache.

The candidate extends the existing K-step admission and flat tuning axis from
4/8 to 4/8/16. K16 means a 1024-element FP4/FP4 reduction tile or a 512-element
FP8/mixed tile. The existing SMEM/TMEM planner, TMA layouts, dynamic-N MMA,
producer ownership, cache priority, CLC scheduling, epilogue and math are
unchanged. The old automatic fallback still chooses only K4/K8. The public MX
runner validates explicit tactics against the registry, so the registry must
contain K16 even for a fixed diagnostic. Do not run all 810 raw AUTO tactics
before this screen warrants it (control has 360).

## Why this axis

K16 can amortize stage acquisition/release, TMA issue, and scale publication
across more reduction work without adding dtype/model/shape branches. Capacity
checks determine whether the larger stage fits. The cost is a shallower operand
ring and more MMA padding on short K; speedup is a hypothesis. CPU estimates for
M128/N16 give two stages across all six dtype/SF contracts. This is **not** a
prediction of kernel latency or a proof of SDK layout support.

Local history explicitly rejects deeper CLC metadata, global static metadata
queues, register donation, compact FC1/FC2 warp counts, and one-CTA channel
reuse. None is repeated here. Earlier wider-K trials tested K8 instead of K4,
not K16. The most relevant positive evidence is that K8 previously beat K4 for
several small/mid-token workloads, while the generality audit showed that a
blanket maximum-queued-K policy could lose NV decode by roughly 4%. Current
AUTO therefore exposes K4/K8. K16 is a new bounded continuation of that direct
measured axis, not a new hand-selected dtype rule.

Evidence:
- `../GENERALITY_AUDIT_2026-10-25.md`: queued-K tradeoff and retained flat axes.
- `../scripts/pipeline_cache_experiment/README.md`: earlier K4/K8 phase evidence.
- `../scripts/wide_k_overlap_experiment/RESULTS.md`: reject old prefill K8 policy.
- `../SCHEDULER_OPTIMIZATION_2026-10-25.md`: depth2/static metadata rejections.
- `../scripts/register_budget_experiment/README.md`: zero-spill controls and
  neutral/slower register donation.

## Static checks

`audit.py` extracts current source methods. All device-method ASTs are
unchanged; only constructor/admission membership differs. Existing 720 planner
cases remain identical. All original 360 tactics retain their relative order;
810 candidate tactics round-trip through the actual MX tactic parser. The
resource census uses explicit SM100 capacity stubs. Scoped pre-commit and
`git diff --check` pass. The initial N16 K16 compilation smoke now passes on B300
for NVFP4, MXFP4x8 and MXFP8; wider selected geometries remain part of the screen.
`audit.json` pins source; `candidate.patch` is the complete source delta.

## Bounded screen

`prepare.py` adapts the existing `generality_k_depth` tooling. It preserves the
latest rebased campaign's selected geometry/scheduler and input cache keys,
replacing only the K-step pair. Existing timings are **not reused**. There are
four cache variants per model/family: K8 both phases, FC1-only K16, FC2-only K16,
and both K16. `cache-provenance.json` records every original and derived hash.

`observe_table.py` calls the unmodified public benchmark and timer. It observes
constructor/actual storage choices without rewriting them, records original
routing bytes, and saves every 100-sample timing array. CUPTI fallback is fatal.
NV includes initial quantization; MX remains prequantized. Fused finalize is
disabled. NV selector `cutedsl` also measures unchanged W4A16 as a drift control;
only W4A4 is an affected result in this first screen.

Run with a source-private workspace whose native C++ cache has already been
linked safely to persistent storage by the root task. This helper neither
constructs nor deletes compilation caches. It can run separate model/family
invocations on root-assigned GPUs:

```bash
python scheduler-k16-20261026/run_fixed.py \
  --project-root /data/ziangli/flashinfer-w4a4-split-dynamic-n/ROUND \
  --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/ROUND/k16-source \
  --python /data/ziangli/flashinfer-w4a4-split-dynamic-n/ROUND/.venv/bin/python \
  --cache-root /data/ziangli/flashinfer-w4a4-split-dynamic-n/ROUND/cache/k16 \
  --gpu 0 --models v41-flash --family mxfp --tokens 32,128,4096 \
  --variants k8,both-k16,both-k16,k8 \
  --out /data/ziangli/flashinfer-w4a4-split-dynamic-n/ROUND/results/k16-v41-mx
```

The initial existing-test smoke passes all three requested formats and both
phases: NVFP4 OAI accuracy, plus MXFP4x8 and MXFP8 functional-K8 versus wrapper-K16
comparison including SiTU gate/up. These small N16 cases exercise short K tails;
they do not establish exactness for V41 K2304 or K3 K3584. Keep that boundary
separate from performance evidence and run the actual-shape correctness gate if
retaining the candidate. Do not infer exact correctness from route/timer receipts. If both-phase K16 is useful,
use `--variants k8,fc1-k16,fc1-k16,k8` and the FC2 equivalent to isolate where.
A narrow win alone is insufficient justification to expand production AUTO;
retention requires general policy value across V3/V41/K3 and affected formats.

## Runtime preparation and failed pre-timing attempts

- Runtime is c3 B300, PyTorch `26.05-py3`, CUDA 13.2, Torch
  `2.12.0a0+5aff3928d8.nv26.05`; GPU 7 is exclusive to this diagnostic.
- Source-private workspace digest is
  `d01e34c2b7f23d1f27df63ad8cc7e339d0bc65b0fb9e8131eb9453ef3112ce17`.
  Seven verified native-cache links preserve C++ build reuse; CuTe objects remain
  private. Receipt: `evidence/cache-receipt.json`.
- The first smoke import used a top-level module name, which broke an existing
  test's relative import before CUDA work. Correct package loading fixed the
  helper only. `smoke-r2` passes all three existing-test calls.
- The first table run correctly rejected old runtime cache metadata (the new
  environment has TVM-FFI post1 and a different DSL library fingerprint). The
  constructor observer then refused fallback K=None, so no untuned timing was
  accepted. `materialize_cache_metadata.py` creates explicit current-runtime
  diagnostic copies, records both metadata sets and hashes, and proves every
  tactic record unchanged. No wildcard metadata or timing reuse is involved.
- `run_fixed.py` preserves the venv interpreter path (`absolute()`, never
  `resolve()`), because resolving its symlink would lose the venv context.

## Rejected fixed-geometry screen

The completed V41 ABBA screen rejects unconditional K16: W4A4 K8/K16 speedups
at 32/128/4096 tokens are 0.9758/0.9876/0.8291; MXFP8 is 0.9979/1.0025/0.8574;
MXFP4x8 is 0.8832/0.8688/0.7416. K16 reduces narrow operand rings from 5 stages to 2
for MX and reduces the held wide FC2 from K256×3 to K512×1. V3/K3 MX screening is complete and also loses; see `results.md` and
`summary.json` for every measured cell. Parent agreed to reject K16 and skip
the remaining NV sweeps and any expanded AUTO campaign. These are fixed-geometry diagnostic
ratios, not retained AUTO numbers and not comparisons with TRTLLM.
