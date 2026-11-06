### Kimi K3 distributed split W4A16 performance

The complete current production patch improves **1.031796×** overall (**3.180% geometric speedup**) and **1.118513×** on prefill. Decode is **1.001039×** and changes direction between repeats. T4 regresses in both repeats (**0.933237×**); all three prefill rows improve in both. These measurements retain that tradeoff and do not imply a uniform gain.

- **Measured sources:** before `316faec37a4706a2ecc7d46265087f8190b40baa`; after `6e070a25f6cdd3c07c715590dd2b0554aaecda0c`. This compares the complete current production patch, including dynamic N, SiTU arithmetic alignment and deterministic-finalizer rounding. The subsequent dense-reference/test change at `eb784bbb14623995c4110217c826f4b724e647bf` leaves production source byte-identical; timing remains attributed to the measured after revision.
- **Environment:** eight NVIDIA B300 SXM6 AC GPUs on one C2 node, `nvcr.io/nvidia/pytorch:26.05-py3`; Python 3.12.3; Torch `2.12.0a0+5aff3928d8.nv26.05`; CUDA runtime 13.2/system nvcc 13.2.78; imported CuTe DSL 4.7.1; CUPTI Python 13.4.0/library package 13.4.58. The campaign uses the project-local NCCL 2.30.7 library directory. Actual runtime metadata and GPU/topology snapshots are retained with each sweep.
- **Workload:** native `benchmarks/bench_cute_dsl_moe_distributed.py --model kimi-k3 --parallel-modes ep --variants w4a16`; H3584/I3072, 896 experts, top-k16, SiTU gate/linear scales 4/25, routed scaling 1.0. Real EP8/TP1 gives 112 local experts per GPU. BF16 activations/output and NVFP4 weights with FP32 accumulation. Token counts are global: each rank starts with `T // 8 + (rank < T % 8)` tokens, including empty ranks at the smallest sizes.
- **Scope:** timed NVLink one-sided dispatch, activation packing, local split FC1/SiTU/FC2, deterministic unfused finalize and return combine. CPU sigmoid/top-k routing is precomputed outside timing. Input/weight preparation, allocation, JIT, autotuning and graph construction are also untimed. This is the synthetic routed-expert core, excluding outer projections, shared experts, router GEMM, attention and full-model serving. The previous single-GPU simulated-EP8 measurements have a different communication/routing scope and remain separate.
- **Timing/control:** before R1 → after R1 → after R2 → before R2 (ABBA), with independent native AUTO tuning in each fresh eight-rank process group. Ten warmups, 100 cold-L2 CUDA-graph CUPTI samples per row, PDL enabled, timer fallback rejected. Per replay, the native helper takes the maximum of the eight rank-local CUPTI activity spans; the reported latency is the median of those 100 maxima. It is not a maximum of rank medians or a sum of kernel durations. Saved AUTO caches are recorded after timing and are not loaded by the primary runs.
- **Seeds:** native weights `1000 + rank`, activations `42 + rank`, global router logits 137 and routing bias 911. Identical native input-generation source and configuration are used in both arms.
- **Grid/metric:** `1,2,4,8,16,32,64,128,256,512,4096,8192,16384`. Only T1/T2 are excluded from retention; T4 is included. Row speedup is `sqrt((Before R1 × Before R2)/(After R1 × After R2))`. Overall is the geometric mean over the remaining 11 rows; decode uses T4–512 (eight rows), and prefill uses T4096/T8192/T16384. No row minima, cross-arm sample pooling or diagnostic substitutions.

All four absolute median columns are in microseconds; ratios use unrounded native sample medians.

| Global tokens | Before R1 (µs) | Before R2 (µs) | After R1 (µs) | After R2 (µs) | R1 speedup | R2 speedup | Paired speedup |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1* | 89.472500 | 89.296500 | 91.040500 | 87.808500 | 0.982777× | 1.016946× | 0.999715× |
| 2* | 97.072500 | 103.009000 | 96.113000 | 108.769000 | 1.009983× | 0.947044× | 0.978007× |
| 4 | 123.505000 | 131.106000 | 130.545000 | 142.417500 | 0.946072× | 0.920575× | 0.933237× |
| 8 | 162.033000 | 158.402000 | 161.473000 | 160.145000 | 1.003468× | 0.989116× | 0.996266× |
| 16 | 180.273000 | 180.593500 | 169.761500 | 178.481500 | 1.061919× | 1.011833× | 1.036574× |
| 32 | 252.610000 | 245.154000 | 245.234000 | 250.883000 | 1.030077× | 0.977165× | 1.003272× |
| 64 | 329.603000 | 334.356000 | 327.491500 | 332.179500 | 1.006447× | 1.006552× | 1.006500× |
| 128 | 383.812000 | 388.389000 | 381.763000 | 385.075000 | 1.005367× | 1.008606× | 1.006985× |
| 256 | 427.874500 | 422.916000 | 408.483500 | 418.821000 | 1.047471× | 1.009777× | 1.028451× |
| 512 | 433.315500 | 436.182000 | 432.996000 | 436.101500 | 1.000738× | 1.000185× | 1.000461× |
| 4096 | 773.671000 | 776.871000 | 676.374000 | 682.967000 | 1.143851× | 1.137494× | 1.140668× |
| 8192 | 1444.335000 | 1442.107000 | 1221.305000 | 1225.019000 | 1.182616× | 1.177212× | 1.179911× |
| 16384 | 2379.889000 | 2364.713500 | 2307.601000 | 2256.029000 | 1.031326× | 1.048175× | 1.039716× |

*T1/T2 are reported but excluded from retention. All other rows, including T4, enter the overall aggregate.*

| Aggregate | Tokens | R1 | R2 | Paired |
| --- | --- | ---: | ---: | ---: |
| Overall | 4–512, 4096, 8192, 16384 (11 points) | 1.039828× | 1.023825× | 1.031796× |
| Decode | 4–512 (8 points) | 1.012152× | 0.990047× | 1.001039× |
| Prefill | 4096, 8192, 16384 (3 points) | 1.117386× | 1.119642× | 1.118513× |

T1/T2/T8/T32 change direction between repeats; only T8/T32 participate in retention. T4 loses in both repeats, and the decode aggregate is above one in R1 and below one in R2.

**Tactic interpretation:** T4096 uses identical full FC1 and FC2 tactics on all eight ranks in all four sweeps: `(M,N,K)=(256,128,256)`, cluster `(2,1)`, raster along M. Its **1.140668×** improvement is therefore observed with matching AUTO choices. Every other token row has at least one rank with a changed tactic across source arms. At T8192, baseline R1/R2 have three/one ranks using N128, while both candidate sweeps use N192 on all ranks. T16384 mixes N128/N192 and changes choices across repeats. These are normal-AUTO results, not a fixed-tactic diagnostic campaign; the current patch also changes SiTU/finalizer arithmetic, and the timed interval includes communication.

The native benchmark, its imported input-generation module and the timer are byte-identical between the two measured sources:

| Source | SHA256 in both arms |
| --- | --- |
| `benchmarks/bench_cute_dsl_moe_distributed.py` | `9f4cab8d6b105a98aaddc2d3221f2ebe42e12cfbfc17faa6494745e961cff422` |
| `benchmarks/bench_moe_deepseek.py` | `9561d42c798eecbdbc2e3edd31889c0475ff1a56dcd6be7b164ffa7068a86371` |
| `flashinfer/testing/utils.py` | `bf532ebc0b82d3551a09bea6bc96017b838bcb52d461f9a5d19573ac9766ac34` |

<details>
<summary>Native distributed reproduction command and evidence</summary>

From independent checkouts of the two measured revisions in the environment above, run this command once per sweep in ABBA order, changing `repo` and `label` for each arm. Use a fresh Python process and distinct output file each time. `FLASHINFER_AUTOTUNER_LOAD_FROM_FILE=0` keeps saved AUTO selections out of primary measurements.

```bash
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export TRTLLM_ENABLE_PDL=1 FLASHINFER_DIST_AWARE_AUTOTUNE=0
export FLASHINFER_AUTOTUNER_LOAD_FROM_FILE=0 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1
export FLASHINFER_WORKSPACE_BASE=/root
# Use the pinned Python environment from the setup section.
export K3_NCCL_DIR=/absolute/path/to/project/ep-nccl-2.30.7
python -m pip install --no-deps --target "$K3_NCCL_DIR" \
  'nvidia-nccl-cu13==2.30.7'
export LD_LIBRARY_PATH="$K3_NCCL_DIR/nvidia/nccl/lib:${LD_LIBRARY_PATH:-}"
repo=/absolute/path/to/baseline
label=baseline-r1
output=/absolute/path/to/fresh/k3-results
mkdir -p "$output"
cd "$repo"
export PYTHONPATH="$PWD"
python -m torch.distributed.run \
  --nnodes=1 --nproc-per-node=8 \
  --master-addr=127.0.0.1 --master-port=29538 \
  benchmarks/bench_cute_dsl_moe_distributed.py \
  --model kimi-k3 --num-gpus 8 --parallel-modes ep --variants w4a16 \
  --timing cupti --cuda-graph --no-fused-finalize --precomputed-routing \
  --warmup 10 --iters 100 --log-timing-samples --verbose \
  --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 \
  > "$output/$label.log" 2>&1
```

The recorded campaign uses an observation wrapper around this unchanged native entry point. Outside its measured call, the wrapper records exact module paths, source hashes, runtime versions and per-rank/per-row AUTO cache files. Checkout-specific native build-cache restoration avoids recompilation when switching arms; it does not load AUTO selections. The wrapper requires CUPTI and refuses to overwrite its rank metadata. It does not change the native timer, input generation, routing or kernels.

**Evidence audit:** all four sweeps exit zero, with 32 complete rank receipts, 416 verified tactic-cache hashes, all 52 absolute medians and all 5,200 finite positive rank-MAX samples. Reconstructed medians agree with native CSV rounding within `0.5e-6 ms`. Full commits, model/options, actual imported versions and source hashes match the recorded protocol. Production hashes match their pinned Git objects; all other recorded runtime/benchmark sources match across arms. Baseline checkouts are clean; the only candidate checkout differences are the three exact vendor-header symlinks to baseline. A runtime path/HEAD capture confirms the expected pinned vendor checkouts. Raw logs, timing vectors, metadata and caches remain preserved; no failed or partial observation is substituted into the table.

The observer records the imported CuTe path and runtime version 4.7.1. Its filtered distribution-ownership flag does not identify the implementation package and is not used as ownership proof. AUTO-disabling environment settings are evidenced by the archived launch script rather than an independent runtime environment snapshot.

</details>

Two sweeps provide a consistency check, not statistical significance. Independent autotuning can change tactics. These K3 results remain separate from the earlier 132 recorded medians and do not replace any existing observation; no MegaMoE or fused-finalize performance result is included in this campaign.
