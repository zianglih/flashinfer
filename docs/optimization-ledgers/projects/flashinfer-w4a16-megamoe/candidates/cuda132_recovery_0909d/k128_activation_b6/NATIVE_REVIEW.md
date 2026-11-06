# K128 activation B6 native review

Both saved H7168/I2048 EP8 captures use640 threads, REG96, STACK0, LOCAL0 and noLDL/STL. Both retain eight2CTA MMA instructions and64 directFP4-to-BF16 instructions; only the activation depth changes relative to the firstK128 captures. Actual FC1/FC2 counts areB6/raw5/ACC2/S2, decoded6 atN64 and4 atN128.

The N128 PTX provides a distinct activation-versus-decoded ring check: FC1 andFC2 activation-TMA producer state wraps at6, selects index0 and XORs its phase at lines2407–2412 and2535–2540. The MMA consumer wraps decodedA at4 (4184–4188) and activationB at6 (4190–4194), using different state registers. Their releases reference separate barrier regions; accumulator commit uses its own240-byte-offset region. N64 producer andconsumer similarly wrap the six-stage activation ring; its decoded ring also has6 stages. Saved excerpts preserve the relevant context.

Listed instructions grow5312→5368 forN64 and5864→5912 forN128. Pipeline tail handling has more stages; these static counts are not latency measurements. The kernel bytes match75f; the later public-test parametrization does not affect this capture. The separate large-H fallback is not covered by these benchmark-shape native captures and must be checked by its actual numerical object/resource record.
