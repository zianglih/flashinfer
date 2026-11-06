# Fresh GLM5 W4A16 shared-helper regression

The only production difference is `moe_w4a16_utils.py`, retained `82254e20` versus the helper-only R2 candidate. Source manifests, all thirteen frozen choices, and the eight-rank route fingerprints are unchanged from the sealed setup. This is a native EP8 GLM5 forward benchmark with serialized C1/A1/A2/C2 phases and 100 strict-CUPTI samples per phase/token. The metric pools 200 per-iteration rank-MAX samples per arm, takes the median, then reports control/candidate latency ratios. Tokens 1 and 2 are measured but excluded from aggregate retention statistics.

## Harness failure history

- `../glm5-r2`: no timing was produced. Rank 0 attempted to read a returned native cubin pathname whose dump directory did not exist. Its exception was masked by the benchmark's collective NVSHMEM destruction while peers were in warmup. A sampled Python stack and the full logs/process receipt are preserved. Only the owned processes were terminated; the node was verified idle.
- `../glm5-r2-attempt2`: stopped during Python initialization, before GPU execution. The failure-only cleanup hook incorrectly treated the public `MoEEpLayer` factory as a class. The corrected hook targets the actual `MoEEpMegaLayer` class.
- This attempt adds a host-only rendezvous around native compile/resource observation, records artifact-only capture errors without allowing them to masquerade as codegen proof, and emits fatal exceptions before collective cleanup. All resource, source, tactic, routing, and timer guards remain fatal. Compile arguments/options and successful native execution/cleanup are unchanged.
- The eight early rank-0 artifact captures in C1 are explicitly marked missing. The compiler dump destinations were then created for all phases/ranks. This changes artifact storage only. Later native kernels have PTX/cubin receipts. No timing is reused from failed attempts.

`retry-provenance.json` records immutable input equivalence and compile forwarding. The successful timing run is `glm5-r2-attempt3`; the setup receipt preserves the earlier harness directory name as provenance, not as the current execution directory. The three original harness filenames are preserved in their own directories.

No sanitizer, retuning, event fallback, or production instrumentation is included. Complete results and native codegen/resource qualification are required before any regression conclusion.
