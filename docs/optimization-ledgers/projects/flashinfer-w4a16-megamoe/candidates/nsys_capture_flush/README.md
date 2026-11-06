# Nsight multiprocess flush retry

This is an effort-only interception of the existing benchmark's `nsys` executable lookup. It does not edit the benchmark, change the MoE work, or alter public API source. The original incomplete reports remain in `profiles/tmem-fitted5-transform2-nsys-001`.

Both original T32/T4096 reports contain 14 fused launches on seven devices; device 2 is missing. Its CPU launch APIs and both NVTX stage ranges are present. SQLite `DIAGNOSTIC_EVENT` explicitly reports 21 incomplete CUPTI events dropped for that process in both reports. The existing strict `audit_nsys_resources.py` assertion remains unchanged and rejects these partial reports.

NVIDIA documented a matching multiprocess range-stop buffer-loss issue (internal ticket DTSP-21073) and recommended ignoring API range end, then stopping a named session externally after the workers finish. This is evidence for testing that capture strategy here, not proof that the same internal bug remains in this exact Nsight release. [NVIDIA discussion](https://forums.developer.nvidia.com/t/question-when-prifilling-megatron-lm/350407)

The current Nsight guide documents that `capture-range-end=none` ignores API range endings, collection can end at application exit or an explicit stop, and collection end flushes trace buffers. The installed Nsight 2026.2.1 CLI confirms `--wait=all`, `--kill=none` and `--session-new` are supported. `--wait=all` is already the default; the changed control is `--capture-range-end=none`, while `--kill=none` makes the worker lifetime explicit. [Nsight Systems guide](https://docs.nvidia.com/nsight-systems/UserGuide/index.html)

## First retry: finite application exit

Copy this directory, preserving the `bin/nsys` symlink, into the remote effort root. Select/freeze the intended kernel source separately before running. The helper never restores source automatically; the existing profile launcher records actual source hashes. Root owns GPU execution.

```bash
cd /workspace/flashinfer-w4a16-megamoe
PATH="$PWD/candidates/nsys_capture_flush/bin:$PATH" \
FLASHINFER_NSYS_FLUSH_MODE=exit \
FLASHINFER_BENCHMARK_SOURCE_SHA=fe4f8132 \
bash profile_tmem.sh nsys tmem-fitted5-transform2-nsys-exit-001 32,4096 \
  '{"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"load_balance_mode":"atomic_counter","token_back_mode":"epi_warps"}'

python3 audit_nsys_resources.py profiles/tmem-fitted5-transform2-nsys-exit-001
```

Only label the source `fe4f8132` if those exact source files are restored; otherwise set an accurate overlay description and use the recorded hashes. This mode runs the original benchmark directly, permits every rank to call its existing `cudaProfilerStop`, and leaves collection open until the finite torchrun process tree exits naturally. The wrapper logs the complete effective command. Export and version subcommands pass through to the real Nsight binary unchanged. Extra teardown activity can be traced, but the existing NVTX stage filter excludes it from the named-stage CSV.

## Explicit external-stop control, if needed

Use this mode deliberately for a second run; there is no automatic fallback or report replacement.

```bash
PATH="$PWD/candidates/nsys_capture_flush/bin:$PATH" \
FLASHINFER_NSYS_FLUSH_MODE=external \
FLASHINFER_BENCHMARK_SOURCE_SHA=fe4f8132 \
bash profile_tmem.sh nsys tmem-fitted5-transform2-nsys-external-001 32,4096 \
  '{"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"load_balance_mode":"atomic_counter","token_back_mode":"epi_warps"}'

python3 audit_nsys_resources.py profiles/tmem-fitted5-transform2-nsys-external-001
```

This uses the same named-session options and inserts only `rank_tail.py` before the existing worker script. The tail executes the complete benchmark unchanged, then holds each successful worker alive after its cleanup. Once all eight ready markers exist, the outer wrapper issues `nsys stop --session=<exact generated name>`, releases the CPU-only tails, and waits for natural exit. Readiness/release markers remain beside the reports as evidence. The tail is outside the measured NVTX stages. Its waits are bounded at 240 seconds; the existing launcher also bounds the full process tree.

## Software CUDA trace control

The finite-exit hardware-trace retry still captured only seven devices. All eight processes reported 50/50 buffers, but device 2 alone lost 163 events whose GPU timestamps were unavailable. The external-stop retry reached all eight ready markers, then `nsys stop` failed with `StopRequest`; root released the exact worker tails for natural exit. Preserve both failed captures. Do not rerun external mode on this installation. The helper now releases the completed tails in `finally` if stop fails and propagates the error.

SQLite diagnostics explicitly identify hardware CUDA tracing. On Blackwell, `--trace=cuda` uses hardware tracing; the documented `cuda-sw` token selects software tracing. Installed Nsight Systems 2026.2.1 lists that token in `profile --help`. A software-trace retry tests the hardware timestamp collection path separately from worker completion; it does not establish the underlying bug in advance. [Nsight Systems CUDA trace modes](https://docs.nvidia.com/nsight-systems/UserGuide/index.html)

`FLASHINFER_NSYS_TRACE_MODE` is unset by default and preserves the benchmark's original trace arguments. The only accepted override is `cuda-sw`, replacing exactly the `cuda` token while keeping NVTX/NCCL and every worker argument intact.

```bash
PATH="$PWD/candidates/nsys_capture_flush/bin:$PATH" \
FLASHINFER_NSYS_FLUSH_MODE=exit \
FLASHINFER_NSYS_TRACE_MODE=cuda-sw \
FLASHINFER_BENCHMARK_SOURCE_SHA=fe4f8132 \
bash profile_tmem.sh nsys tmem-fitted5-transform2-nsys-software-001 32,4096 \
  '{"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"load_balance_mode":"atomic_counter","token_back_mode":"epi_warps"}'

python3 audit_nsys_resources.py profiles/tmem-fitted5-transform2-nsys-software-001
```

## Acceptance

- Both T32 and T4096 must have exactly 16 fused launches across eight devices; preserve the strict assertion.
- Every named routing/staging/fused/reducer row should have 16 instances; inspect diagnostics for incomplete GPU timestamps and missing buffers as well as counts.
- Record actual launch resources: expected two-group REG96/640 threads, grid(2,1,74), cluster(2,1,1), dynamic shared memory216576 bytes for this specialization. Do not equate Nsight's local-memory field with absence of intentional local arrays; use the separate SASS audit.
- Instrumented durations are excluded from CUPTI performance tables. This retry establishes trace completeness and operation/resource attribution only.

CPU checks passed: syntax, Ruff/format, five pure tests covering both rewrite modes, the optional software trace token, JSON/worker argument preservation, rejected unknown trace modes, and release after a failed stop. Run `python3 candidates/nsys_capture_flush/test_rewrite.py`. Hardware-trace retries failed as described above. Software trace with finite exit passed both T32/T4096: exactly 16 fused launches on all eight devices, every named stage row has 16 instances, and no dropped/incomplete CUDA timestamps are reported. The generic NVTX warning remains, with all expected measured-stage ranges individually verified. See `FITTED_NSYS_CAPTURE_AUDIT_001.md` for source hashes and diagnostic artifacts and `BENCHMARK_PROPOSAL.md` for the unapplied minimal integration proposal. No production source edit is part of these helpers.
