# Shared MegaMoE raw-readiness qualification

Passed four existing zero-tolerance calls: retained2b8 versus candidate0871, H/I256/256 and384/640, on recovery B300 GPU6. Full13245-file source and release-cache pre/post checks passed; GPU6 is released and idle. The original preflight-only missing-path failure remains separately preserved.

| H/I | Changed raw queries | Non-NOP C/A | Registers C/A | Local/stack |
|---|---:|---:|---:|---|
|256/256|2|3915/3915|96/96|0/0|
|384/640|4|4015/4015|96/96|0/0|

The captured candidate PTX becomes byte-identical to control when only `mbarrier.test_wait.parity.acquire.cta.shared::cta.b64` is changed back to TRY. All43 blocking fallback TRYs and decoded-slot TRYs are unchanged. Each changed pointer is `raw_shared_base + 8*raw_index` with the original parity; decoded empty slots remain at base+104 for five raw and three decoded stages.

Native opcode counts change only from `SYNCS.PHASECHK.TRANS64.TRYWAIT` to nonblocking `SYNCS.PHASECHK.TRANS64`. The aligned image changes only the two raw instructions/encoding fields; the multi-stage image also has local scheduling/register-assignment changes. No instruction-count reduction or performance claim follows from this gate. Actual launch/resource maximum remains640threads.

`qualification-summary.json` binds raw manifests, receipts, exact captures, complete-opcode replay and barrier proof. The capture wrapper forwards original compiler arguments/options unchanged. This is single-rank `MEGA_NO_DIST=1` qualification; fresh full-node GLM5 CAAC remains held.
