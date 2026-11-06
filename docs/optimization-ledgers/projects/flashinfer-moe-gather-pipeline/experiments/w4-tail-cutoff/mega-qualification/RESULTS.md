# W4 cutoff: shared MegaMoE no-op qualification

Passed four existing single-rank exact calls, two source-paired native specializations. Aligned H256/I256 and logical partial H384/I640 both produce byte-identical PTX, cubin and decoded SASS in current retained2b8 and cutoff candidatecbef9186. Both retain96 registers,640 threads maximum, zero stack/local, identical compiler options, and3915/4015 non-NOP instructions respectively.

MegaMoE passes its full padded MMA K extent to the shared transform, so the new per-group cutoff is compile-time inactive. The numerical calls use the existing MEGA_NO_DIST helper unchanged. Full source inventories and the four-module persistent release cache passed pre/post checks. Recovery GPU3 was verified idle and released after completion.

`qualification-summary.json` binds source/native/archive hashes; `native-summary.json` contains complete opcode and resource comparison; `evidence/` preserves raw receipts, logs, PTX/cubins/SASS and cache checks. No performance, multi-rank synchronization, sanitizer or universal all-specialization claim is made. These unchanged executables do not require another distributed GLM5 timing campaign.
