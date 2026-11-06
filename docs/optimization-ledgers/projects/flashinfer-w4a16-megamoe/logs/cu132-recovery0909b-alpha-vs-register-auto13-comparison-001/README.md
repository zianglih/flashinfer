# Same-node Mega-only AUTO: alpha versus register

Register/alpha geometric-mean latency: **0.9686392416 (-3.136%)**; **10/13 faster**, 3 regressions. Actual tactic changes: **7/13**.

| Global tokens | Alpha Mega ms | Register Mega ms | Change | Alpha/register | Previous tactic | Current tactic |
|---:|---:|---:|---:|---:|---|---|
| 1 | 0.093617 | 0.082961 | -11.383% | 1.128446× | M128/N64, C1, F4, epi | M128/N64, C1, F4, epi |
| 2 | 0.120785 | 0.109761 | -9.127% | 1.100436× | M256/N64, C2, F4, epi | M128/N64, C1, F8, epi |
| 4 | 0.131585 | 0.130481 | -0.839% | 1.008461× | M128/N64, C2, F8, epi | M256/N64, C2, F4, epi |
| 8 | 0.154864 | 0.142034 | -8.285% | 1.090330× | M256/N64, C2, F4, epi | M256/N64, C2, F8, epi |
| 16 | 0.158690 | 0.168225 | +6.009% | 0.943320× | M256/N64, C2, F4, epi | M256/N64, C2, F4, epi |
| 32 | 0.205185 | 0.201377 | -1.856% | 1.018910× | M256/N64, C2, F4, epi | M256/N64, C2, F8, epi |
| 64 | 0.227841 | 0.218049 | -4.298% | 1.044907× | M256/N64, C2, F8, epi | M256/N64, C2, F8, epi |
| 128 | 0.235425 | 0.222354 | -5.552% | 1.058785× | M256/N64, C2, F8, epi | M256/N64, C2, F8, epi |
| 256 | 0.230385 | 0.227202 | -1.382% | 1.014010× | M256/N64, C2, F4, epi | M256/N64, C2, F4, epi |
| 512 | 0.235474 | 0.239698 | +1.794% | 0.982378× | M256/N64, C2, F4, epi | M256/N64, C2, F8, epi |
| 1024 | 0.285155 | 0.271025 | -4.955% | 1.052135× | M256/N64, C2, F8, epi | M256/N64, C2, F4, epi |
| 2048 | 0.347970 | 0.347571 | -0.115% | 1.001148× | M256/N128, C2, F4, reuse | M256/N128, C2, F8, reuse |
| 4096 | 0.499300 | 0.502692 | +0.679% | 0.993252× | M256/N128, C2, F4, reuse | M256/N128, C2, F4, reuse |

Baseline `cu132-recovery0909b-alpha-auto13-001` / alpha487b is consumed through accepted receipt d80825c1 with direct integrity checks; no baseline validator rerun. Candidate `cu132-recovery0909b-epi144-decode96-auto13-001` / registered75 reconstructs its entire original saved result with current V2/raw/resource/MRO/sample/provenance/winner/ranking/cache validators. Each arm has13 raw rows,104 compiled objects and rank-confirmed choices,13 full catalog16 rankings,1,300 samples and10 cache buckets. All208 resources are REG96/640/two decode groups/pool61440/local0. There are no split rows.

Environment: `nvcr.io/nvidia/pytorch:26.05-py3`, eight B300 on `hu-pdx-115` in the same0909b container. Primary metric: unchanged median of100 per-iteration maximum-rank cold-L2 graph-CUPTI spans,3 warmups. AUTO scores remain hot staged-wrapper/reducer GPU events. Whole source changes only Mega kernel e009→4208; canonical weights/input preparation, library/native identities and scorer are unchanged. Native inventory is byte-identical055618ec, all22 entries preserved.

Process wall: alpha 899.177618708s, register 877.625750437s; timing utility: 5.848272062s versus 5.781311815s. These sequential, unbracketed timings and retuned tactics do not isolate a same-compiled-kernel causal effect. No minima or drift correction. Original46136, final fetch82602 and canonical idle71865 close successfully; 111 direct file hashes are retained in [comparison.json](comparison.json). Retention is for root to decide; this report makes no PR edit.
