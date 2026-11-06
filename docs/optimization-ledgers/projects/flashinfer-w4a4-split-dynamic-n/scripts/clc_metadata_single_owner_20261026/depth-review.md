# Independent review of accumulator-derived metadata depth

Source: b85eff41a6c30687a93e95455a3f68ff77d14ac5 + patch 5920de4f2e52f96c6a04d5f80fda2c89b891a693919b792de453fdc686fa352f.

No blocking correctness or capacity issue found. 1280 pure-host metadata-accounting assertions passed.

- Automatic K candidate accounting resolves None with that candidate accumulator count, and actual constructor resolves after selected storage.
- Explicit positive depth remains unchanged.
- SMEM reserves 2 int64 barriers plus4 int32 metadata words per slot (32bytes), and final actual size is checked.
- All producer/consumer states and layout use the same resolved depth.
- Installed SDK PipelineState advances index modulo arbitrary stage count and flips phase at wrap; producer_tail waits all stages.
- Generic shared publication remains release/acquire through the retained elected owner. CLC response ring stays independent at one stage.
- Cache tuple contains raw num_tile_info_stages plus all geometry/resource inputs; None and explicit depth cannot alias.
- Terminal publication is ordered after issued work; all consumers release before state advance, then producer_tail drains every metadata slot.

Caveats:

- acc_stages=1 can still have partial TMEM-window overlap; this formula intentionally leaves those geometries unchanged.
- Depth2 previously regressed decode on an older pipeline; retention must use current paired decode and prefill evidence.

Installed SDK source evidence: PipelineState.py, make_pipeline_state.py, PipelineAsync.py. GPU correctness and timing remain with the candidate owner.
