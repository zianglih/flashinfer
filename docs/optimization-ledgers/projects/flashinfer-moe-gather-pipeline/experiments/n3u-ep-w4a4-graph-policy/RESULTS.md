# Graph-policy diagnostic: no retained improvement

The graph-profiled search selected **exactly the same tactic as the earlier eager search**: route128, FC1M512/N128/twoCTA, FC2M512/N128/twoCTA, Ksteps4/4, CLCoff. It did not identify a better FC1 geometry. Production source and all original frozen choices remain unchanged; no additional holdout or search was launched.

All320 admitted choices plus the existing default race returned finite scores. All114 loaded main-kernel records passed the unchanged resource guard with LOCAL0. The final public100-sample strict-CUPTI median is555.860µs; allfour sample quartiles have median2032MHz and no clock-event reasons. Source13,245-file pre/post checks, actual route identity, fresh policy-bound cache identity and current persistent native ELF/Ninja checks pass. GPU0 was released with noPIDs/0MiB/0%util.

| Existing choice | Native graph selection score (µs) |
|---|---:|
| Frozen FC1M512 / FC2M256, route128, K4/4 | 552.960 |
| Eager- and graph-selected FC1M512 / FC2M512, route128, K4/4 | 550.912 |

The native score margin is about0.37%, but the already-completed independent same-source public-route CAAC holdout of these two geometries was only+0.002966%. The current555.860µs is a single final measurement, **not** a causal speedup over that holdout or historical table. Native selection uses synthetic profile inputs and graph/event timing; public measurement uses actual sigmoid routes, timed input quantization and strict CUPTI. Earlier individual eager scores were not recorded and are not reconstructed here.

For reference, the leading **full-MoE** score for each existing FC1 configuration is below. This ranks each FC1 configuration with its best FC2 pairing; it does not isolate FC1 time or justify a new policy.

| Route / FC1 M×N / CTA / Kstep / CLC | Best paired FC2 M×N / Kstep | Native score (µs) |
|---|---|---:|
| 128 /512×128 /2 /4 /off | 512×128 /4 | 550.912 |
| 128 /512×128 /2 /8 /off | 512×128 /4 | 559.104 |
| 256 /256×256 /2 /8 /off | 256×256 /4 | 571.328 |
| 256 /256×256 /2 /4 /off | 256×256 /4 | 583.664 |
| 256 /128×256 /1 /4 /off | 256×256 /4 | 618.496 |
| 128 /512×128 /2 /8 /on | 512×128 /4 | 632.256 |

The complete score ranking is `fc1-ranking.json`; all321 original scores and100 public samples are in `evidence/evidence/results/native-search/results.json`. Audit results are in `summary.json` and reproducible with `audit.py`. Exact native stdout and routing/model metadata are preserved in the same evidence archive, SHA8a6e53c063f7ebdb26b109cc9c72b65c726bbb46360607749d8cc7689aa819a2.

Search process walltime was170.46s:115 `cute.compile` calls total143.32s at the API boundary,321 profile calls10.40s exclusive of nested compilation. These warmed-cache host spans include cache/guard work and are not cold compiler costs. The only helper change was public policy at the existing tune/replay contexts plus passive host-only score capture; no production, kernel, tactic admission, return value, profiler argument or default-cache change.
