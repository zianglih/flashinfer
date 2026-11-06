# Independent SF pointer-shuffle native peer

The captured evidence verifies a failed resource gate, not a numerical failure. Both affected FC1s compiled and loaded for driver inspection, then stopped before their callable returned to the launch path. The unchanged guard rejected LOCAL48 for MXFP8 G2 and LOCAL16 for per-token G4. G1 passed the existing exact oracle; its FC1, FC2 and finalizer PTX, cubin and SASS are all byte-identical to their matching controls.

| FC1 case | Non-NOP control → candidate | SHFL.IDX | Local loads / stores | Driver local / native stack |
|---|---:|---:|---:|---:|
| MXFP8 N256, K8, G2 | 3,691 → 4,112 | 64 → 72 | 0/0 → 40/12 | 0 → 48 B |
| Per-token N256, K8, G4 | 3,255 → 3,669 | 64 → 96 | 0/0 → 31/9 | 0 → 16 B |
| MXFP4x8 N16, K4, G1 | Raw identity | Raw identity | 0/0 | 0 B |

All three FC1 images retain 168 initial registers and the normal empty compiler-options string. The failure receipts retain valid thread/pool checks; local storage is the only failed driver guard. `cuobjdump` reports spill stack48/16 and declared LOCAL0, while the CUDA driver reports total per-thread local48/16. These are consistent representations of spills, not evidence of zero local usage.

The two-half pointer exchanges survive inside the K loop. MXFP8 has eight extra unpredicated SHFLs at0xdc10–0xdee0 within the0xd1d0→0xf980 loop. Per-token has32 at0xb6f0–0xc0a0 within0xb430→0xdfb0. Original64 payload SHFLs precede those loops. Packed pointer reconstruction and the full-width word addition survive PTX; native `IMAD.WIDE.U32` adds the four-byte lane offset before the copies. Therefore this failure is not explained by hoisting every shuffled pointer before K. The native schedule overlaps some temporary pointer results and incurs spill traffic despite the original one-offset-per-lane source state. It does not establish which individual live value caused each spill or justify another register remedy.

The original route setup is source-identical. Whole-kernel global-load/SF-copy site counts stay13/4 for MXFP8 and29/16 for per-token. These pilots use top_k2, with no PTX divide instructions; they do not measure top_k22 route-division cost. The same four/16 SF copies remain predicated with the existing zero-fill contract; failed affected kernels have no numerical or performance result.

The [replayer](sf_pointer_shuffle_native_peer.py) checked every archive member, both full13,245-file source inventories, identical numerical/capture/guard helpers, all14 native images, the three exact reused-control records and the current046 four-module normal-load/hash/no-op cohort. Successful postflight and idle release are separate from the failed qualification status. No source, cache or GPU mutation occurred in this review.

[Machine-readable receipt](sf-pointer-shuffle-native-peer.json), SHA256 `b531a8a02a4da90acb4df06e6d9945a8c90871a65ed28ae4efe00a4765afc5d5`. Candidate `371510e6a745e8c7845d0918a7d5984386b07ff7eea3eb4749f3f5f8fe6ad6e4`; archive `a3170fe306e838e7a7b748a3c35f2e847805a7a490ff8a4cb99a335fd2aa1ed4`. Reject this candidate at the unchanged resource boundary; no timing claim.
