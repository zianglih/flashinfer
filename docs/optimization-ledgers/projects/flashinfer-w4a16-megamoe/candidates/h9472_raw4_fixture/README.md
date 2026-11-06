# Dedicated four-stage fallback fixture

`h9472-raw4-fixture.patch` is unapplied and test-only. It replaces the normalized
H9216/I64/257-token parameter with H9472/I64/257 tokens, retaining ten GPU cases
per rank. The nine other cases, fixture normalization and numerical assertion/
tolerances are unchanged. H9472 has37 K256 tiles; H9216 has36.

The prior H9216 raw4 statement was incorrect for the actual E4/topk2/capacity257
public test. CPU observation of frozen fe4 source through the actual public
factory, `_ensure_compiled` kernel constructor, and the exact `_launch_fc12`
source prefix through `_fit_raw_stages` found:

| H | EP | Selected raw stages | Selected dynamic SMEM bytes | Raw5 bytes |
|---:|---:|---:|---:|---:|
|9216|1 and2|5|231936|231936|
|9280|1 and2|5|232448|232448|
|9312|1 and2|4|214272|232704|
|9472|1 and2|4|215552|233984|

The available per-CTA capacity is232448 bytes. These counts apply to default
M256/N128, atomic scheduling, E4/topk2/capacity257 and I64. N64 has a different
activation staging size, so the numerical geometry overrides must not inherit
the raw4 claim. H9472 gives a clear fallback margin rather than an exact-boundary
case. GPU validation and real compiled-geometry observation remain root-owned.

Source hashes: kernel `58e4af6b935612ed1a68c27fbf355819a02d5a3e622e3fcf5e1dcff0f91c83f7`,
frontend `d15098fde1977b84b883b08dbd5e7cbb04ee83988f2fc7c28d3159e98e5ac586`.
The source hashes match fe4f8132. Allocation, device-properties queries and
`cute.compile` were mocked; all actual constructors/storage factories and CuTe
layouts ran on CPU, with no CUDA compile or launch. Raw records are
`../../logs/public-h9216-fitter-cpu-001.json`; the successful log is
`../../logs/public-h9216-fitter-cpu-002.log`. The first log retains a helper-only
struct-introspection failure before the observation completed.

The earlier raw/normalized H9216 numerical and stage-attribution artifacts stay
unchanged in the ledger. They establish split/Mega parity and the need for
fan-in normalization; they did not record the fitted stage count.

```bash
git -C flashinfer apply ../candidates/h9472_raw4_fixture/h9472-raw4-fixture.patch
# Default geometry, after application:
CUDA_VISIBLE_DEVICES=0 python -m pytest \
  flashinfer/tests/moe_ep/test_cutedsl_w4a16_mega.py \
  -k 'h9472_i64_m257 and ep1' -vv -s
```

Ruff check/format, Python syntax and `git apply --check` pass. No source or
GPU operation was performed while preparing this artifact.


## Observed H9216 GPU control

The root subsequently ran the original H9216 parameter at explicit M256/N128
on the unchanged two-stage geometry baseline (kernel SHA
`5ea9b59f882cef50e6da6c915295acaa626b92331f4fb592c0744b47628de866`).
The actual public config is E4/topk2/capacity257, atomic/group512/flag4/epi(2,4).
Its `compiled_geometry` record observes raw5, transform2 and accumulator2;
the single numerical case passed with the original tolerance. Thus the
five-stage count is confirmed by a real compiled kernel as well as by the
independent frozen-fe4 CPU fit.

Evidence: [observed record](../../logs/tmem-h9216-observed-control-001/observed/rank0.jsonl),
[test output](../../logs/tmem-h9216-observed-control-001/test.log),
[source hashes](../../logs/tmem-h9216-observed-control-001/provenance.log), and
[postvalidation](../../logs/tmem-h9216-observed-control-001/postvalidation.log).
The post-check invokes `validate_records(..., 'm256n128', 1, expected_tests=1)`;
it checks the expected test result and actual geometry rather than relying on
the selector alone. This control is distinct from the later stage3 candidate.

The root has now applied the H9472 test patch. Its GPU validation remains
separate from the H9216 count correction above.
