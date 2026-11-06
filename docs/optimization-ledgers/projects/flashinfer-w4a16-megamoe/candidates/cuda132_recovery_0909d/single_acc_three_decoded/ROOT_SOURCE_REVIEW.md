# ACC1 / decoded3 source review

Reviewed the actual two-file candidate against published shared-layout commit
056ce0d090d425ee09171e47f6faea61c76c9551. The final nested tuple annotation is
static typing only. The allocation rule is evaluated during construction;
there is no added device predicate or public tactic field.

At N128 the physical accumulator extent, MMA producer state, epilogue consumer
state, barrier storage and cached epilogue TMEM layout all become one. Both FC
mixed-input helpers use the same selected count. The decoded operand starts at
column128 and spans three128-column slots. N64 retains two64-column accumulator
slots followed by three128-column decoded slots. Both consume exactly512 cols.

The private epilogue selects the accumulator by the consumer index when overlap
is disabled. It does not use phase as a physical stage index in this mode.
A one-slot pipeline therefore requires phase reversal on every advance, while
its physical index stays zero. The native capture must confirm that behavior.

Both FC1 and FC2 release after their final TMEM scratch reads and load fence,
before remaining register operations/stores. Partial and empty final subtiles
use the existing alternate release; no new release site is introduced. This
preserves the intended last-epilogue-work overlap even with one physical slot.
No decoded-weight GMEM/SMEM path or shared NVFP4 ABI change is introduced.

Source review passes. Actual native code, ring-wrap numerics and the complete
AUTO sweep remain separate evidence; this review is not a performance result.
