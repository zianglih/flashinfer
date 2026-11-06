# V41 MXFP4x8 T16384 scheduler diagnostic

Final-guard source (`dd266b91` plus patch `f8ba9aee…`, source-equivalent to final commit `7f4e1703` for this MX path), B300 GPU7, `nvcr.io/nvidia/pytorch:26.05-py3`. Exact fresh B+C full-run native cache and routes were reused read-only. The source and caches remain unchanged. All raw NSYS/NCU reports, observed tactics/routes, commands, environment and hashes are adjacent to this note.

**This is diagnostic evidence only.** Three cold CUDA-graph NSYS replays and serialized, base-clock NCU kernel replay are not the public benchmark retention protocol. The fresh full100-replay CUPTI table is authoritative: V41 MXFP4x8 T16384 is0.8497215ms CuTe versus0.865626ms TRT (1.0187×), and CuTe wins all retained V41 mixed token counts. The profiler differences below do not replace those medians.

Native CuTe uses N128, FC1 tile512×128/group2, FC2 tile256×128/group2, K4/K4, static/static. A separate diagnostic cache copy changes only both scheduler booleans to true; its original cache is untouched, and actual constructors confirm CLC and full PDL weight prefetch in both phases. TRT uses native tactic[128,2].

| Phase median (µs) | Native static | Same-geometry CLC | TRT |
|---|---:|---:|---:|
|input prepare|48.544|50.496|Inside FC1|
|FC1|461.313|448.577|483.969|
|FC2|297.088|318.049|258.241|
|combine|72.929|78.752|92.256|

Do not sum the overlapping phase medians. Additive endpoint means show static→CLC: through-FC1−13.42µs, FC2 extension+41.20µs, combine tail+6.82µs. FC1→FC2 median overlap shrinks28.83→12.38µs even though startup weight prefetch remains enabled. The possible contribution of CLC cancellation progress, SM availability and load balance to this overlap change is not independently isolated.

| Isolated NCU metric | FC1 static | FC1 CLC | FC2 static | FC2 CLC |
|---|---:|---:|---:|---:|
|Kernel duration (µs)|609.664|586.432|384.640|448.256|
|DRAM read (GB)|2.570|2.103|1.175|0.944|
|Executed instructions (M)|57.336|57.491|38.742|38.337|
|Tensor active (% elapsed)|75.390|78.410|61.660|52.980|

All six selected NCU kernels match NSYS register counts and saved choices;27 requested counters and six replay passes per kernel. NCU serialization removes native PDL overlap. CLC FC2 reads less memory and executes slightly fewer instructions while tensor activity falls; the result does not support a simple “more instructions/traffic” explanation.

Exact route histogram: 24,283 local routes,96 experts, 235 live N128 route tiles versus863 allocated slots. FC2 has4,700 live logical work clusters but17,260 launch tickets, including12,560 padded cancellation tickets. Current source skips publishing their tile metadata but still drains each CLC response. This is a structural cost and a testable optimization target; these counters do not prove it dominates.

Next candidate: occupancy-bounded ticket grid plus runtime-balanced contiguous live-work groups, with cancellation deferred until the current group’s final tile. Preserve the one-slot metadata ring and PDL contract. Historical W4A16 fixed2/4-route bundles regressed, so coverage proof and fixed static/current-CLC comparisons must precede broad retention.
