# B300 K96 isolated screening

Both K768/two-stage and K256/five-stage crossing prototypes were byte-exact in the bounded cases and slower than matched frozen 13ca K64 controls. Neither was integrated. See `summary.json` for all eight native timing rows, exact coverage, source hashes and generated resources; `raw/` and `raw.tar.gz` retain complete samples, command manifests, PTX, cubins, SASS and NCU. Source audit and reproducible builders remain in `../../scripts/sm103_k96_audit/README.md`.

This is fixed M256N128, per-tensor NVFP4, unfused phase-level evidence on C2 B300 using CUDA13.2 image26.05; it is not the primary AUTO benchmark or a B200 comparison.
