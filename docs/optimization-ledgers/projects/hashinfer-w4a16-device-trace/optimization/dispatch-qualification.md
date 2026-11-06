# Focused qualification for early count release

Prepared on 2026-09-25; **not GPU-executed**. The parent owns the serial GPU queue. This is a correctness suite, not a benchmark or broad numerical/sanitizer qualification.

Files: [harness](/Users/ziangli/playground/projects/hashinfer-w4a16-device-trace/optimization/qualify_dispatch_overlap.py), [serial runner](/Users/ziangli/playground/projects/hashinfer-w4a16-device-trace/optimization/run-dispatch-qualification.sh), [compact first-pass runner](/Users/ziangli/playground/projects/hashinfer-w4a16-device-trace/optimization/run-dispatch-first-pass.sh). `HASHINFER_OPT_SOURCE` selects the checkout or source-only tar snapshot; the same scripts can qualify `control`, `store16`, `counts_overlap`, or another candidate. They import that source first and verify the imported package location. They do not edit its files.

The exact `source_sha256` identifies executed Python bytes. `git_head` is optional and is `null` without `.git`; it is never presented as the final identity of dirty candidate source. `declared_base_commit` records the known experiment base `002ef1454cbacde09972ed5e2ec7dcfe37e55749`, overridable with `HASHINFER_OPT_BASE_COMMIT`. Set `HASHINFER_OPT_EXPECTED_SOURCE_SHA256` for a single-arm run to reject a mismatched snapshot before kernel preparation. All four ranks must report the same source digest, and the final digest must match the initial one.

## Reused tests and contracts

- `tests/moe_ep/test_w4a16_megamoe_numerics.py`: `_make_inputs`, `_make_weights`, `_partition`, `_reference`, `_collect_comparison`, `_fingerprint`. The oracle preserves BF16 operands/handoffs, FP32 expert scales/GEMMs, the approximate SwiGLU contract, top-k slot order, and finite BF16 **integer-bit** equality.
- `benchmarks/trace_w4a16_megamoe.py::routing_ids`: the initial/restored GLM5 routes use the current uniform 256-token/rank trace pattern. Activations/scores use the existing numerical fixture's deterministic seed, not the trace baseline file; outputs are recomputed independently.
- Public `MoEEpMegaLayer`, explicit workspace, fixed native catalog tactics, and the graph preparation/capture lifecycle used by `test_w4a16_megamoe_numerics.py` and `test_mega_cuda_graph_multirank.py`.
- Same-workspace, different-size graphs follow `test_mega_layer_multi_size_graphs_and_eager_interleave`'s lifetime pattern. Every graph captures a stable input address; later phases update tensor contents in place.

No alternative reference math, counter-model simulation, or implementation-mirroring assertion is introduced. One layer and outer workspace survive both tactics, using the existing numerical suite's `frontend.apply_knobs` after graphs retire; this avoids finalizing/reinitializing NVSHMEM between tactics.

## Default matrix

| Profile | Dimensions / input ABI | Launch | Purpose |
|---|---|---|---|
| `glm5` | EP4, H6144/I2048/E256/K8, capacity 256/rank; contiguous BF16, int32 IDs | Unmodified full-device grid | Actual target shape; 64 local experts; many initially idle compute CTAs and local score readers |
| `partial33` | EP4, H288/I448/E132/K8, capacity 32/rank; strided BF16, int64 IDs | Rank 0/1/2/3 use 1/2/3/4 two-CTA clusters, respectively | 33 local experts: one full polling iteration plus one active lane in the last iteration; heterogeneous source CTA counts; existing strided/tail shape contract |

Both profiles use O3 and native catalog indices **6** (M256/N64/K256, epilogue return, group1024) and **1** (M256/N128/K256, dispatch return, group512). Both are deterministic, non-IKR configurations. These are two representative tactics, not an AUTO sweep. Default routing weights apply after FC2, directly exercising early local-score preparation after an immediate DONE record. `--apply-topk-in-fc1` optionally checks the other existing rounding contract in a separate run.

Each tactic retains one workspace through these nine phases:

1. Full initial input: uniform target routing for GLM5; random for partial33.
2. Full input routed only to rank 0's experts, with changed scores.
3. Full input routed only to rank 3's experts, with changed scores.
4. Half-sized input routed only to rank 0.
5. All ranks empty: launch must complete; the next phases validate refill.
6. One **global** token on source rank 0, routed to rank 3. Ranks 1–3 have zero local input; source rank 0 owns no compute work but still needs the returned output and its local scores.
7. Refill the full input with a shifted random expert set.
8. Keep phase 7's routes/activations but change only routing scores.
9. Restore the initial fixture after both counter banks and multiple batch sizes have been reused.

After each update, the first kernel is a captured graph replay—there is no updated eager call to repair stale metadata first. Next, three replays are queued without intervening device synchronization; each output is cloned in stream order and independently checked afterward. Finally, one eager forward is checked. The odd five-launch phase length switches the next phase's starting counter-bank parity. All graphs share the same workspace. Whole-empty expected output is trivially empty; meaningful lifetime validation comes from subsequent singleton/full refill.

With two tactics, nine phases, and the default three queued replays, each profile checks **90 collective outputs / 360 rank outputs**; the runner's two profiles check **180 collective outputs / 720 rank outputs**. Warmup forwards and reference-helper launches are additional and are not included in those counts. Any bit mismatch, nonfinite output, capture error, source mutation, or missing summary fails the run.

## Heterogeneous-grid mechanism

The harness wraps `cutlass.cute.compile` **in its own process** and substitutes the existing `max_active_clusters` argument only for calls with the MegaMoE activation/weight/shared-workspace arguments. Rank `r` receives `r+1` clusters; the wrapper records original and actual values and asserts the override was applied to every observed MegaMoE compilation.

The kernel's existing `__call__` derives both launch grid and `token_comm_args.sm_count` from that argument. Fixed nonzero `group_hint` avoids deriving a new scheduling policy from hardware SM count. Symmetric-buffer dimensions are unchanged. This is an artificial correctness stress, not a production cap option or a performance experiment. The full-grid GLM5 profile does not override the value. Confirm the compile records in the final report; native launch tracing is not performed by this suite.

## Commands for the parent queue

Start with the bounded partial-expert/heterogeneous-grid case across the immediate control and both candidates:

```bash
export CUDA_VISIBLE_DEVICES=0,1,2,3
export HASHINFER_TRACE_IMAGE=nvcr.io/nvidia/pytorch:26.05-py3
export HASHINFER_QUAL_OUTPUT=/workspace/hashinfer-trace/optimization/results/dispatch-first-pass-1
bash /workspace/hashinfer-trace/optimization/run-dispatch-first-pass.sh
```

This runs `store16`, `counts_overlap`, then `parallel_payload`, each with `partial33`, heterogeneous clusters and tactics 6/1: **360 rank-output checks per source**, 1080 total if all pass. It stops on the first failed arm. `HASHINFER_QUAL_SOURCE_ROOT` selects a different parent directory for tar snapshots, and `HASHINFER_QUAL_ARMS` can select remaining arms explicitly. Do not carry a single arm's expected-source hash into a multi-arm runner.

If count overlap passes qualification and the parent's target-performance gate, run its GLM5 profile separately:

```bash
export HASHINFER_OPT_SOURCE=/workspace/hashinfer-trace/optimization/counts_overlap
export HASHINFER_QUAL_OUTPUT=/workspace/hashinfer-trace/optimization/results/counts-overlap-glm5-qualification-1
HASHINFER_QUAL_PROFILES=glm5:full \
  bash /workspace/hashinfer-trace/optimization/run-dispatch-qualification.sh
```

After copying the scripts into the remote effort's `optimization/`, run on the existing C2 image/environment. The example path matches this effort's current remote layout:

```bash
export CUDA_VISIBLE_DEVICES=0,1,2,3
export HASHINFER_TRACE_IMAGE=nvcr.io/nvidia/pytorch:26.05-py3
export HASHINFER_OPT_SOURCE=/workspace/hashinfer-trace/optimization/counts_overlap
export HASHINFER_QUAL_OUTPUT=/workspace/hashinfer-trace/optimization/results/counts-overlap-qualification-1
bash /workspace/hashinfer-trace/optimization/run-dispatch-qualification.sh
```

Run the identical script with `HASHINFER_OPT_SOURCE=.../store16` and a different output directory for the immediate control. `control` is also supported. Do not reuse output directories; the runner refuses to overwrite prior evidence. `HASHINFER_QUAL_TACTICS=6` selects a one-tactic first pass, and `HASHINFER_QUAL_TIMEOUT_SECONDS` changes the default 3600-second per-profile timeout.

One focused profile or alternate weight placement:

```bash
export PYTHONPATH="$HASHINFER_OPT_SOURCE"
python -m torch.distributed.run --standalone --nproc-per-node=4 \
  /workspace/hashinfer-trace/optimization/qualify_dispatch_overlap.py \
  --profile partial33 --grid heterogeneous --tactics 6,1 \
  --apply-topk-in-fc1 \
  --output-dir /workspace/hashinfer-trace/optimization/results/counts-overlap-fc1-qualification
```

CPU-only inspection, without importing torch/CUDA:

```bash
python optimization/qualify_dispatch_overlap.py --plan --profile partial33 --grid heterogeneous
python optimization/qualify_dispatch_overlap.py --plan --profile glm5 --grid full
```

## Evidence and expected cost

Each profile writes `run.log`, `checks.jsonl`, and terminal `summary.json`. Records contain all rank comparisons, fixture hashes, route counts, candidate knobs, source path/digest/declared base and optional Git head, oracle/harness hashes, GPU/rank metadata, versions, compile-time cluster counts, and elapsed wall time. The source digest is verified after execution on all ranks. An absent or failed summary is not a pass. This suite does not make latency measurements or select/promote a candidate.

Planning estimate for the default two profiles on four B300s: **roughly 10–40 minutes per source with cold compilation**, potentially longer with cache misses or CPU contention; warmed runs should take a few minutes, largely reference work. This estimate is unmeasured. Public preparation compiles all four int32/int64 × contiguous/strided staging ABIs per tactic even though this suite executes one ABI per profile; compilation dominates the uncertainty. The runner allows up to one hour per profile and kills the torchrun process group on timeout. Run one tactic first if the queue budget is tight.

Local preparation checks passed: Python syntax compilation, `bash -n`, and both CPU-only plans. Device compilation, all GPU assertions, heterogeneous-grid runtime behavior, and these runtime estimates remain unverified. The default suite excludes O2, all eight tactics, EP8, sanitizer, profiler replay/NCU, raw prestaged launch, and feature/activation matrices. It adds focused evidence for count release; it does not replace the repository's existing broader qualification.

## Remote compatibility re-review

Verified against the selected source:

- `MoEEpTensors.num_tokens` is the `hidden_states.shape[0]` property in `hashinfer/moe_ep/tensors.py`. `MoEEpMegaWorkspace._backend_workspace` and `create_workspace(capacity)` are present in `modes/mega_layer.py`; the resulting `MegaMoEBf16Nvfp4SymmBuffer._sym_roots` is a real field populated with the four outer symmetric roots.
- `warmup(inputs, workspace=handle)` performs an eager forward and synchronization. The backend then warms all four staging ABIs. Capture uses the same explicit capacity handle and accepts live rows from zero through capacity; the frontend's output row is dynamic, while source strides/dtypes select existing specializations. Smaller inputs do not request a smaller workspace.
- With one global token, `_partition` gives counts `[1,0,0,0]`. `_gather_rows` pads **all** ranks to one row before NCCL all-gather, then trims each rank's actual count. All ranks retain the global token for expert-owner reference work; empty source ranks return a valid `[0,H]` output after reducing the nonempty global route tensor. The wholly empty phase uses a trivial empty result instead of invoking zero-length collectives in the oracle; its subsequent refill provides the meaningful state check.
- Random routing comes from top-k indices, and adding a constant modulo the **global** expert count preserves uniqueness. Hot-owner routing replaces those IDs with consecutive local expert indices modulo 33 or 64, so all eight experts remain distinct. It does not fold random IDs modulo local expert count, which could create duplicates. The harness now asserts uniqueness and bounds of every nonempty generated row before execution. Repetition of an expert across different tokens remains intentional.
- Tar-snapshot provenance was tested locally without importing torch or CUDA; missing Git metadata no longer aborts the run. GPU UUID is nullable if that optional PyTorch device-property field is absent.

These are source/API and CPU metadata checks, not GPU runtime validation. The first compact control arm must still pass before interpreting candidate failures as kernel regressions.
