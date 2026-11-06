# Independent final K3 / W4 evidence review

Passed, read-only CPU audit. Reproducer: `audit_k3_w4_final.py`; complete receipt: `k3-w4-final-peer.json`. No source changes or GPU work.

## K3 EP8 MXFP4x8 16K

Replayed all 1,600 CUPTI samples from their actual launch/activity timestamp joins, every phase median, all64 quartiles and telemetry windows, frozen routes/tactics, source/fetch/guard hashes, and 32 directly captured returned-kernel images. No sample filtering, retuning, event fallback, or compiler-option changes. Each source pair stays on its original physical GPU. Native role geometry is identical across all four order blocks.

| Variant | CAAC | ACCA |
|---|---:|---:|
| writer-r1 | +3.579297% | -1.232974% |
| static-sf | +5.147925% | +0.511291% |

Metric is sqrt(C1×C2/(A1×A2))−1 using every100-sample phase median. Component extension deltas use arithmetic means of the two phase medians and are not sums of overlapping-kernel durations.

Writer FC1 cubin is byte-identical across all eight control/candidate phases of both order blocks; writer FC2 differs. Static-SF changes both main images. All32 loaded functions have zero local bytes. Captures bind exact returned library/kernel handles, unchanged compile options, resources and retained PTX/cubin/SASS hashes.

The report accurately preserves the initial loss and later order reversal; +3.58% CAAC is not a throughput win because ACCA is−1.23% and repeat spreads reach5.89%. It also does not prove that a smaller regression is absent.

Native C++ release provenance was independently checked against build-log completion times, file mtimes, ELF hashes and actual Ninja text: `moe_utils`, FP4 quantization and MXFP8 quantization all match the final release artifacts and finish before timed samples. The old debug `dsv3_fused_routing` image was not loaded by these runs. This remains retrospective filesystem/build evidence, not separately captured process mappings; the report states that distinction.

## Full W4 AA refresh

All104 model/topology/token cells and20,800 raw CUPTI samples pass independent replay. All8 jobs×2 phases match frozen routes and original recorded choices, with224 actual LOCAL0 loaded functions. Ten recorded deterministic defaults resolve through40 exact native stage/library joins. Base822, benchmark/tuner/kernel source hashes and full tracked manifests are frozen pre/post; only the R2 shared W4 utility and unrelated swap writer file differ from control. The W4 timed implementation uses helper SHA `d3afcec4…`; the swap writer delta is outside this backend.

Every row in `report/cells.csv` equals the geometric mean of its two complete100-sample medians; all13 token rows remain, and only1/2 are marked excluded from retention. This is AA absolute-latency refresh, with no contemporaneous control or causal speedup claim.

Repeat spread reaches9.079% (V3 EP16K). Of832 quartile windows,4 have no telemetry (K3 EP token1 second pass);53 have a non2032MHz **median** or nonzero clock-event reason. Including brief minimum-clock dips gives59 windows. The raw minima and missing windows are retained. Therefore the existing53 count is correct under its median-based definition, but should not be described as every transient clock deviation.

No blocker found for using these results with those boundaries. Instruction-cleanup retention must rely on the separate causal/codegen evidence; these noisy K3 diagnostics and the W4 AA refresh do not establish an E2E speedup.
