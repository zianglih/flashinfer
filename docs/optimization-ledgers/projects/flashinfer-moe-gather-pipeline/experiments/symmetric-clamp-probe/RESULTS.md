# Signed symmetric clamp qualification and affected-model screen

The final shared helper replaces the nested symmetric minima in the swap-AB and parameterized W4 epilogues. It preserves the original negative canonical NaN result and both signed zeros. The rejected source was a three-file unstaged candidate on retained `2b8eb9d8`; no policy, tactic, staging or synchronization change was introduced.

The bounded raw-bit probe compared2,629,120 saved control/candidate values, including padding, exceptional inputs and non-FP32-exact limit3.1. Final qualification passed16 selected exact calls and24 native pairs. All five affected FC1s remove15 non-NOP instructions:32 ordinary minima become16 XORSIGN minima plus one uniform constant. Complete opcode deltas retain other compiler allocation/address churn. All19 unaffected captures are raw cubin-identical, and all resources remain equal with LOCAL0. The initial MX wrapper-limit harness failure is preserved; its functional check passed, and the continuation only forwarded the same limit into the wrapper.

The full affected benchmark completed13 jobs/208 cells and83,200 strict native CUPTI samples. All original frozen choices/routes,100 samples,10 warmups, cold-L2 CUDA graphs and NV input quantization are unchanged. Timing uses same-GPU CAAC on recovery GPUs0/1/3/5; unsupported V41F TP MX modes were not added. The32 raw token1/2 cells remain in the complete output and are excluded only from retention aggregates.

| Retention scope | Cells | Geomean speedup |
|---|---:|---:|
| All |176|−0.0082%|
| Decode,4–64 tokens |80|−0.0384%|
| Middle,128–512 |48|+0.0093%|
| Prefill,4096–16384 |48|+0.0248%|
| Swap-AB |154|−0.0586%|
| W4A16 |22|+0.3456%|

There are95 negative retention cells. V3 EP MXFP8/16K is−3.0523% with5.1191% control repeat spread. V41F EP W4A4/16K is−2.8624%, with0.1481% control and1.3284% candidate spread; its average FC1 critical-path extension increases11.68µs and FC2 extension increases4.90µs. The opposite W4 EP/16K+3.6176% result is retained with its4.2949% candidate repeat spread. These component averages are not an exact additive decomposition of the geometric speedup statistic.

All211 paired swap native compilation configurations have unchanged registers, dynamic shared memory, occupancy and LOCAL0. All52 W4 cell/stage records join the actual measured compiled library handles and have unchanged resources. The three recorded W4 default choices produce24 checked phase/stage joins through the unchanged resolver. This is runtime resource evidence, not timed-cubin identity for every cell.

All3,328 clock quartiles are retained: one lacks telemetry and42 have a non2032 median clock or nonzero reason. No clock-based filtering, baseline rerun, retuning or sanitizer was performed. Source inventories and the recovered release C++ modules passed full postflight; all four GPUs were released.

**Rejected after independent full raw replay.** The result is broadly neutral despite real instruction removal. The new inline-PTX helper and signed-NaN contract add implementation surface without an E2E gain, while prefill losses remain. No rescue branch or repeat is proposed. The completed review checkout and branch were removed after exact source/status/hash checks; all notes, scripts, probes, failures and raw evidence remain. Main `2b8eb9d8` is unchanged and clean.

Evidence:

- `qualification-summary.json`, `qualification/source-proof.json`, `probe-summary.json` and the preserved original/continuation raw captures.
- `performance/screen/perf-config.json` SHA`34207694412adee02ff6b06363b6fb7c953a3a90e21c926493b58b10e5faefdd`.
- `../../evidence/symmetric-clamp-screen/1793385719415121000/data`:1,057 hash-verified files; archive SHA`f9bab3e836eac2792e3b9802be76cb11622179f62036f990f96cccae3a7acc9a`.
- Sibling `report/{cells.csv,table.md,retention-table.md,summary.json,component-deltas.csv,clock-quartiles.json,swap-resource-pairs.json,w4-resource-deltas.json}` includes every raw row and negative result.
- `audits/symmetric-clamp-{bounded-peer,qualification-root,qualification-peer,setup-root,static}.json` under the project root.
