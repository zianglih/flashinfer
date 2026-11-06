# Final retained ce4a7d8c full refresh

Source: `ce4a7d8c2836c0f8a871ebf5cfe87633172360d8`; kernel `77a5495cca8dedef5bccfaacde64a1004b9a7c421175511f12ffef2d996439b3`.

- Fresh:23 jobs /46 AA passes /364 swap cells /72,800 strict-CUPTI samples on8 B300 GPUs. All archives and loaded-function guards passed.
- Reused:104 W4A16 cells /20,800 samples at6be4971b after514-file dependency/source closure proof. Historical d35/TRTLLM/non-swap baselines unchanged; no baseline reruns.
- Tokens1–2 run but excluded from396 displayed cells. All58 negative cells retained; unsupported cases and fused-baseline markers unchanged.
- All1,088 loaded MoE resource checks passed with zero local bytes. Syntheticwide exact/codegen spill qualification is separate.
- Stock clocks unchanged.3/3,744 quartile windows lack NVML samples and remain unavailable. Fresh AAspread max3.84%; inheritedW4 max12.55%. No fixed-clock or same-instance historical-causality claim.

|Mode|Decode4–64|Middle128–512|Prefill4096–16384|Overall4+|
|---|---:|---:|---:|---:|
|EP|+1.414%|+0.640%|-0.191%|+0.763%|
|TP|+1.471%|+4.442%|+15.543%|+5.960%|

These geometric means include allfive dtypes and compare with reused d35 controls, not only the last isolated changes.

Publication: `32,740`bytes; report SHA256 `84a29234de361041017ca00c9e94d862be471a1e7003181b2c1267dd4c9f4783`; body SHA256 `d94b0c36409d6274afbee3a380710289ab281a25481f7824aae735d81ea9eb48`.

Both complete EP/TP plots were visually inspected. Source/route/cache/math/resource/figure validators passed. All8 GPU workers/descendants exited and nvidia-smi was idle before release; see `lane-status-latest.json`. Parent owns GitHub publication.
