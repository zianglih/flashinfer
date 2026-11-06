# W4A16 MegaMoE fixed F4 versus F8

This experiment measures whether flag_batch=8 is worth returning to the native AUTO catalog. Production source is unchanged at `19e8aebb541684df09e12cc79610338aa429a2cf`. The complete eight-sweep campaign passed. See [DECISION.md](DECISION.md) for the final table and recommendation to retain F4; [final-performance.md](final-performance.md) includes all selected tactics and per-sweep diagnostics.

- **Scope:** W4A16 MegaMoE only, EP4 and EP8. Each EP uses its own node, with no simultaneous GPU experiments on that node.
- **Candidate control:** `worker.py` replaces the module-global `bf16_nvfp4_candidates` in `flashinfer.moe_ep.cute_dsl.megamoe.bf16_nvfp4.autotune` with a wrapper around the original function. It copies the original eight dictionaries and changes only `flag_batch` to 4 or 8. `autotune_bf16_nvfp4_mega_moe` resolves this factory from its module globals at call time. Native candidate filtering, preparation, GPU-event graph scoring, collective rank-MAX winner selection, forward, graph capture and benchmark timer stay unchanged. Both values are existing supported config fields, not new kernel paths.
- **Native eight candidates:** group_hint 512/1024 × tile (256,128,256)/(256,64,256) × epi_warps/reuse_dispatch_warps; two-CTA instructions, scheduler depth2, epi_flag_batch=(2,4), atomic_counter load balancing, in-kernel FC2 reduction false.
- **Order:** F4 sweep1 → F8 sweep1 → F8 sweep2 → F4 sweep2 on each EP host. Every sweep gets a fresh knob cache. This ABBA order controls first/last effects; it does not remove thermal drift or native autotuner noise.
- **Workload:** global tokens `1,2,4,8,16,32,64,128,256,512,4096,8192,16384`, H7168/I2048/E256/topk8, BF16 activations, canonical NVFP4 weights, precomputed FP32 routes, runtime FP32 unit alpha arrays, default SwiGLU, routing weights in FC2, disabled in-kernel FC2 reduction, public forward with owned output handling.
- **Measurement:** three warmups then100 native CUPTI CUDA-graph cold-L2 samples per row and sweep. Aggregate the first-to-last GPU activity span by rank MAX for each iteration. Pool both sweeps into an untrimmed200-sample median. Same deferred-CUPTI-finalize wrapper as the prior three-arm comparison. No Split or W4A4 benchmarking.
- **Timing boundaries:** preparation, weight quantization, compilation, AUTO tuning, graph capture, warmup and L2 flushing stay outside final timing. Native forward input staging, alpha copy and output handling remain inside. Native AUTO scores use hot graph GPU-event timing, distinct from the final cold-L2 CUPTI measurement.
- **Evidence:** source and helper SHA256 manifests before/after, bootstrap/runtime/node/GPU identities, all-rank inputs/routes/weight hashes,100 raw rank spans and100 rank-MAX spans per row, all native eight-candidate10-event scores per rank, selected tactics, and two extra untimed eager output checks. Every rank's repeated BF16 output must match bits and be finite. All four runs for each EP must match output hashes. This is a focused perf/output consistency check, not independent reference or sanitizer coverage and not checking each timed graph replay.
- **Retention:** focus on decode4–512, exclude1/2 from the decision, inspect4K/8K/16K prefill individually. The reported lower-of-two-arm estimate is optimistic and is not a measurement of joint16-candidate AUTO selection.

Runtime files are `run_ep_campaign.py`, `run_sweep.py`, `worker.py`, `cupti_lifecycle.py`, `render_results.py`. The controller validates each completed sweep before launching the next. `validate_harness.py` is a local CPU-only synthetic integrity check; it produces no benchmark evidence.

Launch on a prepared node, using its source-owning environment:

```sh
.venv/bin/python -B run_ep_campaign.py \
  --source /workspace/PROJECT/flashinfer \
  --revision 19e8aebb541684df09e12cc79610338aa429a2cf \
  --image nvcr.io/nvidia/pytorch:26.05-py3 \
  --bootstrap-receipt /workspace/PROJECT/source-ready.json \
  --compile-cache /workspace/PROJECT/cache \
  --output /workspace/PROJECT/results/campaign --ep 4
```

After all eight sweeps finish, render using all EP4/EP8 `ep*-f*-sweep*` directories as positional arguments to `render_results.py --output final-performance`. The validator rejects incomplete rows, mixed source/helper identity, changed fixtures, wrong flag, candidate score/winner mismatch, output mismatch, overlapping/incorrect ABBA order, corrupt rank-MAX values and incomplete CUPTI lifecycle receipts. Per-sweep and25-sample quarter medians are retained without trimming.
