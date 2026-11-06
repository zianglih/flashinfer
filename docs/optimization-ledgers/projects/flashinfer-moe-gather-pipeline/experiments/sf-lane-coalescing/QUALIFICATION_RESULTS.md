# SF lane coalescing: pilot gate stopped

Candidate `86836355` on retained `2b8eb9d8` failed the existing zero-local guard. The remaining nine pairs and the held 56-cell performance screen did not run. The canonical repository was not changed.

| Pilot FC1 | Control | Candidate | Outcome |
|---|---:|---:|---|
| NVFP4, N16/K256, G4 | 168 registers; driver local 0; 1,052 non-NOP | 168 registers; driver local 0; 1,083 non-NOP | Both exact calls passed |
| MXFP8, N256/K256 (K steps 8), G2 | 168 registers; driver local 0; 3,691 non-NOP | 168 registers; driver local 64; 4,112 non-NOP | Rejected before candidate FC1 launch |

The failed MXFP8 image has 43 `LDL` and 15 `STL` sites, versus none in the control. PTX has no explicit local depot. `cuobjdump` labels the allocation `STACK:64 LOCAL:0`; the loaded CUDA function reports `LOCAL_SIZE_BYTES=64`, which is what the guard checks. This is native register spilling, not an observed numerical mismatch. The outer artifact observer did not return after the guard failure; the separate closure extracts the compiler-retained image and preserves that provenance boundary.

The successful narrow pair also exposes additional work. Whole-FC1 static counts change by +31 non-NOP, global loads 12→14, shared loads 10→13, predicate operations 53→60 and register moves 53→57. The gathered offset setup in PTX adds guarded map reads at row-base +128/+256 bytes; it is not merely a source-level array reshaping. Static counts do not establish execution counts or end-to-end performance. Its ordinary-TMA FC2 and finalizer cubins are byte-identical.

Three exact calls completed: both controls and the narrow candidate. No candidate MXFP8 FC1 launch, remaining qualification, W4 test, sanitizer, timing, retuning, or guard relaxation occurred. G1 native equivalence and the remaining topology/padding matrix remain unqualified.

Evidence:

- `qualification-evidence/fetch.json`: archive `1edd5cb862b166b1b3666da0d4c2ad822bb08b1ca307c2792d85893a6dd5ef42`.
- `qualification-summary-partial.json`: complete native instruction-line parsing for the successful pair and exact-result bindings.
- `pilot-native-failure.json`: failed wide FC1 resources, all spill sites and artifact hashes.
- `pilot-closure-evidence/evidence/closure.json`: both full 13,245-file source inventories unchanged; all four persistent release libraries/Ninja descriptions unchanged; GPUs 0/1 released at 0MiB/0% utilization/no PIDs.
- Initial receipt-path failure and the subsequent rolling-idle telemetry stop are preserved separately. Both preceded candidate launch; the resumed controller reused the passed controls and kept all source, compiler and resource checks unchanged.

Recommendation: reject this candidate under the agreed no-spill gate. No performance benefit is claimed or measured. Keep the source patch and CPU/native evidence; do not introduce a shape exception or relax the resource quota to rescue it.
