# Uniform-128 two-epilogue feasibility: rejected as proposed

The compile-only diagnostic fails the resource gate. Do not implement the full two-epilogue design or run performance tests from this proposal. The retained kernel is unchanged.

## Boundary

- Control: retained `b13963b0cc8409aeb92048b9ec7cf3be18f0a57c`; all 514 guarded source hashes verified.
- Diagnostic: swap kernel `2f14abc9ea6969f596a73c7b1c59107bc6635a4eacb2493fda96309c8ec8bbb6`, with 512 FC1 threads, an idle fourth warpgroup, unchanged existing role bodies, no role `setmaxnreg`, and explicit FC1 `-maxrregcount=128`. FC2 remains unchanged.
- This is an artifact-only, unlaunchable compiler probe. `capture.py` returns an object that raises on invocation; both arm receipts record zero owned kernel launches. No correctness, sanitizer, or performance test was run.
- Actual ELF thread count, compiled register cap, source role guard, absence of `USETMAXREG`, and the 65,536-register allocation bound all passed.

## Paired resource results

| Case | Control REG / STACK | Diagnostic REG / STACK | Control LDL / STL | Diagnostic LDL / STL |
|---|---:|---:|---:|---:|
| nv-n16 | 168 / 0 | 68 / 0 | 0 / 0 | 0 / 0 |
| nv-m512-relu | 168 / 0 | 114 / 0 | 0 / 0 | 0 / 0 |
| nv-n256-relu | 168 / 0 | 106 / 0 | 0 / 0 | 0 / 0 |
| pt-n128-situ | 168 / 0 | 93 / 0 | 0 / 0 | 0 / 0 |
| mx4-n128 | 168 / 0 | 78 / 0 | 0 / 0 | 0 / 0 |
| mx8-n256-relu | 168 / 0 | 128 / 144 | 0 / 0 | 18 / 36 |
| mx4-m512-k8 | 168 / 168 | 128 / 96 | 21 / 21 | 51 / 22 |
| fc2-nv | 79 / 0 | 79 / 0 | 0 / 0 | 0 / 0 |
| fc2-mx | 98 / 0 | 98 / 0 | 0 / 0 | 0 / 0 |

Both FC2 controls are byte-identical in PTX, CUBIN, SASS, and resource output. Five FC1 representatives have no local traffic; two fail the no-new-spill gate.

## Location of the added local traffic

- **MXFP8 N256 ReLU2:** all 18 `LDL` and 36 `STL` sites lie in the epilogue main region, after the thread-ID `>255` dispatch at PC `0x4300` and before the gather dispatch at `0xe3e0`. They are interleaved with the existing TMEM ownership transpose and quantization slabs (first loads `0x4b70/0x4bc0`; repeated predicated stores begin at `0x57c0`). Control has no local-memory instructions. This is a real epilogue budget failure, rather than only the previously known control-role spill.
- **MXFP4x8 M512/N128/K8:** retained control has 21 `LDL.64` and 21 `STL.64` sites in control/MMA descriptor work. The diagnostic has six new 32-bit stores before role dispatch, 30 loads/16 stores in the control main region, four loads in epilogue, three in gather, and 14 out-of-line loads conservatively left unclassified. Its smaller stack (168→96 bytes) therefore does not imply improvement: local-load sites increase 21→51. Full site lists and dispatch anchors are in `analysis.json`.

## Decision and limits

Reject the proposed unchanged-epilogue uniform-128 organization before a production rewrite. The abstract two-group ownership proof remains useful, but does not remove this measured resource obstacle. A genuine partition could change live ranges; this diagnostic does not prove every possible two-epilogue implementation impossible. Assigned register count and static instruction sites do not measure peak liveness or runtime spill frequency. `cuobjdump LOCAL:0` is not treated as spill-free when `STACK` and `LDL/STL` are nonzero.

No local review repository was created. Immutable source snapshots, patch, no-launch helpers, arm receipts and all codegen artifacts remain under this directory; GPU7 was released.

Evidence: `analyze.py`, `analysis.json`, `source-proof.json`, `fetch-receipt.json`, and `evidence/{control,candidate}/receipt.json`. Archive SHA256: `14a88f78e84ff614ce2c586e0c1ade5c49efd94cccf7935439275a876e22d188`.
