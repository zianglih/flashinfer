# Post-screen exact/codegen qualification

Prepared only; no GPU jobs have been launched. This reuses the successful
`optimization-20261027/warp-specialization/r2/probe_pair.py` public-chain probe,
merges its existing `probe_channel.py` M512 case, and adds only two coverage cases
needed for the current SF32/ownership changes. It does not add a repository test,
change the production benchmark, invoke AUTO, time kernels, or run a sanitizer.

## Coverage

| ID | Format | N | FC1 M | FC2 M | Activation |
|---|---|---:|---:|---:|---|
|0|W4A4|16|128|128|SiTU|
|1|NVFP4 per-token|32|256|256|SwiGLU|
|2|MXFP8|64|128|128|SiTU|
|3|MXFP4x8|16|256|256|SiTU|
|4|W4A4|128|256|256|SwiGLU|
|5|NVFP4 per-token|256|128|128|SiTU|
|6|MXFP8|256|256|256|SwiGLU|
|7|MXFP4x8|128|128|128|SwiGLU|
|8|W4A4|16|512|256|SiTU|
|9|MXFP8|16|512|256|SiTU|
|10|MXFP8|32|128|128|Relu2|

Each case runs static/CLC and PDL off/on against balanced, skewed, empty and
reactivated graph routing. The balanced path verifies more work than resident
clusters, so CLC is effective rather than silently admitted as static. One/two
CTA groups, routeN16/32/64/128/256, one/two channel tiles, narrow/wide partial
tiles, and distinct FC1/FC2 K steps are covered. Every output is compared as
uint8 storage, both across source hashes and within source across schedule/PDL;
this catches signed-zero bit changes that floating 0-tolerance assertions miss.
Unused physical SF padding is intentionally excluded from the output contract.

Full scope is176 graph replays and88 kernel specializations per source. The
original eight cases remain unchanged mathematically; cases8/9 exercise M512
SF16/SF32, and case10 is a non-gated unchanged-path control. This is pairwise
coverage rather than an exhaustive geometry cross-product. Input payload hashes
must match between sources. No native tuning winners are modified.

## Prepare and run after root releases GPUs

Copy this directory to `BASE/optimization-20261028/warp-polish/gate-tools`.
`make_config.py` is CPU-only and normalizes the two existing receipt schemas.
It validates all342 source files and requires clean99f4 control plus a candidate
that differs only in `moe_swap_ab_kernel.py`. Native compilation caches are
reused from each existing source receipt; none is deleted or copied over.
The blockscaled wrapper uses a process-local compile cache, so a fresh gate
process captures its PTX/CUBIN/SASS even when unrelated persistent caches exist.

```bash
BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026
OLD="$BASE/optimization-20261027/warp-specialization/full-rerun"
POLISH="$BASE/optimization-20261028/warp-polish"
GATE="$POLISH/gate-tools"
CASE=pair-barrier
python3 "$GATE/make_config.py" \
  --control-source "$OLD/current-source.json" \
  --candidate-source "$POLISH/$CASE/source.json" \
  --environment-config "$OLD/config.json" \
  --output "$POLISH/$CASE/exact-gate/config.json"

# Select only a GPU released by the root; GPU0 below is an example.
python3 "$GATE/run_gate.py" --gpu 0 --role control \
  --config "$POLISH/$CASE/exact-gate/config.json" \
  --config-ids 0,1,2,3,4,5,6,7,8,9,10 \
  --output-root "$POLISH/$CASE/exact-gate/full"
python3 "$GATE/run_gate.py" --gpu 0 --role candidate \
  --config "$POLISH/$CASE/exact-gate/config.json" \
  --config-ids 0,1,2,3,4,5,6,7,8,9,10 \
  --reference "$POLISH/$CASE/exact-gate/full/control/result.json" \
  --output-root "$POLISH/$CASE/exact-gate/full"
python3 "$GATE/analyze_codegen.py" \
  --control "$POLISH/$CASE/exact-gate/full/control/result.json" \
  --candidate "$POLISH/$CASE/exact-gate/full/candidate/result.json" \
  --features pair-barrier \
  --output "$POLISH/$CASE/exact-gate/codegen.json"
```

For two released GPUs, use groups`0,1,2,3,8` and`4,5,6,7,9,10` with different
output roots. Each candidate references the same-group control result. Control
results from this new clean99f4 gate can be reused for subsequent candidates if
helper hash, config IDs and input hashes match. They are correctness baselines,
not benchmark samples. Never point the new runner at old1e69 control output.

`--features` accepts a comma-separated subset of descriptor-prefetch,sf-cache,
follower-mma,pair-barrier,pdl-guard for the retained combined patch. The codegen analyzer
requires identical geometry/stage/TMEM calculations, all output-bit hashes and
zero local/stack spills. It checks four descriptor-prefetch sites when retained
and64-thread named barriers in every gatedSF32 FC1 specialization when the
pair patch is retained. The pdl-guard feature requires zero dependency-control
instructions in disabled variants. It records all named barriers and SFB TMA operands for
inspection. Follower metadata quorum/leader predicates and cache-policy data
flow are covered by their separate source proofs plus the1/2CTA runtime matrix;
static instruction sites alone do not prove execution ownership or performance.

Preparation passed CPU AST parsing. Exact runtime results, compiler output and
resource assertions are pending; no pass or performance claim is implied.
