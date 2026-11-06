# Static Gather4 traversal gate

Base22ffe662, candidate kernel8590ed74f7df06e40145e03ea76b572dd32b6094d14a8932de34c7d044a78515. Both source arms have full514-file manifests, preserve frozen native winners and compile with markers disabled.

| Actual FC1 specialization | Whole-kernel non-NOP before/after | Gather-scope non-NOP before/after | Branches before/after | Local bytes |
|---|---:|---:|---:|---:|
| K3 EP8 T4096 M256 N128 K256 cluster2 |1994 /1955|314 /275|182 /170|0 /0|
| K3 EP8 T8192 M256 N192 K256 cluster2 |2046 /1985|405 /344|185 /165|0 /0|
| V3 TP8 T8 M256 N16 K256 cluster2 |1626 /1626|213 /213|199 /199|0 /0|

N16 PTX and CUBIN are byte-identical. All three have unchanged SHFL/R2UR counts, register reservation96, 640 threads, no LDL/STL and no higher reachable general-register index. The non-gather warp scopes have unchanged instruction counts. N128 removes12 uniform branches,12 ULOP3,9 UIADD3 and6 ULEA; N192 removes20 uniform branches/ULOP3/ULEA and19 UIADD3 while adding18 UMOV. Counts are compiled-code evidence, not a latency prediction.

Existing33-case W4 exact gate passed, with zero-local checks on every captured Gather4 specialization. Four-cell fixed-winner CAAC follows: K3 EP4K/8K and V3 TP8/4K, strict100 CUPTI cold-L2 graph timing and read-only NVML, no new autotuning or sanitizer. Full results remain pending.

The first helper transfer exceeded the shell argument-size limit before any remote command ran. The deployment manifest was encoded by its full sorted-hash digest, preserving all514 per-file source hashes in local and remote JSON. An early fetch helper mistakenly downloaded the prior marker experiment metadata; those duplicate bytes are quarantined in incorrect-marker-fetch and are not part of this gate. The correct fresh codegen archive hash is59fc7aaf2edd385a066dbf838dfdb9262e4d880b3572e94309bdfa1a88dfd93b.
