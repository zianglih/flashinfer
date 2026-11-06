# Aligned SF word-clear mechanism qualification

The immutable R4 candidate changes only `nvfp4_quantize.py` from retained22ffe; original thread-width and grid policy remain unchanged. The7-cell CAAC compares this source pair, including input quantization.

Actual routed-hole captures passed18 cases and90 graph replays per arm. Candidate records4/5 (K32, linear) emit `STG.E.U16 ... RZ`;10/11 (K48, linear) emit `STG.E.U8 ... RZ`; canonical layouts and K640 emit `STG.E ... RZ` (32bit). All36 candidate/control records and exact source bindings are in `mechanism-proof.json`. This establishes real1/2/4-byte stores, unlike the rejected unaligned `recast_ptr` R2 implementation.

The public initial-linear path has no row-limit holes, but generated code changes: all7 distinct initial CUBINs differ. At V3 K7168 throughput width128, stack grows0→32B with8 LDL and4 STL sites, registers remain64. The other initial captures retain0 stack. The screen therefore includes V3 EP/TP16K alongside N3U TP8/32/64/4096/16K; input-quantization and intermediate-quantization component timings must be reported separately before retention. Source-level dead branches alone do not establish unchanged external TRT per-token baselines.

The complete raw codegen/qualification capture is under `../per-token-word-clear-aligned/hole-evidence`. Its first archive has a stale self-manifest entry only; root saved `hole-self-manifest-diagnostic.json` and repaired the archive generator. All semantic files, explicitly bound qualification receipts, source hashes and CUBIN resources were independently verified. No generated-code recorder is installed during CAAC; no clocks changes or sanitizer runs are used.
