# Dedicated-only norm SASS proof

Final source b85eff41 + patch9ca20e96ee3f91f104981205962d5473011604061eb933f52e8743735f405f14. The existing exact gate exercises uniform-NV SiTU with dedicated epilogue warps. Both cases use N16/M128; PDL off/on.

| PDL | Control norm LDG | Control tile backedge | Candidate norm LDG | Candidate tile backedge | Registers |
|---|---|---|---|---|---|
|off|0x2090|0x3760 →0x1720|0x1620|0x3780 →0x1730|78 →78|
|on|0x25e0|0x3cf0 →0x1c30|0x1b50|0x3d10 →0x1c60|80 →80|

Norm uses kernel parameter9 / constant offset0x5b8. The candidate load occurs before the initial metadata wait and outside the scheduled-tile backedge, while the control load lies inside that loop. This removes one dynamic norm load plus its constant-pointer load per subsequent scheduled tile. Static load-site count need not change. Registers, SMEM, TMEM and spills do not increase.

All64 source-paired exact replays pass.13/16 SASS outputs are byte-identical. The other non-NV difference is an inline MXFP8 PDL-on kernel with register renaming/scheduling at equal instruction/resource counts; no claim of complete MX binary identity is made. Full four-format fixed CAAC is retained as the measurement boundary.

## config0-fc1-pdl0 control

```sass
/*1ef0*/ FADD R28, R28, 1;
/*1f00*/ MUFU.EX2 R53, R53;
/*1f10*/ LDC.64 R38, c[0x0][0x5b8];
/*1f20*/ FMUL R9, R5, 1.4426950216293334961;
/*1f30*/ FMUL2 R4, R30.F32x2.HI_LO, R0.reuse.F32;
/*1f40*/ MUFU.EX2 R50, R50;
/*1f50*/ FADD R70, R70, 1;
/*1f60*/ FMUL R27, R27, -2;
/*1f70*/ FMUL R6, R36, -2;
/*1f80*/ MUFU.EX2 R9, R9;
/*1f90*/ FMUL R36, R17, 0.57142859697341918945;
/*1fa0*/ FADD R54, R54, 1;
/*1fb0*/ FMUL R29, R27, 1.4426950216293334961;
/*1fc0*/ MUFU.EX2 R31, R10;
/*1fd0*/ FMUL R24, R24, 0.6666666865348815918;
/*1fe0*/ FADD R53, R53, 1;
/*1ff0*/ FMUL R36, R36, -2;
/*2000*/ MUFU.RCP R70, R70;
/*2010*/ FMUL R24, R24, -2;
/*2020*/ FADD R50, R50, 1;
/*2030*/ FMUL R36, R36, 1.4426950216293334961;
/*2040*/ FMUL R13, R13, -2;
/*2050*/ FMUL R40, R24, 1.4426950216293334961;
/*2060*/ FADD R9, R9, 1;
/*2070*/ FMUL R26, R26, 0.6666666865348815918;
/*2080*/ MUFU.EX2 R29, R29;
/*2090*/ LDG.E R61, desc[UR4][R38.64];
/*20a0*/ FADD R10, R41, 1;
/*20b0*/ FMUL R13, R13, 1.4426950216293334961;
/*20c0*/ MUFU.EX2 R40, R40;
```

## config0-fc1-pdl0 candidate

```sass
/*15f0*/ ISETP.GT.U32.AND P0, PT, R2, 0xff, PT;
/*1600*/ @P0 BRA 0x37a0;
/*1610*/ LDC.64 R4, c[0x0][0x5b8];
/*1620*/ LDG.E R59, desc[UR4][R4.64];
/*1630*/ SHF.L.U32 R4, RZ, 0x1f, RZ;
/*1640*/ SYNCS.PHASECHK.TRANS64.TRYWAIT P0, [UR21+0x100], R4;
/*1650*/ @!P0 BRA 0x4f00;
```

## config0-fc1-pdl1 control

```sass
/*2440*/ FADD R28, R28, 1;
/*2450*/ MUFU.EX2 R53, R53;
/*2460*/ LDC.64 R38, c[0x0][0x5b8];
/*2470*/ FMUL R9, R5, 1.4426950216293334961;
/*2480*/ FMUL2 R4, R30.F32x2.HI_LO, R0.reuse.F32;
/*2490*/ MUFU.EX2 R50, R50;
/*24a0*/ FADD R72, R72, 1;
/*24b0*/ FMUL R27, R27, -2;
/*24c0*/ FMUL R6, R36, -2;
/*24d0*/ MUFU.EX2 R9, R9;
/*24e0*/ FMUL R36, R17, 0.57142859697341918945;
/*24f0*/ FADD R54, R54, 1;
/*2500*/ FMUL R29, R27, 1.4426950216293334961;
/*2510*/ MUFU.EX2 R31, R10;
/*2520*/ FMUL R24, R24, 0.6666666865348815918;
/*2530*/ FADD R53, R53, 1;
/*2540*/ FMUL R36, R36, -2;
/*2550*/ MUFU.RCP R72, R72;
/*2560*/ FMUL R24, R24, -2;
/*2570*/ FADD R50, R50, 1;
/*2580*/ FMUL R36, R36, 1.4426950216293334961;
/*2590*/ FMUL R13, R13, -2;
/*25a0*/ FMUL R40, R24, 1.4426950216293334961;
/*25b0*/ FADD R9, R9, 1;
/*25c0*/ FMUL R26, R26, 0.6666666865348815918;
/*25d0*/ MUFU.EX2 R29, R29;
/*25e0*/ LDG.E R61, desc[UR12][R38.64];
/*25f0*/ FADD R10, R41, 1;
/*2600*/ FMUL R13, R13, 1.4426950216293334961;
/*2610*/ MUFU.EX2 R40, R40;
```

## config0-fc1-pdl1 candidate

```sass
/*1b00*/ ISETP.GT.U32.AND P0, PT, R2, 0xff, PT;
/*1b10*/ @P0 BRA 0x3d30;
/*1b20*/ LDC.64 R4, c[0x0][0x5b8];
/*1b30*/ R2UR UR4, R58;
/*1b40*/ R2UR UR5, R59;
/*1b50*/ LDG.E R61, desc[UR4][R4.64];
/*1b60*/ SHF.L.U32 R4, RZ, 0x1f, RZ;
/*1b70*/ SYNCS.PHASECHK.TRANS64.TRYWAIT P0, [UR33+0x100], R4;
/*1b80*/ @!P0 BRA 0x54d0;
```
