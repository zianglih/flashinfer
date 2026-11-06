# One-layer GLM-5 routed-MoE operand byte model

## Result and intended scope

For **the routed experts of one GLM-5 MoE layer**, retaining BF16 inputs for
FC1 and FC2 increases the modeled combined weight-plus-input bytes by only
**0.0581%–0.1275%** at 4–64 input tokens under the assumptions below.

This is logical routed-GEMM operand accounting, **not measured HBM traffic**,
not a full-model footprint, and not a latency prediction. There is no TP/EP
partition in the calculation. The shared expert, attention, router, output
writes, and other layers are outside this precision comparison.

## Verified architecture dimensions

The [official GLM-5 configuration](https://huggingface.co/zai-org/GLM-5/blob/c183ef8c61faee82855eca1ed9bb3a9a7ce3b0b2/config.json)
was fetched from `zai-org/GLM-5` on 2026-10-07. The returned `x-repo-commit` and
resolved download URL both pin revision
`c183ef8c61faee82855eca1ed9bb3a9a7ce3b0b2`.

| Quantity | Configuration field | Value |
|---|---|---:|
| Hidden width H | `hidden_size` | 6144 |
| One routed expert's intermediate width I | `moe_intermediate_size` | 2048 |
| Routed experts E | `n_routed_experts` | 256 |
| Distinct experts selected per token k | `num_experts_per_tok` | 8 |
| Shared experts, excluded here | `n_shared_experts` | 1 |

The official configuration declares BF16. We use it to establish **shapes** and
apply the blog's hypothetical NVFP4 weight/activation representation to those
shapes; the config does not establish that the official checkpoint itself stores
NVFP4 weights. Dense `intermediate_size=12288` is not the routed expert width.
The total number of layers is irrelevant to this one-layer calculation.

Saved source: `evidence/glm5-official-config.json`; SHA256
`308d3ceebe7bd9c2246d20550d5b793098dd03838d1e504f8236063ae152bcae`.
The download provenance is in `evidence/glm5-official-config-provenance.json`.

The earlier kernel benchmarks in this effort use H7168/I2048/E256/top-k8, a
different hidden width. Do not silently present this H6144 example as their
measured traffic. The selected trace's 24 FC1 K256 tiles are compatible with
H6144, but do not independently recover its complete model configuration.

## Routing expectation

Assume each of N tokens independently chooses a uniformly random **set of k
distinct experts**, without replacement within that token. A particular expert
is absent from one token's selected set with probability

```text
C(E - 1, k) / C(E, k) = 1 - k/E.
```

It is absent from all N sets with probability `(1-k/E)^N`. Summing the inclusion
indicators over E experts gives

```text
U(N) = expected distinct activated experts
     = E × [1 - (1-k/E)^N]
     = 256 × [1 - (31/32)^N].
```

Do **not** use `E × [1 - (1-1/E)^(Nk)]`; that describes Nk independent draws
with replacement and permits duplicate expert choices within a token.

These are toy routing assumptions, not an observed routing distribution. Real
expert preference and correlation between token routes change distinct coverage.
For independent tokens with fixed nonuniform expert marginals, uniform marginals
maximize expected distinct coverage; cross-token balancing/correlation requires
separate treatment.

## Weight bytes: one copy per activated expert

An expert's fused FC1 contains gate and up weights with shape `(2I, H)`, and
FC2 has shape `(H, I)`. Together they contain `3HI` weight values. Count:

- Packed E2M1 payload: `3HI / 2` bytes.
- One E4M3 scale per 16 values: `3HI / 16` bytes.
- One FP32 second-level scale for fused FC1 and one for FC2: 8 bytes.

```text
Wexpert = 3HI × (1/2 + 1/16) + 8
        = 18,874,368 + 2,359,296 + 8
        = 21,233,672 bytes
        = 20.25 MiB + 8 bytes.

Expected weight bytes W(N) = U(N) × Wexpert.
```

The **8-byte convention** matches the fused kernel interface:
[FC1/FC2 weights, block scales, and alpha tensors](https://github.com/zianglih/flashinfer/blob/7ca3eb567a2400df70579d55e9bc717ea1784b0c/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py#L440),
[the two weight shapes and 16-value block scale views](https://github.com/zianglih/flashinfer/blob/7ca3eb567a2400df70579d55e9bc717ea1784b0c/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py#L703),
and per-expert [FC1 alpha](https://github.com/zianglih/flashinfer/blob/7ca3eb567a2400df70579d55e9bc717ea1784b0c/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/epilogue.py#L515)
and [FC2 alpha](https://github.com/zianglih/flashinfer/blob/7ca3eb567a2400df70579d55e9bc717ea1784b0c/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/epilogue.py#L338).

A representation with separately scaled gate, up, and down tensors would count
12 bytes instead. That adds only `4U(N)` bytes to both precision totals, leaving
the displayed ratios unchanged at six decimal places. This alternative is a
representation convention, not a claim that independent gate/up global scales
can always be merged without conversion into one fused FC1 alpha.

## Activation bytes: FC1 and FC2 inputs only

Count `R=Nk` routed input uses at each GEMM boundary:

- FC1 reads R H-wide rows. Gate/up are fused, so do not count two separate H-wide
  FC1 input operands.
- FC2 reads R I-wide rows after activation.
- NVFP4 representation has 0.5 payload byte/value, one E4M3 byte/16 values, and
  one 4-byte FP32 second-level activation scale per row at **each** boundary.
- BF16 uses two bytes/value and no quantization metadata.

```text
A4_fc1(N) = Nk × (H/2 + H/16 + 4)
A4_fc2(N) = Nk × (I/2 + I/16 + 4)
A4(N)     = Nk × [(H+I) × 9/16 + 8] = 36,928 N bytes.

A16_fc1(N) = 2NkH
A16_fc2(N) = 2NkI
A16(N)     = 2Nk(H+I) = 131,072 N bytes.
```

The FC1 count is **routed input uses**, not NH unique activation storage. The
same token input is used by k experts; implementations may physically replicate
it, read it repeatedly, or obtain cache reuse. This model counts it once at each
expert's GEMM-input boundary. The per-row FP32 scales are an explicit recipe
assumption, not evidence that every benchmark arm used a per-token override.

Including NVFP4 metadata makes BF16's activation-input bytes approximately
**3.5494×**, rather than exactly 4×, the NVFP4 representation in this example.
Four remains the payload-bit-width ratio.

## Requested table

KiB = 1024 bytes; MiB = 1,048,576 bytes. Each input cell shows **FC1 + FC2 = sum**.
Totals include the same expected NVFP4 weight bytes plus the respective input
bytes. The last column is a **ratio of expected totals**, not the expectation of
a per-routing-sample ratio.

| Tokens N | Usage | NVFP4 input KiB, FC1 + FC2 | BF16 input KiB, FC1 + FC2 | Expected distinct experts | Expected NVFP4 weight MiB | W4A4 total MiB | W4A16 total MiB | W4A16 / W4A4 |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 4 | Decode | 108.125 + 36.125 = 144.250 | 384.000 + 128.000 = 512.000 | 30.53 | 618.253 | 618.394 | 618.753 | 1.000581× (+0.0581%) |
| 8 | Decode | 216.250 + 72.250 = 288.500 | 768.000 + 256.000 = 1024.000 | 57.42 | 1162.772 | 1163.054 | 1163.772 | 1.000618× (+0.0618%) |
| 16 | Decode | 432.500 + 144.500 = 577.000 | 1536.000 + 512.000 = 2048.000 | 101.96 | 2064.735 | 2065.298 | 2066.735 | 1.000696× (+0.0696%) |
| 32 | Decode | 865.000 + 289.000 = 1154.000 | 3072.000 + 1024.000 = 4096.000 | 163.31 | 3307.107 | 3308.234 | 3311.107 | 1.000868× (+0.0868%) |
| 64 | Decode | 1730.000 + 578.000 = 2308.000 | 6144.000 + 2048.000 = 8192.000 | 222.44 | 4504.462 | 4506.716 | 4512.462 | 1.001275× (+0.1275%) |
| 128 | Decode | 3460.000 + 1156.000 = 4616.000 | 12288.000 + 4096.000 = 16384.000 | 251.60 | 5094.925 | 5099.433 | 5110.925 | 1.002254× (+0.2254%) |
| 256 | Decode | 6920.000 + 2312.000 = 9232.000 | 24576.000 + 8192.000 = 32768.000 | 255.92 | 5182.471 | 5191.487 | 5214.471 | 1.004427× (+0.4427%) |
| 512 | Decode | 13840.000 + 4624.000 = 18464.000 | 49152.000 + 16384.000 = 65536.000 | 256.00 | 5184.002 | 5202.033 | 5248.002 | 1.008837× (+0.8837%) |
| 4096 | Prefill | 110720.000 + 36992.000 = 147712.000 | 393216.000 + 131072.000 = 524288.000 | 256.00 | 5184.002 | 5328.252 | 5696.002 | 1.069019× (+6.9019%) |
| 8192 | Prefill | 221440.000 + 73984.000 = 295424.000 | 786432.000 + 262144.000 = 1048576.000 | 256.00 | 5184.002 | 5472.502 | 6208.002 | 1.134399× (+13.4399%) |
| 16384 | Prefill | 442880.000 + 147968.000 = 590848.000 | 1572864.000 + 524288.000 = 2097152.000 | 256.00 | 5184.002 | 5761.002 | 7232.002 | 1.255338× (+25.5338%) |

For example, N=4 touches 30.53 distinct routed experts on average. Their modeled
weights occupy 618.253 MiB, while the two BF16 GEMM inputs account for 0.5 MiB.
The weight bytes are about **1,236.5× the BF16 input bytes** in this example;
this ratio falls to about 563.1× at N=64 as expert reuse increases.

Decode rows 4–512 add 0.058–0.884% to modeled input-plus-weight bytes; prefill rows 4096–16384 add 6.902–25.534%. Token counts/classifications match #5019; its H7168 kernel workload differs from this GLM-5 H6144 byte model.

## Interpretation and limits

- Only one routed-MoE layer is counted. There is no multiplication by model depth.
- One copy of each activated expert's weights is counted, assuming reuse across
  the tokens assigned to that expert in this invocation. Cache persistence across
  invocations, tile-level rereads, and fragmented scheduling can change HBM bytes.
- The shared expert, router, attention/KV, outputs and intermediate **writes**,
  quantizer source reads, temporary buffers, routing metadata, padding, and all
  communication are excluded. This is not total layer traffic in a profiler.
- Neither TP nor EP is modeled. The result is not a rank-local or per-GPU byte
  estimate and cannot be used directly for a rank-local roofline.
- This illustrates why retaining BF16 inputs need not greatly increase the
  dominant logical operand volume. It does not establish the measured pipeline
  bottleneck, bandwidth utilization, actual HBM transactions, or a speedup.
- Real routing skew/correlation can yield different expert counts. Expert-cache
  hits can reduce weight reads enough that activation traffic becomes more
  important. Larger batches also amortize weights over more activation rows.

Suggested compact caption:

> One-layer GLM-5 routed-expert byte model, before TP/EP partitioning. Each token
> independently selects eight distinct experts uniformly from 256. We count
> each activated expert's NVFP4 weights once and the FC1/FC2 input rows once per
> route, including quantization scales. Shared experts, other layer operations,
> output writes, and cache/transport effects are excluded; these are modeled
> operand bytes, not measured HBM traffic.

Suggested main-text takeaway:

> For four GLM-5 tokens, the routed experts contribute roughly 618 MiB of packed
> weights and scales in this model. Their FC1 and FC2 inputs together occupy just
> 0.5 MiB in BF16. Across 4–64 tokens, keeping those inputs in BF16 increases the
> modeled weight-plus-input total by only 0.06%–0.13%.

## Reproduction

Run `python3 traffic_model.py` from this effort root. The script uses 60-digit
decimal arithmetic and writes `traffic_model.json` plus `traffic_model.csv`.
JSON records the dimensions, metadata conventions, assumptions, exclusions, raw
bytes, MiB values, and ratio of expected totals. No HAI source files were changed
by this audit. An independent Decimal-based check by the draft reviewer matched
the results.
