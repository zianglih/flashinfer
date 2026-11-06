# Canonical SF transpose preparation: rejected prototype

The authorized GPU screen rejected this variant: preparation latency is
**2.67–2.69× control for NV8K, 1.83–1.85× for NV16K, and3.12× for MXFP8 16K**
across forward/reverse orders. No full-chain execution, profiling, or production
integration followed. [Raw results](../../evidence/regular-tma-sf-tile/RESULTS.md)
and [final receipt](../../evidence/regular-tma-sf-tile/validation-receipt.json)
preserve the complete evidence. GPU6 is released idle.

Independent source copy: `../../flashinfer-regular-tma-sf-tile`, branch
`experiment/regular-tma-sf-tile`, HEAD
`442d2aa53f68b4640c3ab5118a76f1599ff60d34`. Both Git directories resolve inside
the project. All changes are unstaged.

The copy starts with the active regular-TMA grid16 three-file snapshot.
Only its `blackwell/moe_prepare.py` differs from that snapshot. The frozen
active regular-TMA source, AUTO adapter, and production source were not edited.
[Control manifest](control-manifest.json), [prototype manifest](manifest.json),
and [preparation-only diff](preparation-only.patch) record the boundary.
The manifest was frozen at the CPU gate; its `gpu_compilation_or_execution`
field describes that creation point. The final receipt records subsequent
authorized GPU work. `prototype_snapshot/` holds the exact tested three files.

## Mechanism

The control assigns a CTA to a routed row. Lanes read consecutive four-byte
SF words but store them 512 bytes apart in the canonical layout. A full warp
therefore addresses 32 destination sectors for 128 useful bytes.

This prototype assigns one work item to a **128-row canonical atom × 32 SF
words**, where one word holds four scale bytes. Its four warps process rows
`warp + 4*i`. Each warp copies the corresponding payload K interval with the
existing 16-byte vector operation and loads one contiguous 128-byte SF interval.
There is no duplicate payload copy or additional global pass.

SF words go into one shared tile at `p(row)*33 + block`, where
`p(row) = 4*(row%32) + row//32`. After a CTA barrier, threads vary across `p`,
giving contiguous canonical global stores. Both shared access directions are
bank-unique. Allocation is exactly **128×33×4 = 16,896 bytes**; only 32 columns
are used. A second unconditional CTA barrier protects the tile before reuse.

Physical tile dimensions are fixed compile-time constants for all inputs.
The number of K chunks follows the existing SF column count. The launch keeps
the control's thread-capacity bound but counts row-atom/K-chunk work items.
There is no token-count threshold, shape-specific dispatch, public layout
change, extra global workspace, quantization, or arithmetic conversion.

The W4A16 precedent is its contiguous 16-byte payload permutation
(`csrc/nv_internal/tensorrt_llm/kernels/cuteDslKernels/moeUtils.cu:91–95`). That
helper explicitly defers SF handling at line97; the SF transpose is a new
hypothesis rather than a transfer of an existing W4A16 implementation.

## Preserved ownership and boundaries

- `allocate()` and the public preparation signature are unchanged. Buffers
  remain invocation-local and owned by the existing host. The core and host
  source files are byte-identical to the frozen regular-TMA control.
- Mapping reads require an active row below its tile's valid limit. Original
  token identity remains `mapping[row] // top_k`; the mapping, limits, and
  per-token scale arrays are not rewritten.
- Active padded payload rows are zeroed, including N16's extra16 rows clipped
  to allocation capacity. Full 128-row SF atoms are initialized; unused global
  capacity remains untouched.
- Every shared cell receives a source word or zero, including invalid rows and
  partial K chunks. Final global stores are predicated by actual SF columns.
  All threads participate in both barriers, irrespective of row validity.
- Zero live routes perform no payload/SF work. PDL placement and completion
  behavior remain at kernel entry/end as in the control.

## CPU validation

```bash
python3 scripts/regular_tma_sf_tile_experiment/prove_addresses.py
git -C flashinfer-regular-tma-sf-tile diff --check
```

**72/72 CPU model cases pass.** Six supported format labels cover the three
actual byte-copy geometries: FP4/SF16, FP4/SF32, and FP8/SF32. Cases include
zero live routes; N16/32/64/128/256; N16 extra rows both clipped and extending
into a second SF atom; empty/full/partial tile limits; K chunks containing
1/2/31/32/33/63/64/65 SF words and native K7168; repeated source tokens;
top-k1/2/8; and persistent grid strides1/3/17/256.

The model verifies exact-once 16-byte payload ownership, exact-once canonical
SF word ownership, arbitrary uint32 bit preservation, zero padding, invalid
mapping-read exclusion, unchanged metadata, untouched capacity/end canaries,
and full shared-cell initialization before reads. It checks the original
canonical address formula independently of the producer-to-consumer shared
mapping. Source AST checks confirm unchanged allocation/signatures and verify
the physical tile constants. Independent source review also enumerated44
geometry cases without finding a source-level blocker.

[CPU receipt](../../evidence/regular-tma-sf-tile/cpu-address-proof.json)
records every case and exact source SHA. This CPU proof imports no CUDA/CuTe.
GPU checks were subsequently authorized and are documented below.

## Bounded actual-source GPU checks

The first compilation succeeded. Six smoke graph checks passed, followed by
the31-check bounded suite (including those six;31unique checks and37total
executions). Checks cover arbitrary packed bytes, FP4 SF16/SF32, FP8 E4/E5,
short K and the33-SF-word chunk tail, N16/32/64/128/256, zero/grow/shrink replay,
poisoned invalid mappings, untouched capacity and end canaries. The N16 case
crosses active128→physical144→canonicalSF256.

```bash
python3 scripts/regular_tma_sf_tile_experiment/run_probe.py \
  --tag exact-smoke-r1 --variant tile --suite smoke
python3 scripts/regular_tma_sf_tile_experiment/run_probe.py \
  --tag exact-bounded-r1 --variant tile --suite exact
```

`run_probe.py` records commands, logs, and downloaded JSONs under
`evidence/regular-tma-sf-tile`. It uses managed `/usr/local/bin/h`, actual
`regular-tma` or `regular-tma-sf-tile` imports, the existing candidate native
cache, separate private CuTe caches, and GPU6. It refuses existing output tags.
Provisioning verifies the442 vendor gitlinks and independent project-owned Git
directories; no existing source copy is overwritten.

Prep-only timing ran `control,tile,control`, then `tile,control,tile` with
reversed case order. Each process uses `--suite timing`, default
`--cases nvfp4:8192,nvfp4:16384,mxfp8:16384`, and a distinct `--tag`.
The timer is10warmups/100cold-L2 CUDA-graph CUPTI samples; all1,800samples are
retained. Native DeepSeek routing, sorting, and activation quantization run
outside timing, using the benchmark's seed42 input-generation prefix. N256,
hidden7168, top-k8,32localexperts are fixed. No weights, FC1, or FC2 execute.

Each row passes its own independent byte reference and post-timing output
hash. Original inputs, top-k results, and valid limits match across processes,
but native `moe_sort` produces different sorted row permutations. These are
**not strict fixed-permutation performance comparisons**. All live mapping
hashes are retained, and the final receipt explicitly excludes cross-process
prepared-output equality. The first archive validator caught this overstrong
assertion; its script/log are preserved. The large regression in both orders
was sufficient to reject the candidate without further GPU runs.

## Concrete limitations

- CPU address ownership is supplemented by bounded actual compilation and
  graph exactness checks. No sanitizer or full MoE numerical suite was run.
- A whole 128-row atom per work item reduces the number of live CTAs. Decode
  with few live rows may lose parallelism substantially; even prefill has fewer
  CTAs than the row-per-CTA control. No token-specific fallback is included.
- The 16,896-byte shared allocation, two CTA barriers per work item, shared
  reads/writes, and repeated mapping loads across K chunks can erase the store
  efficiency benefit. Register usage and actual occupancy are unmeasured.
- The 32-to4 sector estimate concerns a full warp's address shape, not measured
  HBM traffic or latency. Cache/write combining may already absorb some of the
  control's scattered stores. Partial K chunks can underutilize lanes.
- The source still uses the hardware thread-capacity launch bound, not an
  occupancy API informed by generated registers/shared memory. This deliberately
  avoids adding another policy change before the first comparison.

The source copy remains available and unstaged. No performance retention is
claimed; this experiment is closed with no further GPU work planned.
