# Shared quantizer and pipeline audit

Audited the retained PR delta against002529e in `nvfp4_quantize.py`,
Blackwell `utils.py`, and `custom_pipeline.py`. No source edits made.

- Per-token quantizer: bounded grid-stride work, narrow CTA width, per-group
  live-row masking, SF physical pitch and startup PDL are all used. The grouped
  options are passed by `fused_moe.py` through keyword dictionaries. Device
  counts/limits are read after the PDL wait; inactive rows zero their SFs; each
  multiwarp row completes before reuse of its reduction buffer. Both narrow
  singlewarp reductions omit the cross-warp reduction. No fallback/version
  compatibility path was identified among these additions.
- The two row-address/amax/quantization implementations and their64-bit pointer
  construction already exist in002529e. Factoring them here would widen the
  cleanup beyond the PR additions and alter kernel trace structure; leave them.
- `PipelineUmmaAsync.create(defer_sync=False)` preserves the existing barrier
  initialization default. The new opt-in is needed by retained callers that
  batch initialization; removing either fence path is not a cleanup.
- `tma_gather4` and `release_gpu` are both used by retained swap-AB and W4A16
  kernels. CTA-group and multicast branches produce required distinct PTX
  addressing/completion behavior. No redundant branch or unused helper found.

## Read-only test and oracle findings

- The sanitizer has one redundant axis: `apply_topk_in_fc1=False` is a singleton
  pytest parameter and asserted false, but the worker CLI has no such knob and
  the worker receipt hardcodes false. Removing the pytest parameter and its
  parent-body assertion would preserve all150 worker configurations; current
  IDs include `topk_fc2`, so retain that ID if scripts rely on it. No edit made.
- W4A16 and blockscaled swap-AB combine references are superficially similar
  but not interchangeable without a larger refactor: W4 handles preweighted
  route terms and always emitsBF16; swap's Triton helper supports BF16/FP16 and
  never reads masked, potentially uninitialized route rows. Do not deduplicate
  them in this behavior-preserving cleanup.
- K96 plan observation, explicit mode rejection, source-bound sanitizer compile
  ownership and coverage receipts encode actual validation contracts; they are
  not redundant guards to remove for line count.

All three owned source files are byte-identical to658a and parse successfully.
No GPU work, sanitizer, commits, pushes, or production tests were run by this
audit worker. Parent coordinates any later focused GPU validation.
