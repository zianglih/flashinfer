# W4A16 raw-stage release R1: not retained

Release after the complete decode loop but before decoded stores is source-valid and passes33existing exact cases. The16-cell screen is mixed: geometric mean−0.111%, decode+0.029%, prefill−0.251%. Tight TPdecode losses atV3−1.030% andV41F−0.610% are not justified by the other modest or noisy gains. A separately qualified R2 will move release to the final raw load, before its decode, removing the cloned state as well.

Base6be4971b; candidatekernel3f19620f0dfd2165a170596fd8b2a7afb5d38064311609c1e5dfa69db28b7683. Source2+/5−, same registers, stages, tactics, CLC/PDL and arithmetic. Local review was fast-forwarded to b139 (only unrelated swap policy changed) after the frozen experiment; remote comparison remains explicitly6be.

## Complete paired screen

C-A-A-C phases on oneGPU perjob,100strictCUPTI samples perphase, coldL2graphs,10warmups, frozenroutes/nativewinners/noAUTO. Cellratio uses arithmetic mean of two phase medians perarm, consistent with the W4campaign. Crosscell aggregates use geometric mean of ratios. B300/CUDA13.2/CuTe4.8, nvcr.io/nvidia/pytorch:26.05-py3. Stockclocks with read-only2msNVML. Initialharnessfailedbeforeworkload due missing source manifests; preserved`screen`, complete restart`screen-r1`, no failedphase reused.

|Job|Tokens|C1 us|A1 us|A2 us|C2 us|Speedup|C spread|A spread|
|---|---:|---:|---:|---:|---:|---:|---:|---:|
|ep-kimi-k3-w4a16|8|84.097|84.209|84.432|84.113|-0.256%|0.020%|0.265%|
|ep-kimi-k3-w4a16|4096|532.212|525.907|554.036|527.651|-1.859%|0.864%|5.349%|
|ep-nemo3-ultra-w4a16|8|51.104|51.232|51.200|51.169|-0.155%|0.126%|0.062%|
|ep-nemo3-ultra-w4a16|4096|390.370|393.058|390.914|391.282|-0.296%|0.233%|0.549%|
|ep-v3-w4a16|8|68.160|67.953|67.808|68.240|+0.471%|0.117%|0.212%|
|ep-v3-w4a16|4096|278.465|277.602|277.938|278.451|+0.248%|0.005%|0.121%|
|ep-v41-flash-w4a16|8|51.153|50.960|51.057|51.136|+0.267%|0.031%|0.188%|
|ep-v41-flash-w4a16|4096|434.419|427.363|431.859|434.978|+1.184%|0.129%|1.052%|
|tp-kimi-k3-w4a16|8|87.568|87.265|87.121|87.665|+0.486%|0.110%|0.166%|
|tp-kimi-k3-w4a16|4096|698.772|697.269|707.460|695.556|-0.740%|0.462%|1.462%|
|tp-nemo3-ultra-w4a16|8|66.160|65.504|65.489|66.240|+1.075%|0.120%|0.024%|
|tp-nemo3-ultra-w4a16|4096|546.531|553.444|545.955|547.411|-0.496%|0.161%|1.372%|
|tp-v3-w4a16|8|56.848|57.441|57.456|56.864|-1.030%|0.028%|0.028%|
|tp-v3-w4a16|4096|482.818|481.378|481.667|481.010|+0.081%|0.376%|0.060%|
|tp-v41-flash-w4a16|8|63.793|64.192|64.160|63.776|-0.610%|0.026%|0.050%|
|tp-v41-flash-w4a16|4096|563.268|565.699|564.180|565.443|-0.103%|0.386%|0.269%|

## Qualification and interpretation

- All628gate evidence files and568timing evidence files hash-verified.33exactcases passed, no failures/skips.32timing guard receipts/128loaded MoEkernels zeroLOCAL; all6,400samples/route/tactic/source checks passed. No missingclockwindows.
- Four paired native FC1/FC2 codegen cases preserveREG96/128 andzeroLOCAL. Seven kernels removezero oroneinstruction; TPV3FC2 removes14 but changes18uniformBRA.U tovector-predicatedBRA and related uniform/vectorallocation. Branch totals unchanged; this is not simply14fewer-equivalent instructions.
- Independent SASS audit confirms all8raw-stage arrivals follow finalLDS and precede firstSTTM. Decoded fence/commit remains afterstores, all synchronization/MMA/load/storecounts unchanged. Sharedraw anddecoded destinations are disjoint; multicast participants/phases unchanged.
- Decode FC1duration grows in all8cells (+0.016–0.544us), while FC2generally drops. TPV3/V41FC2 durations grow+0.472/+0.328us. These overlapping kernel durations are not additive E2Ecomponents. A possible issue is delaying decoded stores with the movedarrival; that is a hypothesis forR2, not a proven cause.
- K3EP4K−1.859% has5.35% candidatephasevariation; its negative measurement remains in the table without a stable-regression claim. V41FEP4K+1.184% has1.05% candidatevariation. No clocknormalization/discarding.
- Source/lifetime andindependentgate audits: `independent-lifetime-audit.md`, `independent-peer-audit.json`. Detailedrawresults: `screen-evidence/screen-r1/perf`; summaries: `perf-summary.json`, `component-summary.json`, `telemetry-summary.json`. No sanitizer.
