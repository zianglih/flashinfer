# GLM5 N32 performance study — setup-only retry

Prepared locally for owner review; do not dispatch until reviewed. This bundle uses the existing container and dependencies. It never requests a devbox, installs packages, runs correctness checks, or changes the blog's source/cache checkout.

The failed v1 control exited before any timing records because all eight workers could not find `flashinfer/data/csrc/nv_internal/tensorrt_llm/thop/fp4Quantize.cpp`. The isolated clone lacked setup-generated data links. No candidate ran; failed captures and sealed v1 inputs remain untouched. This retry uses fresh arm names `glm5-n32-866c-control-v1r1`, `glm5-n32-fc1-n16-v1r1` and `glm5-n32-fc2-combined-v1r1`. No failed timing or baseline is reused.

The retry sequence is a fresh `866c80d0c70a90624b4c2056d12d1543d709609e` control, independent FC1-N16 candidate, then independent combined N32 FC2 direct-pack/early-release candidate. All use the unchanged AUTO16 catalog over **1,2,4,8,16,32,64,128,256,512,4096,8192,16384** tokens, EP8 GLM5 D6144/E2048/N256/K8, one fresh sweep, 3 warmups and 100 cold-L2 CUPTI samples per point. PDL is enabled; fused TMA/in-kernel FC2 reduction is disabled; fused deterministic combine and default FC2 routing-weight placement remain active. Routing is precomputed and untimed. No fixed tactic or refcheck is added.

Before any setup or GPU work, the runner requires the K3 blog supervisor's `status.json` to say `complete`, its `kimi-k3-exit.json` to have returncode0, and its launch source to be866c. It then holds the existing project `.k3-perf.lock` through setup, all captures and restoration, and requires eight idle B300 GPUs with no compute processes. The gate is `/data/home/ziangli/nvfp4-w4a16-blog-draft/captures/b300-rerun/pr6277-866c80d0-k3-20261009`.

Source isolation: the runner creates `/data/home/ziangli/flashinfer-k3-w4a16-megamoe-opt/flashinfer-n32-glm5` with independent Git metadata. It clones Git/submodule objects from the existing opt checkout with `--no-hardlinks`, fetches the sealed866c bundle (a7103 prerequisite), and verifies every tracked866c file plus complete kernel/benchmark and MoE test/reference maps. Neither donor source nor blog source is reset. Before benchmarking, reproduce only `build_backend.py::_create_data_dir(use_symlinks=True)`'s five ignored links: `cutlass`, `spdlog`, `cccl`, `csrc`, and `include`. This occurs under the shared lock after checking setup bytes and source/submodule identity. Existing correct links are accepted; other existing entries are never deleted or replaced. Record resolved targets and verify the complete tracked source remains identical. Do not import the build backend or run editable installation. No network clone or installation occurs. Persistent caches remain at `compile-cache/c2-sm103/{flashinfer,cute-dsl,cuda-driver,triton}`. Direct `cute.compile` may still compile in each process.

Each candidate patch is based independently on866c and must name every changed source path and resulting SHA256. Benchmark, tests/reference and AUTO catalog are unchanged. Exact before bytes and source maps are saved per arm, and the control source is restored after every candidate, including ordinary failures. Each owned arm has a 45-minute timeout; only its process group is signalled. If GPU processes survive termination, restoration stops for owner inspection rather than modifying source beneath a running worker. No unrelated process is killed.

Receipts go to `queues/n32-glm5-v1-retry`; captures to `runs/<arm>`. The immutable measured `run.py` is byte-identical to failed v1 and records all100 raw rank-MAX spans per point. The strict helper requires all13×8 agreeing selected-tactic records, exact fixture/runtime/timing/source contracts, and unchanged source during capture. AUTO selection scores remain separate from final CUPTI measurements. Only T1/T2 are excluded from aggregate retention. Correctness is a later step after useful performance is confirmed.

Local preparation and dry-run (these do not contact the devbox):

```bash
python3 -B next-n32-glm5-v1-retry/prepare.py --candidates next-n32-glm5-v1-retry/candidates.json
python3 -B next-n32-glm5-v1-retry/follow_on.py --check-only
```

The manifest seals all executable inputs and source maps. Once sealed, preserve it; use a fresh bundle version for new patches. Candidate JSON entries contain `name`, `base_commit`, relative `patch`, `changed_paths`, and `after_sha256`. Later versions may keep the same independent checkout and use `--arm <candidate-name>` to run one new candidate, reusing and strictly validating the completed fresh control without replaying it. Output directories are never overwritten.

Owner transfer and dispatch, from the existing HAI configuration directory:

```bash
command -v h  # must be /usr/local/bin/h
/usr/local/bin/h sync k3-w4a16-opt-c2 -c c2 -n ziangli \
  --source-dir /Users/ziangli/playground/projects/flashinfer-k3-w4a16-megamoe-opt/next-n32-glm5-v1-retry \
  --remote-path /data/home/ziangli/flashinfer-k3-w4a16-megamoe-opt/next-n32-glm5-v1-retry
/usr/local/bin/h ssh k3-w4a16-opt-c2 -c c2 -n ziangli -- \
  python3 -B /data/home/ziangli/flashinfer-k3-w4a16-megamoe-opt/next-n32-glm5-v1-retry/follow_on.py --check-only
/usr/local/bin/h ssh k3-w4a16-opt-c2 -c c2 -n ziangli -- \
  python3 -B /data/home/ziangli/flashinfer-k3-w4a16-megamoe-opt/next-n32-glm5-v1-retry/follow_on.py
```

The owner may enqueue while K3 is running; the completion gate prevents overlap. Check-only prints commands and verifies the local seal without source setup or GPU inspection. No helper launches on import.

After captures are downloaded, render cumulative evidence locally:

```bash
python3 -B next-n32-glm5-v1-retry/compare.py --output evidence/n32-glm5-v1-retry
```

Columns preserve original BEFORE/a7103 AUTO8 and historical48fce AUTO16, then append fresh866c control and candidate AUTO16 medians, IQR/raw samples, selected tactics and speedups. Historical samples are never pooled with the new study. The GLM SwiGLU path was unchanged by866c's SiTU/reference revert; the new control also measures runtime drift. Full13 rows remain visible.

The optional sealed `next-n32-glm5-v2` still names the failed original control and must not be dispatched as-is. If register32 is selected later, prepare a fresh follow-up version pointing to the successful `glm5-n32-866c-control-v1r1` capture; preserve the original v2 seal.
