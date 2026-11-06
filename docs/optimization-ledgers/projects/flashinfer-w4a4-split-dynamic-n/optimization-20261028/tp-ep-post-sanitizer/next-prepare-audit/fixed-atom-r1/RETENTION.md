# Fixed SF-atom indexing: retention recommendation

Retain as a small instruction-sanity cleanup, with **neutral end-to-end performance**. This is not a broad speedup claim.

- Base: `83dfef8a656384f5cd10db847602593bb6f9b2c6`. Candidate prepare SHA256: `83e046ef20a750eeca9d9d90d93a0c52877d2d14b32ae19def8fe6dac917d8f4`.
- Entire source delta: one file, **+3/−3 lines**, replacing the fixed signed `//128`, `%32`, and `%128//32` expressions with their exact shift/mask identities. The Int64 promotion remains before multiplication. No branch, policy, synchronization, ownership, layout, allocation, cache hint, public API, or tactic changes.
- The candidate remains unstaged in `flashinfer-prepare-index-review`; canonical source was not changed by this experiment. Patch: `candidate.patch` (SHA256 `cc3d2eec7e0063bfe3d505b3660c778da2a0d47ba56e9d22e4b0b1e22802a54b`).

## Qualification

- Production codegen: **18 paired specializations**, including scaled compact-prefix off/on and PDL off/on. Scaled kernels remove **23–24 static SASS sites**, including four PRMT correction sites. Registers stay the same or decrease by one or two. Memory opcode widths/counts and control/synchronization opcode sequences match; independent memory operations can be scheduled in a different order. No local-memory/stack or uniform-register spill/fill sites.
- Existing byte/canary harness: **552 live CUDA-graph comparisons per source across 92 paired specializations**. Covers route tiles 16/32/64/128/256, SF16/SF32, FP4/FP8/unscaled inputs, 128/256-bit copy widths, PDL off/on, invalid mappings, partial/full/empty/reactivated routes, untouched padding, and grid-stride iterations. All checks pass.
- All **30 unscaled/W4A16 streams** in the byte gate and two representative production streams are identical. No W4A16 timing rerun is needed for this experiment.
- The live byte gate has compact offsets disabled; the separate production codegen gate covers that branch, and public benchmark runs exercise it live. This is not a fresh full MoE accuracy or sanitizer campaign. Those published results remain explicitly bound to `83dfef8a6563`.
- Root ran scoped pre-commit hooks successfully without changing the candidate file. Final integration hooks remain the integrating agent's responsibility.

## Matched performance

`nvcr.io/nvidia/pytorch:26.05-py3`, B300, seven independent GPUs on the secondary C3 devbox. Four models, EP and TP, tokens **4 and 16384**; supported W4A4, PER-TOKEN, MXFP4x8 and MXFP8. Final `83df` managed-cache winners and routing are frozen and checked in every phase. Public functional API, unfused finalize, cold L2, ten warmups, **100 CUPTI samples** per measurement. NVFP4 includes initial activation quantization; MX retains its established prequantized-input contract. No retuning, GPU-event fallback, or external baseline rerun.

**23 jobs, 56 cells, 224 accepted phase medians, 22,400 raw samples.** Each cell compares median(C1,C2) with median(A1,A2), where each C/A value is its 100-sample median, in C-A-A-C order. Positive percentages mean the candidate is faster.

| Group | Geometric mean speed change |
|---|---:|
| Overall | -0.0828% |
| EP | -0.0969% |
| TP | -0.0666% |
| Decode, 4 tokens | -0.0598% |
| Prefill, 16384 tokens | -0.1058% |
| W4A4 | -0.2185% |
| PER-TOKEN | -0.0606% |
| MXFP4x8 | -0.0288% |
| MXFP8 | +0.0233% |

The worst decode row is V41F EP W4A4 at **-0.618%** (33.472/33.472 us control, 33.6645/33.696 us candidate). The worst overall row is V3 EP MXFP4x8 prefill at **−1.650%**; its control medians drift from 698.63 to 679.75 us while candidate medians are 698.02/703.48 us. V41F EP MXFP8 prefill has a more consistent **−0.900%** change. Keep these costs visible; neither is relabeled as a gain. The largest positive row, V3 EP MXFP8 prefill +1.823%, also has substantial phase variation and is not used as a stable benefit claim. No stratum median replaces the standard result.

K3 MXFP8 and V41F TP MX modes are excluded because matching external controls are unsupported, consistent with the retained campaign. W4A16 is unchanged by code generation. Full results: [perf-table.md](perf-table.md), [perf-table.csv](perf-table.csv), [perf-summary.json](perf-summary.json).

## Infrastructure and evidence boundary

Five TP jobs encountered the existing shared generated-header file lock timeout before the failed phase recorded any measurements. Original failure logs and pre-resume receipts are preserved. After workers drained, a nonblocking lock probe succeeded; no cache or lock was deleted. Only missing phases were resumed on their original GPUs, with identical source hashes, winner cache entries, routes and timing settings. All previously successful phases are byte-for-byte preserved. **CAAC order is preserved, but those five jobs have an infrastructure pause.** Successful resumed results are included in the standard calculation; no opportunistic cell replacement or new tactic selection occurred.

The independent aggregator checks all source bindings, route identities, frozen winner/cache identities, arm contracts, lack of tuning, exact 100-sample CUPTI medians, accepted phase hashes, original failures and all 56 expected cells. All **477 fetched evidence files** are hash-verified; source postflight verifies all 348 files for each source and confirms GPUs idle.

Archive: `perf-evidence.tar.gz`, SHA256 `634fe5df14a4cf8df4b19064ac11bdfb146dfa1e92a4a00014b1619966a5e2a4`.

Reproduce the local audit from the project directory:

```sh
python3 optimization-20261028/tp-ep-post-sanitizer/next-prepare-audit/fixed-atom-r1/analyze_codegen.py
python3 optimization-20261028/tp-ep-post-sanitizer/next-prepare-audit/fixed-atom-r1/analyze_gate.py
python3 optimization-20261028/tp-ep-post-sanitizer/next-prepare-audit/fixed-atom-r1/analyze_perf.py
```

Exact executed benchmark commands/environments are in each `perf-evidence/perf/<job>/receipt.json`; raw sample vectors and stdout are adjacent. All native compilation caches and useful local harnesses remain preserved. No extra variants or full benchmark reruns were launched for retention.
