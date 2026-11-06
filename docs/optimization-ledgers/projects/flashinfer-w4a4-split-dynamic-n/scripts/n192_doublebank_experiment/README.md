# Resource-derived N192 double accumulators (13ca)

Diagnostic only; not integrated. N192 NB2 FC1 reuses B across two channel tiles;
FC2 uses two disjoint accumulator banks when 2×accumulator columns plus SFA/SFB
fit in512 TMEM columns. SFB row allocation rounds up128-row blocks. FC2 uses
its existing padded bulk stores (192 is divisible by64), unlike the earlier
N192 diagnostic which unnecessarily disabled them.

Actual native DeepSeek routing, same weight/input preparation, unfused finalize,
10 warmups /100 cold-L2 CUDA-graph CUPTI samples. Each arm checks complete final
output bytes; different routing geometry is permitted but arithmetic is exact.
Production stays clean13ca. The fixed-tactic probes are not primary AUTO data.

| Tokens | N192 double first(us) | N128 production(us) | N192 double last(us) |
|---|---:|---:|---:|
|4096|207.937|210.2245|209.377|
|8192|327.825|321.985|327.456|
|16384|549.313|564.002|548.4975|

The16K improvement is mostly FC2 (152.2245/149.3765us versus161.2us); FC1 is
roughly unchanged. At8K, the FC1 geometry loses more than FC2 gains. Defer this
additional AUTO tactic while the large-prefill mainloop is profiled. No claimed
before/after retention; no baseline sweep rerun. Raw JSON contains all samples.
The initial r1 import failed before GPU execution because the copied package
initializer imported production module names; corrected isolated initializer
is empty. Failed logs are retained.
