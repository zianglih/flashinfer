# Native N16 accumulator release and ring depth

CPU ownership audit against retained aab93f and e14 physical-N16 epilogue.
No new kernel execution or source modification. Initial recommendation is
four operand stages and two accumulator banks, with only the release moved.

## Exact release contract

`_run_narrow_fp4` loads both up16 and gate16 into eight FP32 registers each
per lane. Everything afterward is register arithmetic, SF/output addressing
and global stores; unlike the retained transpose, it does not use accumulator
TMEM as scratch. Once both loads complete, MMA may overwrite that bank even
while the epilogue is quantizing/storing its register-owned values.

Place `fence_view_async_tmem_load()` after both native loads and before one
`acc_pipeline.consumer_release(acc_state)`. The accumulator pipeline is
constructed with128 consumer participants per CTA. All four epilogue warps
must execute the release, outside valid-token/output-channel predicates.
Keep the same consumer state object until the existing single `advance()` at
the end of the persistent tile iteration. Suppress the late core release only
for the exact statically selected early-release path. Other paths retain their
existing release. A duplicate load fence is redundant but harmless; a duplicate
release is a phase-corrupting bug.

The safe initial geometry is one CTA, N16, one channel tile, generated FP4
gated FC1, where the direct branch loads the whole bank before releasing it.
Do not generalize to NB2 or an epilogue looping over multiple channel tiles
unless every fragment in the bank has first been loaded. The ordinary SF
source/MMA pipeline and its newly retained proxy fence remain independent.

| Case | Required behavior |
|---|---|
| `total_tiles==0` | Producer and epilogue loops issue no bank operation; final CTA join/deallocation remains unchanged. |
| Active tile with valid rows0 | MMA publishes one bank; all128 epilogue threads load and release it once, then suppress output/SF stores. |
| Partial rows1…15 | All128 threads participate in ownership; store predicates alone select live rows. |
| M384 channel tail | Every logical channel tile still drains one bank; existing weight/TMA fill and output bounds remain authoritative. |
| More persistent tiles than banks | Index/phase advance once per tile; release uses current index, never the next index or SF-source ring index. |
| Final tile | MMA producer tail waits for the released bank; CTA final barrier still prevents TMEM free before epilogue global-store issue completes. |

Source anchors: retained core944–952 constructs128-participant consumer group;
1244–1332 performs persistent epilogue waits/body/release;1515–1535 commits,
drains and joins before freeing TMEM. e14 utils565–660 has no TMEM operation
after the two initial native loads. The caller's existing arguments already
include the pipeline and consumer state on the overlap-epilogue path.

## Four banks fit the same128-column reservation, if later justified

For the physical-N16 NVFP4 K512/SF16 geometry, SFA and SFB each require32 TMEM
columns. With the unchanged one-SF-stage MMA schedule:

| Accumulator banks | Accumulator intervals | SFA | SFB | Rounded reservation |
|---:|---|---|---|---:|
|2|[0,16),[16,32)|[32,64)|[64,96)|128|
|4|[0,16),[16,32),[32,48),[48,64)|[64,96)|[96,128)|128|

Four is a straightforward later ring-depth experiment: existing formulas use
`acc_stages*acc_cols` for the SF base and bank index for accumulator addressing.
All SF bases retain32-column alignment, each accumulator bank retains16-column
alignment, and power-of-two index/phase math remains cheap. A three-bank ring
also has sufficient byte capacity but adds an unnecessary alignment/state
specialization; it is not recommended for this bounded round.

Two extra full/empty barrier pairs add32 raw bytes, but cross a128-byte alignment
boundary in SharedStorage: expect about128 B total growth, verify the compiled
structure rather than asserting the arithmetic estimate. No extra operand
stage or per-bank register array is needed: the epilogue still processes one
tile at a time. Four banks do not reduce the one-CTA/SM target or change the
allocated TMEM size. These intervals do **not** apply to the separate publisher
prototype, which has two TMEM SF slots and different footprint.

Early release and depth4 should be separate measured steps. Early release may
make depth2 sufficient; a deeper queue cannot overcome a slower epilogue's
steady-state throughput. Keep launch bounds unchanged initially; current
64→50-register results were not occupancy limited by registers and increasing
an abstract budget alone does not remove instruction work. Inspect actual
registers/local memory after the packed-SF change and keep compilation bounded.

Before the first timing: check emitted fence-before-release, a single release
path, exact output/SF bytes including all-NaN and partial/zero cases, and enough
persistent tiles to wrap both bank index and phase. No broad matrix or new
repository test file is necessary for the first bounded screen.
