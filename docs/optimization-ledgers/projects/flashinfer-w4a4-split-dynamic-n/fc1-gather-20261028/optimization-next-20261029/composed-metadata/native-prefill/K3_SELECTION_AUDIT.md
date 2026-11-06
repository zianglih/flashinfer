# K3 native-selection regressions

Source is the same retained `c0c0bc41` in both old-winner and newly tuned replay. This is a tactic-selection result, not a kernel-code regression. Public timing is unfused, cold-L2 CUDA-graph replay with 100 strict CUPTI samples per pass, including initial NVFP4 activation quantization and routing. Two pass medians are combined geometrically; spread is max/min minus one.

| Case | Old winner | New native winner | Change | Old/new spread |
|---|---:|---:|---:|---:|
| K3 EP8 W4A4, 8192 tokens | 479.541 us | 514.127 us | −6.727% | 0.154% / 0.040% |
| K3 TP8 per-token, 16384 tokens | 2020.241 us | 2102.250 us | −3.901% | 0.011% / 0.074% |

The five tactic fields are route tile, FC1 `(M,N)/(CTA-group,1)`, FC2 geometry, FC1/FC2 K-step pair, and shared CLC flag. The third field inside each GEMM sub-tactic is unchanged false.

- K3 EP8 W4A4: old `(128, ((256,128),(2,1),False), ((256,128),(2,1),False), (4,4), False)`; new `(256, ((256,256),(2,1),False), ((256,256),(2,1),False), (4,4), False)`. Native search chose wider token tiles for both GEMMs.
- K3 TP8 per-token: old `(128, ((256,128),(2,1),False), ((512,128),(2,1),False), (4,8), True)`; new `(128, ((256,128),(2,1),False), ((128,128),(1,1),False), (4,8), False)`. FC1 geometry and both K depths are unchanged; FC2 changed from two-CTA M512 to one-CTA M128 and the shared scheduler changed from CLC to static.

Neither old winner was excluded. The read-only admission replay imports the actual frozen kernel/tuner and uses meta tensors with the recorded shapes. It reproduces the native admitted-list SHA `544c9757168f83f80ffa941eb787635e83cd5be041cd7800ef3e070420b89243` for both cases: 320 admitted out of 360 declared tactics, with both old and new winners present. `admission-audit.json` and `admission_audit_remote.py` retain this proof. All 963 profile calls per K3 job returned without exceptions; the native cache consistently replays the same new winner in search and both final passes. No admission or cache fallback explains the regression.

The recorded selection policy is `cuda_graph_profile_replays=None`, `l2_cache_policy=cold`, `use_cuda_graph=False`, with `measurement_policy=None`. Consequently these NV native searches used the inherited host-excluded CUDA-event path, not graph profiling. The benchmark only applies `MeasurementPolicy(execution_mode="cuda_graph")` to MX modes (`bench_moe_deepseek.py:866`). Final CUPTI graph timings and native profiles therefore have different execution/timing boundaries. Native tuning calls the MoE runner, while the public timed chain also includes quantization and routing (`bench_moe_deepseek.py:840`). Even graph profiling would not by itself eliminate this boundary or the seeded profiling-route difference.

The default native event path flushes twice L2 and measures isolated calls; it does not use a warm-L2 policy (`autotuner/autotuner.py:3549`). `MeasurementPolicy(execution_mode="cuda_graph")` enables captured runner replay but still uses CUDA events (`autotune_cache.py:215`). CUPTI is used only for the final public measurements here. Explicit `execution_mode="eager"` is a different host-included policy and must not be substituted for the inherited NV default.

Original per-candidate profile medians are unavailable: this campaign records aggregate host timing and selected caches, not each returned profile score, and normal logs do not contain the scores. The K3 selection-policy mismatch is a plausible cause, not a demonstrated cause. No scores are fabricated or reconstructed from end-to-end latency. The independent benchmark-only `bench-graph-policy` experiment adds after-call score recording and tests graph selection with separate caches and fresh same-GPU old/native controls.

Historical evidence also argues against assuming graph profiling is a universal cure. `optimization-20261027/tuning-measurement-audit/RESULTS.md` found graph gains against older N3U eager winners, but fresh eager searches selected similarly faster geometry. That experiment retained no policy change. The MX-only gate originally preserved NV defaults when moving the MX implementation to the public API; no documented Blackwell NV failure required it. Legacy W4A4/per-token graph profiling passed bounded compatibility then; W4A16 graph profiling had not been tested.

## Follow-up evidence

The independent graph-policy experiment subsequently selected the same K3 winners as eager and did not improve either gap (`../../bench-graph-policy/RESULTS.md`). A controlled K3 EP8 T8192 experiment then changed only route IDs while sharing the exact quantized activations, scales, weights, token weights, graph scope and timers. N256 beats N128 by 3.053% under balanced routes but loses 6.931% under the saved actual routes using CUPTI; event timing reverses similarly. Full actual quantize→route→MoE loses 6.723%. Thus route distribution is sufficient to cause this EP ranking reversal, rather than merely a hypothesis. This does not establish the same cause for TP or justify removing the intentional general load simulation. Full raw evidence and scope are in `../../k3-route-scope/RESULTS.md`.
