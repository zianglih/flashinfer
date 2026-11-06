# Preparation V1 code generation

Completed 2026-10-25 12:24:39 UTC on GPU1 of C2/infra `w4a16-regular-tma-1025`. The immutable V1 preparation SHA-256 is `a514d309fe1647896eb7b9a68d6cb3da693cac7590eac853ca2ea909c818f0bb`. H7168, route tile128, top-k3/8, PDL enabled, and both alignment specializations were compiled separately. No kernels were launched or timed. GPU0 benchmarking waited on the completion marker.

| Top-k | Copy width | Registers/thread | Stack/spill/local bytes | Static shared memory | Actual active CTAs/SM | SASS payload load/store sites |
|---:|---:|---:|---:|---:|---:|---:|
|3|256 bits|28|0 / 0 / 0|0|16|4 / 4|
|3|128 bits|32|0 / 0 / 0|0|16|7 / 7|
|8|256 bits|28|0 / 0 / 0|0|16|4 / 4|
|8|128 bits|32|0 / 0 / 0|0|16|7 / 7|

Occupancy comes from `cuOccupancyMaxActiveBlocksPerMultiprocessor` on the actual compiler-produced cubins with 128 threads and zero dynamic shared memory. The hardware thread-capacity grid bound therefore matches compiled residency for these four specializations. This does not establish a performance benefit.

The wide path emits PTX `ld.global.v4.b64`/`st.global.v4.b64` and SASS `LDG.E.ENL2.256`/`STG.E.ENL2.256`. The fallback emits SASS `LDG.E.128`/`STG.E.128`. The table counts static instruction sites, not full-row dynamic requests: the final 256-bit pass runs only for 64 of 128 threads. Both paths copy exactly the same 14,336-byte row.

Top-k3 division contains `mul.hi.s32 ..., 1431655766`; top-k8 contains a right shift by3. Every PTX entry has exactly five global-pointer parameters. Top-k and dimensions are absent from the runtime kernel ABI. Signed floor-division correction instructions are still present; these captures establish constant specialization, not minimum possible index arithmetic.

PTX target is `sm_103a`, PTX version9.3. Separate assembly used ptxas13.3.73; disassembly used cuobjdump13.2.78. Both assembler logs and driver queries report no spills or local storage.

Raw archive and original reports: `codegen-prep-v1-capture/raw.tar.gz` and its extracted files. `codegen-prep-v1-capture/analysis.json` records artifact hashes, complete entry parameters, vector instruction lines and resources. The original report parser expected a newline before the entry's opening parenthesis, so its `ptx_entry_parameters` arrays are empty. The derived analysis corrects parsing of the unchanged saved PTX; no recompilation was needed, and the original reports remain preserved.
