# Fixed warp-role performance pilot

Completed on eight GPUs after the final r2 runtime gate and root approval.
Frozen performance config: `6cea9dde460dac0e60b3ec209745697b6c577af549c5390cfd148db7ed33763b`.
Candidate patch: `e78b8c481061ce6584b7572ff21cf47f43853edf79f72c064e145d1ecf46e1b3`.
All source, timing helpers and selection-cache contracts remain frozen.
All 80 cells and the bounded follow-up diagnostics are archived; GPUs are released.
See [results](RESULTS.md), [winner diagnostics](DIAGNOSTICS.md), and
[drift repeats](drift-repeat/table.md). The diagnostics do not replace pilot rows.

- Control: retained `1e69d0a39`, with native winner selections reused from the
  completed retained rerun. The source check requires byte identity except the
  two previously recorded AST-identical formatting edits. No old timings enter
  the comparison.
- Candidate: final gated warp-specialization review snapshot, fresh native AUTO.
- 80 cells: V3 EP8, V41-flash EP4, K3 EP8, Nemo3-ultra EP8; W4A4, per-token NVFP4,
  MXFP8, MXFP4x8; 4, 64, 512, 4096, 16384 tokens. Both arms use `swap_ab=True`,
  unfused finalize. NV includes the input quantizer and the existing per-token
  recipe. No TRTLLM, legacy, or W4A16 benchmark execution.
- Native tuning remains eager for NV and graph-based for MX. Public measurements
  require CUPTI, CUDA graphs, cold L2, 10 warmups and 100 samples. Event fallback
  is an error. Candidate AUTO is followed by frozen C-A-A-C.
- Eight assigned GPUs (0–7), one model/family per GPU. W4A4 and per-token use
  separate public invocations to exclude W4A16 without changing the observer.
  MX formats share one invocation. There are 60 subprocess phases, 80 AUTO
  medians and 320 frozen medians (40,000 public CUPTI samples).
- The runner checks all source, helper, gate, config, runtime and reused cache
  hashes at every phase. Every timed operation must hit its frozen native
  selection; source arms must have identical cache keys and routing identities.
  Native C++ artifacts remain in verified persistent caches; CuTe source keys
  are strict and source-private.
- Report `100*(sqrt(C0*C3)/sqrt(A1*A2)-1)` alongside endpoint control drift and
  candidate spread. AUTO timings are diagnostic and excluded from speedups.

The three observer files are byte copies of the final retained-rerun observer.
`tools/freeze_config.py` performs CPU-only final source/gate binding. The gate
manifest must contain `complete`, `source_config_sha256`, and a nonempty `files`
mapping of absolute receipt/result paths to SHA-256 hashes.

After gate approval, on the devbox:

```sh
python3 tools/freeze_config.py --source-config ../r2/config.json \
  --gate-manifest ../r2/final-gate-manifest.json \
  --previous ../../retained-rerun --output config.json
python3 tools/launch.py --config config.json \
  --approved-config-sha256 <frozen-config-sha256> \
  --approved-candidate-patch-sha256 <gated-patch-sha256>
python3 tools/analyze.py --root . --output assembled
```

Run the eight model/family supervisors concurrently only after checking GPU ownership
and idleness. Preserve failed logs/receipts rather than resuming or replacing
them silently. This initial runner intentionally has no resume path.
