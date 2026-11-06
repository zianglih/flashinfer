# W4 live-group Gather4: rejected

Preserve retained475. Candidate patch`cc1c9c83a7d52bb31acfd8f87a2359656a769a603c3539d2a4cb7989a013ca3f` dynamically limits copied rows while retaining the fifthWG, direct TMA completion, cached lane IDs outsideK and row-loop-outer coordinate reuse across K64 chunks. It adds no tactic or model policy.

-40 existing exact tests passed.33 gate cubins (22FC1) and10 paired full-shape codegen cubins have zero local bytes and noLDL/STL. FullmodelK3N128 staticinstructions2008→1897, N1922054→1868; R2UR38/46→26 and fewerbranches. Staticcode size did not predict dynamic performance.
- Same-GPU C-A-A-C,100 strictCUPTI cold-L2 graph samples/phase,10warmups, frozen existing native winners, public functional API, unfused. W4 directly consumesBF16; inputquantization is absent. Sources/routes/cache entries/100samplearrays guarded. Read-only NVML and posthocCUPTI capture change no GPU work or timing calculation; clocks/power were not changed.
- Stable prefill controls lose5–10%, enough to reject without an additional fixed-clock or fullmatrix campaign. K3stock-clock phase drift means its exact losses should not be treated as deterministic; independent V3/N3U controls have≤0.49%repeatspreads and still lose.
- Avoided rows are descriptor-OOB zero-fill/TMA completion work, not equivalent HBM traffic. Four coordinate shuffles plus a runtime group loop repeated perKtile outweighed the skipped instructions even when each broadcast was reused across all K64 chunks. No further loop permutation is justified by these results.
- GPUs3/4/6 finished idle. No kernel was committed/pushed. The inactive local source copy is removed after exact source/patch verification; all raw artifacts remain.

|Model|Topology|Tokens|Speedup|C spread|A spread|
|---|---|---:|---:|---:|---:|
|kimi-k3|EP8|4096|-4.06%|1.33%|4.87%|
|kimi-k3|EP8|8192|-9.65%|11.27%|1.14%|
|nemo3-ultra|EP8|8|-0.01%|0.09%|0.37%|
|nemo3-ultra|EP8|4096|-5.37%|0.02%|0.23%|
|v3|EP8|8|-0.47%|0.16%|0.18%|
|v3|EP8|4096|-10.30%|0.48%|0.08%|
|nemo3-ultra|TP8|8|-0.07%|0.05%|0.00%|
|nemo3-ultra|TP8|4096|-5.43%|0.00%|0.10%|
|v3|TP8|8|+0.31%|0.00%|0.17%|
|v3|TP8|4096|-7.71%|0.03%|0.07%|
