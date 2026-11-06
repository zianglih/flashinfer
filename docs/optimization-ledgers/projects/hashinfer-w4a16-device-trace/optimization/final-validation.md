# Final retained-stack validation

Prepared 2026-09-25. This runbook and driver have only CPU validation; no GPU test result is implied. Run them after deciding the retained stack and completing any owned W4A16 port. They do not promote candidates, acquire GPUs, wait for a queue, or edit production source.

Files: `run-final-validation.sh`, `final_validation.py`, and `final_validation_rank.py`. Copy all three together into the remote effort's `optimization/`. `verify_final_validation_nodes.py` is the reusable CPU node-ID audit. Its first result is `final-validation-node-check/summary.json`: all 36 selected IDs were verified with real pytest collection of source signatures and unchanged pytest decorators, with test bodies replaced by `pass` and no CUDA imports. The real selected source is collected again before execution.

## Core matrix

| Suite | GPUs needed | Existing cases | Purpose |
|---|---:|---:|---|
| `ep4` | 4 | 8 | GLM5 H6144/I2048/E256/K8; **global** T1 and T1024, random/skewed, FC2/FC1 routing-weight placement |
| `ep8` | 8 | 4 | Same GLM5 shape, global T128, random/skewed, both weight placements; EP8 guard |
| `tails` | 2 | 10 | Both return modes on small/tail geometries, N64/N128 pipeline wrapping, and long activation tail |
| `lifecycle` | 2 | 6 | Existing changing-batch/empty-refill cases under static and atomic scheduling, plus collective graph replay/runtime-alpha reload in both return modes |
| `prestaged` | 1 | 6 | Existing direct frontend tests stage inputs before launch; regular, tail and singleton expert shapes, both return modes |
| `synccheck` | 4 | 2 | Conditional existing EP4/O3 synccheck matrix, both weight placements; select only if a **new barrier** is retained |

Each strict GLM5 outer case internally runs all eight deterministic tactics at O2 and O3, covering N64/N128, G512/G1024 and both return modes. Each compiled setting has two eager checks and four graph replays. That is 32 compiler/tactic/execution combinations, 96 independent-reference comparison records, and 496 pairwise comparison records per case. Every comparison requires finite BF16 bit equality, including signed zero. The driver requires these exact records and checks their completion; a pytest skip, missing report, incomplete scan, mismatch, timeout or source mutation fails the suite.

T1 is one **global** token, so EP4 includes three empty source ranks. T1024 is 256 tokens per rank. The native full grid remains enabled in this core matrix. These tests validate numerics and lifecycle, not speed. Supplemental tail/prestaged/uneven-routing tests retain their existing tolerance/reference contracts; they must not be described as additional strict GLM5 bit-equality evidence. Manual graph tests compare replay with eager and exercise in-place alpha updates.

## Exact strict node IDs

All use `tests/moe_ep/test_w4a16_megamoe_numerics.py::test_w4a16_megamoe_numerics` with the following parameter suffixes:

```text
[topk_fc2-random-ep4-glm5-t1]
[topk_fc2-random-ep4-glm5-t1024]
[topk_fc2-skewed-ep4-glm5-t1]
[topk_fc2-skewed-ep4-glm5-t1024]
[topk_fc1-random-ep4-glm5-t1]
[topk_fc1-random-ep4-glm5-t1024]
[topk_fc1-skewed-ep4-glm5-t1]
[topk_fc1-skewed-ep4-glm5-t1024]
[topk_fc2-random-ep8-glm5-t128]
[topk_fc2-skewed-ep8-glm5-t128]
[topk_fc1-random-ep8-glm5-t128]
[topk_fc1-skewed-ep8-glm5-t128]
```

The other exact IDs are listed in the CPU audit summary and in `--suite <name>` planning output. For example, the tail suite includes `tests/moe_ep/test_moe_ep_nvfp4_cutedsl_mega_multirank.py::test_nvfp4_mega_geometry_and_pipeline_tails[w4a16-n64-wrap-epi_warps]`. Synccheck uses `tests/moe_ep/test_w4a16_megamoe_sanitizer.py::test_w4a16_megamoe_sanitizer[topk_fc2-synccheck-ep4-O3]` and the corresponding `topk_fc1` ID. It is launched with ordinary pytest; that existing test starts its own four workers.

## Source and environment setup

Use the existing validated B300 image `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2, PyTorch 2.12 NVIDIA prerelease, and the same CUTLASS/NVSHMEM environment as the retained experiment. The strict oracle depends on the validated BLAS/split-K control API; changing software is a separate validation variable.

Set the **final byte digest from the frozen source manifest**, not a dirty checkout's Git HEAD:

```bash
export HASHINFER_OPT_SOURCE=/workspace/hashinfer-trace/optimization/retained
export HASHINFER_OPT_EXPECTED_SOURCE_SHA256=REPLACE_WITH_FINAL_SOURCE_SHA256
export HASHINFER_TRACE_IMAGE=nvcr.io/nvidia/pytorch:26.05-py3
export CUDA_VISIBLE_DEVICES=0,1,2,3
```

The digest algorithm is the experiment's existing SHA256 over sorted relative paths and contents of `hashinfer/**/*.py`. For a CPU-only plan, omit the expected hash until the manifest is finalized:

```bash
bash /workspace/hashinfer-trace/optimization/run-final-validation.sh --suite ep4
```

Planning imports no torch/CUDA modules. Execution requires the explicit expected hash and a new output directory. Git is optional: tar snapshots report `git_head: null`; the declared base and source byte digest remain available. Every test starts fresh processes, every rank verifies the imported package location and source digest, and each rank saves source closure and software versions. The final summary checks source and selected test files remained unchanged. Do not run under `run-iket`; leave `MEGA_USE_NCU` unset/0 and `MEGA_NO_DIST` unset. The prestaged test sets its own single-rank environment.

## Manual execution after assignment of the GPU slot

Run one suite at a time. Commands use the existing explicit loopback rendezvous, avoiding the hostname failure seen with `torchrun --standalone`.

```bash
bash /workspace/hashinfer-trace/optimization/run-final-validation.sh \
  --suite ep4 --run --owned-transform \
  --output-dir /workspace/hashinfer-trace/optimization/results/final-ep4-1

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
bash /workspace/hashinfer-trace/optimization/run-final-validation.sh \
  --suite ep8 --run --owned-transform \
  --output-dir /workspace/hashinfer-trace/optimization/results/final-ep8-1

export CUDA_VISIBLE_DEVICES=0,1
bash /workspace/hashinfer-trace/optimization/run-final-validation.sh \
  --suite tails --run --owned-transform \
  --output-dir /workspace/hashinfer-trace/optimization/results/final-tails-1
bash /workspace/hashinfer-trace/optimization/run-final-validation.sh \
  --suite lifecycle --run --owned-transform \
  --output-dir /workspace/hashinfer-trace/optimization/results/final-lifecycle-1

export CUDA_VISIBLE_DEVICES=0
bash /workspace/hashinfer-trace/optimization/run-final-validation.sh \
  --suite prestaged --run --owned-transform \
  --output-dir /workspace/hashinfer-trace/optimization/results/final-prestaged-1
```

Use `--owned-implementation` (alias `--owned-transform`) for the final owned
port. It verifies the shared grouped-GEMM helper, vendor token communication
and vendor IKET adapter exactly match PR base `406bc0d`, and requires an owned
`_MegaMixedInput._transform_tile` with both blocking waits intact. Specify the
exact **remaining** probe kinds using `--transform-probes none|raw|tmem|both`:
`none` is the default and means both lookahead probes were removed; `raw`
means only raw-TMA probes remain; `tmem` means only TMEM-slot probes remain;
`both` matches original probe behavior. The selected mode is recorded in the
plan and must match the method. This supports trace ownership even if no
probe optimization is retained. A CPU guard check accepts the R1 port's
`both` mode and rejects the other three modes.

The shared-helper SHA256 must be
`f283fdc3b627e04923951588a42c543be95573899a0eb313c68da3bed0671f76`.
The earlier experiment base `002ef145` already contains shared markers and
is not the restoration target. This guard supplements the full method/import
AST audit in `prepare_owned_trace_port.py`; it is not a substitute for native
code inspection. The sample commands above use the default `none` and must
be amended to the actual retained mode if it differs. A protected-file change
invalidates the owned-only claim; do not remove the guard to conceal it.

For a deliberately smaller gate, pass one or more exact `--node` IDs from the suite. For example, add `--node 'tests/moe_ep/test_w4a16_megamoe_numerics.py::test_w4a16_megamoe_numerics[topk_fc2-random-ep4-glm5-t1024]'` to check the all-tactic/O2/O3 target case first. The plan/summary records `subset: true` and the available full-suite case count; a subset pass is never recorded as full matrix coverage. Omit `--node` for the complete suite.

Each suite stops on its first failed case and does not start another candidate or automatically retry. Default timeout is three hours per fresh-process case (`--timeout-seconds` overrides it); the existing sanitizer also has its own two-hour worker timeout. On timeout/interruption the driver terminates its recorded process tree, including separately grouped torchrun ranks, and leaves incomplete evidence. A completed `summary.json` with `passed: true` is required. Cold compilation of 16 compiler/tactic settings per strict case, four staging ABI specializations, large references and pairwise checks can take substantial time; reserve hours rather than assuming a quick smoke test. No runtime estimate has been measured for this final driver.

## Conditional checks for retained communication changes

If `counts_overlap`, `counts_fence`, or `parallel_payload` is retained, re-run the stateful qualification on the **actual owned final port**, not only its experimental predecessor. Include index 2 (N64/G512/epilogue), index 6 (N64/G1024/epilogue), and index 1 (N128/G512/dispatch); indices 2 and 6 cover the observed target winners.

```bash
export CUDA_VISIBLE_DEVICES=0,1,2,3
export HASHINFER_QUAL_TACTICS=2,6,1
export HASHINFER_QUAL_PROFILES='partial33:heterogeneous glm5:full'
export HASHINFER_QUAL_OUTPUT=/workspace/hashinfer-trace/optimization/results/final-stateful-1
bash /workspace/hashinfer-trace/optimization/run-dispatch-qualification.sh
```

That existing runner accepts the same source and expected-hash environment. It verifies source identity without `.git`. It adds changing routes, score-only updates, both counter banks, first-graph-after-update, queued replay, empty/refill, partial local-expert warp, and heterogeneous CTA counts. The strict matrix covers both routing-weight placements; an additional stateful FC1-placement run is useful if staging/score handoff is changed:

```bash
python -m torch.distributed.run --nnodes=1 --master-addr=127.0.0.1 \
  --master-port=29791 --nproc-per-node=4 --max-restarts=0 \
  /workspace/hashinfer-trace/optimization/qualify_dispatch_overlap.py \
  --profile partial33 --grid heterogeneous --tactics 2,6,1 \
  --apply-topk-in-fc1 \
  --output-dir /workspace/hashinfer-trace/optimization/results/final-stateful-fc1-1
```

If the payload split's new NB11 handoff is retained, additionally run the existing synchronization sanitizer cases:

```bash
bash /workspace/hashinfer-trace/optimization/run-final-validation.sh \
  --suite synccheck --run --retained-new-barrier --owned-transform \
  --output-dir /workspace/hashinfer-trace/optimization/results/final-synccheck-1
```

Each sanitizer case covers random/skewed global T1/T128/T1024, all eight deterministic tactics, eager/graph at O3. The driver requires the opt-in flag and rejects skipped cases. Removing transform peek calls alone does not add a barrier and does not automatically select this suite. Counts' publication proof and native release/acquire inspection remain necessary; synccheck does not prove cross-GPU payload visibility.

Before promotion, restore protected/shared experimental source when porting into the owned adapter, audit the final delta, and repeat matched uninstrumented target performance on the final source. Passing qualification does not establish a speedup. Experimental results and incomplete/skipped suites stay separate from final-head evidence.

## Evidence and preparation checks

Each suite saves its exact node plan, source/test/harness hashes, real collection log, per-case command, complete worker log, per-rank JUnit/provenance, strict JSON/CSV reports where applicable, and a terminal summary. The rank wrapper delegates to unchanged pytest functions. It does not implement replacement numerical tests or adjust tolerances.

CPU preparation validation: source-derived pytest node collection (36 selected nodes), Python AST/syntax checks, shell syntax, plan generation for every suite, and tar-snapshot metadata support. Native compilation and execution remain pending. The bounded matrix excludes exhaustive token powers, memcheck/racecheck, NCU replay, optional in-kernel reduction, new activation variants and package parity. Preserve prior broader evidence without presenting it as testing the new final source.

## Final-source native performance driver

`run-final-native.sh` runs the uniform256/rank target, the complete 13-row native EP4 sweep and the complete 13-row native EP8 sweep, in that order and serially. It uses `benchmark_checked_final.py`, requires an explicit absolute source path, a 64-hex package digest and a lowercase 40-hex tested commit, and does not select a candidate. The commit is a caller attestation for tar snapshots; package bytes are verified before launch and on every rank. It never substitutes the experimental base commit for the tested commit.

Copy these two files together into the remote effort's `optimization/`. Prepared hashes:

```text
run-final-native.sh
  c34093547ba7a1e7630e7a90d1ce76c259625cd6f4608efcd2e1dde9856b1b00
benchmark_checked_final.py
  42f7ee3c15b575048013eb9d5f92f0df331cdfffdf17b699dbd9f2fcaa7a9222
```

After freezing and committing the selected final source, replace both placeholders with its exact recorded values:

```bash
export HASHINFER_OPT_SOURCE=/workspace/hashinfer-trace/optimization/retained
export HASHINFER_OPT_EXPECTED_SOURCE_SHA256=REPLACE_WITH_64_HEX_FINAL_PACKAGE_SHA256
export HASHINFER_OPT_TESTED_COMMIT=REPLACE_WITH_40_HEX_FINAL_TESTED_COMMIT

# CPU-only hash/argument plan; creates no result directory and launches no workers.
bash /workspace/hashinfer-trace/optimization/run-final-native.sh \
  --plan final-owned-native-1

# Run only after assigning this task the exclusive GPU slot.
bash /workspace/hashinfer-trace/optimization/run-final-native.sh \
  --run final-owned-native-1
```

The result label must be new. The driver atomically reserves `optimization/results/final-owned-native-1/`; each scope receives a separate previously nonexistent log and tuning-cache path there. It records the driver/wrapper hashes, source attestation and exact commands. `--plan` is the default when neither mode flag is present. `HASHINFER_FINAL_PYTHON` can name the same environment's Python executable; it defaults to `python`.

Measurement matches `run-incremental-native.sh`: fresh native AUTO selection, three warmups, 100 cold-L2 CUDA-graph CUPTI samples, rank-MAX iteration aggregation, and the unchanged full public-forward boundary. Uniform uses EP4/global1024 and the wrapper's exact H6144 uniform routing fixture. Native EP4/EP8 use H7168 and global tokens `1,2,4,8,16,32,64,128,256,512,4096,8192,16384`. Native AUTO still uses its existing 10 hot tuning samples; this is separate from the final trace fixture's 50-sample hot tuner. The wrapper performs its existing untimed repeat/reference checks after timing; the driver does not add a new numerical suite.

The driver explicitly selects loopback rendezvous, disables elastic retries, clears inherited IKET compiler instrumentation and no-distributed mode, and sets NCU replay mode to 0. Each scope has the same GNU `timeout` limit as the incremental runner: 40 minutes, TERM followed by KILL after 30 seconds. Any worker/timeout failure stops subsequent scopes. Even exit 0 must include the exact expected CSV rows, one benchmark completion and matching source/commit/unchanged-source records. `COMPLETE` is written only after all three scopes pass those checks. An incomplete run keeps its logs and must use a new label if retried; the script never retries or waits for the GPU queue itself.

CPU preparation evidence is `final-native-driver-cpu-check/summary.json`: shell syntax, all three argument lists parsed against the actual benchmark parser AST without CUDA imports, and ten mocked plan/success/refusal/failure cases. Fake CPU launchers checked scope order, explicit metadata, instrumentation cleanup, cache uniqueness, worker-exit propagation, synthetic timeout status 124 and missing-completion rejection. These are synthetic fixtures, not performance results. No real timeout signal-delivery test, GPU process, final-source measurement or retention decision was made during preparation.
