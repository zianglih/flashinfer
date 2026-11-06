# ELECT AUTO iteration-cost audit

Reducing the final 100 measured iterations is unlikely to materially shorten this roughly ten-minute whole AUTO run. The saved rank0 `bench_gpu_time` scopes total only **5.949343 s (1.009% of process wall)**. The measured GPU spans themselves total **0.729769 s (0.124%)**. Most elapsed time lies outside these final measurement calls; the saved records do not divide that remainder into compilation, tuning, setup or other work. The existing protocol is unchanged.

Completed source `ef43bf0fd928f6eaf3c35c5997cd8089efc8b1e3d93c0afb6b3248a4d5cfd5ef`, original session56333: shell/torchrun subprocess **589.757506347 s**, `2026-09-10T11:43:33.710270+00:00` → `2026-09-10T11:53:23.467795+00:00`. Its explicit wall scope excludes outer source/native guards. This is the rejected ELECT run, not the active tail-fence run.

| Global tokens | Saved sample line | Samples | Sum of GPU spans (ms) | Rank0 bench wall (s) |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 130 | 100 | 62.380519 | 0.482407 |
| 2 | 231 | 100 | 23.525528 | 0.430032 |
| 4 | 332 | 100 | 46.464449 | 0.445519 |
| 8 | 433 | 100 | 49.758301 | 0.442212 |
| 16 | 534 | 100 | 68.462872 | 0.446067 |
| 32 | 635 | 100 | 81.567209 | 0.453431 |
| 64 | 736 | 100 | 64.379575 | 0.462213 |
| 128 | 837 | 100 | 48.323263 | 0.454486 |
| 256 | 938 | 100 | 42.407604 | 0.482974 |
| 512 | 1039 | 100 | 44.416330 | 0.451978 |
| 1024 | 1140 | 100 | 58.246215 | 0.467948 |
| 2048 | 1241 | 100 | 57.108472 | 0.452454 |
| 4096 | 1342 | 100 | 82.728177 | 0.477621 |
| Total | — | 1300 | 729.768514 | 5.949343 |

The arrays are explicitly `per_iteration_rank_max`, `cupti`, cold L2, CUDA graph, 100 repeats and three warmups. Their sum is a sum of distributed per-iteration GPU spans, not an eight-GPU utilization integral or process elapsed time; do not multiply it by eight. The first sample of each shape is visibly much longer (13.025–63.304 ms): those 13 samples total **0.458057 s**, while the other 1,287 samples total **0.271711 s**. All samples remain included. No cause is assigned to those first-sample spikes.

The 5.949343 s figure is the sum of the explicitly logged rank0 `wall_scope="bench_gpu_time"` durations, not just kernel time. Other ranks’ wall scopes and the surrounding collective timing are not logged here. Subtracting it from process wall leaves **583.808164 s** outside the rank0 scopes; that residual is not an exact measurement of CPU overhead or compilation time. Even eliminating these whole observed scopes would account for only about 1% of the recorded process duration, subject to that rank0/distributed boundary. Cutting only repeat count removes less work and does not remove fixed preparation.

Available phase markers: the log records distributed/NCCL setup start and completion, prelaunch resource records, thirteen eight-candidate autotune winners/rankings, then final sample arrays and table rows. These setup/compile/tune events have **no individual timestamps or elapsed durations**. The provenance log has only its initial `Thu Sep 10 11:43:33 UTC 2026` timestamp; the outer entry log has untimestamped START/PASS markers. Resource records establish compilation/load occurred, not a measured backend cache miss or compile cost. Autotune’s printed microseconds are GPU-event candidate scores, not tuning wall time.

The existing reconstruction records a separate tuner budget: three eager preparation forwards, one initial graph replay, five estimate replays and ten timed graph replays per candidate. That is distinct from the final `--iters=100` measurement. Thus these saved records support pursuing preparation/compilation/tuning cost attribution or reuse for iteration speed; they do **not** establish which of those dominates. There is no evidence here that reducing final measured iterations would save minutes, and no protocol change is proposed.

This note performs only direct arithmetic on completed saved JSON/log fields. No parser/scorer/validator, benchmark, GPU operation or new timing instrumentation was run.

Inputs:

- [cu132-recovery0910a-atomic-preclaim-elect-default-auto13-direct-001-auto.log](../../../logs/cu132-recovery0910a-atomic-preclaim-elect-default-auto13-direct-001-auto.log) — SHA256 `a764d6e41596cb498e5537b002de2137310234fdd5943abfc0052e5533bca5fa`.
- [execution.json](../../../logs/cu132-recovery0910a-atomic-preclaim-elect-default-auto13-direct-001/execution.json) — SHA256 `7f26230cd75eb96df3b45361da30066e6512b521428d249eb099737c15142956`.
- [reconstruction.json](../../../logs/cu132-recovery0910a-atomic-preclaim-elect-default-direct-auto-reconstruction-001/reconstruction.json) — SHA256 `06da025a7e769a5746a82d051eb65e64f35547fc571c1fa102059e8ccccfaa36`.
