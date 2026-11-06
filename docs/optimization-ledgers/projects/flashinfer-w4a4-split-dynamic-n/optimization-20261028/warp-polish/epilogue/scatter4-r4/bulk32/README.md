# Natural bulk32 qualification

This helper selects supported explicit constructor depths with Kpair4/8; it never mutates the storage planner or geometry. NVFP4 and per-token NVFP4 use M128/N256 and FC2 two operand stages. MXFP8 and MXFP4x8 use M256/N128 and FC2 four operand stages. Each compile asserts32-row/one-stage bulk output, preserving native shared-memory capacity. Both static/CLC and PDLoff/on execute balanced, local-count31/32/33/161 tails, empty, and reactivated graphs. Fresh cb35 control precedes R4;64 executions per source,64 cross-source comparisons expected. No timing or sanitizer.

The first helper attempted the wrapper's FP16 output option for the per-token arm. The existing shared unfused finalizer rejects FP16 with `TypeError: MoE finalize requires BF16 input and output`; this is an existing full-chain boundary, not a candidate failure. That attempt is retained under remote `failed-fp16-public-combine` and local `probe_pair-failed-fp16.py`. The corrected helper uses BF16 full-chain output for all four formats. Earlier standalone scatter-copy probes already covered FP16/BF16, all eight128-byte shared-base phases, and one-to-four valid rows. No shared-finalizer change or bypass was added.

Closed after R4 failed performance retention. The corrected BF16 cb35 control passed64 graph replays and asserted actual bulk32/stage1 throughout. R4 candidate had just started; parent-directed cancellation cleanly terminated only process group828287 with SIGTERM and verified GPU1 idle. No candidate bulk32 full-chain pass is claimed. Partial receipts and any compiler artifacts are preserved in `partial-evidence/`; production source was never changed during the gate.

Partial archive:5512042 bytes; SHA256 `9054ead73a1ef748b924586452133dc8d9386737c254040403b1f374f9a0447a`.

The final stopped receipt captured16 successful R4 candidate bulk32 comparisons for config0 (NVFP4 BF16, static/CLC, PDLoff/on, all four route cases). Configs1–3 were not completed; the complete all-format bulk32 gate remains unqualified.
