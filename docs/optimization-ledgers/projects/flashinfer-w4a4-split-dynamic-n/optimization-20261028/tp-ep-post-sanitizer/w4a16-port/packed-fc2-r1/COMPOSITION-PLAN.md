# Conditional tail + packed-scaling qualification

Do not compose until the independent tail exact/codegen gate passes and both retained-candidate performance decisions are available. Both isolated candidates remain frozen at the same `fd72759b` control.

- Reuse the scheduler's existing `w4a16-tail/gate.py` against a newly frozen composed source. Direct cases 10/11 (K384), 16/17 (K576), 18/19 (K640), plus aligned 6/7 or 14/15 exercise partial and complete K stages. These existing cases include ±0 alpha, cancellation, poisoned adjacent expert storage, CLC/ordinary scheduling and graph replay. Preserve their exact reference and byte assertions.
- Reuse public old64/new16 layout endpoints 27–34 and the four maintained `TestCuteDslMoeW4A16::test_weight_scale_update` cases. Do not add repository tests or duplicate the oracle.
- Retain PTX/cubin/SASS/resources from the composed launch: verify executed MMA counts match the tail plan, FC2 scaling retains the paired form, aligned FC1 streams equal control, and local/uniform spills do not appear. The packed change should not be called a dynamic multiply-count reduction: baseline is already auto-vectorized.
- If independent timings justify both candidates, run a small composed CAAC interaction screen using the same saved winners/routes: V3 EP aligned and V41F/K3/N3U TP partial-K shapes at T64 and T16384. Compare to the original control and/or retained isolated candidate as root directs. No autotune or external-baseline rerun.
- Keep all source, helper, reference, cache and output hashes bound in the new receipt. The inherited source manifest does not include the old shared `tests/test_helpers/w4a16_reference.py`; pin its exact bytes separately against the tracked commit before and after execution.

No composition edits, deployment, GPU launch, or commit were performed by this plan.
