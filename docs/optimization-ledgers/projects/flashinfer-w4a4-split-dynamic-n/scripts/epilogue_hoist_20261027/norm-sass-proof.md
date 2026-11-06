# Current-base scale hoist: repeated norm load

Config0 FC1, inline NVFP4, no PDL. Both arms use b85 plus identical all-CLC policy. The norm pointer is kernel parameter9 / constant offset0x5b8. Control loads norm at SASS0x2840 within the tile loop; candidate loads it at0x0770 before initial metadata wait0x0780. The candidate tile backedge goes to0x08f0, after the norm load, so the hoist removes one dynamic norm LDG and its pointer load for each additional tile. It does not remove a static load site. Register count increases72→75 for this combined norm+alpha candidate; all kernels remain spill-free. Full gate passes64 exact replays.

## control

```sass
/*2780*/ ISETP.GE.OR P0, PT, R67, R62, P0 ;
/*2790*/ LDTM.16dp128bit.x4 R20, tmem[UR23+0x100000] ;
/*27a0*/ @P0 BRA 0x2cf0 ;
/*27b0*/ LDC.64 R6, c[0x0][0x5b8] ;
/*27c0*/ FMNMX3 R5, |R28|, RZ, |R20|, !PT ;
/*27d0*/ IMAD.IADD R13, R67, 0x1, R61 ;
/*27e0*/ SHF.R.S32.HI R17, RZ, 0x1f, R36 ;
/*27f0*/ IMAD.MOV.U32 R8, RZ, RZ, R33 ;
/*2800*/ LDCU.64 UR10, c[0x0][0x5a0] ;
/*2810*/ IMAD.MOV.U32 R10, RZ, RZ, R35 ;
/*2820*/ IMAD.MOV.U32 R9, RZ, RZ, R25 ;
/*2830*/ LDCU.64 UR8, c[0x0][0x590] ;
/*2840*/ LDG.E R6, desc[UR4][R6.64] ;
/*2850*/ FMNMX3 R5, R5, |R30|, |R22|, !PT ;
/*2860*/ IMAD.SHL.U32 R15, R13, 0x10, RZ ;
/*2870*/ SHF.R.U32.HI R16, RZ, 0x7, R13 ;
/*2880*/ IMAD.MOV.U32 R11, RZ, RZ, R27 ;
/*2890*/ FMNMX3 R5, R5, |R32|, |R24|, !PT ;
/*28a0*/ LOP3.LUT R15, R15, 0x1f0, RZ, 0xc0, !PT ;
```

Backward branches:
```sass
/*09e0*/ @!P0 BRA 0x9b0 ;
/*2dc0*/ @P0 BRA 0x8c0 ;
/*40e0*/ BRA 0xa30 ;
/*4140*/ BRA 0xdb0 ;
```

## candidate

```sass
/*0720*/ UIADD3 UR7, UPT, UPT, UR17, 0x4300, URZ ;
/*0730*/ UIADD3 UR6, UPT, UPT, UR17, 0x300, URZ ;
/*0740*/ @P0 BRA 0x2e80 ;
/*0750*/ LDC.64 R70, c[0x0][0x5b8] ;
/*0760*/ SHF.L.U32 R3, RZ, 0x1f, RZ ;
/*0770*/ LDG.E R70, desc[UR4][R70.64] ;
/*0780*/ SYNCS.PHASECHK.TRANS64.TRYWAIT P0, [UR17+0x30], R3 ;
/*0790*/ @!P0 BRA 0x4010 ;
/*07a0*/ LDS.128 R60, [UR17+0x40] ;
/*07b0*/ IMAD.SHL.U32 R69, R64, 0x4, RZ ;
/*07c0*/ SYNCS.ARRIVE.TRANS64.A1T0 RZ, [UR17+0x38], RZ ;
/*07d0*/ IMAD.MOV.U32 R68, RZ, RZ, 0x1 ;
/*07e0*/ LOP3.LUT R69, R69, 0x60, RZ, 0xc0, !PT ;
/*07f0*/ LOP3.LUT R69, R69, 0x7, R64, 0xf8, !PT ;
/*0800*/ IMAD R69, R66, 0x8, R69 ;
/*0810*/ ISETP.GE.AND P0, PT, R60, RZ, PT ;
/*0820*/ @!P0 BRA 0x2db0 ;
/*0830*/ IMAD.SHL.U32 R3, R69, 0x10, RZ ;
/*0840*/ R2UR UR23, R66 ;
```

Backward branches:
```sass
/*0a50*/ @!P0 BRA 0xa20 ;
/*2da0*/ @P0 BRA 0x8f0 ;
/*40c0*/ BRA 0xaa0 ;
/*4120*/ BRA 0xe20 ;
```
