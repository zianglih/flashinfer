# W4A16 static loop interchange qualification

Unstaged review: flashinfer-w4a16-linear-issue-review, retained22ffe662 base, kernelb8f124f187ec169b101c56a72cce2732833b89bf6ef3b72eaa0695f7a04b5da7. Simplifies the previous linear task formulation to two ordinary compile-time loops: K chunks outside, row groups inside. Diff10 additions/11 deletions; no behavioral knob, runtime division/remainder or new ownership exception. Source geometry proof and all copy metadata/bytes/arrivals remain the same as w4a16-linear-issue.

First gate requires identical PTX and CUBIN for actual native N16/N128/N192 between the already33-exact-tested8590 source and this plain loop form. No timing may begin unless all three match and zero-local assertions pass. The24-cell qualification then uses all four models EP/TP, tokens8/4096/16384, unchanged native tactic caches and frozen routes, fresh22ffe same-GPU controls, C-A-A-C100strictCUPTI coldL2 graph samples and read-onlyNVML2ms telemetry. No new autotuning, clock locking or sanitizer.

GPU assignment:3V3,4V41F,5K3,7N3U; EP then TP on each. External agent explicitly released3/4. Root approved broadened screen after source/codegen gate. Existing small K3 drifty rows stay visible in prior folder and are not promoted to a speedup claim. Retention can be based on simpler instructions if broader performance has no material regression.
