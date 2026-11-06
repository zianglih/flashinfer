# N128 and N64 native quality gate

Both saved matched pairs pass the native gate for the existing FC1 first16 runtime trial. Neither capture executes a GPU kernel or establishes numerical correctness or performance. The original N128 receipt and notes are preserved.

| Geometry | Whole instructions, control → candidate | FC1 region | FC2 region | Registers / threads | Stack / local |
|---|---:|---:|---:|---:|---:|
| M256/N128/K256, C2 | 5856 →5864 | 223 →234 | 227 →227 | 96 /640 | 0 /0 |
| M256/N64/K256, C2 | 5528 →5536 | 223 →234 | 227 →227 | 96 /640 | 0 /0 |

Both candidate FC1 bodies have precisely the same instruction histogram and added work. Four packed LDS.128, two SF LDS,64 E2M1 conversions, eight E4M3 conversions,32 BF16 multiplies,32 BF16 fused operations and eight STTM.x8 are retained. Whole-kernel MMA16 and broadcast4 counts are unchanged. Two decode WGs and all four register-redistribution operations remain unchanged.

The N64 capture is `profiles/fc1-first16-e359-m256n64c2-001`. Its first packed LDS.128 is at `0x64f0`; first16 scaled values complete in `R4–R11` at `0x6780`, before decoded TRYWAIT `0x67e0`. The slow path `0x14420–0x14470` writes only `R0/P0`, loops at `0x14430`, and returns at `0x6800`. It and the fast path preserve the packet until direct STTM `0x6b30`.

N64's remaining packed loads `0x6840/0x68b0/0x68f0` precede the next raw-ready probe `0x6b10`. Final STTM `0x7330`, async fence `0x7340`, elected raw release `0x7360` and decoded publication `0x7370` preserve ownership ordering. There are no pre-acquire TMEM stores. Generated PTX retains the same store and wait instructions as the control.

For both geometries, all seven added move instructions trace directly to packed LDS.128 definitions, not decoded BF16 values. The seven extra PRMT instructions and additional mask/packing work are real costs of the per-byte scale path. They are not hidden by the no-spill result. A source-only packed-scale refinement, if justified, is a separate candidate and does not change this admission.

N64 FC2 is instruction-identical after branch-label renaming and candidate uniform-register mapping `{19:20,20:21,21:22,22:23}` to control; N128's separate mapping is documented in `README.md`. No runtime-policy branch or duplicate MMA/decode sequence was introduced. Native source correlation, explicit slow-path liveness, packed-move definitions, complete histograms and file hashes are in the two evidence JSON files.

Both pair summaries report completion with zero exit codes and unchanged source/native state. Their owner before/after files are byte-identical, postflight GPU/worker inventories are empty, and recorded child process groups have no live members. These are saved execution receipts, not fresh remote queries by this reviewer. All analysis here used local files and AST-sliced pure functions from the established reader.
