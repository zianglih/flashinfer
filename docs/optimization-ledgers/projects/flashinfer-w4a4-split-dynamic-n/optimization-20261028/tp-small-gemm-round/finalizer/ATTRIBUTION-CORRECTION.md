# Correction: public finalizer affected-cell classification

This source-bound correction supersedes the affected/unchanged interpretation in `RESULTS.md`, `analysis.json` and `cells.csv`; their original bytes/raw timing are preserved. No run was repeated and the candidate remains rejected.

The experiment removed `and input_is_expanded` from the existing prefill geometry guard. Frozen105474 `_moe_core_impl` already calls `moe_unpermute(input_is_expanded=True, _output_workspace=...)`, including compact swap-AB output. W4A16's launcher omits that argument and uses the helper'sFalse default. The physical compact layout therefore does **not** imply the host flag isFalse: original mapping is still used only for validity and the private dense index supplies the address.

`audit.py` classified every V3/V41F prefill backend as affected, omitting this call-site distinction. The36-cell group contained28 unchanged scaled cells. Correct classification is8 W4A16 cells; the1-line candidate changes4→7vectors for V3 and4→5 for V41F. All other136cells have unchanged geometry. In particular, the old V3EP MXFP4x8−3.501% row is observed unchanged-source variation, not evidence of a candidate-induced regression. No cause or noise label is inferred for that variation.

| Correct group | Cells | Geometric speedup | Worst | Best |
|---|---:|---:|---:|---:|
| affected | 8 | -0.554918% | -1.611653% | +0.850434% |
| unchanged | 136 | -0.018097% | -4.401449% | +2.129296% |

The actual affected W4A16 group still provides no basis for retention. The standalone input_is_expanded=False exact/codegen cases remain valid and show increased registers, but they are not evidence that scaled public calls changed. Native raw observations, all57600samples, source/winner bindings and external benchmark data are unchanged.

`correct_attribution.py` verifies historical call sites/defaults and benchmark dimensions from the archived source hashes without importing CUDA code; `corrected-attribution.json` binds the evidence and preserves the original analysis hashes.
