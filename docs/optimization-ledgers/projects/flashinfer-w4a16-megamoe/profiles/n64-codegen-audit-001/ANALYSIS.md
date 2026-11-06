# N64 two-decoder-group codegen audit

CPU-only inspection of the completed global-4096, EP8, H7168/I2048/E256/K8 codegen captures. No source changes, compilation, GPU queries, or profiler launches were performed by this audit. The generated code has no new local-memory or register-pool blocker. Numerical correctness and performance remain separate gates owned by the parent task.

## Scope and provenance

- Control: `profiles/tmem-fitted5-transform2-codegen-001`, frozen `fe4f8132439df1b812f77279e7d033a5128f1ed4`, M256/N128/K256.
- Candidates: `profiles/tmem-m256n64-codegen-001` and `profiles/tmem-m128n64-codegen-001`, same isolated geometry source, two decoded stages, preferred raw depth five, two transform groups. M128 uses one-CTA instructions inside the physical `(2,1,1)` cluster.
- Candidate kernel SHA256 `5ea9b59f882cef50e6da6c915295acaa626b92331f4fb592c0744b47628de866`; frontend `c358d4abf33de293101b67a5bceead1ca820140a84b916168d33eff4b465aa93`; epilogue `f57edb68382256596d913c7bd86b712d0341b016d6e4c914dd0902620970b0c6`.
- Control kernel SHA256 `58e4af6b935612ed1a68c27fbf355819a02d5a3e622e3fcf5e1dcff0f91c83f7`.
- The corresponding `logs/<capture>.provenance.log` files record source/helper/benchmark hashes and explicit knobs. These captures use flag4, epilogue token return, group512, epilogue `(2,4)`, atomic scheduler, lineinfo, graph timing, warmup1/iteration1. Their timing rows are diagnostic and are not production-performance evidence.
- `source-fe4/` and `source-5ea9/` freeze the three relevant source files. The audit did not infer profile source from the mutable active checkout.
- `analysis.json` contains every rank's original artifact SHA256, resource numbers, selected PTX events/source correlations and barrier initialization constants. `ranks.csv` is the compact raw comparison. The numbered rank0 PTX files make the citations below stable. Within each capture, all eight ranks have byte-identical PTX, cubin and SASS.

## Resources and local memory

| Capture geometry | Registers | Stack bytes | Resource LOCAL | SASS LDL/STL | Static instructions | MMA atoms | TMEM stores |
|---|---:|---:|---:|---:|---:|---:|---:|
| M256/N128 control | 96 | 112 | 0 | 21 | 5672 | 16 | 28 |
| M256/N64 | 96 | 0 | 0 | 0 | 5504 | 16 | 28 |
| M128/N64 | 96 | 0 | 0 | 0 | 5344 | 16 | 28 |

All eight ranks agree. The control's 21 local instructions are the previously audited vendor FC2-router storage (`STL.64` x8, `STL` x8, `LDL.128` x1, `LDL.64` x4). Both N64 variants have no LDL/STL anywhere and no PTX local depot. There are no added transform spills.

All kernels require 640 threads and retain the same register directives: control decreases to 80, transform groups decrease to 80, epilogue increases to 176, dispatch decreases to 64. The role guards remain warpgroup-uniform. Steady-state accounting is `128*(176+80+64+80+80)=61440=640*96`; this is the established register redistribution, with no increased pool demand. It does not prove contention is absent.

`cuobjdump` reports SHARED 1024 for all three while PTX declares an external shared symbol aligned to 1024. That resource value is not a measurement of launch dynamic shared memory. The source/fitter predictions at this shape are 216576 bytes for control and M128/N64, and 183808 for M256/N64. The new captures do not contain observed launch metadata proving those predictions; do not add 1024 to them or describe 1024 as dynamic usage.

## Operands, descriptor and TMEM proof

Both N64 kernels allocate and free 512 TMEM columns. Their two accumulator stages use 64-column pitch (columns 0–127), and decoded BF16 weights start at column 128 with 128-column stage pitch (columns 128–383). There are two decoded stages in these captures; the separate third-stage patch remains outside this audit.

- **M256/N64:** rank0 PTX337–338 allocates512 with CTA-group2;6609–6610 frees512 with group2. Transform setup2695–2712 loads the allocation, adds warp row coordinates, `transform_group*64`, then decoded base128. MMA setup4543 adds the same128;4579–4580 uses accumulator-stage `<<6`;4633–4635 uses decoded-stage `<<7`. Activation SMEM stage descriptor advances by `<<10` in16-byte descriptor units =16384 bytes per CTA.
- **M128/N64:** PTX317–318 and6441–6442 allocate/free 512 with group1. Transform setup2583–2600 constructs the same decoded base128 plus group/row partition. MMA4410 adds128;4442–4443 uses accumulator-stage `<<6`;4492–4494 uses decoded-stage `<<7`. B descriptor advances by `<<11` =32768 bytes per CTA, matching the full N64 B tile.
- All three captures have 16 static TMEM stores in the reused local W4A16 transform helper (eight per FC phase), plus 12 epilogue scratch stores. The transform writes decoded BF16 directly to TMEM and the MMA reads TMEM A; there is no full/global BF16 weight materialization.
- M256/N64 PTX4657–5002 has 16 `tcgen05.mma.cta_group::2.kind::f16` K16 atoms; M128/N644516–4861 has 16 group1 atoms. The inline PTX operands are TMEM accumulator, TMEM A and a64-bit SMEM B descriptor. SASS corroborates16 `UTCHMMA.2CTA` versus16 `UTCHMMA`.
- The first atom uses the outer K-tile counter to disable accumulation only at K tile zero; the next 15 atoms accumulate. The full K256 reduction therefore retains 16 K16 atoms, with the phase selecting 28 FC1 or 8 FC2 K tiles at the profiled dimensions. No blockscaled instruction was substituted.
- M256's descriptor base is `0x10000490`; M128's is `0x08000490`. These encode the intended M and BF16 operands/FP32 accumulator. Generated runtime N forms are `(((valid << 14) + 245760) & mask) | base`, mask `0xeffc0000` or `0xf7fc0000`. The audit exhaustively checks all valid-token counts 1–64 against `base | ((align16(valid)/8)<<17)`. PTX4581–4586 (M256) and4444–4449 (M128) contain those constants. The descriptor rounds runtime N while storage pitch remains fixed64.

## Physical CTA and pipeline proof

M256's MMA preamble4551–4558 tests physical CTA parity and skips MMA on the nonleader, as required for group2. M128's corresponding preamble4346–4450 enters from warp4 and has no physical CTA parity skip; both physical CTAs issue their own group1 MMA.

- **M256 dynamic B:** both FC phases retain the nonleader correction `align16(valid_tokens)/2 - 32`: PTX2333–2345 and2479–2491. The leader contributes rows beginning 0 and the nonleader begins at `align16(valid)/2`; descriptor N and epilogue row mapping agree. Each CTA stores half of the fixed N64 activation tile, with total expected transaction 32768 bytes (PTX2390–2408).
- **M128 activation multicast:** PTX2320–2348 and2441–2469 use multicast mask 3 in both FC phases. Each physical CTA issues its partition of B and multicasts to both CTAs; each destination expects the full 32768-byte tile. No group2 nonleader shift survives in M128. The B consumer barrier expects two releases, one per physical CTA's group1 MMA.

Generated initialization counts (same offsets relative to the shared-storage base):

| Pipeline | Full / empty offsets | M256/N64 full / empty counts | M128/N64 full / empty counts |
|---|---|---|---|
| Raw five stages |0..32 /40..72 |1 /8 |1 /8 |
| Decoded two stages |80,88 /96,104 |512 /1 |256 /1 |
| Activation two stages |112,120 /128,136 |1 /1 |1 /2 |
| Accumulator two stages |144,152 /160,168 |1 /256 |1 /128 |

Counts follow V2 versus V1 semantics rather than copying the original two-CTA values. Named TMEM-retrieve barrier remains 416 participants (`bar.sync 2,416` at M256345/M128325), scheduler consumer 480, dispatch-to-scheduler 160, and terminal communication barrier 640. The transform group-local index and group index remain `(warp-12)//4` and `thread-384-group*128` in each kernel.

No generated-code discrepancy with the prior source/barrier review was identified. The full source-tail and routing-return hazards remain documented in `candidates/w4a16_m128_n64/current2group/GPU_HAZARD_REVIEW.md`. These codegen captures use full-model H/I and do not replace small-dimension tail, odd-token, ring-wrap, both-return-mode, or numerical tests.

## Reproduction and limits

Run `python3 audit_n64_codegen.py` from the effort root. It only reads existing captures, verifies all 24 resource/codegen records, copies frozen sources, and emits the JSON/CSV/numbered PTX. `ruff check` and formatting pass for the helper.

Static instruction counts measure generated text, not dynamically executed work or latency. Absence of local instructions establishes no local-memory traffic in these binaries, not absence of register contention. Geometry numerical validation was still pending when this audit was completed; its launcher had previously failed before kernel launch. Production timing, any promotion decision and accuracy claims must use the parent's independent benchmark and numerical gates.
