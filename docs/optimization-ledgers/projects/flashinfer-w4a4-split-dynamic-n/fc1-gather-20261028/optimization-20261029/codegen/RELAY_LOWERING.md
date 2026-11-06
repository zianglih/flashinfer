# R6 K3 relay lowering

Frozen R6 K3 EP8 MXFP4x8 T4096 FC1, kernel SHA deba8b639fba89e6f76381e8c6bf8bc323ccaf850b973c836f476f8144c4cc0a. This is a source/codegen audit; the separate iKET capture supplies the timing evidence.

The relay waits for local Gather4 and cp.async-SF completion, executes an async proxy fence, then one elected lane publishes a release.cluster arrival to the MMA leader. The elected cluster arrival lowers to a MEMBAR.ALL.GPU sequence every K stage. This is a concrete instruction-efficiency target. Any change to relaxed arrival or fence removal requires a transitive visibility/order argument; it cannot be justified from static instruction counts alone.

PTX lines600–620:
```ptx
    // begin inline asm
    {
    .reg .pred       P1;
    LAB_WAIT:
    mbarrier.try_wait.parity.shared.b64 P1, [%r1118], %r1544, 10000000;
    @P1 bra.uni DONE;
    bra.uni     LAB_WAIT;
    DONE:
    }
    // end inline asm
    fence.proxy.async.shared::cta;
    elect.sync     %r1120|%p193, -1;
    not.pred     %p194, %p193;
    @%p194 bra     $L__BB0_63;
    add.s32     %r1121, %r34, 144;
    mapa.shared::cluster.u32     %r1122, %r1121, 0;
    mov.b32     %r1123, 0;
    mov.b32     %r1124, 1;
    mbarrier.arrive.release.cluster.shared::cluster.b64 _, [%r1122], %r1124;
$L__BB0_63:
    add.s32     %r1127, %r1545, 1;
```

SASS relay wait-to-publication sequence:
```text
1f20 @!PT LDS RZ, [RZ];  // SASS line 1003
1f30 @!PT LDS RZ, [RZ];  // SASS line 1005
1f40 @!PT LDS RZ, [RZ];  // SASS line 1007
1f50 @!PT LDS RZ, [RZ];  // SASS line 1009
1f60 MEMBAR.ALL.CTA;  // SASS line 1011
1f70 FENCE.VIEW.ASYNC.S;  // SASS line 1013
1f80 ELECT P1, URZ, PT;  // SASS line 1015
1f90 VIADD R3, R4, 0x1;  // SASS line 1017
1fa0 ISETP.NE.U32.AND P0, PT, R3, 0x9, PT;  // SASS line 1019
1fb0 SEL R4, RZ, 0x1, P0;  // SASS line 1021
1fc0 SEL R3, R3, RZ, P0;  // SASS line 1023
1fd0 @P1 VIADD R6, R6, 0x90;  // SASS line 1025
1fe0 LOP3.LUT R4, R2, R4, RZ, 0x3c, !PT;  // SASS line 1027
1ff0 LEA R5, R3, UR39, 0x3;  // SASS line 1029
2000 @P1 PRMT R6, RZ, 0x654, R6;  // SASS line 1031
2010 SHF.L.U32 R2, R4, 0x1f, RZ;  // SASS line 1033
2020 @P1 MEMBAR.ALL.CTA;  // SASS line 1035
2030 @P1 MEMBAR.ALL.GPU;  // SASS line 1037
2040 @P1 ERRBAR;  // SASS line 1039
2050 @P1 CGAERRBAR;  // SASS line 1041
2060 @P1 SYNCS.ARRIVE.TRANS64.RED.A1T0 RZ, [R6+URZ], RZ;  // SASS line 1043
```

All payload/SF stage writes in the gather branch use Gather4 or cp.async; no generic shared-store payload write occurs there. Invalid SF words are zero-filled through the predicated cp.async copy. The relay itself does not modify payload/SF storage. Routing/scheduler metadata is a separate pipeline.

Full artifacts: `evidence/0-ep-kimi-k3-mxfp/capture/000-fc1.ptx` and `.sass`.
