# W4A16 five-warpgroup register allocation

Candidate is an unstaged, general FC1 gather-only allocation experiment based on retained `f63e948564582a487f95900c71ef581b90c3f177`. No scheduling/tile/PDL/math changes; regular FC2 is unchanged. Canonical advanced while preparing, so source-equivalent f63 control is deliberately frozen for codegen, not conflated with latest head.

| Role | Retained | Candidate |
|---|---:|---:|
| Epilogue WG | 144 | 112 |
| Control WG | 80 | 80 |
| Dequantization WG 0 | 96 | 128 |
| Dequantization WG 1 | 96 | 128 |
| Gather WG | 64 | 32 |

Both sum to `128 * 480 = 61,440` registers, matching `640 * 96` launch registers. Candidate donors release 10,240 registers: control 2,048 and gather 8,192. Receivers acquire exactly 10,240: epilogue 2,048 and dequantization 8,192. Absolute targets are multiples of eight. Source role branches remain nonreconverging; each warpgroup sets its budget before role-local allocations/work.

This is not a spill-removal hypothesis. Retained codegen is spill-free. Common two-CTA M256/K256 transform partitions decode 128 BF16 elements/thread (64 registers), plus packed inputs/scales and pipeline state. Existing ptxas interleaves STTM stores with later decode fragments under the 96-register target; 128 may expose load/decode/store scheduling freedom. It also reduces the epilogue quota, which can negate the gain or spill: generated code is the first gate.

Prior general alternatives were rejected: gather32/dequant112 was slower on EP and TP; gather32/epilogue176 lost EP prefill. Existing MegaMoE W4 uses the same 144/80/96/96/64 retained allocation, so it provides no evidence that this redistribution should win.

Initial codegen cases are frozen existing tactics: K3 EP8 4096 tokens (N128), K3 EP8 8192 (N192), V3 TP8 8 (N16), all K256/two CTA. Collect paired control/candidate fresh cubins/PTX/SASS and runtime resource attributes. No candidate timing until checking stack/local accesses, role CFG register endpoints, static code changes and transform/epilogue scheduling. Timing, if justified, must first move the isolated patch to latest retained source and run exact cases. No sanitizer or clock changes.

Sources: `moe_w4a16_kernel.py` constructor, `_setup_transform_partitions`, `_transform_tile`, role branches; `moe_w4a16.py` gather ptxas limit; `moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py` role quotas. Prior evidence: `full-20261029/w4a16-gather-ledger.md`, `w4a16-tma-register`, `w4a16-tma-epilogue`, `w4a16-elected-issue/evidence/resources-control`.
