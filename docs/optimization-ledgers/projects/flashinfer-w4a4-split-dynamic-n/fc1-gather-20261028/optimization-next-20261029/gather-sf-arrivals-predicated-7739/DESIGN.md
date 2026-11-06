# Predicated physical SF-owner completion

Base is retained77391. R0 (b139 gate a0328bf1 and local77391 composition abec6f9b) remains frozen in the sibling artifact directory. R1 changes only the spelling of the existing static physical SF-owner condition: a private `_arrive_gather_sf` emits one predicated PTX `cp.async.mbarrier.arrive.noinc.shared.b64`, replacing the structured CuTe `if`. The initialized count remains1+min(route_tile,128). No operand stages, ownership, transaction bytes, copy issue predicates, relay, PDL, tactics or public APIs change.

The actual-module AST proof in `predicate-equivalence.json` restores R1 exactly to the composed R0 by replacing only that helper/call. The earlier exhaustive source proof establishes that excluded threads can issue no SF copy. Selected threads always arrive after their own copies, including when every copy is predicated off on an empty/partial tile.

Official semantics: [PTX13.2.2 cp.async.mbarrier.arrive](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#parallel-synchronization-and-communication-instructions-cp-async-mbarrier-arrive). The noinc form requires initialization to account for the participating arrival count. Predication preserves this count and each participating thread's copy-completion ordering.

First stage is10 compile-only cases/20 owned-kernel captures per arm. It covers fourformats at N16/twoCTA and N256/oneCTA, plus N32/SF16/oneCTA and N64/SF32/twoCTA. No owned MoE kernel is launched; other preparation/quantization helpers may run. Same current77391 control, captured executable resources and matched guard. Compile feasibility must show no new spill/resource regression and improved branch cost before exact qualification. A41-case exact driver is prepared but not launched automatically.

No timing, sanitizer, retention or public-report claim is made by this design note.
