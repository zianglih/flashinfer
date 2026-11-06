# Shared CLC policy comparison

A is the current retained kernel with independently configured FC1/FC2 CLC (720 raw tactics). B changes only the scheduler tactic policy to one shared on/off flag (360 raw tactics). Both arms start with fresh native selection caches; no historical kernel or winner cache is substituted.

`run_screen.py` runs one model/family on one exclusively assigned GPU. NVFP4 uses A–B–B–A; MX uses B–A–A–B. The first pair performs native AUTO before public timing, then the reverse pair replays each arm's saved selections without tuning. Every process uses the public benchmark with 10 warmups and 100 cold-L2 CUDA-graph CUPTI samples. NVFP4 includes initial activation quantization, and the public per-token recipe is preserved. MX inputs are prequantized. CuTe fused finalize is disabled. No TRT arm is rerun. W4A16 is the unchanged incidental control printed by the existing NV selector.

The 13 tokens are `1,2,4,8,16,32,64,128,256,512,4096,8192,16384`. Per-cell speedup is `sqrt(A1*A2/(B1*B2))`. Retention excludes tokens 1/2 and the unchanged W4A16 control. Decode geometric means cover eight points (4–512), prefill means cover 4096/8192/16384. Partial groups are not summarized as complete geometric means.

The observer records raw public timings, full winner caches, exact existing route hashes, requested scheduler flags, native admission counts and tactic-list hashes. It does not change the public benchmark source, reorder candidates, force winners, or add a timed GPU operation. A requested CLC flag remains subject to the production kernel's existing legal static fallback. Native search wall time includes JIT, cache IO, profiling and pre-warm; concurrent workers share CPU resources, so this is campaign cost rather than an isolated compiler comparison.

Config schema (all paths absolute on the remote host):

```json
{
  "python": "/absolute/venv/bin/python",
  "output_root": "/absolute/campaign/results",
  "arms": {
    "A": {
      "repo": "/absolute/full/flashinfer",
      "source_receipt": "/absolute/full/source.json",
      "workspace_base": "/absolute/full/cache/source_hash"
    },
    "B": {
      "repo": "/absolute/shared/flashinfer",
      "source_receipt": "/absolute/shared/source.json",
      "workspace_base": "/absolute/shared/cache/source_hash"
    }
  }
}
```

Source receipts use the existing `head`, `patch_sha256`, and `source_sha256` fields. Source and benchmark hashes are verified before and after every process. Native C++ cache sharing is configured by the project's verified persistent-cache helper; DSL namespaces remain source-private. No worker is launched by importing these scripts.

```bash
python run_screen.py --config /absolute/campaign/config.json --model v3 --family nvfp4 --gpu 0
python run_screen.py --config /absolute/campaign/config.json --model v3 --family mxfp --gpu 1
python run_screen.py --config /absolute/campaign/config.json --model v41-flash --family nvfp4 --gpu 2
python run_screen.py --config /absolute/campaign/config.json --model v41-flash --family mxfp --gpu 3
python run_screen.py --config /absolute/campaign/config.json --model kimi-k3 --family nvfp4 --gpu 4
python run_screen.py --config /absolute/campaign/config.json --model kimi-k3 --family mxfp --gpu 5
python summarize.py --campaign /absolute/campaign/results --output /absolute/campaign/summary
```

The runner refuses an existing result directory. This deliberately prevents an interrupted experiment from silently mixing receipts. Root orchestration owns source deployment and launch approval.
