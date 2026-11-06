# Proposed source-paired MMA-interleave screen

No timing launched. This plan selects code-change coverage from the retained frozen winners before inspecting candidate timing. Six cells per format; all four models and both topologies.

| Job | Mode | Tokens | FC1/FC2 channels |
|---|---|---:|---|
| ep-v3-w4a4 | w4a4 | 16384 | 2/1 |
| ep-nemo3-ultra-w4a4 | w4a4 | 16384 | 2/1 |
| ep-kimi-k3-w4a4 | w4a4 | 4096 | 1/2 |
| tp-kimi-k3-w4a4 | w4a4 | 8 | 1/2 |
| tp-v41-flash-w4a4 | w4a4 | 4096 | 1/2 |
| tp-v3-w4a4 | w4a4 | 8 | 1/2 |
| ep-kimi-k3-per-token | per-token | 16384 | 2/2 |
| ep-nemo3-ultra-per-token | per-token | 4096 | 2/1 |
| ep-v41-flash-per-token | per-token | 16384 | 2/1 |
| tp-v3-per-token | per-token | 8 | 1/2 |
| tp-kimi-k3-per-token | per-token | 4096 | 1/2 |
| tp-nemo3-ultra-per-token | per-token | 8 | 1/1 |
| ep-v3-mxfp | w4a8 | 16384 | 2/1 |
| ep-v41-flash-mxfp | w4a8 | 16384 | 2/1 |
| ep-nemo3-ultra-mxfp | w4a8 | 8192 | 2/1 |
| tp-kimi-k3-mxfp | w4a8 | 8 | 1/2 |
| tp-v3-mxfp | w4a8 | 8 | 1/2 |
| tp-nemo3-ultra-mxfp | w4a8 | 4096 | 1/1 |
| ep-v3-mxfp | mxfp8 | 16384 | 2/1 |
| ep-v41-flash-mxfp | mxfp8 | 16384 | 2/1 |
| ep-nemo3-ultra-mxfp | mxfp8 | 8192 | 2/1 |
| tp-v3-mxfp | mxfp8 | 8 | 1/1 |
| tp-nemo3-ultra-mxfp | mxfp8 | 16384 | 1/1 |
| ep-v3-mxfp | mxfp8 | 4096 | 1/1 |

Frozen current native winners/routes, functional public API, input quantizer included for NVFP4 family, unfused finalize, C-A-A-C same physical GPU, each phase median100 strict CUPTI samples with10 warmups/cold-L2 graph, primary100*(sqrt(C1*C2/(A1*A2))-1); per-FC activity medians and read-only NVML preserved; all negative rows retained.

The two existing M512/N128/K8 MX stress geometries are additional separately reported diagnostics; they are not mixed into the24 native cells. The original failed no-new-local gate remains failed. The source-bound experimental gate must pass before any timing.
