# Kimi K3-shaped EP8 routed-core source audit

Audited 2026-10-08. The four-arm campaign uses FlashInfer
`b730d5f6f5929fe666b24b466144a57f5587ba4b`, the same source pin as the completed
GLM-shaped campaign. This is an **NVFP4 Kimi K3-shaped routed-expert benchmark**,
not native-checkpoint serving. The saved K3 checkpoint configuration declares
compressed-tensors MXFP4 weights with group size 32; the synthetic benchmark
instead quantizes shared BF16-generated weights to NVFP4 once for all arms.

## Geometry and scope

| Field | Value |
|---|---:|
| Model hidden width | 7168 |
| Routed latent width D | 3584 |
| Expert intermediate width E | 3072 |
| Routed experts N | 896 |
| Top-K | 16 |
| EP / expert TP | 8 / 1 |
| Experts per rank | 112 |
| FC1 logical weights per expert | `[2E,D] = [6144,3584]` |
| FC2 logical weights per expert | `[D,E] = [3584,3072]` |
| Groups / selected groups | 1 / 1 |
| Routed scaling factor | 1.0 |
| Activation | gated SiTU, gate scale 4.0, linear scale 25.0 |

The full model's routed path is:

```text
x[7168] -> latent down[3584] -> routed experts + weighted combine[3584]
        -> RMSNorm(eps=1e-5) -> latent up[7168]
```

The latent down/up matrices are shared per layer and applied once per original
token, not once per selected expert. RMSNorm follows routed combination. The
two shared experts operate at width 7168 and combined intermediate width 6144,
outside this latent routed path. The benchmark excludes both latent projections,
the latent RMSNorm, shared experts, and the router GEMM. It includes native routed
staging/communication, FC1, activation, FC2, deterministic combination, runtime
scale copies, and W4A4 activation quantization. Route generation, preparation,
compilation, tuning, graph capture, and L2 flushing remain outside timing.

Useful routed GEMM work is still `6*T*K*D*E = 1,056,964,608*T` FLOPs because
SiTU has gate and up projections. The EP8 achieved rate is that numerator divided
by `pooled_median_ms * 1e9`; it is an aggregate eight-GPU rate. Expected distinct
experts under independent uniform routing are `896 * [1 - (55/56)^T]`; this is a
weight-footprint reference, not another FLOP multiplier. The benchmark records
actual prepared routes and expert/rank occupancy separately.

## Activation and routing

For gate g and linear branch u:

```text
SiTU(g,u) = [4*tanh(g/4)*sigmoid(g)] * [25*tanh(u/25)]
```

The linear branch uses soft tanh saturation, not a hard SwiGLU clamp.
K3's `gemm1_alpha=4` maps to `situ_beta`, and `gemm1_clamp_limit=25` maps to
`situ_linear_beta`; `gate_up_clamp` remains unset.

K3 uses sigmoid scores plus correction bias for top-16 selection, gathers the
uncorrected sigmoid values as route weights, and renormalizes them. With one
group and one selected group, all 896 experts compete. The pinned native
`fused_topk_deepseek` frontend rejects this configuration: its guard requires
`topk_group * n_group >= top_k`, which is false for `1 * 1 < 16`. The first C1
precheck stopped at that guard before collecting any measurements. Its separate
failed-attempt log is retained in `runs/kimi-k3-ep8/failed-attempt-1-c1`.

The benchmark therefore precomputes K3 routing on CPU before tuning, capture,
or timing. The native fixed-seed GPU logits and bias are copied to CPU FP32;
`sigmoid(logits) + bias` selects experts through a stable descending sort, so
ties prefer lower expert IDs. Gathered **uncorrected** sigmoid scores are divided
by their row sum plus `1e-20` and multiplied by the routed scale of 1.0. IDs and
weights are copied back into the native device buffers as INT32 and FP32.
`--precomputed-routing` is mandatory, so this preparation cannot enter the timed
forward. No artificial expert grouping is introduced.

These fixed random inputs remain synthetic, not learned K3 routes. CPU sigmoid
rounding and the explicit tie rule need not match a hypothetical supported GPU
router bit for bit; all four arms use the same prepared IDs and route weights.
The config's separate sampling `top_k=50` is unrelated to MoE top-K.

## Native b730 support and benchmark changes

No kernel changes are needed for this activation. Pinned source entry points:

- `flashinfer/fused_moe/api.py:313`: typed `SiTU(gate_scale, linear_scale,
  clamp_limit)`; the default scales are canonical K3 values.
- `flashinfer/fused_moe/runners.py:426`: CuTe lowers typed SiTU to its gated
  activation ABI using `ActivationType.Swiglu`, non-null `situ_beta`, and
  `situ_linear_beta`. The enum spelling does not mean ordinary SwiGLU is used.
- `flashinfer/fused_moe/cute_dsl/fused_moe.py:296,680`: both the NVFP4-activation
  function and BF16-activation wrapper accept these SiTU parameters.
- `flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/frontend.py:55`: W4A16 Mega
  accepts `activation="situ"`, `situ_beta`, and `situ_linear_beta`; it rejects
  simultaneous SwiGLU parameters or a gate/up hard clamp.
- `flashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/shim/nvfp4.py:112`:
  W4A4 Mega exposes the same activation contract.

The new patcher modifies only the two benchmark Python files already audited
for the GLM campaign:

1. Set `DeepSeekConfig` to the routed geometry above and add explicit
   `model_hidden_size`, `activation`, `situ_beta`, and `situ_linear_beta` fields.
2. In `_distributed_moe_config`, pass
   `activation=SiTU(gate_scale=CFG.situ_beta, linear_scale=CFG.situ_linear_beta)`.
   This shared factory covers both split variants.
3. In `_benchmark_distributed_megamoe`, pass `activation=CFG.activation`,
   `situ_beta=CFG.situ_beta`, and `situ_linear_beta=CFG.situ_linear_beta` to the
   selected native Mega config class. This covers both Mega variants.
4. Retain shared gate/up weight preparation: SiTU is gated, so `[gate,up]`
   canonical halves and split `[up,gate]` interleaving remain appropriate.
5. Replace the unsupported grouped-router setup with the CPU single-group
   preparation above and require precomputed routing.
6. Record routes outside timing, with activation, routed-core scope, and the
   explicit CPU routing policy; retain PDL and no fused TMA/FC2 reduction guards.
   W4A16 Mega's deterministic persistent combine remains active.

Kernels, timing functions, packed-weight generation, seeded input generation,
and the native numerical comparison remain unchanged. Routing configuration
and route generation change explicitly for the K3 policy. Both split and Mega
reference paths now execute SiTU because their effective configuration changes
together.

## Metadata and validation

Workload metadata and every routing observation carry:

```json
{
  "activation": {"name": "situ", "gate_scale": 4.0, "linear_scale": 25.0, "clamp_limit": null},
  "model_hidden_size": 7168,
  "scope": "routed_expert_core",
  "excluded_operations": ["latent_down_projection", "latent_up_projection", "latent_rmsnorm", "shared_experts", "router_gemm"]
}
```

The shape metadata is `{"D":3584,"E":3072,"N":896,"K":16}`. The patcher checks
the exact original SHA256 of both input files and refuses changed or already
patched inputs. Original hashes are unchanged from the GLM audit:

- `bench_moe_deepseek.py`: `9561d42c798eecbdbc2e3edd31889c0475ff1a56dcd6be7b164ffa7068a86371`
- `bench_cute_dsl_moe_distributed.py`: `c956a0a82be282123b21dc3fe043aa95f3282d6c9bd9185d90022b6747596975`

The corrected patcher is frozen at SHA256
`289d4499c2b649904eadfe37fee9e8d52bedbc7ceae9ebea6490c1f8dfa22e35`;
the prepared distributed driver is
`2f0d704e5fa76ef12d91bc87b1d2549d3132b8069317302d38564160a810fd9f`.
Its workload metadata declares `routing_generation_modified=true` and
`routing_configuration_modified=true`, while `kernel_code_modified`,
`timing_modified`, and `reference_check_modified` remain false. Both workload
metadata and per-case routing observations carry this exact policy:

```json
{
  "name": "kimi_k3_sigmoid_bias_topk_cpu",
  "backend": "torch_cpu",
  "tie_break": "lower_expert_id",
  "scores_dtype": "float32",
  "weights_dtype": "float32",
  "n_group": 1,
  "topk_group": 1,
  "routed_scaling_factor": 1.0
}
```

CPU checks apply the patch in memory to the exact pinned sources, compile both
modified files, verify the effective activation arguments for all four arms,
and compare the native timer, reference, input, and weight-function ASTs. The
inner `run_once` and `profile_once` bodies remain unchanged. Source-drift and
reapplication refusal are checked independently.

Real CPU Torch 2.11.0 checks cover empty ranks, equal-score ties choosing IDs
0–15 with weights exactly 1/16, bias-only selection with uncorrected sigmoid
weights, and random 32×896 scores matching an independent Python sort. Each row
has 16 distinct experts; the largest FP32 row-sum error was `1.19e-7`. These
checks establish routing semantics and source wiring, not GPU correctness or
performance. The durable harness and its explicitly CPU-only result are
`validation/kimi-k3-ep8-audit/check_routing_cpu.py` and
`validation/kimi-k3-ep8-audit/routing-cpu-validation.json`. Re-run from this
project root with the existing local Torch environment:

```bash
/Users/ziangli/playground/projects/glm52-w4a16-delta-sync-c2/.venv-delta-cpu-torch211/bin/python \
  -B validation/kimi-k3-ep8-audit/check_routing_cpu.py
```

Before the full campaign, run a separate small native GPU reference check:

```bash
torchrun --master-addr=127.0.0.1 --master-port=29500 --nproc-per-node=8 \
  benchmarks/bench_cute_dsl_moe_distributed.py \
  --mode benchmark --parallel-modes ep --num-gpus 8 \
  --variants w4a4,w4a16,w4a4_megamoe,w4a16_megamoe \
  --num-tokens 32 --timing cupti --cuda-graph --precomputed-routing \
  --no-fused-finalize --megamoe-knobs auto --warmup 3 --iters 10 --refcheck
```

Native `--refcheck` compares Mega W4A16 against the same-weight split W4A16
result with `atol=rtol=1e-2`, outside timing. This is an implementation comparison,
not an independent PyTorch oracle or a W4A4 correctness test. Keep its log
separate from the two production 100-sample sweeps; no GPU result is established
by this audit.

## Model source evidence

Saved checkpoint config revision: `f831ab66814297da540d832a5235f8e904f29d06`.
Saved SGLang model source revision: `7a719e9a65e7f52b012ab37211b5f174e5d3d38d`.
Files reside in the existing independent project
`/Users/ziangli/playground/projects/glm52-kimi-k3-embedding-memory`:

- `kimi-k3-config.json:176,246`: hidden/intermediate/expert/top-K/latent dimensions;
  `:20` activation scales; `:202` native MXFP4 declaration.
- `sglang-source/kimi_k3.py:449,480`: routed expert hidden dimension and constructor;
  `:490,503` activation and routing parameters.
- `sglang-source/kimi_k3.py:603,635`: full-width shared experts and latent projections;
  `:999,1205` combination, RMSNorm, and projection order.
- `sglang-source/kimi_k3.py:2413`: layer 0 is dense; layers 1–92 use the same MoE
  geometry. Learned routing and biases can differ by layer.

Supplemental local SGLang revision
`f761074512c98028b7e9f573a4fb0bef6033ae30` supplies the explicit activation formula
at `python/sglang/srt/layers/activation.py:187` and reference routing at
`python/sglang/srt/layers/moe/topk.py:1557` in the existing
`sglang-flashinfer-w4a16-megamoe/sglang` checkout.
