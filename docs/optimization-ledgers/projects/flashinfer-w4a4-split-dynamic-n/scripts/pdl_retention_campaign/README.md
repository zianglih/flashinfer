# Completed PDL retention campaign

C1 → T1 → A1 → A2 → T2 → C2 completed with182 verified rows. Final paired results and every median are in [the full evidence report](../../evidence/pdl-retention-8c1a/full/README.md); source/gate config remained unchanged throughout. Root owns the retention and promotion decision. Earlier preparation and first-screen notes below are preserved as history.

# PDL retention campaign

Final source `8c1a20173cf166b9fc279f6ae3ec5386250c5c5e` is frozen and independently provisioned. Parent approved C1 → T1 → A1 after all five bounded cases passed exact output checks (9,000 samples). [campaign.json](campaign.json) records the immutable source/gate/GPU configuration; pause after A1 for review before A2. The original pending config and earlier preparation text below remain provenance, not current execution authority.

# Pending PDL retention campaign

CPU preparation only. **No GPU launch is authorized or performed by this preparation.** The rejected `is_fc1` candidate is not eligible; the pending candidate is the parent's eventual reviewed behavior-knob source. `campaign.pending.json` intentionally has `launch_approved=false`, no candidate repo/commit/source hashes, and no bounded-gate receipts. The earlier unused explicit-phase config is preserved as `campaign.pending-explicit-rejected.json`.

The parent has reserved stable physical slots for the future campaign:

|Mode|NVML index|CUDA-visible UUID|
|---|---:|---|
|NVFP4 and native TRT NVFP4|2|`GPU-7e973000-5213-bf29-4ca1-25a6d947f8e3`|
|MXFP8|3|`GPU-8f15506e-8209-ef53-6b00-b04ece9e69d3`|
|MXFP4 weights × MXFP8 activations|4|`GPU-9b1e25f5-48e6-f126-6d93-160b7ea7dd32`|

Each CuTe arm runs the three formats concurrently, one fresh process per format. Native TRT is a separate sequential arm on the NVFP4 GPU, with native logits routing/finalize and no distributed mode. The runner rechecks UUIDs and idle processes before launching. It exposes the full UUID through `CUDA_VISIBLE_DEVICES`, avoiding a CUDA/NVML ordinal assumption.

## Freeze gate and commands

Parent supplies a new immutable `campaign.json` after the bounded gate: approved clean candidate repo and full commit, the exact source-file map tested by the owner, and hashes/paths of the five passing native gate JSONs for T4/T32/T128/T4096/T16384. Each must report complete, FC1/FC2 exact and final bytes exact, and pin the same candidate source map. Set `launch_approved=true` only after parent release. This is an internal execution gate, not a pending user permission request. If cleanup changes source bytes, the old gate cannot authorize the new bytes. Source commits and dirty prototype hashes remain distinct; this runner accepts only a clean committed primary candidate.

Transfer only these new named helper/config files through the managed `/usr/local/bin/h` workflow. Do not modify frozen observers or `fc1_regular_tma_auto/`. Before any executable command, source the established environment on `fi-w4a4-narrow-1025`:

```bash
cd /workspace/flashinfer-w4a4-split-dynamic-n
source scripts/recovery442/env_candidate.sh

# This is always a CPU-only command listing; it launches nothing.
.venv/bin/python scripts/pdl_retention_campaign/run_arm.py \
  --config scripts/pdl_retention_campaign/campaign.pending.json --arm A1

# Only after the parent creates and approves immutable campaign.json:
.venv/bin/python scripts/pdl_retention_campaign/run_arm.py \
  --config scripts/pdl_retention_campaign/campaign.json --arm C1 --execute
```

Approved stage order is **C1 → T1 → A1 → review → A2 → T2 → C2**. Invoke one stage at a time by changing `--arm`. This preserves C-A-A-C and T-A-A-T while sharing candidate data: 156 CuTe rows plus 26 TRT rows, 14 fresh processes. Stop after the first 91-row screen if it does not satisfy the parent's accepted decode/prefill tradeoff. Do not silently invent a universal percentage gate. A slight prefill slowdown may be acceptable to the user; report every point and both repeat directions.

`C1/C2` mean corrected retained **aab current-node controls**, never original a65. Original a65 B1/B2 and earlier TRT evidence stay reused as immutable historical references and are not rerun or pooled. If the parent already has a provenance-matching current-node arm to reuse, verify that evidence and adapt the outer schedule explicitly before freezing the config; do not fake a prerequisite receipt. No such reusable current-node full-grid arm is assumed here.

After all approved stages:

```bash
.venv/bin/python scripts/pdl_retention_campaign/summarize_campaign.py \
  --config scripts/pdl_retention_campaign/campaign.json
```

## Method and controls

Reuse unchanged `scripts/run_split_benchmark.py`, `scripts/unfused-blockscaled/run_split_benchmark.py`, and `scripts/trtllm_nvfp4_reference/run_trtllm_benchmark.py`. The exact 13-token grid is `1,2,4,8,16,32,64,128,256,512,4096,8192,16384`. Ten warmups, 100 cold-L2 CUDA-graph CUPTI iterations, native medians, normal fresh AUTO, single-GPU simulated EP8/TP1, H7168/I2048/E256 with32 local experts/top-k8. Initial quantization, host allocation, compile/tune and communication are outside timed graph replay; routed preparation is inside. Per-tensor/unfused CuTe only; no W4A16, fused CuTe, CAKE or per-token expansion of this campaign. TRT retains its native finalize. Exclude only1/2 from geometric means: eight decode points, three prefill points and11 overall.

The launcher pins observer/source hashes, unchanged benchmark/timer/tuner source, clean production, project-owned Git metadata, shared native-data location and unchanged native source trees. Native header inputs are the actual `flashinfer/data/{cccl,cutlass,spdlog}` roots used by `jit/env.py`, verified against the candidate's gitlinks with clean target content and no parent-directory Git ascent. The data `csrc/include` targets must have identical clean Git trees to the candidate. Unused gitlinks such as NIXL are recorded, not initialized; no distributed work is included. It preserves `cache/candidate-442` for native JIT. CuTe compiler caches are separate per exact commit and format, reused only for that source's repeats. Diagnostic `CUTE_DSL_KEEP` and `CUTE_DSL_DUMP_DIR` are removed from child environments; KEEP would disable normal disk-cache reuse. Compilation options are unchanged. AUTO file loading stays off; saved winner caches are evidence only. Experimental import aliases are not presumed interchangeable with canonical imports.

Both one- and two-CTA cluster tactics remain available. One CTA per SM is not a ban on a two-CTA cluster spanning two SMs. No geometry, launch grid, stage, register, timing or tuner policy changes occur in the outer runner. Source and cache provenance is checked before and after each arm. Prerequisites bind the execution digest, immutable config, source identity and GPU assignments. Optimized Python is rejected because it disables assertion guards. Existing output directories are never overwritten.

The native observers save full-precision medians, logs, routing histograms and all per-token AUTO snapshots, **not the100 individual samples**. The final verifier checks all182 rows, cache hashes, chronology, stable GPU UUIDs and matching native routing histograms, then reports `sqrt(C1*C2/(A1*A2))` and `sqrt(T1*T2/(A1*A2))`. This is not a significance claim from two repeats.

## Completed independent checks and cost evidence

[pair-archive-verification.json](pair-archive-verification.json), regenerated by [verify_pair_archives.py](verify_pair_archives.py), verifies both preceding archives without changing them: every archive member/extracted hash, pinned source and helper, exact-output gate, all 3,600 samples per archive and recomputed medians/ratios.

- Producer-drain versus aab: T4 **1.05467845×**, T16384 **0.99468059×**.
- Cache pair versus adcc: T4 **0.99226032×**, T16384 **0.99521490×**, unretained.

[COST_EVIDENCE.md](COST_EVIDENCE.md) records actual prior logs: previously exercised CuTe sweeps took about15–22 seconds per13-point format; native TRT's artifact-reusing repeat took41.750 seconds, while its first build/download-bearing sweep took405.567 seconds. Those are observer-loop costs, not compilation-only estimates. New canonical-source compilation and three-way CPU contention are not separately measured, so no exact new-campaign wall-time promise is justified. The runner records child process elapsed time without changing the benchmark loop.
