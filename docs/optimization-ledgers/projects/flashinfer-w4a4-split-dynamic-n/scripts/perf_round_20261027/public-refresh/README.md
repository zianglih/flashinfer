# Final public six-table refresh

Prepared for the final pushed source after the MMA-N retention decision. Nothing in this folder launches by importing it. The final f7182d5c refresh is running; its first preflight attempt is preserved separately with zero searches or measurements.

- Six exclusive GPUs: V3 EP8 NV/MX on0/1, V4.1 Flash EP4 NV/MX on2/3, Kimi K3 EP8 NV/MX on4/5.
- Fresh native AUTO selection for every table. No frozen winner cache is loaded. Native C++ build cache is reused only after source hashes agree; changed DSL uses the final source's private workspace and model/family cache namespaces.
- Public defaults preserve raw table formatting and all supported TRTLLM, CuTe DSL W4A4/per-token/W4A16 and MXFP4x8/MXFP8 arms. CUTLASS is excluded by existing public defaults; unsupported K3 arms remain N/A.
- All13 established token counts;1/2 excluded from retention summaries.10 warmups and100 raw cold-L2 CUDA-graph CUPTI samples per result. NV includes the initial activation quantizer, MX stays prequantized, fused finalize disabled.
- Existing observer and timer are unchanged. Nested host spans capture `cute.compile` API time versus profiler work during this necessary AUTO run, without added GPU synchronization. The compilation span includes SDK cache lookup; it is not isolated compiler CPU time. Native C++ build/import time remains separately unclassified.
- Fresh W4A16 is required because the retained packed combine modifies its shared finalizer. Fresh TRTLLM measurements keep all six outputs directly attributable to the final campaign.

After the parent provides and approves the final clean pushed commit:

```sh
python3 scripts/perf_round_20261027/public-refresh/deploy.py --repo flashinfer --head FINAL_COMMIT --name final-public-FINAL_SHORT
python3 scripts/perf_round_20261027/public-refresh/launch.py --deployment scripts/perf_round_20261027/public-refresh/final-public-FINAL_SHORT/deployment.json --gpus 0,1,2,3,4,5
```

The runner derives all source identities, validates every rendered row against native result records, preserves raw100-sample arrays, routing identities, chosen native tactics, quantization contracts and source/environment/helper receipts. Fixed-tactic48-point screens remain separate diagnostics.

The explicit virtualenv executable must keep its lexical path (`Path.absolute()`), because resolving the `bin/python` symlink starts system Python and loses the virtualenv package metadata. The failed initial preflight changed no GPU evidence; corrected runner identity is pinned in the live launch receipt.
