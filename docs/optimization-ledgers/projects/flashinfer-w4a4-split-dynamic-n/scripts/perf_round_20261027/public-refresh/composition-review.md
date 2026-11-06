# Final retained composition replay

The clean final source combines the independently validated packed combine and hardware-granularity dynamic MMA N changes. The reference is the clean94a89e2c packed-combine commit. Existing source receipts and persistent namespaces remain immutable and explicitly attributed.

Run existing probe configurations0 and2 onGPU7 with fresh paired processes: standard NVFP4 narrow and per-token NVFP4 wide, both one-CTA, both PDL modes, changed/empty/padded routes. This gives16 output replay comparisons and8 GEMM pairs. One-CTA descriptor alignment is the only remaining core change versus94a; the packed finalizer is already identical in both sources. The independent96-replay/48-core MMA-N gate covers all4 formats, static/CLC and1/2CTA; the packed combine has98-case exact coverage. This bounded replay checks their final committed composition without repeating those entire suites.

Require source-before/after identity, exact output hashes and no spills before six public AUTO tables start. No sanitizer or broad new test claim.
