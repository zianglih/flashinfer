# Control128 / gather128 / epilogue248 compile qualification

The frozen two-literal candidate on ce4 passes the source-paired compile-only gate. All84 pairs preserve register/shared-resource limits, and all41 FC2 PTX/CUBIN pairs are byte-identical. No owned MoE kernel was launched in this gate. The separate candidate-only existing41-case numeric qualification subsequently passed; see `exact-qualification.json`.

- Source: `d7c17adfd8ebe86f733ffc724eced54354f9811a00523927852bb4efc10ec815`; patch `609832cbf350b6705dac17b4e685e4ef65d9e998fe57f96ab251db21b74ad541`.
- Same384 threads, initial168 registers and64,512-register CTA pool. Actual SASS has control/gather128 donations and epilogue248 allocation.
- The two inherited M512/N128/K8 MX control/MMA spills shrink160→128 stack bytes and20+20→16+16 LDL/STL sites. All local sites remain control/MMA; no epilogue or gather spills appear. Residual128B remains, so this does not eliminate the descriptor-pressure problem.
- Expanded assigned register endpoints reach controlR125, gatherR109 and epilogueR169, within their quotas. This includes implicit TMEM/vector spans and is not a peak-liveness proof.
- Of43 FC1 signatures,11 have fewer static non-NOP instructions,30 are unchanged and2 gain13 instructions in their wide one-CTA NVFP4/per-token gather paths. Range−144..+13; no added branch sites. The two added-instruction cases gain five MOV.SPILL/R2UR.FILL transfers in gather (no LDL/STL). The reduced-spill cases replace two BRA.U sites with BRA despite unchanged branch count. Static counts do not establish runtime gains.
- Actual frozen native N3U EP16K MXFP8 N256/ReLU² and K3 EP16K per-token/SiTU retain identical instruction counts and remain spill-free; their winner/cache/routing identities were verified. Both compile captures stop before an owned MoE launch.

All890 archived files hash-verified, archive `9b930c39b399dd6c6fdb20bf8241ef9668ab828d903619742cb6d1e471bd6d51`. `analyze.py` replays source/resource/role-local checks. The two unknown indirect-control paths inherited from the CFG parser remain explicit in the JSON; neither is one of the spilling paths. No correctness or performance claim is made from this compile gate.

The approved20-cell screen is running in `control128-epilogue248-screen-r1`. It covers four formats, four models, EP/TP and decode/prefill tokens, including the native high-epilogue-pressure case and N3U TP W4A4 T4096 with the exact wide one-CTA K8 geometry that adds13 static instructions. The original T16K plan and its approved single-row correction are both preserved. It reuses frozen winners/routes, strict100-CUPTI C-A-A-C and all negative/spread/clock evidence; no historical baselines or autotuning are rerun.
