# K3 EP16K: cached wide-row quantizer images

The lower-register result generalizes to both wide rows, but the cached images do not explain away the adverse timing. This audit did not compile, load a CUDA module, query the driver, run a GPU, or modify a cache object.

| Timed stage | BF16 input / layout | Registers control → candidate | Non-NOP control → candidate | Local / stack |
|---|---|---:|---:|---|
| Initial quantizer | 16384 × 3584; linear SF | 63 → 56 | 1023 → 925 | 0 / 0 in both |
| Intermediate quantizer | capacity 269184 × 3072; SF 128×4, row group 64 / SF group 128 | 64 → 52 | 1142 → 1042 | 0 / 0 in both |

Both use recipe 23 (precise base quantization, fast-error MSE256), 128 threads, four warps and two SF blocks per thread. The frozen K3 EP8 tactic has route tile 64. Its histogram gives 33,208 live local rows and 36,608 padded rows, including 3,400 holes; the remaining capacity is excluded by the existing valid-row limit. Cuobjdump reports unchanged shared allocation 1024 bytes and maxthreads 128. No LDL/STL appears. These are cuobjdump resource fields, not a new driver resource/occupancy capture.

Each image replaces 128 scalar FADD and 64 scalar FMUL sites with 64 FADD2 and 32 FMUL2 sites: 96 fewer arithmetic instructions. Input also removes one CS2R and one MOV. Intermediate has a further net 4-instruction reduction with integer/address/packing opcode redistribution. Existing FFMA and FTZ opcode counts are unchanged; the earlier native pilot established the ordered RN recurrence. This wider comparison does not claim identical instruction scheduling or a complete new recurrence proof.

| CAAC phase | E2E µs | Initial duration µs | Intermediate duration µs | Intermediate critical extension µs |
|---|---:|---:|---:|---:|
| 0 control |1042.6960|59.0565|133.0575|125.0415|
| 1 candidate |1050.1370|60.7370|137.3610|129.4890|
| 2 candidate |1040.3605|60.2085|136.2570|128.1450|
| 3 control |1033.8010|58.4645|131.1370|123.1850|

The paired E2E result is −0.669546% (+6.998345µs). The arithmetic means of the per-phase component medians rise 1.71225µs initially and 4.70375µs in intermediate critical extension; component medians need not sum to the E2E median. Each candidate quantizer duration exceeds both control durations. Control/candidate repeat spreads are 0.8604%/0.9397%. Both nonzero-reason windows are control quartile 3 (reason 4; all median SM clocks 2032 MHz), with no missing window; neither candidate phase has a clock exception. This audit supplies no new timing and does not replace any phase.

The saved timeline also changes overlap: FC2 starts at 721.942µs in control versus 623.509µs in candidate, while intermediate quant ends 743.734 versus751.134µs. FC2 duration grows 248.714→352.907µs but its critical extension stays 225.634→225.586µs. The existing quantizer publishes its dependent-grid startup signal before row work (`nvfp4_quantize.py:1055–1062`). Lower quantizer register occupancy could permit earlier dependent-kernel residency and change interference, but CUPTI intervals and cached images do not establish that cause. The fixed total grid does not constrain each SM to the average budget or determine total residency across overlapping kernels. Preserve this overlap distinction rather than attributing the loss to spills or explaining it away as clocks.

**Occupancy boundary.** The unchanged host policy supplies `min(padded_M, SMs × (1024 // threads))` CTAs. Here that is 8 CTAs/SM, 1184 CTAs on 148 SMs. Lower register counts can increase hardware capacity but cannot by themselves increase this total launch grid. The average8 CTAs/SM is not an enforced per-SM cap; placement can redistribute, and actual concurrent residency was not traced. Likewise the K640 pilot's driver occupancy 16→20 does not mean that a 2368-CTA (=148×16) grid runs 20 CTAs/SM. No wide-row driver occupancy was queried, and no throughput inference follows from the lower instruction count.

**Provenance.** `evidence/receipt.json` binds four copied objects, fatbinaries, native cubins and cuobjdump outputs. All source fingerprints match the strict qualified arm manifests, all four object/meta reads were stable, and symbols match every phase's saved CUPTI names. The performance harness did not retain quantizer load handles: these are source-bound cache-specialization inferences, not proof of the exact ELF loaded in each timed process. `analyze.py` verifies every extracted payload hash, fully parses all address-bearing SASS lines, joins the frozen recipe/tactic/routes and reproduces the native table and component medians in `summary.json`.

Sources: `flashinfer/quantization/kernels/nvfp4_quantize.py:867–885,935–946,3413–3432`; `flashinfer/fused_moe/cute_dsl/fused_moe.py:835–852`; frozen performance leaf `evidence/paired-4over6-error-cute-only/1793401876554197000/data/results/ep-kimi-k3-per-token`.
