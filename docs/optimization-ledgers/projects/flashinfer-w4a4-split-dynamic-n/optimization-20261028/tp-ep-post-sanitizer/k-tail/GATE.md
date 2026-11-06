# Tail-only runtime gate

Frozen kernel `3fe308714e0c450d3370bdc1d4f57c17957e420421d0ff588447d72103b75f23`
on `d1767be1`. Only the final native MMA stage is peeled; no API or tactic change.
The source, patch, static proof and helpers are deployed to the persistent
`.../optimization-20261028/tp-ep-post-sanitizer/tail-only` root. The control is the
immutable `.../api-cleanup-20261028/full-validation/flashinfer` snapshot. Both
reuse the nine persistent native compiler-cache links; the candidate has its own
strict CuTe cache root.

No gate launches before the parent publishes the complete independent
150-case sanitizer release. `run_pair.py` requires and hashes that release.
Use primary GPU4 only; TP benchmark workers own primary0–3 and secondary0–2.

Initial smoke:

```sh
python3 "$TAIL_ROOT/gate-tools/run_pair.py" --name partial-smoke --gpu 4 \
  --config-ids 0,2,3 --hidden 384 --intermediate 384
```

This pairs control/candidate on NVFP4, MXFP8 and MXFP4x8, with static/CLC,
PDL off/on, one/two CTA, and balanced/skewed/empty/reactivated routing. It
compares48 final output storage-byte replays and24 generated GEMM pairs.
The helper preserves the public wrapper's launch and capacity calculations;
only explicit legal tactic selection and diagnostic code capture are overridden.

If the smoke passes, extend partial-K coverage to configs1,4,5,6,7,8,9,10
at H384/I384, then long/aligned loop controls at H256/I2304 and the minimum
NV64 tail at H128/I64 (192local experts to preserve meaningful CLC work).
Generated resources must have zero local-memory/stack spills; inspect uniform
register transfers separately rather than calling every R2UR a spill. Static
MMA sites can increase from peeling while executed MMA atoms decrease. Standard
CUPTI100-sample CAAC timing follows exact/codegen acceptance, reusing frozen
native winners and never rerunning the external baselines.
