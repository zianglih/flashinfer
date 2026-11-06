# N64 third decoded-TMEM stage, independent candidate

`transform3.patch` is unapplied and changes only the W4A16 kernel, based on the
preserved `w4a16_m128_n64/current2group` geometry candidate. It uses three decoded
weight stages for both M128/N64 and M256/N64. N128 keeps two. The original N64
two-stage artifact is unchanged for a causal A/B. No active checkout or GPU was
modified; there is no measured performance claim.

Base kernel SHA256: `5ea9b59f882cef50e6da6c915295acaa626b92331f4fb592c0744b47628de866`.
Proposed SHA256: `34bbdfba91e4743a7079d436c3181e3825ca771fe584f910c4ee1c37a4165152`.
The exact snapshots and hashes are in `base/`, `proposed/` and `manifest.json`.
Frontend and epilogue are copied only to run isolated CPU probes; they are
byte-identical to the control and are not included in the patch.

## Established rule reused

The local `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py`
computes available transformed-weight depth from remaining TMEM columns in
`_compute_stages_and_tmem_cols`:

```python
transform_stages = (max_tmem_columns - accumulator_columns) // a_columns_per_stage
```

It also caps by shared-memory feasibility. Mega already has its own exact
shared-storage fitter, so this candidate reuses the TMEM rule and lets that
fitter account for its barriers. The CPU probe calls the **real local standalone
fitter** and confirms it chooses three for N64 and two for N128 in every feasible
tested FC1/FC2 layout. This is an existing stage-allocation pattern, rather than
a new inter-work-tile lookahead protocol.

| Allocation | N64 control | N64 candidate | N128 unchanged |
|---|---:|---:|---:|
| Accumulator stages / columns | 2 /128 | 2 /128 | 2 /256 |
| Decoded A stages / columns | 2 /256 | 3 /384 | 2 /256 |
| Decoded A column ranges | 128–255,256–383 | 128–255,256–383,384–511 | 256–383,384–511 |
| Total allocated TMEM | 512 | 512 | 512 |
| Transform barrier Int64 slots | 4 | 6 | 4 |
| BF16 activation stages | 2 | 2 | 2 |
| Preferred raw stages | 5, fitted down to2 | same | same |

Both decode groups split disjoint halves of the **same** K tile. Increasing the
ring adds no producer threads or per-stage arrivals. M128 still has256 transform
producers and128 accumulator consumers; M256 has512 and256. Raw consumers stay8
warp arrivals, activation consumers stay2/1 by M128/M256, and CTA-local retrieve,
scheduler, dispatch and tail barriers are unchanged. The640-thread launch and
96-register cap with176/80/64/80/80 redistribution are unchanged.

## All coupled two-stage sites

1. `_MegaMixedInput._compute_stages_and_tmem_cols` derives depth from512 columns,
   keeps two accumulators and returns `depth * cols_per_a` for decoded weights.
   The inherited `_setup_attributes` consumes this value when constructing
   `smem_layout_a_transform` and the actual TMEM A fragment.
2. `_make_shared_storage` takes `transform_stages` and allocates
   `2 * transform_stages` Int64 barrier slots, covering full and empty arrays.
3. `_fit_raw_stages` passes the actual mixed layout's transform depth to that
   storage factory before computing allocator-order bytes and choosing raw depth.
4. `PipelineAsyncUmma.create` takes `mix.num_trans2mma_stage`.
5. Each decode group's producer state takes that same stage count.
6. The MMA A-consumer state takes that stage count; indexing the actual A
   fragment continues to use `a_state.index`.

Deliberately unchanged literals: activation pipeline/state2, accumulator
pipeline/state2, epilogue accumulator depth2 and512-column allocate/free. The
mixed-layout helper still rebuilds BF16 B with exactly two load stages and the
derived transform depth; its returned B layout is independent of that depth.
The epilogue never touches the decoded-A region and retains fixed accumulator
pitch N. The dynamic BF16 K16 atom loop and valid-token policy are unchanged.

## Ring and tail constraints

The installed CuTe `PipelineState.advance` wraps by comparison with the actual
`stages`, not a power-of-two mask, so three stages are supported.
`reset_count()` changes only the local K counter; index and phase survive
FC1/FC2 and expert boundaries. Both decode groups and the issuing MMA consumer
must preserve this progression; never reset their ring indices per work tile.

`pipeline-state-reference.txt` records the installed helper source. Producer
states initialize with phase1, consumer states with phase0. For a stage3 ring,
after K28 then K8 the next index/consumer phase are(1,1) then(0,0). A raw5 ring
and a B2 ring have different indices and phases at the same boundary; they must
not be tied to the decoded ring. `phase-walkthrough.json` records a source-derived
example through K28/K8/K1/K3; it is not GPU execution evidence.

Each group's producer tail remains outside the persistent work loop. The
installed `PipelineAsyncUmma.producer_tail` waits across `self.num_stages`
buffers, so it drains all three without a new custom loop. The kernel does not
need a third accumulator stage or a separate drain at phase/expert boundaries.
Empty work leaves initial states intact; all-tail/empty/refill behavior still
requires GPU tests before retention.

## CPU evidence and resource effect

`logs/n64-transform3-cpu-002.log` passes224 isolated configuration, actual
CuTe layout, fitter and epilogue cases over four M/N geometries, both schedules
and both return modes, H32..65536. It rejects64 oversized configurations.
Both FC1 fragment128 and FC2 fragment32 are checked. Real A fragments have
one M atom,16 K16 atoms and three/two decoded stages; real B fragments retain
one N atom,16 K16 atoms and two stages. Public config round trips, every
valid-token accumulator footprint and actual dynamic-atom CPU IR also pass.
Complete records are in `cpu-validation.json`.

At H7168/I2048, flag4/atomic/scheduler3:

| Geometry | Raw2 | Raw3 | Raw4 | Raw5 selected |
|---|---:|---:|---:|---:|
| M128/N64, transform3 | 161152 | 179584 | 198144 | 216576 |
| M256/N64, transform3 | 128384 | 146816 | 165376 | 183808 |

The extra16 barrier bytes fit existing alignment slack at raw5, so its total
does not grow. Raw4 grows128 bytes after alignment. The fitter therefore must
use the new storage class rather than reuse the old byte total or assume a
constant16-byte increment. N128 layouts and all their recorded totals stay
unchanged. No new BF16 global buffer or larger TMEM allocation is introduced.

Ruff, formatting, parsing, manifest hashes and patch applicability pass. CPU
layout checks do not establish TMA/UMMA progress, source scheduling/control bits,
spills or numerical correctness. Current toolchain checks preserve the shared
decoder and its pre13.2 branch but do not run the older-toolchain fallback.

## Overlap hypothesis and decisive trial

A third free decoded slot can let both groups decode one additional K tile
while MMA retains older slots. Releasing that raw stage earlier can also let
packed-weight/SF TMA proceed. Because N64 already reserves512 TMEM columns,
the candidate uses previously unused columns rather than enlarging the
allocation. It may also carry existing persistent lookahead across work tiles;
it adds no speculative tile or live per-work-tile register payload.

The one-group N128 PC capture shows free-TMEM-stage backpressure, which motivates
checking this opportunity, but it is a different geometry/group count. A third
slot cannot improve steady throughput when MMA/activation/epilogue remains
limiting, and can add phase arithmetic, barrier setup/tail work or different
codegen. Small K may never use the extra slot within a work tile. Do not claim
improved overlap from capacity alone.

After the two-stage N64 arm passes GPU gates, apply only this patch and repeat
the same full numerical/K-tail/output-tail/ring-wrap/empty-refill/graph tests.
Inspect fresh resources/spills and compare paired CUPTI/event timings with the
same source schedule, input/routing and raw-depth selection. A source-correlated
PC comparison should remap this binary's own query/free-TMEM waits; do not
compare offsets literally or convert sample counts into latency ratios.

```bash
python3 candidates/w4a16_n64_transform3/build_patch.py
git -C candidates/w4a16_n64_transform3/base apply --check ../transform3.patch
CUDA_VISIBLE_DEVICES='' FLASHINFER_CUDA_ARCH_LIST=10.3a python3 \
  candidates/w4a16_n64_transform3/validate_cpu.py \
  /workspace/flashinfer-w4a16-megamoe
```
