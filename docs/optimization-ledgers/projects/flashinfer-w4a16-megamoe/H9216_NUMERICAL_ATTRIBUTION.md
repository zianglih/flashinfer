# H9216 fixture: shared FC1 rounding, exact split/Mega parity

The corrected split diagnostic confirms that Mega and the existing split
W4A16 kernel produce bitwise identical FC1 intermediates, per-route FC2 and
final outputs in both the original raw fixture and the separately normalized
fixture. Both implementations fail the same unchanged torch term-band assertion
on the raw fixture and pass it after scaling only FP32 FC1 globals by 1/sqrt(H).
No kernel tolerance was changed, and no split tail defect was found.

## Run and preparation contract

- Evidence: `logs/diagnostic-h9216-split-002.log`, both arm-specific
  `comparisons.json` files, and `provenance.json` in the corresponding directory.
  Complete saved `outputs.pt` tensors remain in that directory on the devbox.
- Untimed EP1 fixture: H9216, I64, 257 tokens, four experts, top-k2, every token
  routed to experts 0/1, original deterministic test seeds. BF16 input and both
  activation boundaries, separate FP32 post-MMA globals, FP32 route weights
  applied after unweighted BF16 FC2. No activation quantization or fused finalize.
- Split uses its existing fixed default tactic for both FC1 and FC2:
  M256/N128/K256, cluster(2,1), raster_along_m=True. The helper mirrors
  `benchmarks/bench_cute_dsl_moe_distributed.py::_create_shared_ep_weights`:
  exchange canonical gate/up halves to up/gate, interleave64 packed rows and
  matching SF rows, then `block_scale_interleave` and `convert_sf_to_mma_layout`.
  Globals remain separate FP32 tensors and are never folded into BF16 weights.
- The helper captures FC1 before workspace reuse, gathers using moe_sort's
  expanded-to-permuted map, and captures unweighted FC2 before final output
  reduction. It verifies all 514 route positions are unique and valid.
- Recorded source hashes: original test fixture
  `24073ba126d90f1f96c1ea2db0c1f6510d6a562c143f2940b04aada14371bab3`;
  split launcher
  `cd11e0c1c37653b0a58403de04fa31ea20ae75a6ebab1b8330e7091e32d729f7`;
  corrected helper
  `b95a9f01b2f1a34bac78d06acf884d4d017310b5e99a6d3d439e32959d1f528c`.
  The diagnostic manifest records these frontend/test identities, not every
  transitive kernel source. PyTorch is `2.12.0a0+5aff3928d8.nv26.05`.

```bash
cd /workspace/flashinfer-w4a16-megamoe
CUDA_VISIBLE_DEVICES=0 FLASHINFER_CUDA_ARCH_LIST=10.3a \
  python3 diagnose_h9216_split.py --output logs/diagnostic-h9216-split-002

# Saved tensors only; CPU analysis performs no CUDA allocation or launch.
CUDA_VISIBLE_DEVICES='' python3 analyze_h9216_saved.py \
  logs/diagnostic-h9216-split-002
```

The first command has already completed; the output directory is deliberately
exclusive so reruns must use a new name. Neither diagnostic timing is usable as
performance evidence.

## Complete stage parity and oracle outcomes

| Arm | Compared stage | Elements | Split/Mega unequal | Maximum absolute difference |
|---|---|---:|---:|---:|
| Original raw | BF16 FC1 | 32,896 | 0 | 0 |
| Original raw | BF16 per-route FC2 | 4,737,024 | 0 | 0 |
| Original raw | BF16 final output | 2,368,512 | 0 | 0 |
| FC1 globals / sqrt(H) | BF16 FC1 | 32,896 | 0 | 0 |
| FC1 globals / sqrt(H) | BF16 per-route FC2 | 4,737,024 | 0 | 0 |
| FC1 globals / sqrt(H) | BF16 final output | 2,368,512 | 0 | 0 |

| Arm, same for split and Mega | FC1 unequal vs torch | FC1 maximum difference | FC2 unequal vs torch | FC2 maximum difference | Original final band | Final band using actual FC1 |
|---|---:|---:|---:|---:|---|---|
| Original raw | 193 | 64 | 8,762 | 512 | Fail, worst overshoot 193.0321 | Pass |
| FC1 globals / sqrt(H) | 24 | 0.001953125 | 6,038 | 0.0625 | Pass | Pass |

The separate FP64 accumulation diagnostic, rounded back to FP32 before original
FP32 alpha/SiLU/BF16 conversion, also fails the raw final band and passes the
normalized arm. Its FC1 differs from either kernel at 188 raw values versus 24
normalized values. Therefore the evidence isolates the FC1 rounding boundary,
without claiming that torch GEMM accumulation alone is its cause. Both kernels
reuse the same packed-FP32 `exp2`/reciprocal SwiGLU sequence, whereas torch uses
its own SiLU implementation and GEMM accumulation order.

## Worst cell attribution

CPU-only saved-tensor analysis is retained in
`logs/diagnostic-h9216-split-002/mega-stage-attribution.json`. The raw fixture
fails 60 output cells. At token 153, hidden 4803:

| Quantity | Kernel (both split/Mega) | Original torch oracle |
|---|---:|---:|
| FC1 at route 0, intermediate 2 | 9792 | 9856 |
| FC2 route 0 | -2416 | -2176 |
| FC2 route 1 | 5344 | 5344 |
| Final output / FP32 reference sum | -356 | -124.0013428 |

That is the only changed FC1 value in this token. The torch gate 82.4311981 and
up 119.178215 give product 9824.003054, almost exactly the BF16 midpoint 9824
between 9792 and 9856. One BF16 ULP at FC1 thus produces a 240 change in FC2.
Recomputing FC2 from the actual kernel FC1 gives exactly [-2416, 5344] at this
cell and passes the unchanged final-term band over the entire tensor (minimum
margin 1.283515). Original weighted terms are [-2095.057617, 1971.056274]; the
raw final difference 231.998657 exceeds tolerance 38.966579. The existing band
accounts for FC2 term magnitude and reduction rounding; it does not guarantee
protection against an earlier FC1 rounding boundary amplified by FC2.

Normalization changes scaled FC1 standard deviation 74.85997→0.779791 and
maximum BF16 intermediate 52480→5.28125. The normalized arm has zero failed
final cells. The upstream fixture patch applies this normalization only to the
new H9216 geometry, retaining its 36 FC1 K256 tiles and fitted raw
ring. The other nine test cases per rank and all comparison tolerances remain
unchanged. This is fixture conditioning, not a claim of bitwise torch parity.

## Preserved failed diagnostic and final CPU checks

Run 001's split arm passed Mega's gate32/up32 preparation to a different split
ABI. Its split comparisons are invalid and preserved with an explicit README
and the original helper copy under `logs/diagnostic-h9216-split-001`. Its Mega
captures remain valid and the corrected run 002 reproduces their stage results.
The earlier fitted-depth versus forced-raw2 diagnostic remains under
`logs/diagnostic-h9216-001`; both stages were bitwise equal there too.

The normalized fixture is now applied by the parent. Current two-transform-group
source kernel SHA256 is
`58e4af6b935612ed1a68c27fbf355819a02d5a3e622e3fcf5e1dcff0f91c83f7`.
Full `pre-commit run --all-files` passes in the isolated static snapshot,
including mypy/Ruff, with 3682 source hashes matching the active source and no
hook edits. Actual public CPU tests pass 79/79 in the separate host-validation
tree, with 1568 Python source hashes verified and CUDA hidden. Evidence:
`logs/precommit-fitted5-transform2-public-001.{log,provenance.json}` and
`logs/tmem-fitted5-transform2-public-host-001.{log,provenance.json}`. The parent's
full 10-case-per-rank GPU validation is separate from these CPU checks.

After the parent committed `fe4f8132439df1b812f77279e7d033a5128f1ed4`, all
3682 files still matched the completed static validation manifest byte for byte.
The tests were run against the pre-commit source snapshot, not rerun after the
commit operation; the commit did not change those tested source bytes.


## Raw-depth provenance correction

The earlier four-stage label was an unverified expectation, not a recorded
kernel property in the numerical diagnostics. A later frozen-fe4 CPU probe
used the actual public factory/default profile and `_ensure_compiled` kernel
constructor, then ran the exact `_launch_fc12` prefix through its fitting call
with the full pool layout. For E4/topk2/capacity257, H9216/I64, default M256/N128,
both EP1 and EP2 select **five** raw stages at231936 dynamic shared bytes. The
capacity is232448. The original numerical parity/rounding findings above are
unchanged; those diagnostic runs did not establish raw4 coverage.

The separate proposed H9472/I64 replacement selects four stages at215552 bytes
(raw5 would233984) under the same public defaults and has37 K256 tiles. See
[candidate and exact CPU records](candidates/h9472_raw4_fixture/README.md).
Actual GPU compiled-geometry observation remains separate from this CPU result.


The root's later real M256/N128 H9216 control confirms raw5 in the compiled
kernel and passes the unchanged numerical assertion. It used the two-stage
geometry baseline kernel5ea9b59f, not the later stage3 candidate. See the
[observed control and source provenance](candidates/h9472_raw4_fixture/README.md#observed-h9216-gpu-control).
