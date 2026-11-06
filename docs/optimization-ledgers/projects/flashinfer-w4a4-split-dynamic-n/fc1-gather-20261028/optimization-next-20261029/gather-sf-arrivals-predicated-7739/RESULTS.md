# Predicated SF arrival spelling: compile-only rejection

R1 does not achieve its intended branch reduction. The source-level PTX predicate still lowers to a branch and BSSY/BSYNC around an unpredicated SASS ARRIVES. Keep the simpler structured R0 condition for any further ownership experiment; do not retain this private helper on instruction-sanity grounds.

- Base77391; control kernel`dca375bbf01d0fe5fb0c7b8c091e932f2189735c94d4d08b59fa82ea4c6999c1`, candidate`8630cc3bef6d696479cb90a7f1e97a627edbccaf07dbca305fed3d37a02e377c`.
- Ten compile-only cases/20 captures per arm. No owned MoE kernels launched, no timing or numeric-test result claimed.
- Actual executable REG, STACK, LOCAL, shared bytes and role budgets match. All20 resource guards pass. All10 FC2 and3/4wide FC1 CUBINs are byte-identical. The fourth wide FC1 (MXFP8 N256) differs only by uniform-register renaming in the normalized instruction sequence; its opcode counts/resources are identical.
- Init counts correctly become17/33/65 for N16/N32/N64; MMA/TMA/SF-copy/arrival site counts remain unchanged.
- Scope hooks passed with source unchanged. Archive`69aa3203b4561b37c0b61ccc919d066094ba4ed8bcb08150a18fa41ad677a4d5`,225 verified files.

|Capture|Physical N|SF vector|CTA group|Non-NOP delta|BRA delta|BSSY delta|BSYNC delta|
|---|---:|---:|---:|---:|---:|---:|---:|
|000-FC1|16|16|2|+3|+1|+1|+1|
|002-FC1|256|16|1|+0|+0|+0|+0|
|004-FC1|16|16|2|+3|+1|+1|+1|
|006-FC1|256|16|1|+0|+0|+0|+0|
|008-FC1|16|32|2|+7|+2|+2|+2|
|010-FC1|256|32|1|+0|+0|+0|+0|
|012-FC1|16|32|2|+7|+2|+2|+2|
|014-FC1|256|32|1|+0|+0|+0|+0|
|016-FC1|32|16|1|+7|+2|+2|+2|
|018-FC1|64|32|2|+13|+4|+4|+4|

The prepared41-case exact driver was not launched because the compile-only purpose failed. N32/N64 have code-generation/resource qualification and the original exhaustive ownership proof, but not numeric qualification of this R1. Local source and all helper scripts remain preserved pending parent decision.
