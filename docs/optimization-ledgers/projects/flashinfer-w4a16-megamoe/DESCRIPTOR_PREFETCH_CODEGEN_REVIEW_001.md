# Descriptor-prefetch generated-code review

The candidate emits six startup descriptor prefetches on every rank. It does not change the FP4 decode instruction sequence, transform/MMA opcode mix, register targets or local-memory footprint. Adjacent CUPTI timing does not establish a repeatable gain; this static audit alone is not a reason to retain the candidate.

## Scope and source evidence

Compare saved T4096 captures `tmem-fitted5-transform2-codegen-001` and `tmem-descriptor-prefetch-codegen-001`, eight ranks each. Both use H7168/I2048/E256/top-k8, M256/N128/K256, five raw stages, two transform stages and two transform groups. Explicit knobs are group_hint512, atomic_counter scheduling, flag_batch4, epi_flag_batch(2,4), token_back_mode=epi_warps. Each transform group decodes a disjoint half of the same K tile.

The baseline kernel SHA256 `58e4af6b935612ed1a68c27fbf355819a02d5a3e622e3fcf5e1dcff0f91c83f7` matches commit `fe4f8132439df1b812f77279e7d033a5128f1ed4`. Candidate SHA256 `1b827889d20de5c2d770d1f9b98ed0de79d78abc2d6b71cf043680ed6b2eeedc` matches the frozen `candidates/w4a16_cache_hints/measured-prefetch-kernel.py`. Its only source change is a warp-0 startup block calling `cpasync.prefetch_descriptor` for the six invariant FC1/FC2 weight, scale and activation descriptors. No weight payload is prefetched into L2 by this change.

The audit validates all 28 source snapshots against the frozen control/candidate, and the saved PTX/SASS hashes for all 16 rank captures. JSON distinguishes source hashes recorded during capture from unchanged dependency files reconstructed at the verified base commit. The codegen provenance records seven repository files plus the rank capture script; this is distinct from the 16-file provenance in the timing runs.

Both captures used the NVIDIA PyTorch `nvcr.io/nvidia/pytorch:26.05-py3` environment on B300: toolkit CUDA13.2.78, CuTe DSL4.7.1 with bundled compiler CUDA13.3.27. Codegen capture timing is instrumented and excluded from performance comparisons.

## Generated operations and resources

Every rank has the same results:

| Field | Control | Descriptor prefetch |
| --- | --- | --- |
| CTA threads | 640 | 640 |
| Cubin REG/thread | 96 | 96 |
| Cubin STACK bytes | 112 | 112 |
| Cubin LOCAL bytes | 0 | 0 |
| Cubin static SHARED bytes | 1024 | 1024 |
| Explicit PTX local depot | 96 bytes | 96 bytes |
| Static PTX local operations | 40 | 40 |
| Static SASS local operations | 21 | 21 |
| Static total SASS instructions | 5672 | 5696 |
| `prefetch.tensormap` / `UTMACCTL.PF` | 0 / 0 | 6 / 6 |
| Source-attributed transform instructions | 612 | 612 |
| Source-attributed MMA instructions | 127 | 127 |

The candidate's six `UTMACCTL.PF` PCs are 0x0260, 0x0280, 0x02a0, 0x02b0, 0x02c0 and 0x02d0. Their source lines identify wa1, sa1, ba1, wa2, sa2 and ba2, respectively. The startup sequence also calculates descriptor addresses; the increase is 24 total static instructions, not six total instructions.

All 128 FP4 `F2FP.BF16.E2M1.UNPACK_B` instruction texts match after removing PC offsets. The full source-attributed transform and MMA opcode mixes also match. Compiler layout/shared-helper and token-communication counts move slightly, so this audit does not claim the entire steady-state binary is byte-identical. Static source counts are not executed instruction counts or proof of latency.

The same four register-control sites request control80, transform80, epilogue176 and dispatch64. Both transform groups share the transform site. The role allocation remains 128×(80+80+80+176+64)=61440 registers, equal to 640×96 at launch. There is no added register-pool demand.

Of the 21 SASS local operations, 19 map directly to the existing FC2 router's pointer/validity arrays. The same two operations retain generic/unresolved source anchors in both captures. There are no source-attributed local operations in the transform body. The unchanged explicit local depot and local sites provide no evidence of a new spill; STACK112 alone would not establish one.

## Reproduction and timing boundary

```bash
python3 audit_descriptor_prefetch_codegen.py
```

`DESCRIPTOR_PREFETCH_CODEGEN_REVIEW_001.audit.json` retains per-rank sites, resources, opcode comparisons, source checks and artifact hashes. The fuller source mapping is in `profiles/codegen-comparison/descriptor-prefetch.{json,md}`. CPU assertions and Ruff checks pass; the audit launches no compiler or GPU work.

The separate `DESCRIPTOR_PREFETCH_TIMING_001.md` preserves the complete adjacent pair and historical controls, all 50 raw timing rows and 200 actual split-tactic records. The fresh pair shows prefetch +19.40%/+4.35%/+2.54% latency at T1/T8/T64 and −0.69% at T4096. Independent split selections and run variation are disclosed there. The narrow T4096 gain is not stable across earlier controls; no promotion is supported by these measurements.
