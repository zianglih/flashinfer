# Count overlap on R2: reject the addition

Keep retained R2 (`store16_no_raw_peek`). The count-overlap addition passes correctness checks in the completed scopes, but both the specified target and complete EP4 decode matrix regress versus that actual parent. The unfinished EP8 guard is excluded. A later native export confirms increased whole-kernel instruction count, but its diagnostic execution failed; the compilation evidence is kept separate from performance and correctness results.

| Completed comparison versus actual R2 | Before µs | After µs | Ratio |
|---|---:|---:|---:|
| Uniform EP4 target | 324.642 | 330.723 | 0.981613× |
| Native EP4 decode geometric mean, global T4–512 | — | — | 0.980290× |

The uniform target is H6144/I2048/E256/K8, global1024/EP4 (256/rank), uniform routing. Both arms select N64/G512/epi. Native qualification uses H7168/I2048/E256/K8 with the global token counts below. Ratios are parent median / candidate median. These are cold-L2 CUDA-graph CUPTI measurements with 3 warmups and 100 untrimmed per-iteration rank-MAX samples per run, compared against the completed R2 evidence.

| Global tokens | R2 µs | R2 + count overlap µs | Ratio |
|---:|---:|---:|---:|
| 1 | 67.889 | 74.897 | 0.906431× |
| 2 | 95.041 | 102.545 | 0.926822× |
| 4 | 116.368 | 118.097 | 0.985360× |
| 8 | 159.569 | 149.185 | 1.069605× |
| 16 | 195.458 | 210.562 | 0.928268× |
| 32 | 262.723 | 271.315 | 0.968334× |
| 64 | 289.122 | 298.323 | 0.969158× |
| 128 | 323.779 | 331.219 | 0.977538× |
| 256 | 324.131 | 335.204 | 0.966968× |
| 512 | 344.452 | 350.548 | 0.982609× |
| 4096 | 787.415 | 795.560 | 0.989762× |
| 8192 | 1458.622 | 1460.316 | 0.998840× |
| 16384 | 2858.552 | 2849.590 | 1.003145× |

AUTO changes only G at T2/4/8/64/256; N and return mode remain unchanged. Complete tactic dictionaries, samples, dispersion and log fingerprints are preserved in `counts-after-r2-ep4-review-r2.json`. The target and complete EP4 comparison are each an ordered pair, not a contemporaneous ABBA experiment; timing differences are observations, not a proven instruction-level causal attribution.

## Correctness and scope

The target and all 13 EP4 native rows pass matched weight/input/routing/output hashes, finite/repeated output checks and frozen source closure. There are four paired target rank outputs and 52 paired native rank/shape outputs. Independent BF16-bit reference checks cover the target T1024 and native T128 on all four ranks; other native rows establish paired output parity. Final capacity-keyed knob cache entries match the final emitted winner for each key; superseded small-shape winners remain available in their per-shape log records.

The combined source differs from R2 in exactly three files: owned main kernel, owned token communication, and vendored token communication. These count components are byte-identical to the separately qualified `counts_fence` components, with identical parent input files; the retained raw-only transform is unchanged. This proves exact source composition, not replacement of combined-candidate GPU qualification by earlier tests. The earlier stateful counts-fence qualification remains separate evidence.

EP8 was incomplete at the rejection decision and is excluded. The later exact combined codegen export emitted all four compilation artifacts, then rank 3 failed with SIGSEGV 11 before a benchmark completion or timing row. The cause is unknown. Its artifacts establish compilation properties only; that failed execution establishes no timing or correctness success.

## Compilation-only native audit

The matched EP4 H6144, capacity 256/rank, N64/G512/epi diagnostic specialization changes whole-kernel native instructions from **5096 to 5176 (+80)** versus R2. FC1 remains **220 instructions per K tile** and FC2 **223**; both per-K opcode histograms and outlined wait sequences are unchanged. All four staging ABIs retain **REG96 / STACK0 / SHARED1024 / LOCAL0**, without local-memory spill instructions or IKET markers.

Source-manifest and PTX/cubin/SASS fingerprints match the frozen combined source. Native synchronization inspection confirms two relaxed system packed-count REDs, one prefix fence bundle and the original trailing publication fence bundle, plus NB9 arrival followed by high-word system acquire loads. The compiler narrows each PTX 64-bit acquire to the high 32-bit readiness word because the low word is unused by that predicate. This static audit does not claim that the failed diagnostic execution completed and does not reopen the performance rejection. See `native-codegen-counts-after-r2-analysis/comparison.json` and `synchronization-audit.json`; the failed raw log remains `results/counts-after-r2-uniform-n64-codegen.log`.

- Actual R2 source SHA256: `85f18dc5b772155571b21434184b1cef869cc2b0814039c6292943ab344171ff`.
- Rejected combination SHA256: `3ec75add37d200d2c06d986436f3a87c61774706c0c79d0bfab0878b7baf99c1`.

Artifacts: `counts-after-r2-performance-audit.json`, `counts-after-r2-{uniform,ep4}-review-r2.{json,md}`, `counts-after-r2-source-composition-audit.json`, and this report’s companion JSON. Raw completed logs and knob caches are under `results/`. Source identity is the frozen Python-tree hash, not the shared base commit. Only read-only collection and CPU analysis were performed here; no GPU process was started or stopped by this auditor.

Reproduce the completed-scope audit:

```bash
python3 optimization/audit_no_probe_results.py --counts-after-r2 --scopes uniform ep4
```

The parent stopped the unfinished EP8 torchrun with SIGTERM at 2026-09-25T11:39:56.761254+00:00 (PID 134211). Its completed timing rows before stopping were none; all are excluded from retention evidence. The stopping receipt and partial log are preserved as `results/counts-after-r2-ep8-stopped.json` and `results/counts-after-r2-ep8.log`. The separate fixed diagnostic export subsequently produced usable compilation artifacts but failed during execution as recorded above.
