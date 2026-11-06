# W4A16 dequantization artifact audit

The four captured kernels use direct packed BF16 dequantization. Both before
`002529e17b22567a071091053c6c4dc2a55e050e` and after
`a620ce7790b32f7f0ae524a811417d2c6cee1152` report Torch CUDA 13.0,
`cutlass.CUDA_VERSION = DSLCudaVersion(major=13, minor=4)`, and the direct
FP4-to-BF16 helper flag enabled.

`r2/{before,after}/codegen/` contains the actual returned PTX and cubins, their
cuobjdump SASS, native resource usage, and capture receipts. Each FC1/FC2 PTX
contains 64 `cvt.rn.bf16x2.e2m1x2`, 8 `cvt.rn.bf16x2.e4m3x2`, and 64
`mul.rn.bf16x2`; none contains FP16 weight/scale decoding, FP16 multiplication,
or `cvt.f32.f16`. SASS confirms direct BF16 E2M1/E4M3 decoding, with no
`F2F.F32.F16`. Each FC2 kernel has four `cvt.rn.bf16x2.f32` instructions in its
accumulator output epilogue; those are unrelated to weight dequantization.

This is a diagnostic replay of the published EP=8, TP=1 DeepSeek-V3 token-4
configuration, with original observers, sources, frozen tactics, compile
options, 10 warmups, and 100 samples. The resulting diagnostic timing is not
used as performance evidence. The original timed run did not retain these
binaries, so this audit does not claim byte identity to its original cubins.

`verify_capture.py` compares original and replay routing identities, histograms,
arm contracts, frozen tactic/cache keys, and executed kernel symbols. After
FC1/FC2 also match original register-guard entries 2/3 exactly for configuration,
compile options, symbols and native resources. Before has no original register
guard, so its match is limited to the recorded tactic and executed symbol.
`summary.json` records all four results and these limits.

The first attempt failed before launching the first W4 kernel: this SDK returns
requested artifact pathnames when its dump directory does not exist. Explicitly
creating that directory fixed capture in r2. Both r2 processes exited zero.
Original sources and result files were not edited. Original cache content stayed
unchanged except normal `flashinfer_jit.log` appends; native shared libraries and
Ninja files did not change. Private winner/CuTe/driver/Triton copies and all new
outputs remain under this directory. `fetch.json` hashes the fetched evidence.
