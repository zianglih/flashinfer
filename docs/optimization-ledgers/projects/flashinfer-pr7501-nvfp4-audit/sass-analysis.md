### SASS: why #7501 regressed and why the hoist helps

#7501 changed the standard-fast CUDA guard from `vecMax != 0` to `fp8SFVal != 0`: a nonzero block maximum can still round to a zero E4M3 scale, so the encoded-byte check is needed for the numerical contract. In the measured BF16/SF16 TMA specialization, this also changed the dependency of the **global** reciprocal, although that reciprocal only needs `SFScaleVal`.

Selected instructions dumped from the actual measured SM103a binaries with `cuobjdump -arch sm_103a -fun <kernel-symbol> -sass <fp4_quantization_103.so>`; intervening instructions and instruction-encoding words are omitted. Here `R0` holds the global scale and `R71` its reciprocal. Offsets identify instructions, not cycle counts.

```text
Parent 03d7f4a — P3 comes from vecMax before the conversion:
/*2140*/     FSETP.NEU.FTZ.AND P3, PT, R69.reuse, RZ, PT;
/*2170*/     F2FP.SATFINITE.E4M3.F32.PACK_AB_MERGE_C R69, RZ, R69, RZ;
/*2180*/ @P3 MUFU.RCP R71, R0;

#7501 fb02275 — P3 now depends on the converted E4M3 byte:
/*2160*/     F2FP.SATFINITE.E4M3.F32.PACK_AB_MERGE_C R69, RZ, R69, RZ;
/*2170*/     LOP3.LUT P3, R64, R69, 0xff, RZ, 0xc0, !PT;
/*2190*/ @P3 MUFU.RCP R71, R0;

fb02275 + fix — global reciprocal is unconditional and scheduled earlier:
/*1ff0*/     MUFU.RCP R71, R0;
             ... block-maximum reduction and scale computation ...
/*21a0*/     F2FP.SATFINITE.E4M3.F32.PACK_AB_MERGE_C R69, RZ, R69, RZ;
/*21b0*/     LOP3.LUT P3, R64, R69, 0xff, RZ, 0xc0, !PT;
/*2200*/ @P3 FMUL.FTZ R66, R71, R66;
/*2240*/ @P3 MUFU.RCP R64, R66;
```

The fix removes the `E4M3 conversion → byte predicate → global reciprocal` dependency and permits that reciprocal to overlap the reduction/conversion work. The encoded-byte predicate still gates the final scale computation, preserving zero-scale behavior and the original multiply/reciprocal arithmetic. The main/PR binaries show the same removal of predication (`@P3 MUFU.RCP R62, R2` at `0x24b0` becomes an unconditional `MUFU.RCP R62, R2` at `0x2450`). This is scheduling evidence consistent with the matched timing improvements below; no instruction-latency or stall-cycle count is inferred from the dump.
