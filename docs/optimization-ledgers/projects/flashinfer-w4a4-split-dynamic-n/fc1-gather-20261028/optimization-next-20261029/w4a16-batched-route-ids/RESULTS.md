# W4 batched route-ID preload

Status: **rejected for now** by the parent. Instruction reduction is proven, but the bounded screen has unresolved V41F prefill losses. No causal speedup or neutrality claim; no more repetition. The review copy was retired after matching all 514 source hashes and the exact saved patch. Sources/patch, helpers and raw reports remain preserved; no commit/push. GPU3 is idle and released.

## Scope and source

- Logical control: retained `6c6515f2f804af420661d95e4595b5663d7f92d1`; candidate: 17 additions / 5 deletions in `moe_w4a16_kernel.py` only. All 514 source files verified; exactly one differs between arms.
- Candidate kernel SHA256: `86f7d34b5935e915f16f5e3b5588311c4bbc99a02a2758224979092fbbc984e3`. Control: `b8f124f187ec169b101c56a72cce2732833b89bf6ef3b72eaa0695f7a04b5da7`.
- Remote source materialization retains Git HEAD `1b0f1f69acbb7e20055d5aaf76cc29c840779304`; the source manifests and patches, not that old Git label alone, identify the logical 6c control and candidate.
- Up to eight four-row groups share one lane-distributed route-ID load, then fill the existing static warp-uniform coordinate cache with SHFL. Narrow one-group tiles fold to the old mapping. All metadata remains outside K. No staging, barriers, byte counts, PDL, warp ownership, quotas, FC2, tactic, API or math changes.
- CPU proof covers 345,600 cases: legal N8..256 geometry, one/two CTA, four issuers, dynamic second-CTA row offset, every valid tail and topK1/2/3/8/22. Current hardware tactics stop at N192 and require two CTA there. No padding-slack assumption imported from Rubin.

## Qualification

- Existing accuracy selection: **33 passed**, no errors/failures/skips. All 33 captured kernels have zero local storage and no LDL/STL.
- Two additional existing test invocations per arm cover the largest admitted one-CTA route N128, topK3, tail1 and half-tile+1. All four pass; FC1/FC2 codegen has zero local storage.
- Initial extra-test harness used `runpy` without test-package context and failed importing `.utils` before GPU execution. Its failed receipt is preserved. The repaired importlib helper passes; no kernel source changed and the 33 cases were not rerun.
- Own-file pre-commit passed. No sanitizer, new repo tests or clock changes.

| Actual FC1 geometry | Gather non-NOP instructions C→A | Route LDG sites C→A | Static SHFL sites C→A | Local bytes C→A |
|---|---:|---:|---:|---:|
| N16, two CTA | 213→213 | 1→1 | 4→4 | 0→0 |
| N128, two CTA | 275→255 | 4→1 | 16→16 | 0→0 |
| N192, two CTA | 344→321 | 6→1 | 24→24 | 0→0 |
| N128, one CTA, topK3 | 525→458 | 8→1 | 32→32 | 0→0 |

N16 PTX and cubin are byte-identical. The extra one-CTA FC2 PTX/cubin are byte-identical. Representative two-CTA non-gather scopes retain their instruction counts. One-CTA N128 uniform spill/fill sites decrease 14→11; these are uniform-register↔GPR moves, not local-memory spills. No zero-uniform-spill claim is made.

## Initial CAAC

B300 GPU3, existing CUDA13.2/CuTeDSL4.8 environment; source-paired C-A-A-C, frozen native winners and saved route identities, 10 warmups, 100 strict CUPTI cold-L2 graph samples per cell. No autotuning. Each phase value is its 100-sample median; an arm value is the median of two phase medians (an arithmetic mean for two values). Speedup is control/candidate−1. Spread is max/min−1 for the two same-arm phases. Read-only 2ms NVML is saved; stock clocks unchanged.

| Shape | Tokens | Control ms | Candidate ms | Change | C/A phase spread |
|---|---:|---:|---:|---:|---:|
| K3 EP8 | 4096 | 0.5752915 | 0.56292325 | +2.197% | 6.487% / 1.273% |
| K3 EP8 | 8192 | 1.0106145 | 0.9925735 | +1.818% | 1.493% / 5.019% |
| V3 TP8 | 8 | 0.0570565 | 0.0571685 | −0.196% | 0.225% / 0.168% |
| V3 TP8 | 4096 | 0.478955 | 0.47843475 | +0.109% | 0.110% / 0.007% |

K3 phase quartiles drift substantially (e.g. 8K first/last quartiles range approximately 0.924–1.078ms). NVML sometimes records SM clock variation/reason4 but can also report constant clocks during visible timing drift. These are observations, not proof that external frequency variation caused the source comparison. Candidate utilization may itself affect power behavior. The K3 percentages are not a causal speedup claim; no frequency normalization is used. V3 TP is effectively neutral at this screen's resolution.

## Eight-cell extension

Same frozen source, route/cache identities, runtime guards and C-A-A-C protocol, on GPU3. All original rows remain above. The three 16K cells reuse frozen cache sentinel `-1`, which resolves to the unchanged N128/two-CTA/K256 default; no profile or AUTO occurred. Other rows use the saved explicit native tactics. Every loaded FC1 kernel has zero local storage.

| Shape | Tokens | Control ms | Candidate ms | Change | C/A phase spread |
|---|---:|---:|---:|---:|---:|
| K3 EP8 | 4096 | 0.57237125 | 0.5544755 | +3.228% | 1.953% / 0.228% |
| K3 EP8 | 8192 | 1.02269425 | 1.0305900 | −0.766% | 5.998% / 2.326% |
| N3U EP8 | 4096 | 0.40270675 | 0.3998505 | +0.714% | 0.143% / 0.357% |
| N3U EP8 | 16384 | 1.5998180 | 1.53418525 | +4.278% | 0.343% / 7.847% |
| V41F EP4 | 4096 | 0.4544430 | 0.46291475 | −1.830% | 0.767% / 4.683% |
| V41F EP4 | 16384 | 1.5140415 | 1.5783130 | −4.072% | 0.341% / 3.471% |
| N3U TP8 | 16384 | 1.9749650 | 1.97408475 | +0.045% | 0.631% / 0.343% |
| V41F TP4 | 4096 | 0.5675070 | 0.5647955 | +0.480% | 0.226% / 0.304% |

V41F EP16K first quartiles are near 1.313–1.338ms for all four phases, while later quartiles vary 1.54–1.665ms. Its control medians are 1.511/1.517ms and candidate medians 1.605/1.551ms. Both negative candidate medians remain in the result; they cannot be dismissed merely because telemetry is variable. N3U EP16K's apparent +4.28% gain is also unreliable: candidate phase medians vary 1.592→1.476ms, with within-phase quartiles reaching 1.82ms. NVML records varying clock/reason values and can be stale; no source/frequency causal claim or frequency normalization is made.

The instruction reduction is proven, and the stable smaller cells are near-neutral or modestly positive. However, this bounded data cannot establish an across-the-board neutral result with the −4.07% V41F EP16K observation. Decision: rejected for now. Preserve the instruction evidence and all negative rows; do not publish a speedup or neutrality claim. No further runs were launched, as instructed. This W4 decision is independent of the parent’s swap-AB batching experiment.

Read-only `current-head-equivalence.json` verifies all 514 files against current `e780f02cc1f8a7e59f22b8bda6f7acd8f8792b24`: only `moe_swap_ab_kernel.py` differs from the frozen6c control. W4 and its transitive benchmark/wrapper/prepare/test paths are identical.

## Evidence

- `candidate.patch`, `local-source.json`, `geometry-proof.json`, `codegen-analysis.json`, `extra-codegen-analysis.json`, `n16-identical.json`.
- `screen.csv`, `summary.json`, telemetry analysis and original raw CUPTI/NVML/route/cache/source receipts under `evidence/`.
- Initial evidence archive SHA256 `129d6fb83489403ab2d4b76346c0c7af28c75fc6f1576b0fd23f298aece28893`, 7,614,031 bytes.
- Eight-cell extension is isolated under `broad8/`; immutable measured sources are shared read-only. Archive SHA256 `0b8ad879aa542a813a5e477acc8d72da82e2effba05cae735818011c9898f5eb`, 10,824,128 bytes. `qualification.json` binds every guarded result and observed tactic. All raw quartiles and read-only NVML samples remain available.
