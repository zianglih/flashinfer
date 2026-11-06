# FC2 hybrid versus PR head

The requested FC2-only hybrid was retained and pushed in `61c2c367` after the
completed comparison. Its independent checkout,
`../../flashinfer-swap-ab-fc2-hybrid-review/`, is now clean at that commit. It
exactly matches the previously qualified `swap-ab-hybrid-output/fc2-01`
snapshot: kernel SHA256 `aff286440591dec41bca64a78f27515dd5f6c1563f02c87b8702f89e03755b5a`.
The benchmark baseline was the clean PR #7290 head
`61249e0bbd40dd2c6e583e4e48ff95e055a3c7f8`, verified before launch.

The comparison includes the full candidate change relative to PR head:
padded routed BF16 output, removal of compact-output metadata/workspace
interfaces, full-subtile FC2 TMA, and existing coalesced SIMT tails. FC1
payload TMA and native-fragment scalar FC2 tails are excluded.

## Matrix and method

- Four models: V3 EP8/TP8, V41F EP4/TP4, K3 EP8/TP8, N3U EP8/TP8.
- W4A4, PER-TOKEN, MXFP4x8, MXFP8; W4A16 remains a sanity column.
- Tokens: 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 4096, 8192, 16384.
  Tokens 1–2 are measured but excluded from display and retention aggregates.
- Existing comparator eligibility is preserved: K3 MXFP8 and V41F TP MX
  cells remain N/A. There are 468 measured workloads, 396 displayed cells,
  and 308 displayed cells affected by this output-policy change.
- Each job runs fresh C-A-A-C on one GPU, using saved identical tactics,
  routing and managed-cache contents. No autotuning. Each phase uses
  10 warmups and 100 strict CUPTI cold-L2 CUDA-graph samples; event fallback
  is forbidden. This gives 1,872 medians / 187,200 samples.
- Both arms use unfused swap-AB. NVFP4 includes input quantization with the
  established per-token recipe. No TRTLLM or non-swap controls are rerun.
- Eight B300 GPUs on the existing C3 devbox
  `fi-moe-descriptor-recover-1028` in `ziangli`. Reused image
  `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2. Persistent native compilation
  cache links are verified and retained.
- Prior exact qualification is reused because all 348 relevant source hashes
  match the frozen FC2-only candidate. No new sanitizer run or repository
  test additions. The subsequent authorized commit, push and PR-body refresh
  are recorded in [publication/README.md](publication/README.md).

All scripts, raw samples, logs, source hashes, device identity and plots stay
under this directory. The public benchmark remains
`benchmarks/bench_moe_deepseek.py`; observers only collect host-side metadata
and native timing outputs.
