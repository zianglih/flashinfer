# EP4 GLM-5 uniform 4096-token trace

Source commit: `4ba4b61f99a3b6af11b87975af6043978a35899a`. Source-plus-fixture SHA256: `c22c4938e43d009f71b89ac578a9312eb86ea6ad663eb791057b9ab8e894a41f`.

Named shape `--shape glm5-ep4-uniform4096` resolves to 1024 tokens/rank (4096 globally). H6144/I2048/E256/top8 and the native full grid are unchanged. Every token selects eight distinct experts, two per owner. All 256 experts receive 128 tokens globally, 32 from each source rank; each GPU receives 8192 routes. Total routes32768: local8192, remote24576. Each correctness comparison covers 6291456 BF16 output elements/rank.

The default remains `glm5-ep4-uniform128` (32/rank). Explicit `--tokens-per-rank 1`, `32`, `256`, `1024` and other positive counts remain supported. Shape and explicit token count are mutually exclusive. Existing numeric workload metadata, cache keys and source checks are unchanged. A named shape and the equivalent explicit token count resolve to identical numerical metadata.

Only benchmark harness, tracing guide and existing CPU fixture tests changed; kernel/package code is untouched. Six fixture/parser functions pass without importing Torch/CUDA/CuTe/HashInfer. Scoped pre-commit and `git diff --check` pass. `cpu-checks.json` binds all3 checkedfiles; `cpu-checks.txt` preserves exact output. No GPU validation performed by this helper task.

From the source checkout on C2, use a fresh experiment directory (root owns GPU execution):

```bash
export CUDA_VISIBLE_DEVICES=0,1,2,3 OMP_NUM_THREADS=1 MEGA_USE_NCU=0
export HASHINFER_TRACE_IMAGE=nvcr.io/nvidia/pytorch:26.05-py3
unset CUTE_DSL_COMPILER_OPT CUTE_DSL_ARCH MEGA_NO_DIST
trace_root="../trace-glm5-ep4-uniform4096-$(date -u +%Y%m%dT%H%M%SZ)"
export CUTE_DSL_CACHE_DIR="$trace_root/cache/cute"
python -m torch.distributed.run --nnodes=1 --master-addr=127.0.0.1 \
  --master-port=29629 --nproc-per-node=4 -- \
  benchmarks/trace_w4a16_megamoe.py --mode baseline \
  --shape glm5-ep4-uniform4096 --warmup-iters 3 --timed-iters 50 \
  --output-dir "$trace_root/checks"
run-iket --output-dir "$trace_root/iket" profile --enabled-cluster 0,0,0 \
  --postprocess all --keep -- \
  python -m torch.distributed.run --nnodes=1 --master-addr=127.0.0.1 \
  --master-port=29629 --nproc-per-node=4 -- \
  benchmarks/trace_w4a16_megamoe.py --mode capture \
  --shape glm5-ep4-uniform4096 --warmup-iters 3 --timed-iters 50 \
  --output-dir "$trace_root/checks"
```

Baseline performs native8candidate tuning and independent-reference validation. Capture reloads the saved winner, compiles before the rank barrier and executes exactlyone target launch/rank. Its native cluster0 filter does not cap the launch. Use fresh profiler and checks directories for each shape; the4096shape's local tactic cache is `autotune-t1024-cache.json`. Keep all historical evidence unchanged. The new capture must be audited with4096-derived counts, not the older128-global fixed-count assumptions.
