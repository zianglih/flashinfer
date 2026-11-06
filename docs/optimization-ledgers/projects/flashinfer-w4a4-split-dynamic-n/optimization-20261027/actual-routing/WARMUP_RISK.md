# Actual routing is not automatically representative routing

Read-only audit; no serving changes or additional GPU experiments were made.

## Concrete serving warmup source

Local SGLang checkout `sglang/` is at
`010eb729bea2b7ef2bcd572a72c171f75ad900fb`. Its unrelated MoE integration
review edits are preserved; the runner files cited below are unchanged.

- `python/sglang/srt/model_executor/runner/base_runner.py:96–102` initializes
  dummy input IDs, embeddings, request indices and positions to zero.
- `base_runner.py:257–285` performs the FlashInfer warmup once and supplies
  `_autotune_buffers()` to `_flashinfer_autotune`.
- `base_runner.py:392–416` invokes `_dummy_run` inside the FlashInfer
  autotuning context; `_dummy_run` directly slices supplied input-ID and
  position buffers at562–565.
- `runner/eager_runner.py:155–175` allocates decode-shaped dummy buffers for
  this forward. `decode_cuda_graph_runner.py:729–742` instead reuses the
  static decode graph buffers. These are initialization inputs, not a
  trace of incoming requests.
- `runner/flashinfer_autotune.py:290–370` runs the model warmup under
  `autotune(True)` and `autotune_v2(mode="tune")`, then persists winners.

This does not prove the resulting model logits are all zero: learned
embeddings, attention state and model-specific routing intervene. It does
establish that supplied warmup routing can differ materially from live
request routing. Repeated dummy tokens can produce concentrated expert
choices, including little or no local work on some EP ranks.

## What the proposed hook does and does not guarantee

The source/GPU gates prove that tuning sees the supplied workload, preserves
input bytes and cache identity, and remains capture-safe. They do not prove
that the supplied workload is representative.

Only the exact full-shape bucket uses actual inputs. A single maximum-size
warmup still profiles all smaller buckets synthetically. The matching bucket's
winner is persisted under the same shape-only key; later calls with another
routing distribution reuse it. A zero-local-work warmup could therefore rank
mostly launch/prepare/combine overhead, then reuse that winner for substantial
live GEMM work. No proposed runtime host read, distribution key, public knob,
or per-model special case addresses that issue.

## Bounded follow-up if the two-cell experiment improves performance

Do not expand before the current frozen comparison is complete. If promising:

1. Freeze both naturally selected native winners. Evaluate them on the same
   retained source, with exactly the same weights and activation inputs, so
   comparisons isolate tactic generalization rather than kernel changes.
2. Generate several independent router seeds through the benchmark's existing
   routing method. Keep top-k, EP offset, shape, scale semantics, input
   quantization and the100-sample CUPTI C-A-A-C schedule unchanged.
3. Add valid routing-skew stress cases with unique expert IDs per token:
   concentrated but nonzero local work, repeated hot-expert choices, and an
   EP rank receiving no local routes. The last case is a degenerate warmup
   diagnostic, not a retention speedup target.
4. Record local-route totals, active-expert counts and count histograms for
   each profile; compare medians and drift for both winners on each. If
   evaluating the policy rather than just the initial winners, independently
   tune on a concentrated/empty warmup and evaluate those naturally selected
   winners on the same realistic holdout routes. No forced winner enters a
   native AUTO run.

Retain only if improvement survives held-out routing without substantial
regression. Failure would argue against universal actual-input profiling;
correcting the shared helper's zero-quota bug or studying Hopper-style seeded
uniform synthetic routing would be a separate general-policy experiment.
Neither alternative has been changed or measured here.
