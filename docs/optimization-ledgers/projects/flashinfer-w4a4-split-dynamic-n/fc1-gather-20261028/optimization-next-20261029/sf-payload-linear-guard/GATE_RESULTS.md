# Untyped linear/unsigned mapping: compile stopped

No owned kernel compiled or launched. The first exact case stopped at a CuTe DSL type-merge error: setup `row` was UInt32 while its K-loop assignment was Int32. No numerical or performance result exists. The typed follow-up explicitly converts the computed SF row to Int32 while retaining unsigned payload ownership/bank indices; it runs the same gate in a separate immutable source folder.

All failed source/configuration and compiler diagnostics are archived. No tactic, quota or policy workaround was added.
