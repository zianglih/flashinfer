# Fresh managed-cache validation of PR7290

Measured source: `d1767be1f42fdc371f90db4fb06598299ea32845`. Frozen source and persistent C++ cache links are in `source.json`; runtime and helper hashes are in `runtime.json` and `helper-manifest.json`. Canonical source is untouched by this harness.

C3 devbox `fi-moe-nvfp4-port-1026`, namespace `infra`, B300, image `nvcr.io/nvidia/pytorch:26.05-py3`. Eight model/family workers now run independently on GPUs0–7. The first six started on0–5; after the separate tests passed and released6–7, the two queued N3U jobs started there. `expansion-receipt.json` records the controller-only handoff; existing workers were untouched. The worker never shares a GPU with another worker. Compilation storage persists; no caches are deleted.

Eight jobs: V3 EP8, V41F EP4, K3 EP8, N3U EP8 × NVFP4/MXFP. NV measures W4A4, per-token and W4A16; MX measures MXFP4x8 and MXFP8. TP1. Tokens `1,2,4,8,16,32,64,128,256,512,4096,8192,16384`; 1/2 run but are excluded from display and retention.

Each job freshly tunes with the benchmark's native managed-cache/policy contexts, then runs A1/A2 in separate processes with tuning disabled. Policy `auto` retains native NV timing semantics; MX uses the public graph MeasurementPolicy. The native fallback tactic participates as intended by the shared tuner. No old JSON winner cache is loaded. Each new managed cache is content-frozen after tune; A1/A2 must replay its winners and leave it unchanged.

All accepted public timings use CUDA graphs, cold L2,10 warmups,100 CUPTI samples. Event fallback, profiling during replay/capture, cache misses, source mismatch, route mismatch, and median/raw-sample disagreement fail the job. NV input quantization is included; MX input is prequantized. SwapAB finalization is unfused. Tune-pass public timings are retained as diagnostics but excluded from final medians. Two accepted pass medians are geometrically combined. Expected accepted evidence:260 cells,520 medians,52,000 raw samples.

All TRTLLM/non-swap/pre-PR baselines are reused from existing evidence. All five current CuTe formats are refreshed, including W4A16. The report keeps44×9 display cells and the existing red/green plot style.

`benchmark-tools/observe_benchmark.py` adapts the existing full-rerun observer only for the managed directory and policy context. It also observes no-profiling replay and fallback winners. `arm_contracts.py` and `nested_timing.py` are copied unchanged. Tuning wall spans distinguish inclusive/exclusive profile and `cute.compile` API time without additional CUDA synchronization; compile spans include SDK cache work.

Collect after all eight workers complete, reusing the established archive/fetch implementation:

```sh
python3 optimization-20261028/warp-polish/final-polish/fetch_evidence.py \
  --campaign api-cleanup-20261028/full-validation/campaign.json \
  --output api-cleanup-20261028/full-validation/full-evidence
python3 api-cleanup-20261028/full-validation/build_manifest.py
python3 api-cleanup-20261028/full-validation/report/assemble_report.py \
  --manifest api-cleanup-20261028/full-validation/measurements.json
```

Live receipts remain under remote `BASE/api-cleanup-20261028/full-validation/runs/<model>-<family>/receipt.json`; raw paths are `{tune,a1,a2}/results.json` with matching sibling logs. `status_remote.py` is read-only. No PR publication is performed by these scripts.
