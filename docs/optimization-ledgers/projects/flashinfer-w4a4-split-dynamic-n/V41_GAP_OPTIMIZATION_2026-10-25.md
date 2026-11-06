# V41-Flash gap optimization

Retained control: `0c1e00fc3e4f913c8c241796c70a29673737c542`.
Experiments live as unstaged changes in independent project-local clones.
Retention uses V3 EP8 and V41-Flash EP4, all three requested formats, the
established native AUTO cold-L2 CUPTI methodology, and excludes1/2-token rows.

## Replacement runtime

The previous `fi-w4a4-narrow-1025` devbox no longer exists. Requested
`fi-v41-gap-1025` in c1/ziangli with8B200 GPUs, `--bare`, no size argument,
explicit image `nvcr.io/nvidia/pytorch:26.05-py3`.

Immediately before the request, checked the live NGC PyTorch catalog and
NVIDIA's26.09 release matrix.26.09/26.08 use CUDA13.4.1,26.07 uses13.3.1,
26.06 uses13.3.0, and26.05 is the newest CUDA13.2 release
(CUDA13.2.1.009). Sources:
https://catalog.ngc.nvidia.com/orgs/nvidia/containers/pytorch
https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel-26-09.html

The managed HAI CLI must run from an HAI checkout; the first project-directory
attempt failed before creation. The subsequent managed CLI invocation from the
shared HAI checkout only requested the devbox and changed no HAI source files.
The c1 request remained unassigned due to queue capacity and was deleted.
c2 had B300 GPUs available, but its default220-CPU request could not fit.
Recreated only our unscheduled c2 request with64CPU/512Gi/500Gi, still omitting
`--size`; the CLI requires all three explicit resource fields when any is set.
`fi-v41-gap-c2-1025` on c2/ziangli is now ready with8B300 GPUs. Rechecked the
same official container catalog immediately before requesting c2.

Fresh controls are required on the replacement host even if durable compiled
artifacts survive. Historical public tables are not substituted for controls.

## Independent directions

- Profile native CuTe/TRTLLM V41 phase spans at matched routes and AUTO tactics.
- Reuse narrow activation tiles across two output-channel tiles in one CTA.
  Accumulator depth is bounded by actual TMEM capacity and scale columns;
  operand stage fitting remains based on actual SMEM layouts.
- Revisit dedicated mixed FC1 epilogue overlap after the switch to regular TMA.
  This changes only the existing compile-time overlap policy, not model rules.

GPU allocation: profile0/1; fresh V41 controls2/3; V3 controls4/6;
channel-reuse gate/screens5; mixed epilogue overlap7.

## Fresh runtime and admission gates

C2 host `hu-pdx-150`,8B300 SXM6 AC GPUs, actual driver595.91.07. The c1
durable project is absent from c2 storage, so recovered clean0c under
`/data/ziangli/flashinfer-w4a4-split-dynamic-n/v41gap-c2-20261025`, with the
usual `/workspace/flashinfer-w4a4-split-dynamic-n` alias. Actual imports are
Torch2.12.0a0+5aff3928d8.nv26.05/CUDA13.2, CuTeDSL4.7.1 and CUPTI13.4.58;
architecture10.3a. Full runtime receipt:
`evidence/v41gap-c2-bootstrap/environment.json`.

Reuse candidate passed252 actual layout/resource policies and18 exact
baseline-geometry versus reused-geometry comparisons. Raw gate:
`evidence/narrow-channel-reuse-r1/gate.json`.

Mixed epilogue overlap and MMA K-tail candidates pass scoped pre-commit.
They remain unstaged, independently pinned, and not retained. The K-tail
candidate computes native instruction extents from fragment geometry and
preserves the existing TMA/pipeline allocation.

Fresh controls began on all assigned GPUs. First-use native `moe_utils`
compilation serializes the processes through its build lock: observed active
`ptxas` compiling `trtllm_fused_moe_routing_custom_cluster.ptx` for sm103a.
Sleeping observers alone are not evidence of deadlock; no processes were
killed or benchmark samples relabeled.

## Retained mixed FC1 epilogue policy

Committed and pushed `853aaf69d706b291afee477f738956b997033f53`.
The one-line policy removes the mixed-format restriction on the existing
geometry-based dedicated epilogue. No tactics, kernel math, pipeline capacities,
model dimensions, or runtime conditions are added. Homogeneous FC1 and FC2
constructor policies are unchanged.

| Model | Format | Paired decode | Paired prefill | Paired overall |
|---|---|---:|---:|---:|
| V3 EP8 | MXFP4 × MXFP8 | 1.041320× | 1.049441× | 1.043529× |
| V41-Flash EP4 | MXFP4 × MXFP8 | 1.051087× | 1.089749× | 1.061493× |

C1/A1/A2/C2 native AUTO, fixed GPU per model, all13 tokens;1/2 excluded.
Every retained token improves in both repeats. V3 MXFP8 control is1.000027×
overall. Exact source, route bytes, GPU and timing checks passed; complete
medians/cache receipts remain in the model mixed-overlap evidence directories.
V41 paired report: `evidence/pr7290-v41-mixed-overlap-a2/paired.json`;
V3: `evidence/pr7290-v3-mixed-overlap-a2/runner-paired.json`.

Twelve static/SM2 and12 CLC/clamp10 payload/SF byte comparisons passed, plus
the existing focused49 gate (49 passed,98 warnings,19.19s). All83 measured
source pins match the committed source. No broad suite/sanitizer campaign was
run. Independent interaction review found no blocker:
`evidence/mixed-epilogue-overlap-r1-clc-exact/review.md`.

Matched V41T128 phase trace supports FC1 serialization as the cause:
native284.0335→269.570us, FC1 lifetime186.145→171.937us. Inter-kernel
FC1→FC2 overlap decreases9.024→6.976us. Kernel lifetimes include dependency
waits; they are not additive compute times. Native TRT259.586us still wins
this point. Evidence: `evidence/v41-pipeline-profile-c2-overlap-r1`.

## Rejected screens and remaining gap

- Narrow output-channel reuse: V41 fixed N16 T32/128/512 full-chain geomeans
  NV0.9785×, mixed0.9867×, MX80.9904× for both-FC reuse. Individual FC1/FC2
  controls and252 resource/18 exact checks are preserved. No full sweep.
  `evidence/narrow-channel-reuse-r2-fixed`.
- MMA K-tail predication:24 exact cases pass, but native V41 NV overall
  0.995366×, V3 0.999355×. Rejected without repeat sweeps. Original failed
  gate used an unsupported control-only no-scatter configuration; corrected
  actual-FC2 gate is separately preserved in `evidence/mma-k-tail-r2`.
- Fresh B300 matched TRT traces locate the remaining NV gap in FC2: T32
  CuTe FC1 78.913us vsTRT85.601, FC2 48.513 vs37.472. Trace lifetimes include
  PDL waits, so use native whole-chain numbers for retention.
- Half-SMEM co-residency is deferred: shrinking CLC resources below half-SM
  capacity could admit two same-kernel CTAs, contrary to the desired one-CTA
  policy; `min_blocks_per_mp=1` does not impose a maximum residency.

Independent FC2 CLC and reduction-tile experiments are starting. Root's
`flashinfer-fc2-narrow-bulk-review` extends existing stmatrix/bulk output to
narrow tiles, bounds slabs by allocated token extent, and computes input
stage capacity with the actual added epilogue storage. It remains unstaged
and unretained pending exact scatter and timing gates.

## FC2 diagnostic decisions

- FC2-only CLC depth1 passed16 exact cases but fixed V41 N16 T32/128/512
  speedups were NV1.0050/1.0093/0.9901×, MX81.0086/1.0113/1.0062×,
  mixed1.0071/1.0143/0.9865×. Repeated T512 losses preclude broad retention.
  `evidence/fc2-clc-r1-fixed`.
- Existing bulk output extended to narrow tiles (32-column slab) passed45
  byte cases; fixed full-chain geomeans NV1.001166, MX81.000425,
  mixed1.000472× are neutral. `evidence/fc2-narrow-bulk-r1-fixed`.
- Native16-column output slab passed45 byte cases and fixed N16 geomeans
  NV1.002440, MX81.001453, mixed1.000727×. Review found a latent metadata
  index defect only when this slab became a fallback for N32 or larger.
  The isolated R1 timing used N16, where indexing is unchanged; do not
  retain the broader buggy prototype. Corrected separate copy
  `flashinfer-fc2-narrow-bulk16-offset-review` passes81 initialized-byte
  comparisons, including forced16 slabs on N32/64/128 and reversed mapping;
  no corrected-source performance claim yet.
- Shorter K with capacity-derived minimum one-CTA depth, +1 and maximum
  depth was tested via existing compile knobs. Actual physical SMEM is
  233472B and all emitted configurations keep1 CTA/SM with zero local
  bytes. NV geomeans1.002574/1.002326/0.983074×; MX8
  1.006763/1.001613/0.990904×; mixed0.963959/0.982355/0.996646×.
  Reject universal shorter K. Source/math/cache hints were held constant;
 48 byte cases passed. `evidence/fc2-kstage-r1-fixed`.

A final focused co-design experiment combines the corrected16-column output
slab with a physical N16 B/C allocation for narrow scatter. This can fit an
additional NVK512 operand stage from capacity, without shortening K. The
older physicalN16 rejection was FC1 with fixed4 stages, so it does not
measure this design. Keep the new copy unstaged until its own gates decide.

The original-to-final public comparison is being refreshed on B300 because
old B200 numbers cannot supply a controlled same-hardware comparison. Reuse
archived measurement bodies with only explicit V3 CFG validation compatibility;
all old evidence remains unchanged. Current4-table backend runs use clean853a.

## Current B300 backend status and FC2 profile

Clean853 V41 public tables completed, both family processes exit0 and13/13
rows. Source hashes are unchanged. Native TRT/CuTe geometric means:

| Format | Decode | Prefill | Overall excluding1/2 |
|---|---:|---:|---:|
| NVFP4 W4A4 | 0.980951 | 1.080700 | 1.007204 |
| MXFP8 | 0.976838 | 1.015361 | 0.987197 |
| MXFP4 × MXFP8 | 0.993647 | 1.072223 | 1.014487 |

These are current single-sweep backend comparisons, not stability claims.
`evidence/pr7290-v41-final-853a-b300-r1/current-ratios.json` binds full-precision
medians and all raw source/method receipts. V3 tables are running sequentially
on the same GPU1/3 assignments.

Matched NV V41T128 FC2 NCU kernel replay: CuTe92.416us vsTRT90.624us,
DRAM reads545.817MB vs544.577MB, throughput77.52% vs79.16% of sustained peak,
tensor active7.32% vs3.74%, long-scoreboard71.81% vs72.43%. CuTe executes
fewer warp instructions (9.389M vs12.259M). Kernel replay removes concurrent
PDL/cache behavior; it cannot replace full-chain timings. The much smaller
isolated gap suggests startup/cache/scheduling interaction deserves review.
Evidence: `evidence/v41-fc2-ncu-c2-r2`.

The selected TRT NV T128 FC2 cubin uses actual descriptorN8, while our core
rounds to16. Existing descriptor-onlyN8 V3/B200 results are neutral and do not
measure the physicalN16 plus native16 bulk epilogue co-design currently gated.

## Published retained evidence

PR7290 body refreshed and read back exactly for clean853a. Draft remains open;
no PR comment added. Body `pr-body-final-853a-b300-r2.md`,64215bytes,
SHA256 `5b7ebe289e442f673094cf6494866b9549e3dd70612b02aee4dd74e4d0c32f69`.
Published readback `artifacts/pr7290-published-853a-b300.json`.

Fresh same-GPU B300 originala65→853 C1/A1/A2/C2 V3 EP8:

| Format | Decode | Prefill | Overall excluding1/2 |
|---|---:|---:|---:|
| NVFP4 | 1.082386 | 1.001229 | 1.059621 |
| MXFP8 | 1.093366 | 1.093598 | 1.093429 |
| MXFP4 × MXFP8 | 1.243515 | 1.065232 | 1.192126 |

NVFP4T16384 is0.978904× (slower in both repeats); explicitly disclosed.
All156 native medians and262 input hashes are preserved in
`evidence/b300-original-final-v3-r3/paired-summary.json`. Original observer
measurement bodies are unchanged. All13 activation/router/routes/histograms
match; retained expert-weight hashes at1/32 match, with remaining weight
construction covered by V3 input AST/runtime/seed equivalence. Original all13
full input hashes are preserved. This bounded validation replaces redundant
large-weight hashing for faster iteration. Initial scalar-view companion
failure and superseded coordinator are preserved and not presented as passes.

The body contains four complete clean853 public backend tables, precise runtime
and source bindings, the49-test log and explicit deferred suite/sanitizer scope.
It states the task-local observer reproduction boundary and preserves7196-first.

PhysicalN16 + native16 bulk output is rejected: V41 fixed whole-chain geomeans
NV0.992761, MX81.000942, mixed1.000256×. Extra NV stage4→5 does not help.
All99 exact cases and360 layout checks passed; no source was retained.

Next bounded candidate: early FC2 A/SFA prefetch with explicit FC1 metadata
publication, on separate unstaged853 copy. PTX13.2 §9.7.13.13 explicitly permits
GPU release before launch_dependents to synchronize with dependent start in the
same memory domain. Generic standalone defaults remain off; B/SFB remain behind
the dependency wait. No additional buffers or stage constants. Source review
and changed-data captured replay gate precede three-arm clean/off/on timing.

## PDL weight startup screen

The single-stage candidate passes162 changing-data exact graph replays across
all three formats, N16/N128, PDL on/off, K384 tails and zero local routes.
Independent source and emitted PTX/SASS review confirms the FC1 release precedes
its signal, FC2 A/SFA alone precede its wait, and the first stage's transaction
bytes are acquired exactly once. Captured codegen coverage is NVFP4 N16;
the other formats have source review and replay coverage.

V41 fixed N16 full-chain C1/Off1/On1/On2/Off2/C2, same GPU0 and native10/100
cold-L2 CUPTI timing:

| Format | T32 | T128 | T512 |
|---|---:|---:|---:|
| NVFP4 | 1.003737× | 1.003346× | 1.002917× |
| MXFP8 | 1.003614× | 1.002678× | 1.002035× |
| MXFP4 × MXFP8 | 1.004062× | 1.005403× | 1.001826× |

These ratios compare clean853 to publication+prefetch. Every affected point
improves in both repeats, but the gains are small and do not close the TRT gap.
The publication/factored-loader-only arm generally costs0–0.24%; the unchanged
W4A16 arm is a timing noise control. All source, route and tactic checks passed.
Evidence: `evidence/pdl-weight-prefetch-r2-fixed/{summary.json,summary.md,raw}`.
This is fixed-tactic diagnostic evidence, not native AUTO retention.

An independent `flashinfer-pdl-weight-prefetch-multistage-review` now primes
`min(num_stages, ceil_div(K, tile_k))` existing A/SFA stages before waiting.
Its count comes from the actual compiled pipeline and reduction extent; no
model, token, dtype-specific stage count or additional storage is introduced.
K384/K2304 replay gates cover short K and stage-ring wrap before fixed screening.

Provenance-only PR body revision `pr-body-final-853a-b300-r3.md` was published
and read back exactly (64499bytes, SHA256
`c5fd21ff93a2af0da2a1a021ec927f60492dfb94478aea0039b939b7087a9ed2`).
It distinguishes host nvcc13.2.78 / PyTorch CUDA13.2 from CuTe's Python JIT
packages `nvidia-nvvm==13.3.73` and `nvidia-cuda-nvcc==13.3.73`, confirmed
identically in all12 native original/final records, and pins those packages.
All tables, timings, validation and scope are unchanged. Readback:
`artifacts/pr7290-published-853a-b300-r3.json`; head remains clean853a and draft.

## Capacity-derived full-stage prefetch

The multi-stage prototype passes351 exact captured replays:324 K384/K2304
cases plus27 restricted-SM persistent-work-tile cases. Independent codegen
inspection finds four distinct expected-byte barriers and A/SFA transfers before
the wait for the captured NVFP4 N16/K2304 specialization; B/SFB remain after it.
The fifth K iteration reacquires normally, as do later persistent work tiles.

V41 fixed N16 C1/single1/multi1/multi2/single2/C2, native10/100 cold-L2 CUPTI:

| Format | T32 clean/multi | T128 | T512 |
|---|---:|---:|---:|
| NVFP4 | 1.017542× | 1.009001× | 1.005491× |
| MXFP8 | 1.010904× | 1.005916× | 1.005536× |
| MXFP4 × MXFP8 | 1.007583× | 1.005977× | 1.006180× |

All nine points improve in both repeats and beat the single-stage variant.
Source, routes and fixed tactics verify for every arm. Evidence:
`evidence/pdl-weight-prefetch-multistage-r1-fixed`.

The separate integrated copy `flashinfer-pdl-weight-prefetch-integrated-review`
adds explicit default-false public-wrapper knobs and enables their matching
publication/prefetch contract only inside supported complete chains. It also
confines both routing release and the first startup trigger to warp0, after the
unchanged all-thread wait. Per-token quantization, Rubin/localized, fused finalize
and two-CTA FC2 retain their existing path. FC1 can still be two-CTA or CLC.
Frozen five-file patch:
`a92c766dfdfc1ca8051b0e5c93afe90b77225391c1203271137debcbb3d3d685`.

Actual public-On replay gate passes324 cases, including FC1twoCTA→FC2oneCTA
and two-CTA FC2 fallback, without mutating the selected On flags. Existing49
focused repository tests pass (49passed,98warnings,25.70s);83 source pins remain
unchanged. Evidence: `evidence/pdl-weight-prefetch-integrated-r1` and
`evidence/pdl-integrated-focused49`.

Native AUTO retention is running on fixed per-model/family GPUs: V3NV5/MX4,
V41NV7/MX6. C1 controls are complete; A1 includes the four full public backend
tables, then A2 and C2 use CuTe-only selectors. All13 tokens are measured;
1/2 remain excluded from retention. The benchmark differs only by one static
readiness assignment and two explicit call kwargs, proven by full-module AST
reversal in `public-contract.json`; old source receipts are not rewritten.

Latest user steering additionally prioritizes cache tiers under the new early
A/SFA traffic and independent startup work beyond the prefetched operands.
Those experiments use separate source copies and the frozen integrated candidate
as their control. Streamed weights, reused activation payload/scales and their
handoff lifetimes must be considered together; avoid blanket LAST protection
of buffers whose useful lifetime has ended.

## Retained full-capacity A/SFA prefetch

Committed and pushed `24c48b9fd5d7c38fdcea213376602f97635c4ef9`.
All 83 source pins match the measured integrated candidate exactly. The
production and review copies are clean; the independent experiments remain
unstaged in separate source copies. Retention binding and the independently
recomputed 43 evidence hashes are in
`evidence/pdl-weight-prefetch-retained/receipt.json`.

Clean853 → retained24c paired native AUTO speedups:

| Model | Format | Decode 4–512 | Prefill 4096–16384 | All retained |
|---|---|---:|---:|---:|
| V3 EP8 | NVFP4 | 1.012010× | 0.999296× | 1.008526× |
| V3 EP8 | MXFP8 | 1.006996× | 0.991430× | 1.002727× |
| V3 EP8 | MXFP4 × MXFP8 | 1.007438× | 1.000762× | 1.005613× |
| V41-Flash EP4 | NVFP4 | 1.018181× | 0.999376× | 1.013017× |
| V41-Flash EP4 | MXFP8 | 1.010011× | 1.012533× | 1.010698× |
| V41-Flash EP4 | MXFP4 × MXFP8 | 1.011057× | 0.995969× | 1.006919× |

Every decode group improves in both repeats; all six overall geomeans improve.
Prefill results are mixed. V3 MXFP8 T16384 uses the same unaffected two-CTA
N256/M256 tactic with both new behavior flags false; the control changes
724.21→764.20 us while the candidate stays 758.15→759.26 us. This limits causal
interpretation of that point. The existing W4A16 arm is a noise control, not an
optimization claim. Full data and tactic audits are under
`evidence/pdl-integrated-{v3,v41}-{c1,a1,a2,c2}`.

The A1 full public table sweep puts V41 NVFP4 and mixed-format decode roughly
at TRTLLM parity (1.000751× and 1.002421×), while MXFP8 is still about 1.3%
behind (0.986885×). These single-sweep ratios do not establish a stable lead.
The four complete raw tables will replace the previous final tables after the
current cache and metadata candidates are resolved.

Existing focused tests pass 49/49; the real public-chain gate passes 324 exact
changing-data graph replays and the named persistent codegen gate passes 27.
Scoped pre-commit and commit hooks pass. Broad tests and sanitizers remain
deferred. Source and generated-code audits preserve A/SFA-only early access,
GPU release before the FC1 trigger, B/SFB after the wait, and one acquisition
per stage. Stage capacity and static K determine prefetch depth.

Next experiments use this retained source as their byte-identical control:
SFA-FIRST, followed separately by B-LAST activation protection, and independent
first-tile metadata before the wait. The initial SFA fixed screen improves all
six model/format geomeans by about 0.24–0.56%; native AUTO retention is pending.

## Retained cache tiers and subsequent startup experiments

Committed and pushed `8b74eb6fa77651bb20dacb56b8e13872f3ad9885` after the
full two-model native AUTO sweep. Its source matches the measured cache-tier
candidate (base853 plus patch
`dddd7db2146b2f6acbcdbf6868a9d6248052c49da6c89b5cf8937a1801ad611b`).
The actual Git parent is24c; both identities are explicit in
`evidence/pdl-cache-tier-retained/receipt.json`, which independently verifies
83 source pins and42 input evidence hashes. Production and review clones are
clean. SFA uses FIRST and FC2 B uses LAST only in the existing eligible
prefetch geometry; SFB remains normal.

Direct24c →8b74 native AUTO speedups (1/2 tokens measured but excluded):

| Model | Format | Decode 4–512 | Prefill 4096–16384 | All retained |
|---|---|---:|---:|---:|
| V3 EP8 | NVFP4 | 1.007790× | 0.999684× | 1.005573× |
| V3 EP8 | MXFP8 | 1.005336× | 0.998044× | 1.003342× |
| V3 EP8 | MXFP4 × MXFP8 | 1.005470× | 1.003162× | 1.004840× |
| V41-Flash EP4 | NVFP4 | 1.005204× | 1.000392× | 1.003889× |
| V41-Flash EP4 | MXFP8 | 1.005150× | 1.008473× | 1.006056× |
| V41-Flash EP4 | MXFP4 × MXFP8 | 1.007677× | 1.002214× | 1.006184× |

All six decode groups improve in both repeats; all overall means improve.
The inactive M256/N256 two-CTA FC2 specializations produce byte-identical
PTX, cubin, SASS and resource reports between the omitted-policy control and
explicit-zero-policy candidate for all three formats. Nine changing-route
replays also match exactly. This closes the code-generation concern for these
specific wide geometries, without attributing timing noise to inactive hints.
Evidence: `evidence/pdl-inactive-wide-r1/comparison.json`.

The retained full-table A1 sweep places V41 decode at1.002014× NVFP4,
0.996605× MXFP8, and1.012698× mixed against same-format TRTLLM. These are
single-sweep ratios, not a stable lead. The MX arms in these historical tables
assemble low-level components inside the benchmark; they must not be described
as measurements of the forthcoming public MX wrapper.

Subsequent isolated screens, all preserved as unstaged source copies:

- Two independent A/SFA issuer warps:135 exact replays and byte-accounting
  codegen pass, but V41 fixed decode means are1.000311/0.993517/0.995178×
  for NV/MX8/mixed. Rejected; no V3/native sweep.
- Descriptor prefetch:324 exact replays plus27 named codegen cases pass;
  register/SMEM/local resources equal control. V3 means are
  1.000654/0.999196/1.001290×; V41 are1.000945/1.000377/1.000874×.
  Held, not retained: tiny gains with repeatable small V3 MXFP8 losses.
- Live-count-only metadata hoist:351 exact replays, unchanged resources;
  V3 means1.00180/1.00128/1.00187× and V41
  1.00027/1.00156/1.00242×. Eligible minor candidate, not yet retained.
- FC1 A/SFA prefetch:216 exact replays plus9 preparation-codegen replays;
  release precedes the first trigger in PTX and SASS. Corrected per-token
  observer gate adds36 exact replays. The initial observer-only failure is
  preserved and is not a kernel/runtime incompatibility claim. Fixed V3
  means0.998208/1.003232/1.001221×; V41
  1.001794/1.002745/0.997797×. All six T4 points improve, but larger decode
  losses make FC1-only unretained. A separate producer-only dependency wait
  will test overlapping scheduler/consumer startup while all128 activation
  producer lanes remain dependency-gated.

## Public benchmark ownership correction

The user identified that the MX benchmark assembles sort/FC1/FC2/combine and
selects `prefetch_weights_before_wait` itself. Replace that implementation with
the existing public function/wrapper. Extend the library to accept unfused
W4A8 and homogeneous MXFP8 as `quant_mode="w8a8"`, matching the established
W4A4/W4A8/W4A16 naming. Library code owns all PDL/prefetch policy. Preserve
the quantized inputs, routing, cache/timer contract and graph-autotuning
configuration; record an exact assembly-to-public equivalence gate before
fresh final timings. Historical measurements and receipts remain immutable.
Preparation and trace/reference support must describe the actual weight
precision rather than silently falling back to W4A4 semantics.
## Public API parity and startup screens, 2026-10-25 follow-up

Final public source is pushed as `adf02fdd4a8fd2a5d4d2ca54b6969cd65572d93d`.
All85 pins match the reviewed API candidate, and the clean source passes53
focused tests. FC2-only producer waits and init-fence consolidation are held;
neither earns another runtime behavior. The full public-table refresh is
`evidence/public-api-final-adf-r1` and preserves all13 tokens.

The completed A1 tables place V41 MXFP8 decode at0.988745x versus matched
TRTLLM, with the larger remaining point gaps at T32–512. V41 NVFP4 decode is
1.003324x and therefore near parity, not a stable-lead claim. V3 NVFP4 decode
is1.027671x. These are single-sweep backend comparisons, distinct from the
repeated implementation-retention comparison. If optimizing further, profile
the V41 MXFP8 middle decode range before repeating the now-held FC1 prefetch,
split-issuer, fence or producer-wait experiments. Raw tables and independently
recomputed ratios are retained in
`evidence/b300-public-final-bridge-r1/final-a1-matched-backend-check.json`.

The public API candidate on clean `8b74eb6fa77651bb20dacb56b8e13872f3ad9885`
uses `quant_mode="w8a8"` for homogeneous MXFP8 and admits unfused W4A8.
It removes the benchmark's private MX runner and all benchmark-selected
pipeline policies. The frozen seven-file patch is
`167e501598e18a4fe6225f715853bc486f691e80558e97e2d1ab00ffba36c0f6`.
There are 85 source pins, including public configuration and trace templates.

The compatibility gate passed 72 exact output comparisons, with identical
quantized inputs, filtered tactics, graph-autotune policy and actual kernel
arguments. Six new/extended API/cache tests and seven existing W4A8 tactic
cases pass. The independent audit is
`evidence/public-mxfp-moe-r1/independent-audit.json`. A bounded native AUTO
C–A–A–C screen is pending on both models, all three formats, tokens
4/32/128/512, using the unchanged 10/100 cold-L2 timing protocol. This is not
yet a performance retention claim.

FC1 prefetch plus producer-only dependency waits remains unretained. Relative
to the retained FC2-prefetch control, fixed decode geometric means are
V3 NV/MX8/mixed 0.998696/1.006356/1.001813 and V41
1.002319/1.004784/0.998657. V41 mixed T32/T128/T512 lose in both repeats
(0.994614/0.993988/0.992748 paired ratios). Moving scheduler/MMA/epilogue
setup ahead of the producer wait does not remove that FC1 regression.
Evidence: `evidence/pdl-producer-wait-r1-fixed/summary.json`; source, gates
and rejected edits remain in the separate review copy.

The next isolated screens use clean 8b74: FC2-only producer waits and
initialization-fence consolidation. Neither changes stage capacity or model
thresholds. The fence candidate passes 45 changing-route exact comparisons;
all 27 named compiled kernels retain registers, shared memory, occupancy and
cluster/barrier/PDL instruction sequences. Predicate coalescing accompanies
some removed fences, so any timing gain must be attributed to the complete
candidate, not just a count of fence instructions. Timing is still pending.


## Baseline and benchmark-family update

User changed retention/performance baseline to same-shape TRTLLM; stop further CuTe-before/after campaigns. The interrupted api-cleanup-final-r1 campaign is preserved with an explicit cancellation record; completed historical results remain intact. Clean2b7 cleanup remains pushed and validated (68focused tests,84cross-source exact outputs,168changing-route replays total). Future final bodies use matchingTRT comparisons and four raw model/family tables.

Add independent CuTe/TRT per-tokenNVFP4 arms alongside existingW4A4/W4A16; remove the old global --use-per-token-activation option. Per-token activation recipe: disable baseFP4 quantization fast math, MSE4over6 withE4M3max256 and4over6fastmath enabled. Initial andFC2activation quantization use matching scale inverse1/(256*6); weights remain the existing standard preparation. Restore scoped settings between arms. Shorten MXFP4xMXFP8 display label toMXFP4x8; remove BF16 speedup columns, retain BF16 latency baselines.

V41MXFP8 profiling on cleanadf identifiesFC2 memory throughput as the remaining mid-decode gap. AtT128 isolatedNCU replayFC2: CuTe162.272us/80.70%DRAMpeak versusTRT154.240us/84.78%; tensor<9%,longscoreboard~80–85%,nospills. ExactCuTeTMA bytes1,239,367,680 match82experts*40tiles*9Ktiles*(32768weight+1024SFA+8192activation); BphysicalN32 accounts241.83MB. TRTtotalTMA1,059.89MB is consistent withN8activationloads (~60.46MB) plus~1.89MBSFB. Excess traffic is activationoverfetch, notweightscale/policy; do notblindlyreverse retainedcachetiers orrepeat oldN16+bulk experiment. Preserve evidence/v41-mxfp8-gap-adf-r1 and evidence/v41-mxfp8-gap-adf-ncu-r1.


## Standalone per-token tables and model defaults

Pushed benchmark commit `c5c79ef0dbfaa805f992cf5007d6376110876500` and V3 EP8 default follow-up `6b6bf0cf9da684f8a7d60f77b6b0c135f4c54c8f`. The per-token change passed 62 CPU checks and a focused B300 gate: three CUDA/CuTe quantization shapes were byte-identical across payload, block scales and token scales; public function/wrapper outputs matched; both internal FC2 calls received the requested recipe. V3 T4 and V41 T32 native selector smokes passed. The defaults follow-up passed 26 CPU cases covering model defaults and explicit overrides.

All four fresh public tables completed on clean c5c, with 13 rows each and exit 0. Exact commands explicitly used V3 EP8 and V41 EP4, so the subsequent default-only change is inactive for those runs. Raw evidence is in `evidence/per-token-final-r1-v3/raw` and `evidence/per-token-final-r1-v41/raw`. These are one sweep per model/family, not repeatability evidence; no new implementation-before/after campaign was run.

The user subsequently requested a third preset, Kimi K3 EP8, from the distributed benchmark: hidden 3584, intermediate 3072, 896 experts, top-16, ungrouped sigmoid routing, SiTU(4,25). Preserve table columns and show unavailable backend cells when the activation is unsupported. Add two K3 tables without rerunning the completed V3/V41 data. Source and helper receipts must distinguish the measured commits.

A bounded read-only NCU follow-up proposes copying an N16 prefix into unchanged physical N32 B storage, rather than shrinking allocation or changing stages/TMEM/epilogue. The predicted reduction at the profiled V41 MXFP8 T128 point is 120,913,920 TMA bytes (9.756%); this is not a latency prediction. Compilation/layout validation remains pending. See `evidence/tma-b-copy-prefix-feasibility-r1/review.md`.


## Final six-table publication

Pushed and retained source: `84f9a8e79ce2d5bf93243dfcc4b1fb117441f682`. PR #7290 now displays six complete outputs directly: NVFP4 and MXFP for V3 EP8, V4.1-Flash EP4, and Kimi K3 EP8. Old before/after tables and duplicate aggregate summaries were removed. The MX tables use the final grouped `Speedup vs TRTLLM` formatter with captured full-precision medians; this is a disclosed display-only replay, not new timing.

The four V3/V41 sweeps were measured at c5c79ef0; K3 MX at 4ec7a29d; corrected K3 NV at 84f9a8e7. The failed original K3 NV sweep remains local and contributes no table rows. The pinned native catalog has no per-token NVFP4 SiTU kernel, so that K3 arm, TRTLLM MXFP8 and BF16 are explicitly N/A. All seven supported K3 public arms passed the focused capability gate; this does not establish cross-backend numerical equality.

Publication: `evidence/per-token-final-body/publication.json`; body SHA256 `1bb0cb0ba159aadd35d1062aaeefea1f604e972a2e7e60b1091f04786bc064ff`, 58,635 bytes. GitHub readback matches exactly; PR remains draft at the pushed head. The renderer and its 195 bound inputs reproduce the body with reads from all review source copies blocked. Preserve the evidence snapshots, helpers, ledgers and original stdout.


### Concise public presentation

At the user's request, the published body now keeps brief design/validation prose and the same six direct outputs, with an opening token-by-token CuTe DSL W4A4 versus TRTLLM W4A4 (NVFP4) speedup table for V3 EP8, V4.1-Flash EP4 and Kimi K3 EP8. All 39 ratios were independently recomputed from captured full-precision medians. Detailed setup, provenance, failed attempts and validation records remain local.

Latest body: `pr-body-final-84f9-trt-only-concise-speedups.md`; SHA256 `70d32c5d32f6624ec2bb623099b122cdcfec7133bf67a8519849adae63991337`. GitHub readback matches exactly and the draft PR head is still clean/pushed 84f9a8e7. Receipt: `evidence/per-token-final-body/publication-concise-speedups.json`. No benchmark rerun or production source change was needed.


### Workspace cleanup

Removed all 86 redundant FlashInfer source copies, leaving only the clean canonical `flashinfer/` checkout. The first 16 copies had retained-source proofs; the following 70 comprised 64 experiments and six clean baselines. At the user's explicit direction, the newly created recovery archives for the 64 unretained experiments were discarded. Existing optimization ledgers, results, raw benchmark evidence and helper scripts remain intact. `SOURCE_COPY_ARCHIVE_LEDGER.md` records source identities and disposition.

The current concise PR body still renders byte-for-byte from preserved evidence after removing every source copy. Its SHA256 remains `70d32c5d32f6624ec2bb623099b122cdcfec7133bf67a8519849adae63991337`. Cleanup receipts are under `evidence/retained-copy-cleanup-2026-10-25/` and `evidence/experiment-copy-cleanup-2026-10-25/`; `archive-disposition.json` records the intentional unretained archive removal.
