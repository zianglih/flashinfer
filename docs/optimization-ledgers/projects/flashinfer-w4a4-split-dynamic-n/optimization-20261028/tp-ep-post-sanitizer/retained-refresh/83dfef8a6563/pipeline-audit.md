# Retained pipeline dependency audit

Source: `83dfef8a656384f5cd10db847602593bb6f9b2c6`. The adjacent
`pipeline-audit-source.json` binds source SHA and exact line anchors. This is an
additional source audit, not a new timing or sanitizer result.

| Resource / boundary | Current ownership and necessary wait | Conclusion |
|---|---|---|
| Barrier initialization / TMEM allocation | One init fence; cluster publication for two CTA; allocator retrieval establishes the CTA join. | Async barrier visibility and shared allocation ownership remain necessary. Do not drop the init fence based on a later generic barrier. |
| PDL startup | Activation producer and epilogue wait for predecessor payload. Weight and scheduler roles can run ahead when routing has been published by the selected startup contract. Their exit waits preserve dependency completion. | Do not generalize payload readiness to metadata, or remove the publication/acquisition contract. Startup work is already split by dependency. |
| Weights, weight scales, activation, activation scales | Two independent TMA producer warps own their issue paths, share one operand ring/full transaction count, and independently wait for the same empty phase. Weight ownership supplies one final tail. | Shared readiness is appropriate because MMA consumes all four operands together. Splitting full barriers would add bookkeeping without permitting an earlier MMA. Producers do not wait for each other's issue before starting their own copies. |
| MMA / operand release | Wait for complete operands; copy scales and issue all channel tiles; release the stage only after the last channel tile has consumed shared B/SFB. | Earlier release can overwrite operands still read by the second channel tile. Existing rejected release experiments and final sanitizer evidence support retaining the ownership boundary. |
| Partial K / K96 | Full-stage loop and the short final stage are separate compile-time sections. Native K96/K64 instruction plans live inside the same owned operand stage and release it once. | No runtime per-instruction K predicate, extra pipeline phase, or K96-specific barrier is introduced. |
| TMEM accumulators / epilogue | Accumulator empty/full phases protect different lifetimes from the operand ring; epilogue release allows the next accumulator writer. Output scratch has its own asynchronous store lifetime. | Merging accumulator and operand phases would couple otherwise independent producer/consumer progress. Keep them separate. |
| Compact FC2 output | After the existing PDL payload wait, epilogue reads compact prefixes and the M0 owner publishes dense indices. Full slabs use bulk TMA; tails use row stores. Combine reads dense indices after its wait and validity check. | No new grid barrier, kernel, or BF16 capacity. Caller routing maps remain unchanged. Prefix/index lifetimes must not move before publication. |
| CLC / ordinary scheduling | CLC fetch completion protects the hardware response; metadata ring release/acquire protects scheduler stores until all actual consumers finish. Ordinary scheduling compiles these rings out. | Fetch and metadata have different reuse lifetimes and cannot safely share one phase. The terminal CTA join drains metadata consumers. No additional speculative request or scheduling axis is warranted by the evidence. |
| TMEM teardown | Role-specific tails and the final CTA join precede relinquish/free; two-CTA deallocation retains its cluster agreement. | No safe blanket wait/barrier deletion identified. |

Final validation separately passed 95 pytest cases, 11 cache tests and 384
sanitizer graph replays with actual compact full/tail slabs. IKET markers remain
available. The final TP NSYS profiles are stored under `nsys-tp-prefill/` and
identify remaining stage costs; aggregate wait percentages are not evidence that
a particular synchronization can be removed.
