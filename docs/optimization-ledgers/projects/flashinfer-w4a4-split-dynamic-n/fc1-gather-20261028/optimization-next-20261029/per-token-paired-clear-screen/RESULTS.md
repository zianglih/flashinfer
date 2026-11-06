# GCD-width SF clears, isolated from CTA width

This screen compares width-only R1 against width+word-clear R2, both on retained374; it does not compare R2 directly with374. Width/grid policy, MoE kernels, routes and frozen tactics are identical. Only inactive scale-row zero stores change to compile-time1/2/4-byte words. Control quantizer SHA `374e6f1ab34407d493c274c75f420d56bb3c4b00a2817c6f3fa0b26a1d261b40`; candidate `6de911367a86ad6cdc9549d6344bc220205f10c0517be7b0f41ee7c4a1ab335d`.

**Codegen correction:** the recast-pointer implementation did not generate wider stores. Actual SASS scalarized each intended4-byte SF zero word into four `STG.E.U8` instructions. These results qualify only that unaligned implementation, not an aligned16/32-bit store design. See `codegen-analysis.json` and `CODEGEN.md`.

Recommendation: do not retain the paired-width combination. Word-clear partially recovers its decode loss but does not establish full recovery, and it introduces a stable16K slowdown in this case. Evaluate word-clear alone on the original width policy if pursuing the instruction cleanup. Avoid adding model or recipe exceptions.

- Gate:80 existing exact cases,64 direct cases/256 graph replays/4 routed cases, plus18 all-layout hole cases/90 graph replays passed. The CPU source-AST address proof covers6,908,940 aligned contiguous stores, including linear odd/even column counts and routed remapping.
- Method: N3U TP8 at8/32/64/4096/16384,5cells and2,000strictCUPTI samples. Complete C-A-A-C onGPU0,100samples/phase,10warmups,cold-L2 graphs, public unfused API,input quant included, no retuning. All4 receipts and32 loadedMoE resource guards passed. No instrumentation options or clock changes; all80 clock quartile windows sampled2032MHz with reason0. No sanitizer.
- Results:32tokens+1.109% and64tokens+0.416%;8tokens−0.287% is within repeats.16K−0.645% has only0.063/0.087% control/candidate repeat spread, so it is a meaningful concern.4096 is−0.117% with similar repeat spread. Preserve the full table below rather than reducing this to the+0.093% average.
- At16K, intermediate quantization grows435.315→447.579µs while initial input quantization falls33.904→32.816µs. The initial quantizer has no inactive rows, so source/codegen effects need consideration beyond saved zeroing work. PDL components overlap and cannot be summed.
- External-control caveat: the width-only baseline-impact proof does not automatically apply to this new shared-kernel change. Initial linear quantization never executes the inactive clear under its API contract, but the compiled kernel still receives separate runtimeM/paddedM values; changed register allocation/scheduling could affect its active path. Require codegen equivalence or refreshed evidence before asserting unchanged TRT per-token timing.

Archive SHA256 `b4431ba4bfda784c0e63b7fe53b564964df172c302c7d87808fd15d207340420`;192files verified. All phase medians, component samples, clocks and source/cache/register receipts are under `evidence/`. No poisoned source was timed.

|Model / mode|Tokens|Format|C1 µs|A1 µs|A2 µs|C2 µs|Speedup|C spread|A spread|
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
|N3U TP8|8|PER-TOKEN|64.064|64.144|64.064|63.777|-0.287%|0.450%|0.124%|
|N3U TP8|32|PER-TOKEN|127.345|125.616|125.376|126.433|+1.109%|0.721%|0.191%|
|N3U TP8|64|PER-TOKEN|148.897|147.921|148.305|148.561|+0.416%|0.226%|0.260%|
|N3U TP8|4096|PER-TOKEN|545.587|546.148|545.620|544.900|-0.117%|0.126%|0.097%|
|N3U TP8|16384|PER-TOKEN|1727.275|1738.284|1739.788|1728.363|-0.645%|0.063%|0.087%|
