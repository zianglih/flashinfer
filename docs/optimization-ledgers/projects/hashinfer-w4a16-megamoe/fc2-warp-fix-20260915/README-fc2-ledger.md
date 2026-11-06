# Proposed upstream ledger update

Append one sentence to the existing `epilogue.py` adaptation row:

> Select each FC2 warp's own 32-row TMEM view.

This describes the correction relative to the ledger's pinned upstream 7f source.
It records the representation change without adding runtime results, performance
claims, a new backend section, or attributing the historical O2 anomaly to this
fix. It applies to both FC2 output-return modes because the shared raw accumulator
view is sliced before either mode consumes it.

`README-fc2-ledger.patch` changes only that existing row. It is prepared against
HashInfer commit `4ead24f1513ad2cff4c88a56b4ab3078d390d7ed` and has not been applied
to the working repository or frozen validation source. Apply later as a separate
documentation change so the current run's source manifest remains accurate.
