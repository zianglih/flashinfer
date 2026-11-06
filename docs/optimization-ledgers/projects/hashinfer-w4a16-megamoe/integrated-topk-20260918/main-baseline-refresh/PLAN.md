# Fresh main68 versus selected7dc performance plan

Prepared locally only; no staging, GPU commands, or source edits. Retain `7dc96269`: b215 has no aggregate gain and a clear within-arm 16-token regression.

Use **one fresh A1/B1 pair on hu-pdx-99, same boot** after both NCU phases close. A1 is main `68eb1fefb84701131213e423f2c20cf953bb5918`; B1 is measured selected `7dc9626909834bc70209e09784e9dfdebadceff2`. This refresh compares the full PR result with main. Keep the earlier 04/1ad/7dc table as historical incremental evidence; do not divide a fresh main arm by an older or cross-node candidate arm for the replacement headline table.

Minimal preparation:

1. Copy the existing `paired-benchmark/run.py` (3c4c6825) into a new helper directory. It already runs a complete serial A1/B1 pair and accepts exact candidate commit/manifest arguments. Change only its obsolete secondary setup SHA, hostname and boot binding to the current primary proof (4c6aa1a8; hu-pdx-99; af9b307c-73d6-415d-898c-6cb2664707e5), plus namespace/prose/unused port. Both sources have 104 files, so no source-count adaptation is needed.
2. Reuse all six worker/benchmark/timer/owner/comparator/fingerprint helpers byte-for-byte. Use the already frozen main archive/manifest and selected7dc archive/manifest; no source rebuilding or new fixture generator. The manifest/source hashes were checked locally for this plan.
3. Bind fresh output directories, actual source paths, the unchanged primary Python/environment proof, and the exact selected source pins. Use the existing cleanup/timeout/idle and chunked collector patterns. Keep each arm's CuTe/CUDA/Triton/Torch and AUTO caches separate and fresh. Clear profiling/debug flags as the existing driver does.
4. Run both full sweeps, then reuse the existing strict comparator and audit patterns once. No extra correctness or codegen suite is needed: this is a fresh timing pair on already qualified source, with the worker's existing untimed finite/repeat checks and full cross-arm output comparison.

Unchanged workload and timing:

- EP8, H7168 / I2048 / 256 experts / top-k8; BF16 activations, directly initialized NVFP4 weights and precomputed routing.
- Global tokens `1,2,4,8,16,32,64,128,256,512,1024,2048,4096,8192`.
- Public forward, deterministic combine (`--no-fused-finalize`), AUTO over four tactics, O3 and maxregs96. Main includes standalone staging/reduction; selected7dc fuses both into MegaMoE. Routing selection, initialization, AUTO and compilation stay outside GPU timing.
- `--warmup 3 --iters 100 --timing cupti --cuda-graph --megamoe-knobs auto --log-timing-samples`, cold L2, each sample aggregated as rank maximum. Retain all 100 samples per row, including first-sample outliers.
- Equal input, route and weight hashes across all eight ranks; all 112 rank/token outputs finite and BF16 bit-exact. Selected tactics may differ legitimately; report them, never force a winner for parity.
- Show all 14 raw median/MAD rows, main/selected speedup, and 8–8192 geometric mean. Retain quarter medians to disclose drift. One serial pair does not eliminate temporal effects.

Boundaries/risks:

- Do not reuse old hu-pdx-115 main timings. The helper's old secondary metadata must be replaced; its actual workload and timing code remain unchanged.
- Primary proof/boot/environment must still match immediately before each arm. After NCU, require all profiler/worker groups gone and all GPUs idle. If the node or environment changes, make a new bounded proof rather than relabeling existing evidence.
- Main68 is the requested fixed PR base, not a claim about the latest upstream main. The canonical PR head 948e9a1 differs from selected7dc only in README and an autotuner docstring; label the measured source7dc exactly, with that documentation-only qualification.
- A fresh main-only arm plus the older sealed7dc arm is cheaper but leaves a wider uncontrolled time gap. Prefer the existing full two-arm driver for the promised final PR comparison.
