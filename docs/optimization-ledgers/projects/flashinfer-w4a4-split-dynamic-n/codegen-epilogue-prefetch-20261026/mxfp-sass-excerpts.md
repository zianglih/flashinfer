# MXFP8 scale-load SASS excerpts

Instruction offsets refer to the full sibling `.sass` files. Context retains branches and address calculation.

## control-0def601d token-32/fc1-n16-m128

```sass
...
/*2ab0*/ UIADD3 UR11, UPT, UPT, UR6, UR11, URZ;
/*2ac0*/ UMOV UR10, URZ;
/*2ad0*/ ULEA UR5, UR10, UR57, 0x3;
/*2ae0*/ SHF.L.U32 R5, R68, 0x1f, RZ;
/*2af0*/ ISETP.GE.AND P0, PT, R75, 0x1, PT;
/*2b00*/ SHF.L.U32 R65, R69, 0x1f, RZ;
/*2b10*/ SYNCS.PHASECHK.TRANS64.TRYWAIT P1, [UR5+0xa0], R5;
/*2b20*/ @!P1 BRA 0x5c10;
/*2b30*/ @!P0 BRA 0x3cf0;
/*2b40*/ R2UR UR12, R66;
/*2b50*/ IMAD.HI.U32 R60, R2, 0x38e38e39, RZ;
/*2b60*/ R2UR UR13, R67;
/*2b70*/ BSSY.RECONVERGENT B0, 0x3cf0;
/*2b80*/ LEA R38, P0, R3.reuse, R72, 0x2;
/*2b90*/ SHF.R.U32.HI R63, RZ, 0x3, R60;
/*2ba0*/ LEA.HI.X.SX32 R39, R3, R73, 0x2, P0;
/*2bb0*/ IMAD R2, R63, -0x24, R2;
/*2bc0*/ LDG.E R3, desc[UR12][R38.64];
/*2bd0*/ ULEA UR12, UR10, UR11, 0x5;
/*2be0*/ IMAD.IADD R0, R2, 0x1, R61;
/*2bf0*/ SHF.L.U32 R0, R0, 0x7, RZ;
/*2c00*/ LDTM.16dp64bit.x16 R20, tmem[UR12];
/*2c10*/ LDTM.16dp64bit.x16 R4, tmem[UR12+0x100000];
/*2c20*/ LEA.HI.SX32 R0, R0, UR4, 0x1f;
```

## epilogue-prefetch token-32/fc1-n16-m128

```sass
...
/*2b20*/ LEA R52, P0, R5, R70, 0x2;
/*2b30*/ SHF.L.U32 R0, R63, 0x1f, RZ;
/*2b40*/ LEA.HI.X.SX32 R53, R5, R71, 0x2, P0;
/*2b50*/ SHF.R.U32.HI R3, RZ, 0x3, R3;
/*2b60*/ ISETP.GE.AND P0, PT, R69, 0x1, PT;
/*2b70*/ SHF.L.U32 R72, R66, 0x1f, RZ;
/*2b80*/ LDG.E R52, desc[UR12][R52.64];
/*2b90*/ SYNCS.PHASECHK.TRANS64.TRYWAIT P1, [UR5+0xa0], R0;
/*2ba0*/ IMAD R61, R3, -0x24, R4;
/*2bb0*/ @!P1 BRA 0x5bf0;
/*2bc0*/ @!P0 BRA 0x3cd0;
/*2bd0*/ ULEA UR12, UR10, UR11, 0x5;
/*2be0*/ LEA R0, R61, R2, 0x7;
/*2bf0*/ BSSY.RECONVERGENT B0, 0x3cd0;
```

## control-0def601d token-32/fc2-n16-m128

```sass
...
/*2970*/ R2UR UR7, R7;
/*2980*/ LDG.E R4, desc[UR8][R4.64];
/*2990*/ ULEA UR8, UR11, UR49, 0x3;
/*29a0*/ IMAD.U32 R10, RZ, RZ, UR6;
/*29b0*/ IMAD.U32 R11, RZ, RZ, UR7;
/*29c0*/ LDG.E R7, desc[UR12][R10.64];
/*29d0*/ SYNCS.PHASECHK.TRANS64.TRYWAIT P1, [UR8+0xa0], R6;
/*29e0*/ VIADD R4, R4, -UR5;
/*29f0*/ VIMNMX R0, PT, PT, R4, 0x10, PT;
/*2a00*/ ISETP.GE.AND P0, PT, R3, R0, PT;
/*2a10*/ @!UPT UIADD3 URZ, UPT, UPT, URZ, URZ, URZ;
/*2a20*/ @!P0 LDC.64 R8, c[0x0][0x5a8];
/*2a30*/ @!P1 BRA 0x4f10;
...
/*2af0*/ R2UR UR7, R77;
/*2b00*/ UIMAD UR4, UR4, -0x28, UR14;
/*2b10*/ UIADD3 UR4, UPT, UPT, UR4, UR15, URZ;
/*2b20*/ LDTM.16dp64bit.x16 R20, tmem[UR5];
/*2b30*/ LDTM.16dp64bit.x16 R44, tmem[UR5+0x100000];
/*2b40*/ ULEA UR4, UR4, UR10, 0x7;
/*2b50*/ LDG.E R86, desc[UR6][R86.64];
/*2b60*/ UISETP.GT.AND UP0, UPT, UR4, 0x13ef, UPT;
/*2b70*/ PLOP3.LUT P1, PT, PT, PT, UP0, 0x80, 0x8;
/*2b80*/ UISETP.GT.AND UP0, UPT, UR4, 0x13ff, UPT;
/*2b90*/ ISETP.GE.OR P1, PT, R3.reuse, R0.reuse, P1;
/*2ba0*/ PLOP3.LUT P0, PT, PT, PT, UP0, 0x80, 0x8;
/*2bb0*/ ISETP.GE.OR P0, PT, R3, R0, P0;
```

## epilogue-prefetch token-32/fc2-n16-m128

```sass
...
/*2990*/ IMAD.U32 R7, RZ, RZ, UR7;
/*29a0*/ LDG.E R4, desc[UR8][R6.64];
/*29b0*/ VIADD R4, R4, -UR5;
/*29c0*/ LEA R84, P0, R9.reuse, R86, 0x2;
/*29d0*/ LEA.HI.X.SX32 R85, R9, R87, 0x2, P0;
/*29e0*/ VIMNMX R0, PT, PT, R4, 0x10, PT;
/*29f0*/ LDG.E R84, desc[UR8][R84.64];
/*2a00*/ SYNCS.PHASECHK.TRANS64.TRYWAIT P1, [UR6+0xa0], R5;
/*2a10*/ ISETP.GE.AND P0, PT, R3, R0, PT;
/*2a20*/ @!UPT UIADD3 URZ, UPT, UPT, URZ, URZ, URZ;
/*2a30*/ @!P0 LDC.64 R8, c[0x0][0x5a8];
/*2a40*/ @!P1 BRA 0x4ef0;
/*2a50*/ VIADD R78, R3, UR5;
/*2a60*/ @!P0 R2UR UR8, R76;
```

## control-0def601d token-4096/fc1-n128-m256

```sass
...
/*28f0*/ LEA R77, R60, UR8, 0x2;
/*2900*/ UIADD3 UR19, UPT, UPT, UR61, UR10, URZ;
/*2910*/ USHF.L.U32 UR20, UR20, 0x1, URZ;
/*2920*/ ULEA UR15, UR18, UR45, 0x3;
/*2930*/ SHF.L.U32 R7, R73, 0x1f, RZ;
/*2940*/ LDC.64 R8, c[0x0][0x630];
/*2950*/ SYNCS.PHASECHK.TRANS64.TRYWAIT P0, [UR15+0x80], R7;
/*2960*/ @!P0 BRA 0x5c20;
/*2970*/ IMAD.HI.U32 R61, R4, 0x38e38e39, RZ;
/*2980*/ R2UR UR10, R69;
/*2990*/ LDCU.64 UR16, c[0x0][0x610];
/*29a0*/ R2UR UR8, R74;
/*29b0*/ IMAD.WIDE R8, R5, 0x4, R8;
/*29c0*/ SHF.R.U32.HI R61, RZ, 0x2, R61;
/*29d0*/ R2UR UR9, R75;
/*29e0*/ IMAD R2, R61, -0x12, R4;
/*29f0*/ LEA R2, R2, UR10, 0x1;
/*2a00*/ IMAD.SHL.U32 R2, R2, 0x80, RZ;
/*2a10*/ LDG.E R72, desc[UR8][R8.64];
/*2a20*/ IMAD.SHL.U32 R61, R61, 0x80, RZ;
/*2a30*/ ULEA UR14, UR18, UR19, 0x7;
/*2a40*/ LEA.HI.SX32 R2, R2, UR4, 0x1f;
/*2a50*/ UMOV UR8, URZ;
/*2a60*/ SHF.R.S32.HI R5, RZ, 0x1f, R2;
/*2a70*/ LEA.HI R0, R5, R2, RZ, 0x7;
```

## epilogue-prefetch token-4096/fc1-n128-m256

```sass
...
/*2950*/ ULEA UR15, UR18, UR45, 0x3;
/*2960*/ SHF.L.U32 R0, R73, 0x1f, RZ;
/*2970*/ IMAD.HI.U32 R61, R4, 0x38e38e39, RZ;
/*2980*/ R2UR UR10, R69;
/*2990*/ LDCU.64 UR16, c[0x0][0x610];
/*29a0*/ IMAD.WIDE R6, R5, 0x4, R6;
/*29b0*/ LDG.E R72, desc[UR8][R6.64];
/*29c0*/ SYNCS.PHASECHK.TRANS64.TRYWAIT P0, [UR15+0x80], R0;
/*29d0*/ SHF.R.U32.HI R61, RZ, 0x2, R61;
/*29e0*/ IMAD R2, R61, -0x12, R4;
/*29f0*/ LEA R2, R2, UR10, 0x1;
/*2a00*/ IMAD.SHL.U32 R2, R2, 0x80, RZ;
/*2a10*/ LEA.HI.SX32 R2, R2, UR4, 0x1f;
/*2a20*/ SHF.R.S32.HI R5, RZ, 0x1f, R2;
```

## control-0def601d token-4096/fc2-n128-m256

```sass
...
/*2620*/ IMAD.U32 R11, RZ, RZ, UR11;
/*2630*/ IMAD.U32 R5, RZ, RZ, UR7;
/*2640*/ ULEA UR4, UR6, UR15, 0x1;
/*2650*/ LDG.E R7, desc[UR12][R10.64];
/*2660*/ USHF.L.U32 UR4, UR4, 0x7, URZ;
/*2670*/ LDG.E R64, desc[UR8][R4.64];
/*2680*/ SYNCS.PHASECHK.TRANS64.TRYWAIT P1, [UR16+0x60], R0;
/*2690*/ LEA R92, P0, R7, R90, 0x2;
/*26a0*/ VIADD R64, R64, -UR5;
/*26b0*/ @!P1 BRA 0x4d60;
/*26c0*/ LEA.HI.X.SX32 R93, R7, R91, 0x2, P0;
/*26d0*/ UISETP.GT.AND UP0, UPT, UR4, 0x13ff, UPT;
/*26e0*/ VIMNMX R70, PT, PT, R64, 0x80, PT;
...
/*27e0*/ @P4 VIADD R6, R69, UR5;
/*27f0*/ @!P3 R2UR UR12, R72.reuse;
/*2800*/ @!P3 R2UR UR13, R73.reuse;
/*2810*/ @!P2 R2UR UR10, R72.reuse;
/*2820*/ @!P2 R2UR UR11, R73.reuse;
/*2830*/ @!P1 R2UR UR8, R72;
/*2840*/ LDG.E R92, desc[UR18][R92.64];
/*2850*/ @!P1 R2UR UR9, R73.reuse;
/*2860*/ @P4 R2UR UR7, R73;
/*2870*/ LEA.HI.X.SX32 R0, R0, RZ, 0x1, P0;
/*2880*/ LEA R4, P0, R5.reuse, UR24, 0x2;
/*2890*/ LEA.HI.X R5, R5, UR25, R0, 0x2, P0;
/*28a0*/ @P4 IMAD.WIDE R8, R6, 0x4, R8;
```

## epilogue-prefetch token-4096/fc2-n128-m256

```sass
...
/*2620*/ IMAD.U32 R65, RZ, RZ, UR7;
/*2630*/ R2UR UR7, R73;
/*2640*/ LDG.E R64, desc[UR8][R64.64];
/*2650*/ VIADD R64, R64, -UR5;
/*2660*/ LEA R92, P0, R5.reuse, R90, 0x2;
/*2670*/ LEA.HI.X.SX32 R93, R5, R91, 0x2, P0;
/*2680*/ LDG.E R92, desc[UR6][R92.64];
/*2690*/ UIMAD UR6, UR4, -0x14, UR14;
/*26a0*/ SYNCS.PHASECHK.TRANS64.TRYWAIT P0, [UR16+0x60], R0;
/*26b0*/ ULEA UR4, UR6, UR15, 0x1;
/*26c0*/ USHF.L.U32 UR4, UR4, 0x7, URZ;
/*26d0*/ @!P0 BRA 0x4d40;
/*26e0*/ VIMNMX R70, PT, PT, R64, 0x80, PT;
/*26f0*/ UISETP.GT.AND UP0, UPT, UR4, 0x13ff, UPT;
/*2700*/ BRA.U UP0, 0x3730;
```
