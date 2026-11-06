# FC1 direct activation gather experiment

Current result: [RESULTS.md](RESULTS.md). The tested local-TMA R6 version remains unstaged for review; the measured variants regress against retained head and have not been retained.

- Base: `d35fcfda03875077b3af8455575cc1d20e866a8c` (current retained PR head).
- Review checkout: `../flashinfer-fc1-gather-review`, independent clone, changes remain unstaged and unpushed.
- Scope: swap-AB FC1 input collection only, dedicated activation gather warpgroup. FC2 regular TMA and W4A16 are unchanged.
- Goal: eliminate standalone routed activation/SF prepare traffic and its launch, while preserving public layouts, arithmetic, routing and tactics.
- Start with TMA gather4 payload and asynchronous original-row SF loads. Prior direct payload cp.async/LDG256 experiments lost isolated FC1 performance but used different warp ownership; see `../scripts/loader_experiment/README.md`.
- PDL: `moe_sort` releases dependent kernels before its routing outputs are written. Without prepare's completion wait/republication, FC1 metadata consumers must wait for routing before use. Initialization can overlap. FC1 republishes routing before starting FC2, retaining FC2 weight/SF prefetch.
- Validation: focused exact/reference and public-call coverage first, no sanitizer. Then same-GPU paired C-A-A-C public benchmark with frozen routes/tactics, 10 warmups and 100 strict CUPTI cold-L2 graph samples. No TRTLLM/old baseline rerun.
- Runtime: existing C3 devbox `fi-moe-descriptor-recover-1028`, 8 B300 GPUs, `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2. Dedicated compile workspace with nine persistent native-cache links.

## Qualification progress

- R1 was rejected at compile time: a mixed dynamic/static branch traced an unused descriptor. No performance evidence was collected.
- R2 explicit constexpr branch guards passed all32 existing cases on4B300 GPUs.
- R3 distributes `(row group, K chunk)` Gather4 commands across all4 warps and passes the same32 cases. Full payload/SF coverage is unchanged.
- R3 and R4 both passed the supplemental 12 existing cases, including six confirmed active CLC cases and PDL on/off (44 selected cases per revision; no sanitizer).
- R4 removes the gather warpgroup's synchronous scale wait using local asynchronous completion and one elected relay publication per CTA. Compile-time FC1 stage depths are 2–11, typically 4–6, with no stage-depth loss across the 224 checked FC1/FC2 plans. See `r4/staging-audit/`.
- R4's 15-job same-GPU CAAC screen completed 144 cells, including 32 unchanged W4A16 controls, at 8/256/4096/16384 tokens. Affected-format geometric-mean speedup versus retained head is −33.89% EP and−16.02% TP; W4A16 control is −0.16%. This candidate is not suitable for retention. Full measurements and plots: `r4/report/` and `r4/plots/`.
- R5 replaces only the FC1 Gather4 payload mechanism with 128-bit cp.async from all 128 gather threads. Payload and SF share local asynchronous completion; weight/SFA TMA remains independent. Its first compile hit a DSL variable-type collision; R5b only renames the payload-local variables and passes all 44 selected tests.
- R6 keeps Gather4 but uses CTA-local completion for payload and SF together. A local barrier expects 128 asynchronous SF arrivals plus one payload transaction announcement; the existing relay publishes readiness once per CTA. It passes all 44 selected tests and retains four-warp issuing, stage depth, FC2 and W4A16 behavior.
- R5b, R6 and the R7 incoming-PDL diagnostic completed the same four-job CAAC screen. Neither payload transport nor incoming-launch eligibility recovered the main regression. The review copy restores the exact tested R6 source; all comparison rows are in `comparison.csv`.
- CUPTI activity capture attributes the K3 EP8 MXFP4x8 4096-token regression to FC1; see `r6/cupti-timeline/RESULT.md`. The internal FC1 stall cause remains unresolved. No candidate was committed or pushed, and no PR body was changed.
- The original C3 devbox disappeared after all R4 evidence was collected. Replacement `fi-fc1-gather-1028` uses the same explicit image and the same eight GPU UUIDs; persistent runtime, sources and cache links were reverified. The bounded NCU retry timed out during profiler startup without producing counters; it is excluded from all performance conclusions.
