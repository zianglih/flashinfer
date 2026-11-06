# Proposed direct-local completion screen

24 native cells,20 affected one-CTA FC1 and4 unchanged two-CTA controls. Six cells/format; all four models, EP/TP, CLC/static. No timing launched.

| Job | Mode | Tokens | FC1 group | CLC |
|---|---|---:|---:|---|
| ep-v3-w4a4 | w4a4 | 16 | 1 | False |
| ep-kimi-k3-w4a4 | w4a4 | 32 | 1 | True |
| tp-v41-flash-w4a4 | w4a4 | 8 | 1 | False |
| tp-nemo3-ultra-w4a4 | w4a4 | 4096 | 1 | False |
| tp-nemo3-ultra-w4a4 | w4a4 | 16384 | 1 | False |
| ep-nemo3-ultra-w4a4 | w4a4 | 16384 | 2 | False |
| ep-v3-per-token | per-token | 8 | 1 | True |
| tp-kimi-k3-per-token | per-token | 8 | 1 | False |
| tp-v41-flash-per-token | per-token | 8192 | 1 | True |
| tp-nemo3-ultra-per-token | per-token | 4096 | 1 | True |
| tp-nemo3-ultra-per-token | per-token | 16384 | 1 | True |
| ep-kimi-k3-per-token | per-token | 8192 | 2 | False |
| ep-nemo3-ultra-mxfp | w4a8 | 8 | 1 | True |
| ep-v41-flash-mxfp | w4a8 | 32 | 1 | True |
| tp-v3-mxfp | w4a8 | 8 | 1 | False |
| tp-kimi-k3-mxfp | w4a8 | 512 | 1 | False |
| tp-nemo3-ultra-mxfp | w4a8 | 8192 | 1 | False |
| ep-v3-mxfp | w4a8 | 16384 | 2 | False |
| ep-v3-mxfp | mxfp8 | 8 | 1 | True |
| ep-v3-mxfp | mxfp8 | 512 | 1 | True |
| ep-v41-flash-mxfp | mxfp8 | 128 | 1 | True |
| tp-v3-mxfp | mxfp8 | 8 | 1 | False |
| tp-nemo3-ultra-mxfp | mxfp8 | 32 | 1 | True |
| ep-nemo3-ultra-mxfp | mxfp8 | 16384 | 2 | False |

{"total": 24, "per_format": {"w4a4": 6, "per-token": 6, "w4a8": 6, "mxfp8": 6}, "affected": 20, "unchanged": 4, "decode": 12, "middle": 2, "prefill": 10, "clc": 11}

Frozen retained native winners/routes; public functional API, unfused finalize, NVFP4 initial input quantizer included. SameGPU C-A-A-C,100 strict CUPTI samples/10warmups/coldL2 graph each phase. Primary100*(sqrt(C1*C2/(A1*A2))-1). Preserve perFC medians, repeatspreads, NVML, everynegative row. Report affected20, unchanged4, and overall24 separately; rank FC1 component changes alongside E2E. All FC2 source behavior is unchanged.

No new tuning or tactics. All native MXFP8 prefill winners are2CTA, so affected MXFP8 coverage reaches512 while16K is an unchanged control; do not imply affected largeprefill coverage. No sanitizer or baseline historical fullreport/TRT rerun.
