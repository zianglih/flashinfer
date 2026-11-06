# Capacity-derived operand depth for independent SF readiness

**Closed, unretained.** This fresh experiment compares five operand stages against the frozen four-stage compact-SFB + physical-N16 + distributed-TMA + independent-SF-readiness source. It does not compare directly with production98fd and does not compound ratios measured on another GPU. Production and the source owner's copy remain unchanged.

## Source and scope

- Base Git commit: `98fd3566b5f945c100f48cddacf25deb2432cbc2`.
- Actual control: `../../flashinfer-sf-readiness-review`, core `0f570a27aec49f767b414b7e4fcc163433598b5d344cc8b86fb4114d9802f9d1`.
- Actual candidate: `../../flashinfer-sf-readiness-stage5-review`, core `c849d5aa71d6f33646c97868b5ba6374e7092997e384f8557288b217e55add84`.
- Both use identical compact epilogue utils `e14d3300a97fa508b0039065a6b29b876a0e14d20a5456ef18bf0a662c168274`.
- [manifest.json](manifest.json), [stage-only patch](stage-refinement.patch), and [full delta from98fd](candidate-vs-98fd.patch) pin the source. The manifest's `gpu_execution:false` describes its initial build step; [summary.json](summary.json) records subsequent completed execution.

The eligibility remains the owner's generated-FP4 NVFP4 FC1 N16 compact-publisher contract. Other phases/formats/layouts retain their existing depth. The selector uses static stage widths/extents, SM100 capacity and complete barrier/alignment accounting; it has no token-count or model-K dispatch. A compile-time actual-SharedStorage-size guard checks the estimate. The kernel body is byte-identical to the four-stage control: all roles, math, SF publication, completion operations and tails are unchanged. No API, preparation, MegaMoE, register budget or cache policy change.

A/B payload and SFA/SFB source rings use the derived depth5. The independent published-SF TMEM ring remains2. Payload slots release after MMA; shared SF-source slots release after SF copy completion. Producer/source/MMA states continue across persistent work tiles, wrapping at their own depths; no five-to-two divisibility requirement exists. The source and payload producer tails still drain their respective empty phases, and the publisher drains the two-slot TMEM ring.

## Capacity proof

Native per-stage allocation is A32768 + B4096 + SFA4096 + compactSFB2048 =43008B. The full storage prefix counts A/AB/SFA/relay full+empty arrays (8 entries per stage), accumulator barriers, TMEM holding,128-byte alignment,512-byte epilogue scratch, and the deallocation barrier/alignment. It is1024B at both depths.

|Depth|Operand bytes|Prefix bytes|Total bytes|Headroom under232448B|
|---:|---:|---:|---:|---:|
|4|172032|1024|173056|59392|
|5|215040|1024|216064|16384|
|6|258048|1152|259200|Does not fit|

The old scratch-capacity estimator omitted the additional SFA barrier array. The candidate counts all8 entries/stage; the fixed FC1 scratch was unaffected by that old estimate. [CPU receipt](cpu-capacity.json) covers26 wrap/tail cases including zero work and fewer-than-stage-count loops, and confirms kernel-body identity. [Capacity audit](CAPACITY_AUDIT.md) records the installed DSL source and lifetime caveats. This CPU model is not a GPU memory-ordering proof or sanitizer result.

This is distinct from the rejected [physical-B16/five-stage variant](../small_b_experiment/README.md): that source retained C32 and the original joint readiness/SF publication; this control already has compact SFB, C16, and independent SF readiness. The present comparison isolates only operand depth relative to that control.

## Bounded actual-source diagnostics

GPU4 on C1 `fi-w4a4-narrow-1025`, nodeB200-92, B200 UUID `GPU-9b1e25f5-48e6-f126-6d93-160b7ea7dd32`; image `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2.78, CuTeDSL4.7.1, CUPTI13.4.0. Native JIT epoch remains candidate442. A private CuTe cache separates this experiment. All remote shells source `scripts/recovery442/env_candidate.sh`.

Actual `bench_moe_deepseek` seed42 inputs: H7168, I2048, top-k8,256 experts/32 local, NVFP4 per-tensor, unfused finalize; fixed N16/M128 one-CTA tactic. T32 exact smoke, then T32/T128 adjacent ABA/BAB full chain and FC1/FC2 wrappers:10 warmups,100 cold-L2 CUDA-graph/CUPTI samples per arm. Same native input tensors are reused within each process. Full-chain sorting can change within-expert permutation; isolated phases retain captured routing metadata. FC1 includes regular preparation; phase times are nonadditive. Observer-held intermediate allocations are disabled for full-chain timing. All source/input/output hashes and initialized phase output/SF bytes are checked pre/post timing.

|Tokens|Whole-chain control/candidate|FC1 including prep|Unchanged FC2|
|---:|---:|---:|---:|
|32|0.989312×|0.985468×|1.001060×|
|128|0.996202×|0.991301×|1.000562×|

[RESULTS.md](RESULTS.md) contains every arm median. Ratios are the geometric mean of three control medians divided by the geometric mean of three candidate medians. All3 successful processes,6 paired phase checks,36 arms and3600 samples verified. The refinement loses roughly1.1%/0.4% whole-chain and1.5%/0.9% FC1. No direct production comparison or further runtime matrix is warranted for this negative result.

[Codegen receipt](codegen-summary.json) verifies all12 binaries. Both arms use FC1 320threads/50registers and FC2 288threads/90registers, with static shared1024B and zero local/stack bytes. PTX shows five payload-full and five payload-empty barriers in the candidate versus four in the control. The source model and successful actual-size guard establish capacity; no new driver occupancy profile was run. The prepared `compile_resources.py`/`load_actual.py` are preserved but were **not executed**.

No failed GPU execution occurred. No sanitizer, wider dtype/per-token/tail numerical matrix, primary AUTO campaign or TRT comparison was run. All files remain unstaged. The archive's final process query confirms GPU4 has no active process.

## Reproduction and archive

Existing CPU verification:

```sh
python3 scripts/sf_readiness_stage5_experiment/check_capacity.py
python3 scripts/sf_readiness_stage5_experiment/summarize.py
```

The already-executed remote commands were:

```sh
cd /workspace/flashinfer-w4a4-split-dynamic-n
source scripts/recovery442/env_candidate.sh
.venv/bin/python scripts/sf_readiness_stage5_experiment/run_remote.py --mode smoke
.venv/bin/python scripts/sf_readiness_stage5_experiment/run_remote.py --mode screen
```

The runners refuse to overwrite existing receipts. Exact commands, timeout300s, environment, source snapshots, every sample, PTX/CUBIN/SASS and resource dumps are preserved in [raw.tar.gz](../../evidence/sf-readiness-stage5/raw.tar.gz),1999899B, SHA256 `424ee773400b0cd83209697b8b0a5f6b8ad3738d9d51dda2ee4e261cdf929f04`. [Archive receipt](../../evidence/sf-readiness-stage5/archive-sha256.json) records the managed-h collection command. The local artifact manifest also pins CPU audits and helpers added after remote collection.
