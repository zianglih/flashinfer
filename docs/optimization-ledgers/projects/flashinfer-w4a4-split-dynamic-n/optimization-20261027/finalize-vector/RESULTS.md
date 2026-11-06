# Rejected at generated-code screen

The three source-paired exact cases passed on C3 B300 GPU2 with CuTe4.8 and
CUDA13.2. All six actual PTX/cubin/SASS/resource artifacts are preserved in
`evidence/codegen`; no spills, no changed packed-arithmetic count, and no changed
128-bit payload load/store count were observed.

| Case | Registers, control → candidate | Instructions, control → candidate | ISETP, control → candidate |
|---|---:|---:|---:|
| H128, top-k8, one vector |32 →34|248 →240|13 →9|
| H7168, top-k8, seven vectors |80 →40|936 →1328|9 →20|
| H2048, top-k22, two effective vectors |58 →102|736 →1136|27 →65|

The loop interchange does shorten the seven-vector accumulator lifetime, but
adds42% static instructions there. For top-k22 it increases both registers and
instructions substantially (+54% instructions), consistent with repeated
control work and longer routing-metadata lifetimes. This fails the intended
general simplification criterion. The one-vector case is also not codegen
identical, although its instruction count is slightly lower.

Rejected before the optional28-case exact follow-up and before any end-to-end
timing. No performance claim is made from these counts. GPU2 was released; the
full retained-candidate campaign's current and legacy source manifests were
verified unchanged before and after the gate. Its frozen snapshot is untouched.

Candidate finalize SHA256: `f90f4a9d25aa6c097eb8166bc3fca1800df4f4af9bc1ae2baa87a48b98b45b5b`.
Evidence archive SHA256: `e30d1cca6e5793d6e07a0c570a5e63a24daad9cc5ab0903ce0fee70dbd07d96e`.
The source-only review clone is closed after verifying its exact patch/source;
all helper scripts and raw evidence remain here.
