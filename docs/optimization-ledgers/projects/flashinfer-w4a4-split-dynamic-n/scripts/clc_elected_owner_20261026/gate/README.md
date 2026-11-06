# Elected-owner CLC gate preparation

No source clone, source mutation, or GPU launch is performed by these preparation files. Root approval and immutable candidate freeze are required before deployment.

Use the unchanged full720 six-field host policy on both sources, with control at retained kernel `9b4721b0`. Candidate is `flashinfer-clc-elected-owner-20261026` at that same base plus only the device ownership patch. The shared-flag benchmark source is independent and stays frozen. Public-wrapper probe tactics explicitly request CLC for FC1 and FC2; admission must compile effective CLC for both phases. Native AUTO is bypassed only in this diagnostic gate.

The eight cases cover standard NVFP4, per-token NVFP4, MXFP8 and MXFP4x8 with both one and two CTAs, N16/N128/N256, M512 multi-channel tiles, inline/dedicated epilogues, SwiGLU/SiTU, and PDL off/on. Each graph changes balanced, skewed, empty, and reactivated local routing plus input/route weights. Empty/padded routes exercise terminal scheduler publication. The 1,025-token shape produces more live work than resident capacity.

`run_pair_gate.py` runs control then candidate with exact input and output hashes. Each source produces 64 changing-route replays and 32 core PTX/cubin/SASS artifacts. It can be split across GPU6 (`--config-ids 0,1,2,3`) and GPU7 (`--config-ids 4,5,6,7`); `validate.py --shard ... --shard ... --output validation.json` combines both.

All source receipts are verified before and after each process. Native C++ artifacts must come from the existing verified persistent cache; each immutable source has its own DSL namespace. Validation reports resource and instruction differences, requires no spills and unchanged storage, pipeline geometry and UMMA commits. It makes no performance or sanitizer claim.
