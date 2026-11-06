# Phase-interleaved paired TMEM transpose

Candidate base b13963b0cc8409aeb92048b9ec7cf3be18f0a57c, kernel f5260ba779b7b42cdc87a2bf1ddd287ae07c22d674e69bcbee618d0e6f03d80b. Source remains unstaged in `flashinfer-paired-transpose-review`.

The same private helper handles one or two 16x32 fragments at compile time. Paired calls issue both R1 stores, both R2 loads, both R2 stores, both R3 loads/stores and both R4 loads. This follows Rubin `TmemTranspose32x32Inplace` in `flashinfer/moe_ep/kernel_src/sm107/next_cutedsl_megamoe/src/sources/kernel_src/rubin/inference/mega/block_scaled_swap_ab_fc12_epilogue.py:710`. The existing one-fragment path retains the identical copy-atom/rectangle sequence. No shape, dtype or model dispatch is added.

Both initial accumulator fragments must be loaded before scratch reuse. Source rectangles are upper/lower halves of32x32; final destinations are left/right halves. Both R2 source loads precede either R2 destination store because the destinations cross-alias the sources. Later destinations are disjoint. The existing final TMEM-read fence and accumulator release follow both final loads unchanged. `prove_order.py` executes the actual old/new helper AST with region tracing and verifies each read's last writer, all per-fragment atom/address sequences, permutations and caller fences. It does not prove the compiler's async completion handling; actual compiled code and exact GPU coverage remain required.

Affected callers: gated per-token FC1, nongated FC1 (including ReLU2 quantized output), and existing nongated fallback. Ordinary gated quantized FC1 and packed16-bit FC2 use one fragment and should remain unchanged in generated code. BF16 per-token FC1 still passes through the existing standalone quantizer between FC1/FC2.

Qualification: scoped precommit and diff-check passed; source-bound paired39 existing exact cases and captured native resources/SASS are next. Require no new local-memory traffic or resource growth relative to matched control (including known M512/N128/K8 MX4 spill stress). Inspect FC2 and one-fragment paths for unintended changes. No sanitizer or new repository tests.

If qualified, a predeclared24-cell same-node CAAC screen uses all4models/topologies per-token at T8 and prefill (16cells); N3U EP/TP W4A4/MXFP4x8/MXFP8 at prefill (6cells); two unaffected gated controls V3EP W4A4 and K3TP MXFP4x8 prefill. Use existing frozen winners/routes,100 strict CUPTI samples perphase,10warmups,coldL2graphs,noeventfallback,noautotunefallback. Retain all negative rows and NVML variation. Token1/2excluded. These screening aggregates are not full-matrix speedup claims.


## R1: explicit TMEM phase completion

R0 was compile-only:8cases/16kernels perarm, resourcesunchanged, all8FC2 and6single-fragmentFC1 PTX identical;2pairedFC1 reorderonly. No ownedkernellaunch. Source f5260ba7 and evidence remainimmutable.

PTX13.2.2 §9.7.16.6.4.2 and.4.5 require explicitcompletion for non-pipelined ST→LD and LD→overwriting-ST; register dependencies alone are not a general TMEM memory-order guarantee. Both old andR0 PTX omitintermediatewaits. R1 kernel232e3a6a5a0fd9e748ae1628a63346c1f257f23863949473cd9214058b109aa9 adds oneinitialloadwait, threestore-phasewaits, twointermediateloadwaits, and onefinalloadwait. Thesearewarp-localtcgen05waits sharedbyallfragments, no CTAbarrier. Existingcallerreleasefencesremainforscopeisolation.

ActualhelperASTpending-regionmodel now verifies no dependentreadbeforestorecompletion or overwritebeforeloadcompletion for both1/2fragments; sourcepermutations/callers unchanged. precommitanddiffcheckpassed. R1changesone-fragmentpaths too, so no FC2/PTXidentityclaim forR1. Matchedcodegen/resources first, thenexistingexact, no perf untilqualified. A speedupclaim must notattributecombinedwait+reordering solelytointerleaving.

Officialsource: https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#tcgen05-memory-consistency-model
