# R11 structured warpgroup codegen

R11 fixes the register-budget propagation problem seen in R9. The same fixed
C80/E256/G128 budget now gives each warpgroup its own emitted GPR range and
eliminates all observed local spills in the N3U TP8 prefill FC1 kernels.

| Case | R6 initial regs / stack | R9 initial regs / stack | R11 initial regs / stack | R11 LDL / STL sites |
|---|---|---|---|---|
| N3U TP8 T16384 MXFP8 | 168 / 208 B | 168 / 488 B | 168 / 0 B | 0 / 0 |
| N3U TP8 T16384 MXFP4x8 | 168 / 208 B | 168 / 488 B | 168 / 0 B | 0 / 0 |
| K3 EP8 T4096 MXFP4x8 | 81 / 0 B | not sampled | 168 / 0 B | 0 / 0 |

For N3U, R11's control, epilogue and gather regions use at most R14, R214 and
R125 respectively. R9 had restricted all these role bodies to at most R77
after their early join. K3 uses at most R63/R74/R63. The address ranges and
counts are saved in `role-gpr-ranges.json`. These are static machine-code
facts, not profiler instruction counts or a performance result.

All three FC1 specializations passed the guard before their compiled callable
was returned to launch code: reqntid384, exact dec80/inc256/dec128 policies,
donors<=R0<=256 and required59392<=initial64512 registers. The three FC2
specializations have reqntid256, no setmaxnreg, and zero stack/local-memory
instructions. All jobs passed all513 source hashes, full-patch checks,
frozen winner/cache/route identity checks and persistent native-cache checks.

FC2 resource usage and instruction counts match R6: 1912 SASS instruction
sites for K3 and4464 for each N3U mode. The SASS instruction stream is not
identical: uniform-register assignment and branch layout changed with the
structured dispatch. `fc2-codegen-comparison.json` and the three SASS diffs
preserve this boundary. Do not claim bit-identical FC2 machine code.

The source is built from exact R6, not R9. All six original role bodies are
AST-identical after removing the three policy calls; comments are preserved.
Setup and final cleanup are byte-identical, other methods are unchanged, and
80 combinations of resident warp/CTA/gather/CLC role selection agree. Source
proof is in `../../register-structured/source-proof.json`.

PDL ordering is unchanged relative to R6. The host disables weight startup
prefetch for gathered FC1 (`enable_pdl and not gather_input`), so all FC1
warps already wait before role dispatch; R11's later register policy adds no
new weight/scheduler dependency wait. FC2 retains startup prefetch and compiles
out the register policy. Moving independent FC1 work ahead of its existing
wait is a separate future optimization, not a regression caused by R11.

Source kernel SHA256:
`3a2b03635a13faa50549de903eebb265a13c50d8ac804c2ae3b1e245da10650f`.
Archive SHA256:
`32228a11351b5f3d1e53bd20cd370b13a69a01fb6f71ba8973955b5d5953280a`.
All47 archived file hashes verified locally. GPU0 was idle/released at export.
No broad accuracy tests or sanitizer ran. Instrumented timing samples are
excluded from retention. Existing compilation caches remain intact.
