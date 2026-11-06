# FC2 and deterministic-finalize overlap diagnostic

Use this after the ordinary benchmark. The default is four profiles: 4096 tokens,
per-tensor/per-token activation scaling, baseline/candidate unfused finalize.
Each profile captures 20 cold-L2 CUDA-graph replays using the existing native
`bench_moe_deepseek.py --profile-cuda --profile-backend cute-dsl` implementation,
EP8/TP1 and initial activation quantization included. `--backends cutedsl` is
required by the native profile-mode parser; the profile-backend filter selects
W4A4 alone.

This is a fixed-tactic mechanism diagnostic. Both arms load an identical snapshot
of the baseline production-selected cache with `--no-autotune`. This differs from
the primary benchmark's independently autotuned production-dispatch comparison.
The external worker records actual selected tactics; the shell checks equal cache
hashes and equal selected tactics and rejects a MoE fallback tactic. Preparation,
cache loading, compilation, and graph capture happen before the profile range.

## Commands

Copy `scripts/profile_finalize.py` and `scripts/run_profile_finalize.sh` to the
same relative paths on the devbox. The existing root-level benchmark,
`overlays/<candidate>/flashinfer`, and baseline tactic caches must already exist.
Do not run concurrently with the performance benchmark.

```bash
cd /hai-workspace/fi-w4a4-finalize
bash scripts/run_profile_finalize.sh combined 4096
```

Replace `combined` with the candidate overlay name. For a decode-only follow-up,
use `1`; for both decode and prefill in one run use `1,4096` (eight profiles).
The scripts refuse to overwrite existing profile directories.

```bash
# Decode follow-up with the same settings and selected caches:
bash scripts/run_profile_finalize.sh combined 1

# Force the Torch CUDA profiler if Nsight Systems is unavailable:
PROFILE_BACKEND=torch bash scripts/run_profile_finalize.sh combined 4096
```

`auto` prefers installed `nsys`. Its command uses CUDA-profiler-API capture,
`--trace=cuda,nvtx --cuda-graph-trace=node --sample=none --cpuctxsw=none`, then
exports SQLite. The fallback wraps the native benchmark externally, starting and
stopping `torch.profiler` where that benchmark invokes `cudaProfilerStart/Stop`;
it exports a Chrome trace. No FlashInfer or benchmark source is modified.

Each directory `artifacts/profiles/<arm>/<scale>/tokens-<N>/` contains the full
command, cache/benchmark hashes, runtime import identity, cache snapshot, selected
tactics, profiler log, raw trace, kernel list, per-iteration `overlap.csv`, and a
median `summary.md`. Nsight traces also retain their `.nsys-rep` file.

## Interpretation and extraction

The table reports FC2 duration, finalize duration, their overlapping GPU-activity
interval, the positive launch gap, and the combined FC2-to-finalize span. Finalize
duration includes its PDL wait. An overlapping activity interval establishes
overlapping kernel lifetimes; it does not establish that the reduction reads FC2
outputs before FC2 finishes. The useful overlap is launch/preamble/metadata work,
with dependent output reads protected by the wait. The old warp-specialized FC2
tail may already signal before its last epilogue work completes.

Use the ordinary benchmark for latency claims. Profiling changes overhead and may
affect scheduling. Compare absolute pair spans alongside overlap: a longer
finalizer interval can simply reflect more time waiting after an earlier launch.

Extraction requires exactly 20 FC2 and finalize kernels and same-stream pairing.
If the installed compiler uses different generated kernel names, the raw trace
and `kernels.csv` are retained. Inspect names and rerun only extraction:

```bash
python scripts/profile_finalize.py extract \
  artifacts/profiles/combined/per-token/tokens-4096/trace.sqlite \
  --output artifacts/profiles/combined/per-token/tokens-4096 \
  --expected 20 --fc2-regex 'GroupedGemmFinalizeFusion' \
  --finalize-regex 'ExpandedFinalizeKernel|expanded_finalize|moeUnpermuteKernel'
```

For Torch traces, pass `trace.json` instead. Missing CUDA graph-node events are an
unsupported capture result, not zero overlap; the extractor fails explicitly.
Nsight and Torch results should be compared within the same profiler backend.

Prepared and syntax/extractor-checked locally; no GPU profile has been run by the
script author.
