# Final composed-head full refresh (prepared, not launched)

Fresh364 swap cells:23 jobs, four models and both EP/TP, all supported swap dtypes,13 tokens including1/2 internally. Display excludes1/2. Reuse104 unchanged W4 cells measured at6be plus every existing TRTLLM/non-swap baseline. No baseline rerun, retune, sanitizer or clock change.

`run_perf.py`, its seven observers/guards and `worker.py` are byte-identical to retained-b139-full. Each job runs candidate A-A on one physical GPU,10 warmups and100 strict CUPTI cold-L2 samples; no fallback/AUTO; frozen routes, native winners and caches. NV includes input quantization. Output is unfused. Engine runtime guards remain unchanged. Eight lanes 0–7 were balanced using previous complete phase durations. Source ce4a7d8c was bound after final qualification; stage verified source and frozen winners before the eight-GPU launch. Timing retains all AA pairs and all negative cells.

Do not bind/launch until the finalSF composition passes, is retained and pushed, and root authorizes the final campaign. These commands separate the operations; staging never launches:

```sh
python3 bind_source.py --head FINAL_40_DIGIT_SHA --source-json FROZEN_REMOTE_SOURCE_MANIFEST --gpus 0,1,2,3,4,5,6,7
python3 stage.py --box fi-gather-6be-1029
python3 launch.py --box fi-gather-6be-1029
```

The binder checks all514 canonical committed blob hashes, keeps the remote actualGitHEAD/patch identity separate, and proves only the swap kernel changed from6be. That strict closure qualifies W4, sharedquantizer, benchmark and historical baseline reuse. Staging rechecks sourcefiles/Gitdiff, all23 winner-results hashes and every frozen cache entry. Launch rechecks files and requires every allocated GPU idle. Persistent native/CuTe caches and the immutable source's complete data symlink are reused.

After completion, run the existing fetchers/analysis/guards, then the configured `finalize_evidence.py` and publication assemblers. `publication/` is populated at source binding from the prior validated templates; only candidatehead/artifactdirectory are substituted. Before final body/plots, update its concise implementation/test prose for the retained six-wait/tree/SF changes and inspect both heatmap panels. Root owns GitHub publishing. Historical comparisons are scoreboards, not fresh same-GPU causal baselines.

Preparation evidence: `preparation.json`, `infrastructure-check.json`, `frozen-winners.json`, `lane-plan-basis.json`. No source binding, remote staging or worker launch has occurred as of this preparation.

Transport helpers invoke the managed `/usr/local/bin/h` through the existing remote wrapper with cwd `/Users/ziangli/rl/hai`; no HAI checkout files are edited. Benchmark engine/observers remain byte-identical.
