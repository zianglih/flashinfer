# Retained7dc versus routing-preparation772 on the secondary

- Fresh A1(retained7dc) then B1(routing-preparation772) serial pair on hashinfer-fused-qual-0918,c2/infra,hu-pdx-7,boot30b16995-7b03-4179-8699-1f7be11b670e. Independent review before launch; bounded772 qualification is complete.
- Six runtime helpers remain byte-identical to the proven main-baseline-refresh-replacement pair. Driver changes only baseline pins, setup identity, prose and port29973. Both frozen104-file sources are staged separately and verified before/after.
- EP8,H7168/I2048/E256/K8,precomputed routing,1–8192 powers of2,AUTO4,O3/maxregs96,deterministic combine. Both arms measure the fully fused public forward.
- Three warmups,100 cold-L2 CUDA-graph CUPTI rank-MAX samples per row. Keep all samples; report14median/MAD rows,winners,7dc/772 ratios and8–8192 geometric mean. Verify identical fixtures/weights/routes and112finite BF16 bit-exact outputs.
- Initialization,compilation,AUTO,routing selection,graph capture and L2 flush are excluded. Distinct empty per-arm caches; unchanged process timeout and owned-group cleanup; fresh idle/environment check for each arm.
- Single serial pair does not cancel temporal drift. Candidate adds transport orchestration and must demonstrate material benefit. No production source edits,pushes,promotion,sanitizer rerun or primaryhu9 access.
