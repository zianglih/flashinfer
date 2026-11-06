# Fitted one/two-group Nsight Systems capture audit

The original two-group capture is incomplete at both T32 and T4096: it contains 14 fused kernel instances on seven devices, while the one-group control has the expected 16 instances on eight devices. Device 2 has no GPU kernel activity in either two-group report. The strict `audit_nsys_resources.py` assertion fails and remains unchanged; these reports are retained as partial diagnostic evidence.

| Capture | Tokens | Fused instances | Devices captured | REG/thread | Threads/CTA | Grid | Cluster | Dynamic shared bytes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tmem-fitted5-nsys-001 | 32 | 16 | 8 | 128 | 512 | (2,1,74) | (2,1,1) | 216576 |
| tmem-fitted5-nsys-001 | 4096 | 16 | 8 | 128 | 512 | (2,1,74) | (2,1,1) | 216576 |
| tmem-fitted5-transform2-nsys-001 | 32 | 14 | 7 | 96 | 640 | (2,1,74) | (2,1,1) | 216576 |
| tmem-fitted5-transform2-nsys-001 | 4096 | 14 | 7 | 96 | 640 | (2,1,74) | (2,1,1) | 216576 |

Nsight reports static shared memory 0 and local memory/thread 0 in these activity records. Those fields are preserved as reported; they do not replace the separate cubin/SASS inspection, which identifies driver/static storage and intentional FC2 router local arrays. The captured two-group launch resources agree with the previously checked codegen. The fused kernel accounts for 97.752064% at T32 and 97.451688% at T4096 of named-stage GPU time on the seven captured devices; these are partial summed trace shares, not full EP8 performance estimates. All profiled durations are excluded from CUPTI timing comparisons.

## Missing-device evidence

Device 2 is a missing trace, not a missing benchmark worker:

| Tokens | Device 2 PID | CPU launch API records | routing ranges | Mega ranges | Incomplete CUPTI events dropped |
| --- | --- | --- | --- | --- | --- |
| 32 | 159076 | 17 | 2 | 2 | 21 |
| 4096 | 160265 | 17 | 2 | 2 | 21 |

The CUDA context and profiler start/stop APIs exist for both processes. SQLite diagnostics explicitly say the 21 events were incomplete because GPU timestamps had not been retrieved when collection stopped. Other processes also show ignored profiler start/stop messages and some missing-buffer diagnostics. The launcher's stdout does not print these messages; they are embedded in `DIAGNOSTIC_EVENT`.

The existing benchmark synchronizes CUDA and performs a distributed barrier before stopping. That establishes GPU-work completion, not completion of independent process-local profiler flushes. A NVIDIA investigation of a matching multiprocess capture-range failure identified lost peer-process buffers when API stop ended collection, tracked as DTSP-21073. Its workaround ignores API range end and stops the named session externally. The match supports testing that strategy; it does not establish the internal cause of our installed release without a controlled retry. [NVIDIA investigation and workaround](https://forums.developer.nvidia.com/t/question-when-prifilling-megatron-lm/350407)

## Retry and artifacts

`candidates/nsys_capture_flush/README.md` provides two explicit, effort-only retries. First, leave API-triggered capture open until the finite process tree exits (`--capture-range-end=none --wait=all --kill=none`). If necessary, use the stronger named-session external stop with all eight workers held alive after completion. There is no automatic fallback and no production benchmark edit. Both require a fresh name and the unchanged 16-instance/eight-device gate. The documented CLI semantics support ignoring API range end, waiting for children and explicitly stopping a session. [Nsight Systems guide](https://docs.nvidia.com/nsight-systems/UserGuide/index.html)

```bash
python3 diagnose_nsys_capture.py \
  profiles/tmem-fitted5-nsys-001 \
  profiles/tmem-fitted5-transform2-nsys-001 \
  --output logs/fitted-nsys-capture-diagnostic-001.json
```

The JSON contains every per-process runtime API count, named NVTX range count, diagnostic message, resource row, original named-stage CSV row and SQLite hash. Original `.nsys-rep`, `.sqlite`, `.kernels.csv`, launcher logs and provenance are retained. CPU extraction and Ruff checks pass. No active repository changes were performed during the investigation.

## Controlled retry results

The finite-exit retry `tmem-fitted5-transform2-nsys-exit-001` completed successfully as a process, but both shapes still contain only 14 fused launches on seven devices. The logged effective command confirms `--capture-range-end=none --wait=all --kill=none` and a named session. Each rank now reports 50/50 CUPTI buffers; device 2 alone drops 163 events for unavailable timestamps, while the other seven ranks drop zero. Device 2 PIDs are 168361 at T32 and 169431 at T4096. This excludes incomplete process-buffer delivery as a sufficient explanation; ignoring API stop until finite application exit does not repair this trace. Full extraction is retained in `logs/fitted-nsys-capture-exit-diagnostic-001.json`.

The explicit external-stop retry reached all eight ready markers, but `nsys stop --session=fi-flush-172797-1d7b3b7f` failed with `StopRequest`. Root released that exact session's completed workers so they could exit naturally. Its log is retained in `logs/tmem-fitted5-transform2-nsys-external-001.log`. The effort helper now releases held workers in `finally` and preserves the failed-stop status; external mode should not be retried on this installation.

Every affected process explicitly reports “Hardware tracing used for CUDA tracing.” NVIDIA documents that `--trace=cuda` uses hardware tracing by default on Blackwell and that `--trace=cuda-sw` forces software tracing. The installed Nsight 2026.2.1 help confirms `cuda-sw` support. The next controlled diagnostic keeps finite-exit mode and changes only the CUDA trace token, with original NVTX/NCCL and worker arguments preserved. This tests a hardware timestamp-path hypothesis, not a proven driver or kernel cause. The exact command is in `candidates/nsys_capture_flush/README.md`; the strict 16-instance/eight-device acceptance rule remains unchanged. [Nsight Systems trace modes](https://docs.nvidia.com/nsight-systems/UserGuide/index.html)

## Software-trace result: measured-stage coverage passes

`tmem-fitted5-transform2-nsys-software-001` passes the unchanged strict audit at both T32 and T4096. Each report contains exactly 16 fused launches, two on each of devices 0–7. Every named routing/staging/fused/reducer row has 16 instances, and both routing/Mega NVTX ranges appear twice for every rank. All ten recorded repository source hashes match the declared `fe4f8132439df1b812f77279e7d033a5128f1ed4` source; the newer remote Git HEAD is not used as evidence of the compiled kernel.

| Tokens | Fused launches/devices | REG/thread | Threads/CTA | Grid | Cluster | Dynamic shared bytes | Fused share of named-stage summed time |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 32 | 16 / 8 | 96 | 640 | (2,1,74) | (2,1,1) | 216576 | 97.305429% |
| 4096 | 16 / 8 | 96 | 640 | (2,1,74) | (2,1,1) | 216576 | 98.428902% |

All 16 rank/shape diagnostic sets explicitly say “CUDA legacy/software instrumented trace was collected.” None reports dropped or incomplete CUDA timestamp events. A generic “Not all NVTX events might have been collected” warning remains; the expected measured-stage ranges and launches are individually verified, so the acceptance is scoped to those stages rather than claiming every process event was captured.

The controlled change from the failed finite-exit run was the trace token, from `cuda` to `cuda-sw`, with the same source and collection-lifetime settings. This is evidence that software tracing avoids the observed hardware-trace timestamp failure on this installation. It does not establish a general hardware-trace defect across devices/releases. Software instrumentation overhead makes the recorded durations unsuitable for the CUPTI performance table or direct comparison with hardware-trace durations.

Raw resources and CSV rows are in the capture's `resource-summary.json`; full per-process diagnostics are in `logs/fitted-nsys-capture-software-diagnostic-001.json`. `logs/nsys-software-validation-001.json` records source-hash verification, effective command lines and scoped acceptance. The strict audit stdout is retained as `logs/tmem-fitted5-transform2-nsys-software-001.resource-audit.log`.
