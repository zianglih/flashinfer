# Bounded FC1 protected-prefix experiment

Review copy: `flashinfer-fc1-prefix-review`, based on `d02c487a15d0636e902c3f7a5e0bf7cf4a03156d`, with one unstaged shared-core change. `source-proof.json` and `candidate.patch` freeze the source. No new tactic axis, model/dtype profitability rule, overlap allowance, wrapper setting, or register-role policy is added.

The implementation extracts the current activation transform and finish/store work into two reused helpers. Only the first `overlap_activation_steps - 1` protected slabs are retained in registers. The final protected slab follows the original direct path, including release immediately after the protected TMEM operations; its output is then finished, followed by the saved prefix's output. All unprotected slabs retain the existing traversal. The single-slab and inactive paths have no additional buffer or output reorder.

The buffer contains activated FP32 values: 16 per gated slab or 32 per ReLU² slab. The capacity-derived policy currently allows at most two protected slabs, so only one extra slab is retained. Reverse traversal, partial-slab predicates, and the virtual slab mapping across M512's two channel tiles are preserved. No extra TMEM transpose, reduction, barrier, or arithmetic expression is introduced.

## Difference from earlier rejected overlap experiments

Relevant prior evidence is under `scripts/perf_round_20261027/epilogue-overlap` and `register-overlap`.

- **Earlier V1:** stored all protected fragments, then released after finishing the last per-token activation. The compiler placed its release 269–276 operations after the final TMEM read. This candidate retains the baseline release *inside* the final slab's transform, before per-token or ReLU² activation. An earlier buffered per-token slab is activated before buffering to reduce its saved payload.
- **Earlier V2:** moved all per-token activation after release, keeping both protected up/gate pairs live (64 FP32 values per lane before additional temporaries). It achieved early release but had a 184-byte stack and 83 LDL/32 STL sites, so it was rejected before timing. This candidate buffers only the first activated 16-value gated fragment; it does not retain the last raw up/gate pair across a separate protected-prefix loop.
- **Register-role composition:** tried to repair V2's resource failure through independent role redistribution. This candidate leaves register roles untouched and must pass the resource gate on its own.

These are structural differences, not evidence of a performance win. Actual resource allocation and release placement must be checked before timing. If this version spills or repeats V1's delayed release, stop rather than adding another resource policy.

## Gate

`probe_chain.py` adapts the passed source-paired bulk-drain r3 graph gate. It uses the current-nemo-mx control source and the frozen candidate, verified native-cache reuse, private DSL caches, and GPU6. No AUTO or timing runs in this gate.

Eight explicit native cases cover standard gated NVFP4, SiTU/one CTA, per-token gated NVFP4, non-gated ReLU², per-token ReLU² with M512/N128, an inactive NVFP4 control, and one-slab MXFP8/MXFP4x8 controls. Each captures PDL off/on and replays balanced partial routes, zero local work, and reactivated skewed routes. The 2049-token workload proves FC1 work exceeds launch residency in balanced cases, exercising persistent phase turnover.

Both sources consume the same serialized input bundle. The per-token recipe uses MSE 4over6, E4M3 max256, error fast math enabled, and base quantization fast math disabled. Weights retain standard quantization. Validation compares canonical live FC1 payload and generated SF bytes by unique expanded-route ID, and final output bytes. Inactive padded rows are excluded from intermediate comparison. It also records compiled geometry, ownership fields, PTX/cubin/resources, and stops on nonzero stack/local memory or PTX local accesses.

The proposed later screen is the ten actually active native winners from `../fc1-prefix-audit/coverage.csv`, plus inactive controls, with frozen tactics and the established public cold-L2 C-A-A-C timing. No timing is authorized by a gate merely starting; send the source/resource/exactness result for review first.
