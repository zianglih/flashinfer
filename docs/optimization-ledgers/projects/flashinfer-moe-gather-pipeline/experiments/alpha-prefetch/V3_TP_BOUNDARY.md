# V3 TP8 per-token T16384: explanation boundary

The frozen primary row loses **2.9957%** with C/A repeat spreads **0.0115% / 0.0155%**. The exposed FC1 interval decreases **1.632 µs**, while FC2-after-FC1 increases **44.801 µs** (FC2 duration +44.873 µs). Input quantization changes only +0.008 µs. Thus the recorded loss primarily lies in FC2’s exposed interval, not the FC1 gather duration.

The actual loaded winning configurations are unchanged across all four phases: FC1 M256/N256, two CTAs; FC2 M128/N256, one CTA; K steps4/4, K96, CLC and PDL on. FC1 stays168 registers and195,584 bytes dynamic shared memory; FC2 stays138 registers and199,680 bytes dynamic shared memory. Both have one active CTA/SM and zero local memory. This row does **not** support attributing the loss to register-count or occupancy growth.

The source moves the existing expert-alpha load before the accumulator wait in both GEMMs and reuses the scalar. The saved representative native qualification proves that motion for four pilot GEMMs, but it does not include a PTX/SASS pair for this exact winning FC2 CLC/C1/N256 specialization. The benchmark guard captures exact returned-library resources and configuration, not SASS. Therefore the existing artifacts do not establish which instruction scheduling or wait interaction caused this tight loss. No additional timing, profiling or codegen capture is needed for the rejection decision.

`v3-tp-per-token-16k-boundary.json` binds the raw phase/resource receipts, complete row and component deltas. The primary data remain untouched.
