# Small-N stage depth and persistent occupancy experiment

Independent `../../flashinfer-small-n-occupancy-review` clone at98fd, one unstaged
core change. No production or public API change. This is an explicitly forced
experimental policy, not a validated generic resource fallback.

The host passes `max_active_clusters=num_sms`; the existing kernel launches that
many CTAs with `min_blocks_per_mp=1`. Reducing shared memory alone cannot provide
two resident CTAs when the persistent grid has only one CTA per SM. The earlier
`small_n_widek_experiment` has a generated widek2 module, but keeps this same grid;
its measured small-N decisions compare3/4 stages and do not test this mechanism.

For existing one-CTA K8 N16/N32/N64 only, set two operand stages, double the
persistent CTA grid, and request `min_blocks_per_mp=2`. TMEM/epilogue ownership,
thread roles, math, preparation, TMA, small-N SF cp.async and public tactics are
unchanged. Every other geometry retains its old branch. No model H/I/token-count
selection or dtype threshold is introduced. Initial admission and timing are
NVFP4 N16/N32 only; no other-format correctness or performance claim.

The first stage2-only admission correctly stopped: although99,200 B fits twice
in233,472 B/SM and128 TMEM columns fit twice in512, the driver still reports one
CTA, even with zero dynamic SMEM and100% shared carveout. The cubin reserves128
virtual resources at CTA entry, the entire per-SM pool; current permit release is
at kernel end. `stage2_only_core.py` and `manifest-stage2-only.json` preserve this
non-launched source. The final trial additionally moves
`relinquish_alloc_permit()` after the completed allocation for the eligible branch
only; all subsequent accesses and eventual free remain unchanged.

This is a supported lifetime operation, not cubin metadata editing. Retained
98fd contains immediate-release precedents in
`flashinfer/attention/prims_ts/kernels/mla_decode/throughput_latency_1cta/kernel.py:2543`
and `flashinfer/prims_ts/gemm/kernel.py:3707`. [CuTe allocator documentation](https://docs.nvidia.com/cutlass/4.7.0/media/docs/pythonDSL/cute_dsl_api/utils.html)
and [PTX allocation contract](https://docs.nvidia.com/cuda/parallel-thread-execution/index.html#tcgen05-instructions-tcgen05-alloc-dealloc-relinquish-alloc-permit)
allow continued use/free after relinquishing; future allocations are prohibited.
Our kernel allocates exactly once.

Compile-only checks cover NV N16/N32 and both phases, preserving all8 cubins,
PTX and SASS. Candidate99,200 B vs control197,504 B dynamic SMEM;128 TMEM columns;
64 FC1 /94 FC2 registers in this raw specialization; no local memory. The
`.minnctapersm 2` directive is present. SASS `UVIRTCOUNT.DEALLOC.SMPOOL 0x80`
moves from0x3c50 to0x05c0 before the mainloop. Initial driver occupancy remains1;
it measures admission before dynamic resource release, so it is recorded but is
not used to deny a supported steady-state residency experiment.

Actual-native T32/N16 NCU then proves overlap: mean active CTAs/SM1.88 FC1 and1.93
FC2; mean active warps16.87/17.24 for9-warp CTAs. Launch296 CTAs,99,200 B dynamic
SMEM, actual64/90 registers. Exact FC1 payload/SF, FC2 and full final bytes passed.
NCU durations are diagnostics, never retention medians. The allocation/virtual
resource distinction matters: merely requesting more blocks with the old late
permit does not establish concurrent residency.

Harness timing uses actual native routing/weights, fixed public tactics, the
original full chain including prep, and10 warmups/100 cold-L2 CUDA-graph CUPTI
samples per arm. It swaps actual-source classes and separate caches only; source
math/preparation/host functions are unchanged. Phase byte checks reuse initialized
output allocations; all captured intermediate references are released and
observer capture disabled before full-chain graph capture. No baseline/primary
rerun. Future promotion would need a clean generic static resource policy and
broader exact coverage; this trial deliberately does not add that complexity.

Failed diagnostic attempts are preserved: admission-r1 crashed because the
helper used the wrong `cuFuncSetAttribute` argument order, before any launch;
admission-r2 stopped on the stage2-only occupancy gate. `inspect-admission.log`
lacked an initialized current context and was corrected in-r2. The first
`admission-early-r1` still used the old source after an oversized transfer command
was rejected; it is excluded. Correctly staged early-permit admission is-r2.

## Result: rejected

All16 full-chain arms pass exact phase/final bytes;1600 samples are retained.

|Tokens|N|Control µs (A/A)|Candidate µs (B/B)|Control/candidate|
|---:|---:|---|---|---:|
|32|16|105.4565 / 106.1760|109.4885 / 109.5360|0.966245|
|32|32|106.5130 / 106.7520|109.7280 / 109.7930|0.971501|
|128|16|143.3760 / 143.4250|145.6965 / 145.5690|0.984672|
|128|32|144.0805 / 143.9845|146.5920 / 146.3040|0.983507|

Everycase regresses1.56–3.49%; noT4/T512/otherformat/primary extension. Actual
source remains unstaged. The next explicitly requestedK4/four-stage latency-
hiding follow-up is a separate clone/directory, not a change to this evidence.
Archive `evidence/small-n-occupancy-98fd/raw.tar.gz`, SHA256
`bc4e246772f73ca75b948fed11b32ccca7d815c06ebf69ee02f39f6f6a36f6ff`.
