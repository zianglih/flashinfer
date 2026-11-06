# Current phase lower-bound diagnostics

These intentionally omit the entire epilogue and produce invalid outputs.
They are diagnostic latency bounds, never correctness or retention evidence.
Production remains7829fc00; only isolated immutable modules are changed.

Actual native NVFP4 T16384, H7168/I2048,32 local experts/topk8,
M256/N256/cluster2, C1B200GPU3, nvcr.io/nvidia/pytorch:26.05-py3.
10warmups/100 cold-L2 CUDAgraph/CUPTI samples, same captured inputs/allocations.

| Phase | Valid control us | Epilogue omitted us | Exposed difference us |
|---|---:|---:|---:|
| FC1 |323.7130|300.0170|23.6960|
| FC2 |178.6080|90.4645|88.1435|

The experiment preserves scheduling, TMA/gather/SF pipelines, MMA, accumulator
barriers and releases; it omits each epilogue call only. Removing that call also
changes compiler scheduling/resources, so differences are not a precise
attribution of epilogue execution time. The bounds nevertheless motivate
mainloop work for FC1 and further bulk-output R2S vectorization forFC2.
No primary sweep or existing baseline data was rerun.
Raw logs and JSON: `logs/current-phase-bounds-n256-r1.*` at project root.
