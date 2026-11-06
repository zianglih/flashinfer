# Native K96 accumulation and zero-padding qualification

K96 is a numerical contract change. The existing NVFP4 update arithmetic remains sufficient when applied at the actual instruction boundaries, including the reset at each acquired pipeline stage. Do not treat a K256-stage kernel as globally uniform K96 or as a K512-stage kernel.

- **Source:** independent scalar CUDA probe against pushed `d1767be1f42fdc371f90db4fb06598299ea32845`; original shared oracle SHA `911951361eed612514b3fc6b55efd1233b606483152d25c66af8d2f78be4b6aa`.
- **Runtime:** secondary C3 `fi-moe-sanitize-1028`, GPU6 B300 SM103; image `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2.78, driver 595.91.07, PyTorch `2.12.0a0+5aff3928d8.nv26.05`, CuTe DSL 4.8. GPU UUID `GPU-55563f08-7de4-1809-b469-968e568fa223`.
- **Isolation:** one CTA, direct FP32 TMEM readback, no activation or output quantization. Each native instruction repacks payloads into independently 1024-byte-aligned SW128/16-byte-atom K-major operands, absolute LBO, base offset zero. This qualifies numerical grouping, not production TMA/descriptor progression, pipeline synchronization, two-CTA execution, or performance.
- **Cache:** native artifacts remain under persistent `native-cache-r2`; other native/DSL caches were retained. No sanitizer was run for this small numerical probe.

## Native results

The first run covers 7,104 pairs: all 960 one-hot positions across K192/256/512, and 1,024 unit-scale plus 1,024 wide-scale random pairs for each K. Every K64 result agrees with the existing reference bit for bit; all one-hot and unit-scale K96 controls agree too.

| K | Native candidate updates | Wide-scale K64 versus K96 mismatches |
|---:|---|---:|
| 192 | 96, 96 | 258 / 1,024 |
| 256 | 96, 96, 64 | 216 / 1,024 |
| 512 | 96, 96, 96, 96, 64, 64 | 326 / 1,024 |

The first K256 mismatch is `615938.9375` (`4916602f`) versus `615939.0` (`49166030`). A smaller discriminator puts three nonzero products at K0, K16, and K64:

```text
products: 2^16 + 2^-16 - 2^16
K64:      0              FP32 bits 00000000
K96:      0.000015258789 FP32 bits 37800000
```

This difference survives BF16 storage. Payload codes are A=`2,2,10`, B=`2,2,2`; both operand scale bytes are `0x78` in blocks0/4 and `0x02` in block1. All other products are zero.

A K512 run consisting of two K256 stages, `[96,96,64,96,96,64]`, differs from eight K64 updates in 378/1,024 wide-scale cases and from a single K512 stage in 344/1,024. Stage boundaries must therefore be retained in the oracle plan.

## Same arithmetic, explicit update plan

The project-local AST qualification changed only the existing oracle's update traversal, scratch width/masking, and scalar-pair indexing. Decode, exponent alignment, grouped sums, truncation, and FP32 carry conversion are unchanged. It matches native FP32 bits for all 8,129 pairs under both control and candidate sequences (16,258 comparisons), including the cancellation discriminator and repeated K256 stages.

The maintained candidate now accepts an optional sequence of native instruction widths. A small offsets tensor drives the existing arithmetic in a runtime loop, avoiding source duplication and large fully unrolled reference kernels. Existing K64 and MX defaults remain unchanged. The existing test module observes the selected compiled kernel's stage width on compilation and cache hits, then supplies separate FC1/FC2 plans. No production API, cache format, tactic axis, tolerance, or reference self-test is added.

`reference-candidate.json` and `reference-candidate.patch` bind the unstaged reference/test source in `flashinfer-tp-k-tail-review`. The actual maintained candidate also passed all 16,258 native FP32 comparisons; its source SHA is `17c646d4d59bef607ca8693e5c583e103d46aa4f85f8c55f0d29aa54ad420b21`. Raw results, commands, and source are in `updated-reference-evidence/`, with their hashes in `receipt.json`. Ruff, syntax, and whitespace checks passed. Integrated production K96 correctness remains the scheduler's gate; these native numerical results alone do not qualify it.

## Skipping padded K64 updates

All 1,089 comparisons are bit exact:

- 1,024 wide-scale K192 dot products versus the same data padded to K256 with an extra zero K64 update.
- 64 zero/negative-zero payload cases: payload codes0/8, scale bytes0/1/56/126, initial carries ±0, ±minimum subnormal, ±1, and ±maximum finite FP32. One valid zero update versus four zero updates agrees in every output bit.
- The crafted cancellation prefix versus the same padded update.

Negative-zero initial carry becomes positive zero after the first valid zero MMA in both arms. This is not a claim about skipping every instruction for a zero-K problem.

## Evidence and reproduction

Local `evidence/` retains all raw input/output tensors, results, commands, compiler logs, PTX, cubin, SASS, source, and runtime receipts. Archive SHA `bf23acf952da1ed345731ad1e70eda52732ffd531d65244ae4b3a6b91e7411c9`; 69 files are hash-verified by `evidence-verification.json`. Remote root is the same suffix under `/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026`.

Raw reports:
- `evidence/run-r2/result.json`: native controls and numerical differences.
- `evidence/model-r1/result.json`: 7,104-pair oracle qualification.
- `evidence/followup/result.json`: cancellation, stage reset, and padding.
- `evidence/model-followup/result.json`: 1,025-pair follow-up oracle qualification.

Build command (paths supplied by `controller-r2.py`):

```sh
/usr/local/cuda/bin/nvcc -gencode=arch=compute_103a,code=sm_103a \
  -O3 -lineinfo --shared -Xcompiler -fPIC --keep \
  --keep-dir native-cache-r2 native_probe.cu -o native-cache-r2/native_probe.so
```

The initial CPU-only compile with `-arch=sm_103a` also emitted an unsupported generic `sm_103` fallback and failed. The explicit `-gencode` command fixed that; failed logs are preserved. This was not a production-kernel failure.

The [PTX ISA](https://docs.nvidia.com/cuda/parallel-thread-execution/#tcgen05-leading-dimension-byte-offset-absolute-address) documents the absolute-LBO alignment and swizzle restrictions. The accumulation model is empirically qualified against hardware; the ISA is not being cited as a guarantee of its internal rounding details.
