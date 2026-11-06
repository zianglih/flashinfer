# Aligned SF word view, final bounded quantizer cleanup probe

R6 restores the retained padding/device interface; R5 is rejected after persistent initial-linear spills and negative V3 timings. It differs from aligned-clearR4 only by recasting the16-byte-aligned SF base once into a1/2/4-byte tensor, then indexing with the divisible byte offset / element width. This preserves the proven alignment before dynamic indexing and removes per-store pointer reconstruction.12added/3removedlines, no new policy/API/branch.

Run31 bounded initial/layout cases and inspect actualstore widths + originalV3K7168initial resources before any performance. If the initial spill persists, stopthisquantclearround andretire thecopy. FrozenR4/R5 source/evidence remainsuntouched. No TRTbaseline refresh unless a candidate is eventuallyretained.
