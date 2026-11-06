# Fixed-N production generated code

Run `swap-tmem-codegen-t4096-001` used EP8, H7168/I2048, E256/top8,
global4096 tokens, M256/N128/K256, two-CTA instructions, and ptxas cap128.
The eight per-rank PTX/cubin/SASS folders are retained under
`../../profiles/swap-tmem-codegen-t4096-001`; `summary.json`, each
`resources.txt`, and `tmem-instructions.txt` summarize the raw evidence.
`logs/swap-tmem-codegen-t4096-001.provenance.log` records source hashes.

All ranks report the same resources and instruction counts:

| Registers | Stack bytes | Static shared bytes | Local bytes | SASS instructions |
|---:|---:|---:|---:|---:|
| 128 | 112 | 1024 | 0 | 5808 |

The shared figure above is static shared storage; it excludes the dynamically
allocated shared workspace. It is not the total shared-memory footprint.

Direct TMEM dataflow is present in the generated code. In rank0 PTX, lines
3699–3901 and 5238–5510 contain 32 transform store sites with
`tcgen05.st.sync.aligned.32x32b.x8.b32`. The MMA at line5805 has the form
`tcgen05.mma.cta_group::2.kind::f16 [acc_r32], [A_r32], B_desc_r64, ...`:
the bracketed 32-bit A operand is TMEM, while B is the BF16 activation SMEM
descriptor. SASS shows `STTM.x8 tmem[...]` from line2324 and
`UTCHMMA.2CTA ... gdesc[...], tmem[...]` from line4127. Decoded BF16 weights
therefore feed MMA directly from TMEM. There is no decoded weight SMEM store
or global BF16 weight buffer in this path.

The nonzero stack does **not** establish transform register spills. PTX line53
explicitly declares a 96-byte local depot. All observed SASS local accesses
(`STL.64`8, `STL`8, `LDL.128`1, `LDL.64`4) map to the existing FC2 router's
eight 64-bit destination pointers and eight 32-bit validity entries. Their
source is vendor `epilogue_refactor.py:2360–2390`, read at2444–2445. No local
load/store appears in the weight transform. Increasing transform registers
is not justified by these accesses.

The instrumented run completed, but its one-iteration CUDA-event number is
excluded from performance evidence. The paired CUPTI runs explicitly unset
all CuTe dump/lineinfo/cache instrumentation variables.
