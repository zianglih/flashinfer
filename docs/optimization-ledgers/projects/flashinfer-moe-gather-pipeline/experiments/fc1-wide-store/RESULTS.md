# Adjacent FC1 payload stores: reject

The tested register-tensor joins do not produce wider stores. Both the two-dimensional join and the flat 32-element join generate identical PTX and cubins with explicit local-memory staging. No candidate kernel was launched after its resource guard failed, and no performance benchmark ran.

| Variant | Source kernel SHA256 | Initial registers | CUDA local bytes | Payload stores |
|---|---|---:|---:|---|
| Retained `02de7785` | `788b7f58267a773f049b25216d689ab6f60649ec168e1d278e0f3ef8ae6c8e17` | 168 | 0 | 16 × 64-bit |
| R2, `(16, 2)` register tensor | `47acaac2857b9d19fb802b78bc1929e26256c5d688dad397891c2bd686f12de0` | 168 | 272 | 16 × 64-bit |
| R3, flat 32-element tensor and static views | `1031f1a5dae35079da4ea16c708cb0482103ff772092ff591308df0c72582e31` | 168 | 272 | 16 × 64-bit |

The first exact case was nongated ReLU² W4A4, 193 tokens, hidden size 1024, intermediate size 640, two experts/top-2, M512/N128, two CTAs, PDL on, unfused output. The existing exact oracle passed on the control. This correctness-only harness used the existing two-active-cluster cap; the actual selected kernels used the ordinary scheduler. Candidate compilation completed, but the zero-local-memory guard stopped it before execution. Remaining queued MXFP8, W4A8, per-token, gated, and actual-CLC cases were not attempted.

PTX already contains a 256-byte `.local` depot, with eight `st.local.v2.b32`, eight `st.local.b64`, and eight `ld.local.b64` instructions around the converted payload joins. Native SASS has 16 `STL.64` and eight `LDL.64` instructions in this epilogue, without reducing the payload's 16 `STG.E.64` sites. `cuobjdump` reports `STACK:272 LOCAL:0`, while the CUDA function's `LOCAL_SIZE_BYTES` attribute reports 272 bytes. This is explicit packed-register-tensor materialization before PTXAS, not evidence of register-allocation spilling.

R2 and R3 have identical PTX SHA256 `17682b543d18a30947b8189884abd1ecc070cc61624295a2e35b90580b4a8d29` and cubin SHA256 `a83faea3fdffdf1e3c8d627b541f4e6b0df42206c3e28d91a50af5149184fe5d`. The changed representation therefore does not repair the lowering. R1 stopped earlier at a CuTe `absmax` type-join error; R2 replaced that temporary with the identical inline expression.

Evidence lives in this directory and sibling `fc1-wide-store-r2/` and `fc1-wide-store-r3/`: frozen patches/source manifests, private harnesses, full command/environment logs, source/resource receipts, exact control outputs, generated artifacts, and download hashes. The 13,245-file committed manifest matched the qualified composed source before each campaign. Scoped source checks remained active and the resource guard was never relaxed. The persistent native compilation cache was reused.

The review source copy is removed after recording its hash/status and preserving these external artifacts. Main source remains `02de7785`; GPU0 is idle. No commit, push, PR update, or performance claim results from this experiment.
