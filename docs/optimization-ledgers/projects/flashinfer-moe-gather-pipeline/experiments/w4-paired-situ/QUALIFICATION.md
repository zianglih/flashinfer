# W4 paired-SiTU exact/native qualification

Passed on recovery node `fi-gather-pipeline-recovery-1030`, C2, GPU3 (B300), using the original release compiler options and persistent native C++ cache. Recovery readiness `d3b6f1ca...` and cache-ready `6fc628e9...` bind the rebuilt routing/moe_utils ELFs; there was no source, tactic or compiler-option change during qualification.

Base retained49 versus candidate5e61: six paired geometries, 12 existing zero-tolerance calls, 18 native image pairs. Both complete source manifests passed preflight/postflight. Capture and resource guards stayed byte-identical to the prior qualification harness. The first transport attempt stopped before source copy/GPU launch because two recovery receipts were local-only; it is preserved under `qualification/preflight-attempt-1/`. The successful campaign copies those audited records into its own leaf and verifies the current remote cache-ready/ELF/Ninja identity.

| Case | SiTU gate / linear beta | Layout; CTA; CLC; PDL | FC1 non-NOP before → after |
|---|---|---|---:|
| 0 | 4 / none | swap;1;off;on | 1502 →1478 (−24) |
| 1 | 4 /25 | swap;2;on;on | 2020 →1924 (−96) |
| 2 | 0.8 /1.5 | legacy;1;on;off | 1564 →1516 (−48) |
| 3 | 1.75 /none | legacy;2;off;on | 1932 →1884 (−48) |
| 4 | ordinary SwiGLU | swap;1;on;on | raw image identical |
| 5 | ordinary SwiGLU | legacy;2;off;off | raw image identical |

For all four affected images, the entire opcode delta consists of scalar FMUL/FADD replaced by half as many FMUL2/FADD2. There is no additional MOV or control-flow instruction growth. Native PTX retains explicit RN packed multiply/subtract and scalar approximate FTZ EX2/RCP; no FFMA contraction appears. SFU counts and modifiers are identical. Resources remain96 registers/LOCAL0 for FC1 and128/LOCAL0 for FC2. All14 unaffected image pairs (FC2, finalizers, and two SwiGLU FC1 images) have byte-identical PTX/cubin/SASS.

Sealed evidence: `qualification/evidence/1793379350474754000/data`; archive SHA256 `3fd55985b2798580ce7265cce247c0783583b0a5d474935cfcf064406e2fea9e`. `analyze.py` replays `qualification-summary.json` from the224 fetched files. This is finite-output exact/native qualification, not exhaustive exceptional-value/NaN-payload testing or a performance result. The full26-cell K3 screen is held pending independent native review and launch preflight.
