# Paired 4over6 error recurrence

The current c1ac K640 per-token quantizer contains two separate scalar error recurrences. Pair candidate4 and candidate6 in the two independent FP32 lanes; keep input index order 0 through 15, explicit RN subtraction/multiplication/addition, and scalar absolute value for MAE. Replace the existing private helper and its two calls with one tuple-returning call. No new helper, policy, public argument, dtype branch, reduction tree, FP4 conversion, scale-selection order or max-chain change.

## Source and arithmetic boundary

`source_proof.py` executes the actual old/new helper ASTs with symbolic floating-point operations. Each output lane equals the original ordered graph, with exactly 16 additions. Replacing only the new helper and its call restores the entire original module AST. Strict-error scoring remains unchanged; the new helper applies only to `err_use_fast_math=True`, for either base-quantization math choice and either FP16/BF16 input. The existing FP16 candidate decode and its RN FP16 products are unchanged.

PTX `add/sub/mul.rn.f32x2` applies independent FP32 operations to each lane. Explicit RN, operand order and absence of FTZ/FMA are required. MAE has no packed abs equivalent here, so it retains the same scalar abs operations. PTX does not promise NaN payload identity; no such guarantee is inferred. Native/exact checks must cover classification/output behavior rather than treating symbolic finite-value equivalence as a substitute for execution. [PTX floating-point instructions](https://docs.nvidia.com/cuda/archive/13.2.0/parallel-thread-execution/index.html#floating-point-instructions-add).

## Existing instruction evidence

Current retained K640 image `ff00cf52bf25550ace511512220c9baf801c3cfd55d29524e6026c1cfec05ba0` is bound by `profiling/n3u-tp-per-token-16k/retained-c1ac/quant-640-ptx-reuse.json`. Its same-image PTX at lines 1138–1424 has 32 scalar RN subtractions, 32 scalar RN error multiplications and 32 scalar RN additions, with no packed operations. The actual SASS has no FADD2/FMUL2. This is not a runtime function-call optimization: CuTe helpers are inlined.

Nominal arithmetic sites per 16-value scoring block are 96 scalar to 48 packed for MSE, or 96 scalar to 64 instructions for MAE (32 scalar abs retained). Packing may add moves and change scheduling or register liveness. The actual retained profile has 61 registers, 64 threads, LOCAL0, 16 resident CTAs; instruction issue is 78.74%, DRAM 18.31%, barrier 4.72%, math throttle 5.81%. This motivates a bounded native probe, not a throughput claim.

The exposed CUDA implementation in `csrc/nv_internal/tensorrt_llm/kernels/quantization_utils.cuh` interleaves candidate4/6 scalar scoring in the same order, but does not explicitly use packed FP32. No matching generated CUDA quantizer native image was established by this audit; compiler vectorization there is unknown.

## History and qualification

Bounded history lookup found no tested paired-candidate error recurrence in either CLOSED_LEADS index or the prior per-token warp-reduce, paired-width, two-blocks and handoff-475 notes. Paired-width refers to two SF blocks per lane, not two candidate errors. The reverted max-chain reassociation and rejected scalar-hoist spill are separate; the latter reinforces the liveness gate.

Use the existing scalar-hoist exact/native harness with retained c1ac versus this one-file overlay. Quantizer `cached_ops` must be isolated per arm; the four immutable release C++ modules may be shared after hash/no-op checks. First pilots cover actual BF16 K640 recipe MSE256/error-fast and a supported FP16 error-fast stress case, with a cheap unchanged strict-error control. Keep native resource guards, compile options, live-row/graph checks, output-byte comparison and all prior failed evidence. No performance timing is authorized before native/resource/exact review.

The public quantizer also supplies the timed TRTLLM PER-TOKEN input stage. If retained, affected TRTLLM denominator rows require fresh measurement; historical published rows must not be relabeled as this candidate.

Current status: **rejected after the complete 42-cell CAAC screen**. Source/proof/hooks, independent source/native peers, six exact arm calls with 24 graph replays, and 26 existing-reference tests passed at `5f232629`. Affected native pilots lower instructions and registers; the strict control remains byte-identical with its inherited local storage. However, CuTe PER-TOKEN averages −0.3062% and TRTLLM PER-TOKEN −0.1183%, with tight normal-clock N3U TP prefill losses of −2.8275% and −3.6937%. All 23 negative cells and all clock observations, including three missing quartiles, are retained. See [final results](RESULTS.md), [full primary screen](performance/RESULTS.md), and [independent raw replay](../../audits/paired-4over6-error-full-data-peer.json). No rescue or further timing. The source/patch and unavailable first attempt remain preserved; only the inactive local review worktree/branch is retired. Canonical c1ac and PR evidence remain unchanged.
