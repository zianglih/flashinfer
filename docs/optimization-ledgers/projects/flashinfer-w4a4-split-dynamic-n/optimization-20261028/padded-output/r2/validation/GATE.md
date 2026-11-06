R2 padded-output qualification

- Frozen candidate kernel: `ec675177a1cc759c027471c0926aacc8908e28eea656857afcca297945b6dcb8`; five-file candidate over retained `61249e0bbd40dd2c6e583e4e48ff95e055a3c7f8`. Only the kernel differs from R1.
- 208 exact graph replays per source and 104 paired GEMM compilations passed: 128 main N128/N256 replays, 64 N16/N64 non-bulk replays, and 16 forced-valid-depth bulk32/stage1 replays. Includes one/two CTA, static/CLC, PDL on/off, all four scaled formats, changing balanced/skewed/empty/reactivated routing, poisoned FC2 output, and original inverse-map checks.
- Eight existing wrapper accuracy/graph tests passed, including unchanged fused, legacy and W4A16 paths. No sanitizer was run, as requested.
- Final valid output storage bits are compared. Invalid padded output rows are intentionally unspecified; their contents are not tested.
- All 52 FC1 SASS streams match the retained control. FC2 has 6–625 fewer static non-NOP instruction sites, register changes −32 to +4, unchanged uniform spill/fill counts, and no local-memory or stack spill. These are static code-generation observations, not a performance claim.
- `gate-evidence/evidence-verification.json` verifies all 1,074 archive member hashes. Raw PTX/cubin/SASS, pytest XML/logs, source receipts and exact output receipts are retained under `gate-evidence/evidence`.
- Performance is a separate two-pass candidate-only screen, compared to immutable R1 C1/C2 on the same actual devices/routes/winners. The gap between control and candidate collection permits time drift; this is not an uninterrupted CAAC run.
