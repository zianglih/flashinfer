# Universal SF-order result

Candidate `f377110b2d6ef19205af30c277a65ce783274729744d205943d3e6997ec24cf3` on clean base `fb66a27e`. Source remains unstaged in `flashinfer-fc1-gather-sf-order-review`.

- Universal sequence: SFA0, optional SFA1, optional gathered-B wait, SFB. One SFB copy site; no new behavior knob.
- 7 existing exact tests passed; 8 additional local exact-oracle cases passed with M512 FC1/FC2 with full 512-channel outputs, all four formats and CLC off/on. These local cases reuse the repository oracle and NVFP4 test construction. No repo test additions or sanitizer.
- Same-GPU C-A-A-C screen: 44 cells, 17,600 raw strict CUPTI samples, frozen routes/tactics; 36 affected cells and 8 W4A16 diagnostics.
- All 128 runtime compile-resource observations in 10 phase receipts passed.
- Affected gmean **+0.098%**; decode +0.028%, middle -0.020%, prefill +0.191%. This is effectively neutral overall.

| Shape / family | Gmean |
|---|---:|
| kimi-k3 EP | +1.049% |
| nemo3-ultra EP | +0.014% |
| v41-flash EP | -0.383% |
| v3 TP | +0.185% |
| v41-flash TP | +0.103% |

Large prefill cells are noisy: V41F EP16K MXFP8 −1.288% has 3.60% control /2.61% candidate phase spread; MXFP4x8 −1.798% has 7.00% /0.24%. K3 EP16K MXFP4x8 +4.280% has 3.21% /0.79%, with both candidate passes below both controls. V3 TP16K MXFP4x8 +1.211% has 0.64% /1.88%. Do not treat these single-cell magnitudes as stable standalone wins or regressions.

This supports retaining the cleaner independent-readiness ordering for instruction/lifecycle clarity if desired, without claiming a broad speedup. The FC2 two-channel reorder has explicit exact validation.

The extra local-test runner first rejected collection because its parser only admitted `tests/` node paths. A local helper-only parser adjustment was made, then all eight tests passed; no kernel or oracle changed. Original selection and failed collection receipt are preserved separately.

Artifacts: `report/cells.csv`, `report/summary.json`, `evidence/validation/{smoke,two-channel-local-validated}`, `evidence/perf`. Archive SHA256 `f120d77934423e0fefb5ec5f39474978f495c776e2da5b699d15860ff78b4bda`.
