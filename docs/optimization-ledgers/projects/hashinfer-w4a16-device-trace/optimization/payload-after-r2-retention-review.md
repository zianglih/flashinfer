# Parallel payload on R2: reject the addition

Keep retained R2. The payload addition has no demonstrated target benefit, leaves EP4 decode flat, regresses EP8 decode, and adds eight whole-kernel instructions plus a named-barrier handoff. Numerical checks pass, but the added complexity is not justified by the completed measurements. The contemporary fixed-target ABBA also favors R2 slightly; this supports rejection without claiming a precise causal slowdown.

| Comparison versus actual R2 | Ratio |
|---|---:|
| Uniform EP4 H6144 target, global1024 | 0.981803× |
| Native EP4 H7168 decode geometric mean, globalT4–512 | 1.001494× |
| Native EP8 H7168 decode geometric mean, globalT4–512 | 0.979254× |

Ratios are retained-parent median / candidate median. Both models use I2048/E256/K8. Each AUTO timing run uses 3 warmups and 100 untrimmed cold-L2 CUDA-graph CUPTI samples, aggregated as per-iteration rank maximum. The uniform target uses uniform routing, 256 tokens/rank. Native rows use the benchmark’s standard fixture. The baseline is the actual R2 raw-only snapshot, not R1.

| Global tokens | R2 EP4 µs | Payload EP4 µs | Ratio | R2 EP8 µs | Payload EP8 µs | Ratio |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 67.8890 | 71.5530 | 0.948793× | 79.3600 | 71.0565 | 1.116858× |
| 2 | 95.0410 | 94.9130 | 1.001349× | 95.0080 | 92.5130 | 1.026969× |
| 4 | 116.3685 | 114.5450 | 1.015920× | 98.5605 | 104.5925 | 0.942329× |
| 8 | 159.5690 | 146.2895 | 1.090775× | 125.2810 | 130.7520 | 0.958157× |
| 16 | 195.4580 | 207.9050 | 0.940131× | 137.3125 | 145.1525 | 0.945988× |
| 32 | 262.7230 | 262.4980 | 1.000857× | 170.2240 | 168.6090 | 1.009578× |
| 64 | 289.1220 | 295.4580 | 0.978555× | 195.0085 | 195.0890 | 0.999587× |
| 128 | 323.7790 | 321.5225 | 1.007018× | 197.2330 | 196.7850 | 1.002277× |
| 256 | 324.1310 | 329.7470 | 0.982969× | 191.6805 | 198.9445 | 0.963487× |
| 512 | 344.4515 | 343.7630 | 1.002003× | 203.6170 | 200.4340 | 1.015881× |
| 4096 | 787.4150 | 775.1910 | 1.015769× | 461.1870 | 474.9130 | 0.971098× |
| 8192 | 1458.6225 | 1441.6265 | 1.011789× | 786.6575 | 783.6400 | 1.003851× |
| 16384 | 2858.5520 | 2860.1210 | 0.999451× | 1508.2635 | 1525.0635 | 0.988984× |

The target changes from **324.642 to 330.659µs**, with N64/G512/epi in both arms. EP4 AUTO changes N128→N64 at T2, and G at T8/64/256/16384. EP8 changes N128→N64 at T2, and G at T1/4/16/128/4096. Return mode is unchanged throughout. Earlier small-shape cache winners are read from the log; final capacity-keyed cache entries match the last winner for each key.

## Contemporary fixed-target ABBA

A1/B1/B2/A2 measured **330.851 / 333.203 / 330.2905 / 330.2265µs**, all with the same N64/G512/epi tactic. Pooling all 200 untrimmed samples per arm gives **330.499µs R2 versus 331.650µs payload = 0.996529×**. Three warmups, cold L2, CUDA graphs, CUPTI and per-iteration rank maximum remain unchanged. All 16 rank/run independent-reference checks pass, and source/fixture/output hashes plus exact driver/helper/fixed-knob provenance were independently rechecked.

The contemporary control is slower than the older 324.642µs R2 target baseline, so the original ordered-pair 0.981803× is not a clean causal estimate. A1→A2 moves only −0.6245µs, while B1→B2 changes −2.9125µs; the small pooled difference is not evidence for a precise penalty. It does establish no compelling target gain. This fixed-target check does not replace the AUTO matrix or explain every native-shape difference.

The completed remote summary was independently recomputed from the copied raw logs, and every row matches exactly. Artifacts are `results/payload-r2-fixed-confirmation-1/`, `payload-after-r2-fixed-review.{json,md}`, and `payload-after-r2-fixed-audit.json`. The original remote fixed-knob record is preserved; the local audit maps its driver path to a byte-identical, SHA-verified local script.

## Numerical and source scope

All 27 rows pass frozen source closure, matched input/routing/weight/output hashes, and finite/repeated outputs: 4 paired target rank outputs, 52 native EP4 rank/shape outputs, and 104 native EP8 rank/shape outputs. Independent BF16-bit reference checks cover the target on all four ranks and native globalT128 on all four/eight ranks. Other native rows establish paired output parity, not independent-reference coverage.

The combined snapshot changes only owned main-kernel and token-communication files versus R2. Those payload components are byte-identical to the separately qualified parallel_payload source, with the same parent input files; retained raw-only transform code is unchanged. Earlier stateful empty/refill/graph/heterogeneous-grid validation belongs to that separate component and does not replace final combined-source validation.

## Exact combined native codegen

The fixed EP4 H6144, capacity256/rank, N64/G512/epi export matches the frozen source and all PTX/cubin/SASS fingerprints. The timed Int32/vector ABI changes whole-kernel native instructions **5096→5104 (+8)**. FC1 stays **220 instructions per K tile**, FC2 **223**; both opcode histograms and outlined wait sequences are unchanged. All four staging ABIs retain **REG96 / STACK0 / SHARED1024 / LOCAL0**, with no local-memory spill instructions or IKET PMTRIG instructions.

For all four ABIs, native code has exactly one NB11 arrival and one NB11 wait. The payload async-proxy fence precedes arrival, arrival precedes the epilogue register increase, and the dispatcher’s wait is immediately followed by the original NB10 grid synchronization. This confirms the intended generated handoff, not an execution-time benefit. If retained, the final stack needs numerical/lifecycle qualification and a separate synchronization-sanitizer check for the new named barrier.

The legacy codegen driver reports BENCHMARK_COMPLETE and four exports, but provides no final source-closure marker or independent oracle. Its 0-warmup/1-sample diagnostic duration is excluded from retention timing. The parent observed driver termination and empty GPU contexts separately. The compiled-source fingerprint checks remain valid independently.

## Limitations and artifacts

Full AUTO comparisons are ordered sweeps against an older R2 measurement; their ratios do not isolate instruction-level causes or remove time drift. The contemporary fixed-target ABBA is a separate experiment and cannot replace the full AUTO matrix. Reject this addition and keep R2; do not add NB11 to the final stack.

- R2 SHA256: `85f18dc5b772155571b21434184b1cef869cc2b0814039c6292943ab344171ff`.
- Candidate SHA256: `1bc75d6fa090a747ed0e54e6924feba94039c4cdf4f6c0da4207e371738950db`.

Artifacts: `payload-after-r2-performance-audit.json`, `payload-after-r2-{uniform,ep4,ep8}-review-r2.{json,md}`, `payload-after-r2-source-composition-audit.json`, `native-codegen-payload-after-r2-analysis/direct-r2-audit.json`; completed raw logs and caches are under `results/`. Only read-only collection and CPU analysis were performed by this auditor.
