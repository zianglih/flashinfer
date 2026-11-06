# Raw-ready probe removal: recommend retaining the narrow step

Recommend using frozen `store16_no_raw_peek` as the next cumulative experiment parent. This keeps the TMEM-free probe and removes only the raw-ready probe. The recommendation weighs the user’s preference for small native instruction reductions, the fresh target gain, and the EP4 result. It does **not** claim improvement for every shape or EP. The actual owned implementation still requires the planned final validation before publication.

| Step: R1/Store16 → raw-ready probe removed | Ratio |
|---|---:|
| Fresh uniform EP4 target, same N64/G512/epi tactic | 1.005571× |
| Native EP4 decode geometric mean, global T4–512 | 1.010446× |
| Native EP8 decode geometric mean, global T4–512 | 0.990668× |

Ratios are Store16 median / raw-only median; above one is faster. The fresh target is H6144/I2048/E256/K8, global1024/EP4 (256/rank), uniform routing: 326.4505→324.642 µs. Native qualification uses H7168/I2048/E256/K8 with the global token counts below. Keep these fixtures and their controls separate. Each run uses cold-L2 CUDA-graph CUPTI, 3 warmups and 100 untrimmed per-iteration rank-MAX samples; medians use all samples, including first-sample outliers.

## Complete native rows

| Global tokens | EP4 R1 µs | EP4 raw-only µs | Ratio | EP8 R1 µs | EP8 raw-only µs | Ratio |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 67.841 | 67.889 | 0.999293× | 64.944 | 79.360 | 0.818347× |
| 2 | 93.936 | 95.041 | 0.988379× | 90.945 | 95.008 | 0.957230× |
| 4 | 119.185 | 116.368 | 1.024203× | 98.849 | 98.561 | 1.002927× |
| 8 | 159.138 | 159.569 | 0.997299× | 122.961 | 125.281 | 0.981482× |
| 16 | 196.258 | 195.458 | 1.004093× | 137.234 | 137.312 | 0.999425× |
| 32 | 269.443 | 262.723 | 1.025578× | 164.977 | 170.224 | 0.969176× |
| 64 | 294.435 | 289.122 | 1.018376× | 193.745 | 195.008 | 0.993521× |
| 128 | 320.212 | 323.779 | 0.988982× | 193.522 | 197.233 | 0.981185× |
| 256 | 330.323 | 324.131 | 1.019103× | 191.746 | 191.680 | 1.000342× |
| 512 | 346.707 | 344.452 | 1.006550× | 203.169 | 203.617 | 0.997802× |
| 4096 | 795.143 | 787.415 | 1.009814× | 460.692 | 461.187 | 0.998927× |
| 8192 | 1484.748 | 1458.622 | 1.017911× | 786.690 | 786.658 | 1.000041× |
| 16384 | 2857.385 | 2858.552 | 0.999592× | 1480.067 | 1508.264 | 0.981305× |

The EP8 limitations are material: T1 is 0.81835×, T2 is 0.95723×, T32 is 0.96918×, T128 is 0.98118× and T16384 is 0.98131×. T1/T2 select N128 rather than the control’s N64, while T32/T128/T16384 keep the same tactic. These observations cannot be erased by the target result or the geometric mean. EP8 T4 is 1.00293× at the same tactic, so the strong T4 regression seen with removing both probes is absent from this raw-only AUTO row.

EP4 tactic differences: T2 changes N64→N128 and G1024→G512; only G changes at T4/8/64/256/16384. EP8: T1 changes N64→N128 and G512→G1024; T2 changes N64→N128 and G1024→G512; only G changes at T8/64/256/512. Return mode remains unchanged. The full emitted tactic dictionaries are in the companion summaries. Final knob caches are audited against the last occurrence of each capacity key; earlier small-token shapes can retune the same key and must be read from their own emitted records.

The native comparisons each use one ordered sweep against older R1 measurements; they are not fresh matched ABBA experiments. The fresh target is a short ordered pair within the partial-probe series. The earlier fixed T4 ABBA tested **both-probe removal**, not this candidate, and is not evidence of raw-only causal timing. Thus small differences may include drift and AUTO selection variation; no statistical significance or universal slowdown/speedup is claimed.

## Direct-parent native codegen

| Matched uninstrumented N64/G512 uniform artifact | R1/Store16 | Raw-only | Delta |
|---|---:|---:|---:|
| Whole native instructions | 5112 | 5096 | −16 |
| FC1 repeated K-loop body | 225 | 220 | −5 |
| FC2 repeated K-loop body | 231 | 223 | −8 |
| Weight stores per K-step | 4 x16 | 4 x16 | unchanged |
| Convert/scale ops per K-step | 136 | 136 | unchanged |
| REG / STACK / SHARED / LOCAL | 96 / 0 / 1024 / 0 | 96 / 0 / 1024 / 0 | unchanged |
| Whole-function LDL / STL / PMTRIG | 0 / 0 / 0 | 0 / 0 / 0 | unchanged |

The exact FC1 delta removes one each of `TRYWAIT`, `BRA`, `LEA`, `S2R`, and `SHF.L.U32`. FC2 removes those five plus one `IADD3`, one comparison and two `LOP3.LUT`, while adding one `VIADD` (net −8). All other per-K opcode counts, including conversion, scale arithmetic, shared loads, stores, required fences and arrivals, are unchanged. Both phases retain two outlined blocking wait helpers with the same five-opcode retry sequences. There is no added wait-path spill or hidden local-memory traffic.

This evidence comes from the completed exact frozen raw-only export, selected by Int32-routing/contiguous-vector-BF16 ABI. Its manifest source-file map, configuration, stage metadata, PTX and cubin fingerprints are verified against the actual Store16 parent. It is not the earlier isolated no-probe experiment against the PR base. Static reductions are scoped to H6144 capacity256/rank,N64/G512/epi; they do not promise a fixed dynamic instruction saving on every readiness path or counts for all AUTO-selected specializations.

Reproduce the CPU analyses:

```bash
python3 optimization/audit_no_probe_results.py --raw-only
python3 optimization/analyze_native_codegen.py \
  --arms control store16 store16_no_raw_peek-uniform-n64-codegen \
  --output optimization/native-codegen-raw-probe-r1-analysis
```

## Correctness, source identity, and retention boundary

All 27 target/native rows pass fixture/output-hash parity, finite/repeated-bit checks and frozen source closure. The native EP4/EP8 comparisons contain 52 / 104 paired rank/shape outputs. Independent BF16-bit reference checks cover native T128 on all ranks and the fresh uniform T1024 target on all four ranks. Other native rows establish paired output parity, not independent-oracle coverage. Final capacity-keyed cache winners also match the logs.

The source delta from R1 is one shared `_transform_tile` method: remove the initial/next raw-ready probe and its cached-status argument; keep the TMEM-free probe and blocking waits. Before final publication, apply the owned implementation port, restore the protected shared helper to PR base, and run the selected final numerical/tail/lifecycle coverage against that actual port. This audit does not qualify a prepared dispatch composition or imply that the other probe-removal candidates are retained.

- R1 SHA256: `7a48709ed07bc8496908625b921927b04dbcca495d7a3b1ced9a7bd28d072234`.
- Raw-only SHA256: `85f18dc5b772155571b21434184b1cef869cc2b0814039c6292943ab344171ff`.

Both are frozen source snapshots based on 002ef145; the base commit is not their final source identity. Environment: hu-pdx-38, boot 1b51b917-b064-4570-afbb-5acd4c450cd9, NVIDIA B300 SXM6 AC, nvcr.io/nvidia/pytorch:26.05-py3, torch 2.12.0a0+5aff3928d8.nv26.05, CUDA 13.2, CUPTI 13.4.0.

Artifacts: `raw-probe-performance-audit.json`, `raw-probe-{uniform,ep4,ep8}-review-r1.{json,md}`, and `native-codegen-raw-probe-r1-analysis/{comparison,delta-vs-store16}.json` plus phase SASS extracts. The companion retention JSON binds these results. Raw completed logs/caches and copy receipts remain in `results/`; only the rank0 manifest/PTX/cubin/SASS/resource summaries were copied for codegen. No compiler cache or causal report was overwritten, and no GPU work or production edit was performed by this auditor.
