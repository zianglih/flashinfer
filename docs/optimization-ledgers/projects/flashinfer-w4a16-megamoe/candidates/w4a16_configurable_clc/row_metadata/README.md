# Held CLC row metadata candidate

Prepared against central source `57e2d2793d99321aeebd7db4aa619e81759993a56a8c508cb126eb27f5942fd2`. Only three owned implementation files change; all12 saved precision files matched that frozen manifest before editing. Primary, vendored sources, GPU state and the held tight-launch/payload/SF/task-or-terminal candidates were not modified.

Patch SHA256: `ccb26f629616c2ba62934c0b03dd45a5969f72aef259dc8099d14651d103d657` (`+137/-55`, three files). Exact base/proposed bytes and per-file hashes are saved alongside `handoff.json` and `source-manifest-base.json`.

## Data and ownership

`clc_metadata` is appended after existing local workspace regions, outside the counter-zero prefix. It contains an aligned four-word scalar header (only word0 is read), four Int32 words per expert `{row_begin, data_begin, sf_begin, count}`, then one expert ID per logical row. Its capacity uses the existing full worst-case row bound. The existing bitmap, queue allocation, fallback cursor, physical launch grid and fixed dispatch/finish grids are unchanged.

After `dispatch_barrier` returns, warp0 of each fixed CTA loads immutable packed expert counts, masking the low32 bits. It scans streaming32-expert chunks using a five-step full-warp prefix sum. CTA0 writes expert headers and total rows. For row IDs, each lane writes only `row % (num_ctas*32) == cta*32+lane`, striding within each expert's interval. This produces every actual row exactly once, including skew beyond the physical compute grid. Row iteration and metadata addresses use Int64; logical count/prefix fields retain the current Int32 contract.

All warp lanes execute the scans/broadcasts. The lane-dependent row loop contains only stores and arithmetic, followed by a full-warp synchronization before the next broadcast. No grid/rank barrier, shared-memory allocation, metadata atomic or readiness counter is added. The original dispatch calls remain in order: prep, count barrier, new warp0 metadata construction, original payload pull.

Fixed dispatch completion on the same stream joins every metadata writer before compute reads it. Total rows is a value, not a ready flag. Every replay overwrites total rows (including zero), all expert headers and the used row range; unused entries are never read and need no reset. Existing fixed finish still waits for the whole physical compute grid before resetting mutable queue/counter state.

## Coordinates and preserved representation

`active_cluster`, `run` and `schedule` now load total rows instead of scanning experts. `phase_work` computes row/feature from the existing phase-specific feature count, reads `row_expert`, loads its expert header, and applies the original CTA-coordinate/valid-token arithmetic. Accepted C1/C2 physical clusters remain `(C,1)`, with internal swapped scheduler axes `(1,C)`: both C2 CTAs share the logical token row and have separate feature coordinates. Counter row identity remains `row_begin + tile_n_idx == row`.

Both valid work and terminal sentinels preserve the existing eight logical fields/eight physical words, including the activation-scale prefix. The record/extension and fused scheduler files are byte-identical. Readiness enrichment still runs after mapping; ready flags are not cached in metadata. Range checks prevent sentinel and empty-rank table accesses. Negative mapper indices were not an accepted claim path before this candidate and now also yield the invalid record.

## Host evidence

`python3 -B check_host.py` imports no CuTe runtime. It interprets the **actual proposed** helper/builder AST as32 cooperative lanes, suspending at the actual shuffle/synchronization sites. Independent cumulative formulas check expert headers and row IDs. It executes the **actual old and new** scalar phase-mapper ASTs and compares every returned field, including SF offsets, both phases, C1/C2 feature coordinates and terminal records. An observable enrichment hook verifies that both paths retain it.

Results:134 builds,8,097 row writes,107,066 work-record comparisons,7,860 active-guard checks and66 smaller/empty replays in reused allocations. Expert counts include1/7/17/31/32/33/63/64/65/97/129/257; cases include empty experts/ranks, sparse counts, partial tiles, a single5,001-row expert, nonzero packed high bits, randomized CTA order and claims, and66 fixed CTAs with fewer useful rows. Padding domains are independently varied to detect accidental aliasing. Large host-only layout cases check that metadata append leaves every prior offset and the zero prefix unchanged; no larger native count range is claimed.

Additional AST checks establish unchanged ownership, queue, broadcast, cancellation, bundle-lifetime helper, tails, workspace-capacity/grid formulas and original dispatch calls. Removing only metadata append/wiring from the proposed kernel yields full-module AST equality with the base. Variable-length workspace extraction/reconstruction retains both tensors and constants. Ruff check/format and read-only `git apply --check` pass. Host log SHA256: `45569ae0167637ca624b856db3187db92edb68b9e2d7b15372c77d9764d6c1e3`.

An independent builder-only source review by `iteration_prep` found no concrete collective, SSA or visibility defect: full-warp scans precede predicated accumulation; chunk/source-lane loops are uniform; post-store warp synchronization joins lane-dependent loops; chunk carries do not depend on those loop values; dispatch completion publishes all metadata writes. That review did not compile or execute the candidate.

## Limits and next trial

No native compilation, GPU numerics/replay or performance evidence is claimed. Native validation must check the added pointer serialization, shuffle/loop lowering, early guard ordering, descriptor loads, mapper resources and fixed-dispatch occupancy. Prefix work is replicated across the bounded fixed grid and may add dispatch cost; the dependent row/expert lookup adds memory latency. The source change is intended to remove repeated compute-side scans, but NSYS did not isolate their causal contribution. Trial after the separately controlled tight launch, then combine only accepted changes with a new source identity.
