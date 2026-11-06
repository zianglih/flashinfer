# Retained e780 EP/TP refresh

All23 swap-AB jobs /364 cells /46 AA phases /72,800 strict-CUPTI samples completed at e780f02c. All514 guarded source files match the committed source. Frozen routes, existing-tactic winners, observer helpers, input quantization, timing and clock configuration are unchanged. GPUs0/4/5/6/7 were verified idle and released. No historical baseline was rerun.

The complete468-cell report reuses104 W4A16 measurements from6c6515f2 after byte-equivalence and transitive-path review; their original phase paths and measurement head are preserved. Only moe_swap_ab_kernel.py changes between those heads.

| Mode |Decode4–64|Middle128–512|Prefill4096–16384|All4+|
|---|---:|---:|---:|---:|
|EP|+1.43%|+0.60%|+0.07%|+0.83%|
|TP|+1.55%|+4.48%|+15.60%|+6.02%|

Ratios use historicald35 controls from another B300 instance, not new same-GPU retention evidence. All396 displayed4+ cells include64 negative values;1/2-token results remain in raw artifacts. The9-column external scoreboards preserve every historical baseline, unsupported entry and legacy-fused mark.

Fresh46 runtime receipts /864 loaded MoE kernels passed with unchanged compile options and0 local bytes. Reused W4 evidence adds16 receipts /224 kernels. These resource claims exclude quantizers. Six of3,744 combined NVML quartile windows are unavailable. The largest fresh AA spread is4.37%; the largest reused W4 spread remains6.47%. Stock clocks were unchanged; telemetry does not establish causal clock attribution.

All23 per-job archives (92,201,500 bytes;2,194 semantic result files) and their manifests are verified. completion.json indexes archive/source/resource/clock receipts. Independent CPU audit: ../cyclic-protected-span-e780/independent-publication-audit-e780.json.

Local draft includes the full five-column EP/TP plots/tables, nine-column external tables, eight final A2 panels, separate W4 and swap diff counts, and the original checklist. The final PNGs were visually checked. publication/validation-receipt.json binds the draft and assets. No GitHub writes by this child.
