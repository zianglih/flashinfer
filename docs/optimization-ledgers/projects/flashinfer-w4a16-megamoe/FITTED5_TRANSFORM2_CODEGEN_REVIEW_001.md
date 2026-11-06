# Fitted two-warpgroup codegen audit

All eight ranks pass the static resource review. The complete 5,672-instruction SASS sequence is identical, after removing source annotations and PC labels, to the corrected constant-raw5 two-warpgroup capture002. The preferred-five fitter and subsequent comment cleanup introduce no device-instruction change for this specialization.

- Capture: `profiles/tmem-fitted5-transform2-codegen-001`, H7168/I2048/E256/top-k8, EP8, T4096, dynamic N and flag4/epi return profile. This is instrumented codegen evidence; its single event timing is excluded from performance claims.
- Exact kernel SHA256: `58e4af6b935612ed1a68c27fbf355819a02d5a3e622e3fcf5e1dcff0f91c83f7`. All seven repository source hashes recorded by the codegen launcher were checked against frozen sources; inherited source files used for attribution have separately checked snapshot hashes and are marked when absent from launcher provenance.
- All ranks: REG96, 640 threads, STACK112, resource LOCAL0, static SHARED1024. Dynamic shared memory is separate from this resource field.
- Launch CTA register pool: 640×96=61,440. Five 128-thread roles request 176/80/64/80/80, totaling61,440. The two transform groups both decrease to80 before processing. The control release is one whole-warpgroup site. SASS sites are control80 at0x0f70, transform80 at0x5d10, epilogue176 at0x8fa0 and dispatch64 at0xcbf0.
- Local storage remains a 96-byte PTX depot, 40 PTX local operations and21 SASS local operations per rank. Nineteen source annotations directly identify inherited FC2 router arrays; two adjacent anchors remain unresolved. There are no transform-attributed local accesses and no new footprint relative to fitted one-group or corrected constant-raw5 two-group.
- Fitted one-group emits6,048 static instructions with REG128/512 threads; the two-group version emits5,672. The source-attributed transform block contains612 static instructions instead of983, including128 rather than256 FP4 unpack instructions. Both groups decode disjoint halves of each K tile, so this is per-thread code size, not a reduction in total decoded weight work or a throughput claim.

The earlier failed two-group capture001 is preserved separately: it requested65,536 registers from a61,440-register CTA pool and stalled on the epilogue allocation. This corrected capture uses balanced targets and completed production warmup on all eight ranks. Full13 CUPTI results and PC samples are separate evidence for performance and contention.

Reproduce the CPU extraction:

```bash
python3 compare_public_codegen.py profiles/codegen-comparison/fitted5-transform2.config.json --output profiles/codegen-comparison/fitted5-transform2.json
```

Full source-correlated data: `profiles/codegen-comparison/fitted5-transform2.json` and `.md`. Per-rank normalized-instruction hashes and checked register arithmetic: `profiles/codegen-comparison/fitted5-transform2.audit.json`. Captured compiler is the CuTe DSL4.7.1 bundled CUDA13.3.27 compiler; toolkit nvcc13.2.78 is a separate version.
