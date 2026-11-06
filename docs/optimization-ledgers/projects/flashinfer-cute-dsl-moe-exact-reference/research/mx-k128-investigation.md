# Exploratory MX K128 launch-fault investigation

Frozen production: `8c1a20173cf166b9fc279f6ae3ec5386250c5c5e`.
One B200 on `fi-w4a4-narrow-1025`, GPU3. No production changes were made.

The original edge probe faulted after six passing NVFP4 cases, at its first
homogeneous MX control. It tested logical K64 by padding native K to 128,
32 routed rows, one expert, 128 output channels, physical tactic `(128,32)`,
PDL disabled, and unfused finalize. The original asynchronous traceback
alone did not locate the failing operation.

The isolated probe now synchronizes after preparation, each integer-oracle
orientation, and the native launch. Both oracle orientations pass and agree
at FP32 storage-bit level before the native launch faults. A native-only
process, without launching either oracle, reproduces the fault.

| Receipt | Channels | Native K | Output | Input storage | Native result |
|---|---:|---:|---|---|---|
| mx-k128-fp32-r3 | 128 | 128 | FP32 | raw bytes | illegal instruction at synchronization |
| mx-k128-bf16-r3 | 128 | 128 | BF16 | raw bytes | illegal instruction at synchronization |
| mx-k128-typed-nativeonly-r4 | 128 | 128 | FP32 | E4M3 | illegal instruction at synchronization |
| mx-k128-channel256-r4 | 256 | 128 | BF16 | E4M3 | zero bit mismatches |
| mx-k256-control-r4 | 128 | 256 | FP32 | raw bytes | zero bit mismatches |
| mx-k128-pad-allocation-r5 | 128 | 128 | FP32 | raw bytes; doubled backing allocation | illegal instruction at synchronization |

All tensors have zero storage offsets and pointers aligned to 128 bytes.
Ordinary SF tensors have canonical 512-byte physical atoms: shape
`(32,4,1,4,1,1)`, strides `(16,4,512,1,512,512)` at 128 channels/K128.
The padded-allocation control doubles A/B/SF backing allocations, preserves
the logical shape and strides, fills additional data bytes with zero and
additional scale bytes with UE8M0 unity, and still faults.
The capability adapter accepts this geometry (`M % 128 == 0`,
`K % (4 * sf_vec_size) == 0`, routed capacity divisible by route tile).
Its explicit pointer types make raw-byte versus E4M3 tensor metadata
irrelevant to the native data interpretation; both were nevertheless tested.

The passing 256-channel/K128 control agrees with the parent task's passing
full-chain K128 configuration. The broader native instruction-prefix
qualification used K256 zero padding for MX and remains 12/12 exact. Do not
describe the exploratory failure as a generic native K128 bug or supported
shape boundary. The cause remains unresolved; the degenerate weight/SF
geometry is a possible lead, not a demonstrated cause. No production fix
belongs to this reference-only investigation.

Suggested PR limitation:

> One exploratory homogeneous MX control (128 output channels, K128,
> physical tactic 128x32) reproducibly faults during the native launch.
> The independent oracle completes, and controls at 256 channels/K128 and
> 128 channels/K256 are bit-exact. Full-chain MX K128 also passes. The fault
> remains unresolved and is not counted as an oracle numerical mismatch.

Scripts and complete raw receipts are preserved in
`artifacts/mx-k128-investigation/`; source hashes are recorded beside them.
