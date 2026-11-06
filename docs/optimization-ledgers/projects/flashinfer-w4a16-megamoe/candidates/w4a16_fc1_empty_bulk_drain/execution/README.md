# Empty FC1 bulk drain: complete, retained as cleanup

Root retained the five-line epilogue deletion under the user's preference to keep pure cleanup, **with no speedup claim**. Commit `0f361bc04664c574c91f96ecff3c259b8d4fdb14` contains one changed file/five deletions; source `3efa6e71d3ca07bdcd3fd41c6498879b346088dd64252ccd3162f6cc2a1ddc26` and epilogue `ee769bd0` match the executed bytes. Root confirmed a clean checkout and passing commit hooks, including mypy/Ruff. Root confirmed the fork push and live draft PR head0f361bc0.

The removed bulk group has no FC1 epilogue producers. BAR1, completion flags, TMEM fences/releases and the actual dispatch bulk drains remain. Both direct-return native captures passed: REG96/640 threads/two decode groups/STACK0/LOCAL0, grid `[2,1,74]`, dynamic shared200064/230784bytes. N64 has5496 padded instructions and N1286032; both remove the empty drain/control overhead. The unchanged EP2 numerical cohort passed **8 rank tests/32 objects across N64/N128 and both return modes**, retaining original oracles/tolerances, LOCAL0/S2 and epilogue flags `(2,4)`. Host135 remains historical on8d.

Original AUTO82856 completed true0 in **585.834477s**, with13 rows, default8 tactics,104 compiled/winner records,104 rankings and1,300 samples. Source3efa/native38a68 remained exact and GPUs/workers are idle. No restoration is required.

| Complete control | 8–4096 latency GM change | Lower rows | All13 latency GM change | Lower rows |
| --- | ---: | ---: | ---: | ---: |
| Primary default57e2 | +0.519590% | 3/10 | −0.751061% | 5/13 |
| Separate whole-best098c | +1.964819% | 4/10 | +1.995430% | 5/13 |

[Both full13 tables and selected tactics](../../../logs/cu132-recovery0910a-fc1-empty-bulk-drain-independent-comparison-001/README.md) remain unchanged. Tokens1/2/4 are reported but excluded from retention. The complete098c published performance table remains the whole-best reference; no row substitution, new baseline run or performance promotion follows this cleanup decision.

Proof `e607b4726152216ae87a179d2823a5a08f88286f7cba2a33601a3deef92f2cb5`; result `353b1b64fb750fc2bf6447ee954c4500417ed0f259e7c4f149c931d2ac98daf9`; comparison `cb37def2789007c651fa62ed772be0d9ed1b96d7e0280d534526d056dc6597c9`; AUTO closure `35532e29c4680bfc0806f78850c8f6b2fcac6ee6d8be09b4b7f969d59a7530a6`. [retention.json](retention.json) contains exact summaries and pins; [native admission](NATIVE_ADMISSION.md) and [numerical summary](numerical-summary001.json) preserve scope.

These are sequential historical whole-run comparisons, not paired drift-adjusted measurements. Native simplification is not an end-to-end gain. No arithmetic/validator, test, timing or GPU operation was repeated for this summary; no PR body or product source was edited.
