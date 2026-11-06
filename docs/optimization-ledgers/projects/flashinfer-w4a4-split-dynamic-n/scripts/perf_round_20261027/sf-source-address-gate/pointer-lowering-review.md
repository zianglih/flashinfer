# Masked pointer lowering

The installed SDK maps `Pointer.__add__` to `cute.add_offset`. A compile-only probe kept that operation alive via an uninvoked output store and used the same global address space and byte element type as SF storage. The final LLVM dialect IR contains:

```mlir
%1 = llvm.getelementptr %arg0[%arg1] : (!llvm.ptr<1>, i32) -> !llvm.ptr<1>, i8
```

There is no `inbounds`, `nuw`, or `nsw` flag on the GEP. Computing a masked address beyond the physical allocation therefore does not introduce an inbounds/provenance poison promise through this operator. The complete paired kernel artifacts separately retain integer address arithmetic and cp.async source size0 on inactive rows, so no source bytes are accessed there. This is a minimal installed-lowering proof, not a claim that full production LLVM IR was captured. No function or GPU kernel was invoked by the probe.

`pointer-lowering-review.json` binds the successful probe and installed SDK source hashes. Earlier hidden-device timeout and return-only DCE probes remain separate and provide no positive evidence.
