# Independent phase-boundary audit

Reviewed clean commit `54f5c682bbaa52a23a46b6bb76e3cfdce347ec97`. **Keep the current shared ownership.** No concrete boundary bug, import cycle, duplicated mainloop, or uniquely owned code requires another move. Source, original comments and public interfaces remain unchanged; this audit ran no tests or GPU work.

| Component | Current responsibility |
|---|---|
| Blackwell gather/act module, lines 28–78 | FC1 capability adapter: retains the logical activation/weight `can_implement` interface and validates FC1 output/layout constraints. It intentionally has no independent device mainloop. |
| Blackwell grouped/finalize module, lines 94–361 | Shared low-level MMA, SF addressing, TMEM load/transpose, and output operations. |
| Same module, lines 364–1278 | Common epilogue: FC1 activation/quantization and FC2 scaling/scatter share TMEM movement, vector conversion/store and accumulator-release machinery. |
| Same module, lines 1281–3201 and 3204–3253 | One common storage planner, prepared-input TMA mainloop, CLC/static scheduling, PDL and epilogue orchestration; then the FC2 capability adapter. |
| Host gather/act wrapper, lines 893 and 948–993 | Checks the FC1 adapter, normalizes activation/output contracts, then calls the common launcher with input preparation and activation fusion. |
| Host grouped/finalize wrapper, lines 85–309 and 941–987 | Owns the common compile/launch cache; FC2 calls it with prepared input and scatter output. |

The dependency direction is acyclic: FC1 device adapter → shared device module; FC1 host wrapper → common host launcher → shared device module. The common device module does not import the FC1 adapter. Both phases instantiate `Sm100BlockScaledGroupedGemmKernel` directly through `_run_blockscaled_gemm`; the two named phase classes preserve capability-check interfaces, not separate pipeline implementations. `fused_moe.py` dispatches through the two host wrappers, and the tuner uses the common kernel for tactic admission. Existing capability tests import the phase adapters. The JSON inventory records exact import sites and source hashes.

Hopper and Rubin have a different reason for their physical split:

- Hopper FC1 directly gathers unpermuted activation rows with a cp.async producer pipeline and loads weights with TMA; FC2 uses ordinary TMA for both inputs plus a routing-metadata pipeline and scatter/reduction epilogue. Their distinct kernel classes therefore own different dataflow and synchronization designs. See Hopper gather/act lines 20–49 and finalize lines 14–32.
- Rubin FC1 owns A/SFA gather producers, activation and quantized-output publication; FC2 owns an ordinary TMA operand pipeline and scatter/finalize epilogue. Both files define their own complete kernel class. See Rubin gather/SwiGLU lines 197–231 and finalize lines 157–185, 971–1004. They are not two adapters around one shared mainloop.

Blackwell now prepares routed input before FC1, so regular TMA, the scheduler, storage calculations and MMA pipeline genuinely serve both phases. Copying the Hopper/Rubin split would either duplicate that shared implementation or add an abstraction to reconnect it. Moving FC1 epilogue methods alone into the existing FC1 adapter module would also introduce a reverse dependency unless its inheritance/import relationship changed. The current epilogue already shares token-group handling between activation and finalize modes, so a clean separation is more than a location change.

The finalize filename is historically phase-specific, but its module/class documentation already states the shared FC1/FC2 role; the FC1 module explicitly says it is a capability adapter. A rename, extra common module, or new class hierarchy would add review churn without resolving a concrete problem found here. Retain the design and comments as they are.
