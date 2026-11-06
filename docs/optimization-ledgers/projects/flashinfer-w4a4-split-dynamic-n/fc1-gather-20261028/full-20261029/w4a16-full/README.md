# W4A16 final no-prepare comparison

Final candidate source patch:26bce62f6fb27f821a7e17aad04170f304e808201bfb04e10edba08fe91619d6 against fb66a27e. Local source remains unstaged in flashinfer-w4a16-tma-clean-review. FC1 five-WG TMA Gather4; FC2 unchanged four-WG regular TMA; no new tactic axes.

104 cells: four models V3 EP8/TP8, V41F EP4/TP4, K3 EP8/TP8, N3U EP8/TP8; tokens1,2,4,8,16,32,64,128,256,512,4096,8192,16384. Tokens1/2 are run but excluded from retention. Both arms use BF16 inputs directly and unfused finalization. The NVFP4-family --include-activation-quant flag adds no quantizer for W4A16.

Candidate native search uses existing23 W4A16 tactics bounded to the actual13 token buckets. Then paired C-A-A-C on each same physical GPU compares oldfb66+old winners versus finalcandidate+native winners, with10warmups/100strictCUPTI cold-L2 graph samples. Separate clean32 source-only screen isolates final source simplification from retuning; this full campaign measures source+tactics.

B300C3 fi-gather-opt-1029, image nvcr.io/nvidia/pytorch:26.05-py3, torch2.12/CUDA13.2/CuTe4.8/CUPTI13.4/driver595.91.07. Native C++ caches and CuTe DSL cache are persistent under /data. Source/runtime/route/winner/sample-count guards enabled. Source frozen throughout all lanes.

Preflight:40 existing exact cases passed. Six additional existing cases ran through a local-only alignment harness:8 FC1 launches with contiguous BF16 views at pointer%32=16, covering both weight layouts, partial routes, top_k3, multicast and two-CTA shapes. All passed. The first alignment harness attempt had a stale pytest parameter ID and stopped in collection before kernel execution; corrected run is offset-alignment-v2. No sanitizer.

All104 cells completed across five lanes on GPUs1,2,3,4,6. Remote artifacts: optimization-next-20261029/w4a16-full. run_full.py is the complete exact-command/timing/source guard harness; run_lane.py/launch.json on the remote record GPU job assignment.

Final C-A-A-C geomeans excluding1/2: EP decode+0.32%, EP prefill+0.54%; TP decode+2.84%, TP prefill+17.30%. Decode is4–256 tokens; prefill is512–16384 tokens. Tables include every88 retention cell. Main remaining gaps are V3EP8tokens−4.50%, V41FTP8−2.63%, K3TP8−2.75%; K3EP4096−6.69% and8192−5.47% have the same old/new tactic and2.91/3.95% control-repeat spread. Preserve these cells rather than selecting only gains. `cells.csv` retains all104 cells, four phase medians, both repeat spreads and both tactics.

Native search used23 existing tactics,35 compile calls/EP arm and50/TP arm;312 profiler calls per13-token arm. Search wall40–73s/arm, measured cute.compile exclusive16–46s, profile exclusive4–5.5s. `native-search.csv` preserves per-arm accounting; compilation includes SDK cache work and profiling includes warmup/graph/wait machinery. All guards passed.
