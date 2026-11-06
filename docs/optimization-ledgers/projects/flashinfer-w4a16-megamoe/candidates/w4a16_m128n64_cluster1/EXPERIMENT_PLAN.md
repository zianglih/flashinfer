# CUDA 13.2 next experiment: M128/N64/K256 physical C1

Select C1 before K128. Both preserved patches matched published6315f94/kernel34bb at the start of this review. The root agent subsequently applied only C1: kernel e00942e45f690e22258bb7f649b1be87b5a1cad72d61286251f6885ed10da42b. No default, tuner entry or public knob changes are included. Exactly two decode warpgroups remain fixed.

## Why this is the bounded next test

| Candidate | Existing source and evidence | Coupled changes / risk | Decision |
|---|---|---|---|
| M128/N64/K256 C1 | Existing split topology `((128,(1,1)),(128,(1,1)))` in `cute_dsl/tuner.py:978`; current split K256 at972. Uses existing generic layout, local release, scheduler and configured-cluster launch paths. Preserved88-case real CPU constructor/layout/fitter validation and80 config acceptance/rejection checks pass. | Remove paired CTA residency and B multicast; double the number of scheduler work claims for the same aligned feature extent. Arithmetic, M/N/K, raw/decode/activation/accumulator depths, register roles and thread count stay unchanged relative to M128 C2. | Test C2/C1/C2 on the same patched source. |
| K128 | Preserved224-case real CPU constructor/layout/fitter validation passes; existing helper supports eight K16 atoms instead of sixteen. Current split tuner fixes K256. | Doubles FC1/FC2 K iterations at DSV3 from28/8 to56/16 and changes N64 decoded depth3→6 (N1282→4), per-stage fragment/SMEM geometry and phase wrapping. | Keep unapplied. Current profile does not establish raw/decoded starvation; this is a less isolated next experiment. |

The old ledger first retained K as an axis (`flashinfer-w4a16/w4a16_optimization_experiments.md:276–282`), but later K256-only pruning removed K64/K128 (`:4127–4135`), and the current split source confirms fixed K256. A separate route256/K128 experiment lost to route128/K256 (`:2320–2356`); its different N/accumulator contract prevents treating that result as a direct Mega K128 test. These are source/history priors, not B300 fused-Mega performance predictions.

The current N64/stage3 PC capture is dominated by scheduler work-publication sleeps with severe rank skew. It does not prove a cluster scheduler bottleneck or predict a C1 gain. The C1 hypothesis is finer independent CTA scheduling without pair synchronization; the costs are more scheduler claims and losing activation multicast. There is no avoided feature padding in aligned H7168/I2048. The primary comparison must therefore keep M128/N64/K256 and all non-cluster knobs fixed; comparing C1/M128 directly with C2/M256 would mix topology and MMA geometry.

## Frozen numerical harness and completed gate

`experiment/` contains a copy of the existing geometry plugin with a physical-cluster selector and stronger observed-layout assertions. Original helpers and the public test file are unchanged. The wrapper reuses the v2 source attestation, original timeouts, original pytest markers and all10 public cases per rank:3 normal/exact-routing/graph cases,4 geometry/ring/tail cases,2 reference-return-mode cases and1 clamp case. Reference-return tests additionally exercise H288/I448/M257. H9472/I64 exercises fitted raw4; smaller cases use raw5. No tolerance or reduction boundary changed.

Root completed fresh C1 EP1/EP2; the independent CPU audit verifies **10 EP1 and10 per EP2 rank**, all1,571 source files and7 runtime helpers equal current local e009, and pre/post attestation unchanged. Each rank execution observed16 compiled geometries:15 raw5 and1 raw4. All use C1/M128/N64/K256,640 threads,2 transform groups,decoded3/acc2 and128+384 TMEM columns. Evidence: `c1-numerical-audit-001.json` and `logs/tmem-c1-numerics-001-c1-ep{1,2}`. No GPU work was performed by this reviewing agent.

Remote commands (already executed for C1; retain for reproduction):

```bash
bash candidates/w4a16_m128n64_cluster1/experiment/run_numerical.sh 1 1 tmem-c1-numerics-001
bash candidates/w4a16_m128n64_cluster1/experiment/run_numerical.sh 1 2 tmem-c1-numerics-001
```

Optional fresh C2 numerical controls use first argument2. The baseline C2 device methods are unchanged by the C1 patch; record separately whether fresh same-source C2 numerics were run. The timing auditor requires fresh C1 numerics and accepts an explicit optional C2 numerical prefix.

The four runtime files are frozen in `experiment/runtime-helper-manifest.json`. `run_controls.py` final SHA256 is `ae72996e1fb5ecab2f87f87356e43e2c4224c425d70f2ad722fc5982a88e87da`. Its invalid `--no-refcheck` draft argument was removed before any upload/run. `actual-parser-validation.json` proves the generated full argv parses through the benchmark's actual argparse declarations, with `refcheck=false`; the removed flag is rejected by the negative control. CPU checks are explicitly synthetic helper checks, not additional GPU tests.

## Same-source measurement

Primary five points: **1,16,64,256,4096 global source tokens**, real EP8, H7168/I2048/E256/top-k8. Both arms use M128/N64/K256, raw5/decoded3/activation2/accumulator2,640 threads/2WG, flag4, group512, atomic scheduler, epilogue flags(2,4), `epi_warps`, in-kernel FC2 reduction false. Only physical cluster(2,1,1) versus(1,1,1) changes. Both use one-CTA MMA instructions.

```bash
python3 candidates/w4a16_m128n64_cluster1/experiment/run_controls.py \
  tmem-c1-controls-001 --tokens 1,16,64,256,4096 --execute
```

Without `--execute`, this only prints the planned commands and performs no GPU work. The executed order is C2-before, C1, C2-after on exact e009 source. The wrapper uses the existing EP8 launcher:3 warmups,100 CUPTI iterations, CUDA graph, cold L2, same full-forward timing scope, split `--no-fused-finalize`, no profiler environment flags. The optional strict split-final-tensor refcheck is omitted because the already documented BF16 rank-partial versus all-route reduction boundary differs; the independent numerical oracle remains required. Source/helper inventories are asserted unchanged before and after each arm. Actual split tuner choices are persisted for every rank and shape.

If the first five points give a reproducible benefit beyond the observed C2 drift, repeat the same C2/C1/C2 wrapper with all13 powers of two from1 through4096. Retain both C2 endpoints separately; do not average away drift, treat split spread as a confidence interval, or turn a sub-1% isolated difference into a win. A benefit against M128/C2 alone is insufficient for tuner promotion: compare any surviving C1 candidate with the current recorded winning tactic on matching inputs/source before adding a curated tactic. K128 and any geometry/stage combinations remain separate.

CPU result audit after root fetches all three complete arms:

```bash
python3 candidates/w4a16_m128n64_cluster1/audit_controls.py \
  tmem-c1-controls-001 --numerical-prefix tmem-c1-numerics-001
```

The auditor lives outside the frozen runtime-helper directory. It checks all30 raw latency rows for five points,120 actual split records, full-source equality, requested/logged knobs, numerical geometry and group counts. Output preserves original printed decimals, complete tactics, candidate change against each baseline separately, signed baseline drift and changed split-tactic ranks. Add `--control-numerical-prefix PREFIX` only when those actual C2 numerical artifacts exist. It does not generate a gain claim from incomplete arms.

## Codegen and conditional profiling

Use existing helpers; no new profiler is necessary before a measured effect justifies it. Capture C1/C2 at the same global4096 capacity to compare generated resources. These commands launch GPUs and belong to the root agent after coordinating GPU ownership:

```python
import json
import subprocess
from pathlib import Path
for cluster in (2, 1):
    knobs = json.loads(Path(f"candidates/w4a16_m128n64_cluster1/c{cluster}-knobs.json").read_text())
    subprocess.run([
        "bash", "run_public_codegen.sh",
        f"tmem-m128n64-c{cluster}-codegen-001", "4096",
        json.dumps(knobs, sort_keys=True),
    ], check=True)
```

`run_public_codegen.sh` already captures all8 rank PTX/cubin/SASS and runs `summarize_public_codegen.py`. Audit complete rank inventory and within-arm binary consistency; preserve differences between arms. Check actual resources against640 threads/cap96 and host-predicted216,576 dynamic shared bytes at H7168, with no stack/local allocation or LDL/STL. Inspect any added local instruction by its own source location, especially transform versus vendor FC2 router, before claiming no added spill.

Trace the new PTX/SASS rather than importing old line offsets:16 non-blockscaled BF16 `UTCHMMA` instructions (no `.2CTA`),512-column CTA-group1 TMEM allocation/free, decoded region128..511 with three128-column stages, two64-column accumulators, and unchanged176/80/64/80/80 register roles. C1 activation B release expects1 arrival versus2 for M128/C2; raw-empty8, decoded-full256/empty1 and accumulator-empty128 remain unchanged. TMEM retrieve/scheduler/dispatch-ready/tail participants remain416/480/160/640. Confirm C1's inherited no-B-multicast path. Anticipated grid is(1,1,148) versus C2(2,1,74) on this148-SM device; record actual launch attributes instead of assuming occupancy.

If a repeated timing difference warrants further explanation, choose one measured shape and use the existing source-attested profile wrapper, with the corresponding `c1-knobs.json` or `c2-knobs.json`:

```bash
python3 run_current_profiles.py nsys tmem-m128n64-c1-nsys-001 256 candidates/w4a16_m128n64_cluster1/c1-knobs.json
# Only if source-specific PC evidence is needed after the software trace:
python3 run_current_profiles.py ncu tmem-m128n64-c1-ncu-pc-001 256 candidates/w4a16_m128n64_cluster1/c1-knobs.json
```

The existing NCU launcher coordinates all8 ranks and bounds sampling passes. Require eight completed reports, matching pre/post source, zero drops/overflow and conserved PC sums. Reuse `extract_pc_samples.py`, `export_ncu_action_sass.py` and the generic `profiles/n64-profile-audit-plan/audit_pc_capture.py` with newly frozen C1 source and fresh SASS. C1 PC offsets and optimized line tags must be remapped. Keep instrumented durations, aggregate collective wait fractions and cross-capture sample ratios out of production latency claims. Never compare transform-group counts in this iteration.
