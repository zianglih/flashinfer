# Final A/B producer-ownership audit

**Reject both full A/B variants as implemented.** On identical qualified coverage, A is **−3.826%** overall (51/64 cells negative) and B is **−3.690%** (49/64 negative). The added merged-producer cursor/polling machinery is not justified by these results. This conclusion does not apply to the separately prepared minimal W4A16 FC1-only variant, which is outside this audit.

| Backend | Qualified arms | A, token 4 | B, token 4 | A, token 4096 | B, token 4096 |
|---|---:|---:|---:|---:|---:|
| W4A4 | 8 | −1.746% | −2.141% | −0.866% | −0.376% |
| Per-token | 8 | −0.680% | −0.991% | −3.151% | −3.062% |
| W4A16 | 8 | −0.288% | +0.164% | −0.209% | +0.935% |
| MXFP4x8 | 5 | −14.177% | −14.039% | −19.566% | −19.845% |
| MXFP8 | 3 | −1.200% | −1.094% | −1.528% | −2.193% |
| **All** | **32** | **−3.135%** | **−3.165%** | **−4.512%** | **−4.212%** |

Positive means faster than each variant's fresh retained control. Each cell uses `sqrt(C1*C2)/sqrt(A1*A2) − 1`; table aggregates are geometric means of cell ratios. Token 4 is the decode point and 4096 the prefill point; this is not the full 13-token matrix. A and B each have their own complete same-GPU CAAC control, not a directly interleaved A-versus-B experiment.

## Coverage and failed qualification

Each variant expected 31 jobs / 36 supported model-topology-backend arms / 72 cells. Each finished 29 complete CAAC jobs / 64 cells; the same two N3U mixed-MX jobs failed resource qualification. The common measured set is therefore exactly 64 cells per variant. **No cell from either incomplete mixed job enters the aggregate**, including any partially collected decode point or MXFP4x8 result.

| Variant | Failed job | Blocking specialization | Driver local allocation | Excluded cells |
|---|---|---|---:|---:|
| A | N3U EP8 mixed MX | MXFP8 gathered FC1, N256 / two CTA / K128 | 8 bytes | 4 |
| A | N3U TP8 mixed MX | MXFP8 gathered FC1, N256 / two CTA / K128 | 8 bytes | 4 |
| B | N3U EP8 mixed MX | MXFP8 gathered FC1, N256 / two CTA / K128 | 8 bytes | 4 |
| B | N3U TP8 mixed MX | MXFP8 gathered FC1, N256 / two CTA / K128 | 8 bytes | 4 |

Each failure is a prelaunch `no_native_local` guard rejection; all other recorded resource checks pass. `LOCAL_SIZE_BYTES=8` establishes local allocation, **not proven register spilling**: these receipts query the loaded CUDA function, without SASS/PTX attribution. The failures stop in candidate phase 1 after a complete control phase. There is no completed CAAC timing for those jobs. The prior unsupported K3 MXFP8 and V41F TP MX arms remain outside the declared matrix and are not reclassified as experimental failures.

## Independent checks and limits

- Replayed all **51,200 strict CUPTI samples**, 232 complete phases, 232 runtime guard receipts and **1,024 loaded MoE functions with driver local allocation zero**. Recomputed every raw activity-span duration, phase median and geometric CAAC ratio; results match the existing qualified aggregator. All 100 negative variant-cells remain in the CSV/table.
- Bound all 3,165 source hashes per arm to retained `658a0c89` and the frozen A/B copies; only the two owned kernel files differ. A swap `02031c5f`, W4 `0ba17644`; B swap `15d9533f`, W4 `b29cce29`. Checked the sealed tracked-manifest hashes, seven observer hashes, phase source receipts, unchanged compilation options and register policies.
- Checked every selected frozen route, runner/key/tactic identity, native backend selector, input-quantization contract and cache hit. No AUTO/admitted tactics or profiling calls. Cache entry bytes match the original winners; both arms and every per-token manifest retain their frozen cache contents. The additive MX runtime namespace proof is preserved; it does not change any selected entry or permit retuning.
- Same physical GPU within every CAAC job, 10 warmups, 100 cold-L2 CUDA-Graph CUPTI samples per phase, no event fallback. NVFP4 input quantization is included; W4A16 consumes BF16 directly; MX initial quantization remains excluded. Source-bound component durations are retained, but overlapping PDL kernels must not be summed into end-to-end time.
- All **2,048 sample-quartile clock windows** have NVML observations. Maximum control/candidate repeat spreads are A **2.058% / 4.059%**, B **3.566% / 3.011%**. Most quartile median clocks are 2032 MHz. Recorded exceptions include V41F EP MXFP8 at 2010 MHz in both an A-candidate and control quartile; A K3 TP MXFP4x8 control at 1987 MHz with power-cap reason 4; A V41F TP W4A16 control with reason 4 at 2032 MHz; and B K3 TP W4A16 control at 1875 MHz with reason 0. All rows remain included. The latter limits interpretation of the small B W4A16 prefill gain.
- The dominant MXFP4x8 losses are much larger than their repeat spreads. For example, K3 EP4096 is A **−26.533%** (control/candidate spreads 0.029%/0.198%) and B **−25.967%** (0.258%/0.024%). The ownership change affects both FC roles, so these end-to-end results alone do not identify which internal instruction or dependency caused the loss.

No repository edits, GPU work or PR publication were performed by this audit. Numerical smoke qualification belongs to the campaign's separate gate evidence; this report independently audits performance provenance, resources and arithmetic.

## Artifacts

- [Full paired A/B table](full-table.md): all 64 common cells and both repeat spreads.
- [Raw phase table](raw-phase-table.md): all 128 variant-cells with C1/A1/A2/C2 medians.
- [Full CSV](cells.csv): full-precision raw medians, ratios, spreads, clocks and FC1/FC2 component medians.
- [Audit receipt](summary.json), [failed-job receipts](failures.json), [clock exceptions](clock-exceptions.json), [all phase components and quartiles](phase-components-and-clocks.json), [bound evidence hashes](evidence-hashes.json).
- [Replay script](../audit_final_ab.py), reusing the existing `harness/analyze_perf.py` for component and clock analysis while independently validating raw source/timing/cache identities and the CAAC arithmetic.
