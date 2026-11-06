# T128 split W4A16 profile diagnostics

Completed saved profiles only; no new profiling or GPU execution by this review. Both arms reuse their original normal T128 row cache without retuning, with fused finalize and the same H7168/I2048/E256/top-k8, EP8/TP1 simulation. Both caches select GEMM1/GEMM2 `((128,16,256),(2,1),True)`.

The [baseline selection record](profiles/baseline-t128-ncu-selection.json) identifies GEMM2 as the second actual grouped-GEMM graph node. Both Nsight Systems SQLite traces and NCU records confirm its grid `(2,1,74)`, block `(512,1,1)`, 128 registers/thread, 191552 bytes dynamic shared memory and zero local memory. The Nsight Systems records report zero static shared memory for this launched tactic. This selected tactic differs from the small fixed C1 compile-only cases in [the native comparison](NATIVE_COMPARISON.md).

| Saved measurement | Baseline | Top-k constexpr |
| --- | ---: | ---: |
| Nsys GEMM1, one captured replay | 92.448 µs | 91.425 µs |
| Nsys GEMM2, one captured replay | 49.025 µs | 48.961 µs |
| NCU `smsp__inst_executed.sum` | 29425862 instructions | 29368453 instructions |
| NCU kernel duration | 53.440 µs | 50.400 µs |
| NCU DRAM reads | 247.815168 MB | 219.568896 MB |
| NCU DRAM writes | 10.900224 MB | 146.944 kB |

**The NCU arms use different replay modes:** baseline application replay with strict matching; candidate kernel replay. Both request `--set full`, with cache/clock control disabled. Consequently the duration and traffic differences above are diagnostic observations, not speedup or bandwidth-reduction evidence. Even the executed-instruction count can include different polling/replay behavior; the fixed native comparison directly establishes the top-k arithmetic reduction. The exported full-metric CSVs do not contain a direct integer-operation sum counter. Nsys durations are also one instrumented replay, not a repeated performance test.

Actual full-profile files:

- [Baseline NCU CSV](profiles/baseline-t128-ncu.csv) and [candidate NCU CSV](profiles/candidate-topk-t128-ncu.csv); adjacent `.ncu-rep` files retain the full collected reports.
- [Baseline Nsys SQLite](profiles/baseline-t128-nsys.sqlite) and [candidate Nsys SQLite](profiles/candidate-topk-t128-nsys.sqlite); adjacent `.nsys-rep` files retain the traces.
- [Corrected candidate NCU command](remote-prep/run_candidate_ncu002.sh) and [log](remote-prep/candidate-ncu002.log). The first candidate attempt failed option parsing before launch because `--app-replay-mode strict` cannot accompany kernel replay; [that log](remote-prep/candidate-ncu001.log) remains preserved.

The successful candidate report retains warnings for six unavailable CTC metrics, uncontrolled caches/clocks and absent imported source files. `--set full` requests the full metric set but does not make unavailable metrics present. Use the separately exported line-info native dumps for source-correlated arithmetic inspection.

Latency evidence remains the complete unprofiled [first A/B pair](TOPK_BENCHMARK_COMPARISON.md) and [repeat A/B pair](TOPK_BENCHMARK_REPEAT_COMPARISON.md): geometric-mean latency changes of −1.383239% and −1.521506% over 8–8192 tokens, respectively. Both pairs retain all 14 rows; no minima are selected across runs.
