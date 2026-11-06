# TMEM startup rendezvous: existing rejected mechanism

Read-only follow-up at retained `2b8eb9d8`. No source/GPU experiment.

Narrowing TMEM publication to its users would let weight/gather producers start earlier, but this exact mechanism was already qualified and rejected for both backends. It is distinct from merely moving the pointer load, which was also rejected.

- [Swap startup design](../../flashinfer-w4a4-split-dynamic-n/fc1-gather-20261028/optimization-next-20261029/swap-tmem-startup/DESIGN.md) moved allocation to epilogue warp4 and reduced publication to160 MMA/epilogue threads, preserving two-CTA cluster publication and adding the necessary one-CTA initialization join. [Fourteen-cell result](../../flashinfer-w4a4-split-dynamic-n/fc1-gather-20261028/optimization-next-20261029/swap-tmem-startup-screen/RESULTS.md): geometric−0.022%, prefill−0.130%, including N3U EP4K−1.132% with tight repeats. Extra startup ownership/synchronization was not justified.
- [W4 result](../../flashinfer-w4a4-split-dynamic-n/fc1-gather-20261028/optimization-next-20261029/w4a16-tmem-wait/RESULTS.md) narrowed640/512 participants to416 MMA/epilogue/dequant threads without changing the full pipeline-init wait.33 exact cases passed; codegen added two static barrier sites. Original and fresh K3 comparisons remained negative, including repeat8K−8.211%, with explicit clock/power variability. No general gain justified retention.
- [Pointer-only codegen](../../flashinfer-w4a4-split-dynamic-n/fc1-gather-20261028/optimization-next-20261029/tmem-pointer-scope-b52/CODEGEN.md) kept every barrier/owner unchanged; that separate proposal also has a rejected timing result in the closed-lead ledger.

The current all-role startup rendezvous also publishes initialized barriers. Removing it is not merely deleting an empty TMEM wait. No new measured startup signal distinguishes another implementation attempt from these closed designs, so no prototype is proposed.
