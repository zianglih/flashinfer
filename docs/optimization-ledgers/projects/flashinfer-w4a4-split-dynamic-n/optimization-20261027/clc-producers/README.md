# Exclude inactive producers from scheduler work

Folded experiment based on e2728, one kernel file, +6/−3 lines. The solely owned review clone was removed after verifying its exported patch and independent Git metadata; the combined active candidate retains this delta. Physical CTA layout stays unchanged. When activation SF uses TMA and epilogue has its own warpgroup, only warp zero owns producer work. Warps1–3 skip the per-tile/K loops and tile-info consumption. They still participate in allocation, initialization, startup PDL waits/signals and the final CTA join; there is no early return. Epilogue dispatch explicitly excludes those idle warps.

CLC tile-info consumer count is computed from active producer, epilogue and MMA roles: affected overlapped-TMA kernels use192 threads instead of288. Narrow-SF kernels retain all four producers because their cp.async scales require128 participants; inline epilogues also retain all four because those producers own epilogue work. No tactic, dtype, model, layout, physical-role, barrier-capacity, cache or register-budget policy changes.

The source audit distinguishes rejected FC1/FC2 six-warp compaction (physical remapping/192-thread CTA) and producer-role loop extraction (extra unrolled code/registers). This candidate only removes nonparticipating roles from actual work and metadata synchronization. Prior artifacts: `scripts/fc1_tma_roles_experiment/README.md`, `scripts/fc2_roles_experiment/README.md`, `scripts/producer_role_loop_20261026/README.md`.

Gate plan: first an affected wide per-token NVFP4 source pair, CLC/static and PDL off/on, with changing/empty/reactivated routes. Capture PTX/SASS/resource proof before extending to all four formats and narrow-SF controls, with a separate internal inline-organization check. No new upstream tests or sanitizer. Timing only after exact/codegen gate, using frozen public native winners and CUPTI-only cold-L2 10/100 C-A-A-C. Persistent verified native C++ cache retained.

## Initial bounded result

The affected wide per-token smoke passes 32 exact source-paired replays (16/source), covering CLC/static × PDL off/on × four routing mutations. All eight compiled source pairs have unchanged registers, physical CTA dimensions, shared/TMEM capacity and zero spills. Actual non-NOP SASS sites fall by 0–21. CLC FC2 with PDL falls from 2,010 to 1,989 sites at 125 registers; its tile-info barrier initialization changes from 288 to 192 arrivals. Static FC2 with PDL falls from 1,856 to 1,845 sites, also with unchanged resources. These are static instruction counts, not a throughput claim. Source/role audit enumerates every combination and proves MMA, scheduler publisher and teardown bodies byte-identical.

The extended gate covers six configs × two shared CLC states × two PDL states × four routing mutations. The public timing screen is limited initially to five existing CLC winners: V3 W4A4 T256; V41 W4A4 and per-token T4096; Nemo W4A4 T128 and per-token T4096. No tactic override or native AUTO is necessary for those cells.

## Full format gate

The six-config source pair passes 192 exact replays (96/source), with 48 paired kernel captures. All sixteen narrow-SF control SASS files are byte-identical. Thirty-two affected kernels change: most lose 2–28 static non-NOP instructions, with unchanged registers or a two-register reduction. One MXFP4x8 FC1 static/PDL-off capture grows 13 instruction sites and four registers; all captured PDL-on configurations have unchanged or improved register counts. No spills occur, and physical CTA dimensions, shared/TMEM capacities and pipeline stages remain unchanged. The full archive SHA256 is `38f5ef82035c1ba1eb1caca562557dae0ec47a46a82126fb5b3eac3b91be41b7`.

Coverage clarification: the current public launcher always chooses the dedicated epilogue, including MXFP4x8. Therefore this full public-wrapper gate does not cover internal inline epilogues. A separate paired helper overrides only the kernel constructor's `overlap_epilogue`/`overlap_activation_accumulators` to False in both sources; this is a diagnostic preservation check and is not a production tactic or timing override.

## Final screen and disposition

Accepted by the parent for the combined broad retention screen as an instruction/synchronization cleanup, with **no speedup claim**. The five-cell screen is effectively neutral: geometric mean 0.999650× (−0.0350%). Nemo per-token T4096 is −0.2469% and should be watched in the combined matrix. All five native selections have route-N128/N256 in both FC1/FC2 and use the dedicated epilogue, so all five exercise producer_warps4→1; none is a narrow unchanged control. `affected-path-proof.json` records exact saved tactics and every source/workspace/cache binding.

|Model|Mode|Tokens|C0 µs|A1 µs|A2 µs|C3 µs|Change|
|---|---|---:|---:|---:|---:|---:|---:|
|nemo3-ultra|CuteDSL PER-TOKEN|4096|309.9535|310.8975|311.2340|310.6420|-0.2469%|
|nemo3-ultra|CuteDSL W4A4|128|137.3120|137.1690|137.2165|137.2005|+0.0463%|
|v3|CuteDSL W4A4|256|148.1610|148.1610|148.1610|148.1605|-0.0002%|
|v41-flash|CuteDSL PER-TOKEN|4096|406.0340|406.2110|405.7785|406.0025|+0.0058%|
|v41-flash|CuteDSL W4A4|4096|351.2665|351.1705|351.2825|351.3300|+0.0204%|

All twenty successful frozen phases and 2,000 original CUPTI samples independently verify. The first driver attempted an unsupported combined selector with `--w4a4-only`; the observer rejected it before benchmark import or GPU work. Its failed launch receipt is preserved, and only the four unfinished cells were resumed using separate supported selectors. The valid V3 cell was not rerun. `timing-verification.json` explicitly records that excluded unstarted invocation.

The separate internal inline-organization source pair passes another32 exact replays. Seven of eight SASS pairs are byte-identical; the eighth differs only in uniform-register assignment with unchanged1,128 instructions,124 registers and zero local memory. This diagnostic does not change public launch policy.

Final timing/inline archive SHA256: `4161a7727d91c55706f2cbde306c3e0f8f5da5bab4f0451392b7699b4c980eeb`. No new upstream tests, sanitizer runs, native AUTO changes, commits or pushes. GPUs2/3 are released. The parent copied the small kernel patch into the frozen combined candidate; the isolated review clone was removed after confirming its sole modification exactly matched the exported patch (`source-cleanup.json`).
