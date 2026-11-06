# N32 GLM5 codegen capture

Prepared only; none of these commands has been executed. This is diagnostic
compilation plus a short native launch, **not performance-retention evidence**.
Use the existing B300 / `nvcr.io/nvidia/pytorch:26.05-py3` runtime after the
current GPU queue finishes. The task owner stages source and owns scheduling;
this runbook neither applies a patch nor resets a checkout.

Compare exact `866c80d0c70a90624b4c2056d12d1543d709609e` with one isolated
candidate at a time. Keep original scheduler, original activation/reference,
two decoder warp groups, PDL, deterministic combine and disabled FC2 reduction.
Use GLM5 D6144/E2048/N256/K8, EP8, original SwiGLU, routing weights in combine.

## Capture one matching specialization

Use `runner/dump_compile.py` directly **inside torchrun**, wrapping the native
benchmark rather than the parent harness. It returns the original compiled
callable and changes only export settings (`CUTE_DSL_KEEP`, per-rank dump dir).
Do not use the older K3-specific `runner/capture_artifacts.py` or `native_entry`
adapters. Do not add debug, lineinfo, ptxas, optimization or cache-disable flags.

The command below requires a completed `runs/glm5-n32-866c-control-v1` capture,
reuses its environment and checks the pinned runtime versions. Capture the full
13-token list, with one warmup and one sample per point. Prioritize T32's binary
for decode analysis and use T512 to inspect capacity specialization and the
mixed occupancy regime. Static disassembly does not demonstrate that both sides
of the N16 runtime branch executed.

Set `N32_ARM` / `N32_SOURCE_MAP` for each independently staged source:

| Arm label | Expected source map |
|---|---|
| `baseline866c-m256-full13` | `next-n32-glm5-v1/source-maps/control.json` |
| `fc1-n16-m256-full13` | `next-n32-glm5-v1/source-maps/glm5-n32-fc1-n16-v1.json` |
| `fc2-combined-m256-full13` | `next-n32-glm5-v1/source-maps/glm5-n32-fc2-combined-v1.json` |

Source must already match the selected map. This uses a fresh output directory,
fails if the shared performance lock is occupied, and leaves original exports
and logs intact. Use a fresh label for a repeated capture.

```bash
export N32_PROJECT=/data/home/ziangli/flashinfer-k3-w4a16-megamoe-opt
export N32_SOURCE="$N32_PROJECT/flashinfer-n32-glm5"
export N32_ARM=baseline866c-m256-full13
export N32_SOURCE_MAP=next-n32-glm5-v1/source-maps/control.json
cd "$N32_PROJECT"
python3 -B - <<'PY'
import csv, fcntl, hashlib, importlib.metadata as md, json, os
from pathlib import Path
import subprocess

root = Path(os.environ['N32_PROJECT']).resolve()
source = Path(os.environ['N32_SOURCE']).resolve()
arm = os.environ['N32_ARM']
expected = json.loads((root / os.environ['N32_SOURCE_MAP']).read_text())
control = json.loads((root / 'runs/glm5-n32-866c-control-v1/run.json').read_text())
assert control['complete'] and control['model'] == 'glm5'
assert control['image'] == 'nvcr.io/nvidia/pytorch:26.05-py3'
for package, version in control['runtime_versions'].items():
    assert md.version(package) == version, (package, md.version(package), version)

def source_map():
    names = subprocess.check_output([
        'git', '-C', str(source), 'ls-files', '--cached', '--others',
        '--exclude-standard', '-z', 'flashinfer', 'benchmarks'], text=True)
    return {name: hashlib.sha256((source / name).read_bytes()).hexdigest()
            for name in names.split('\0') if name and (source / name).is_file()}

def save(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')

def idle_gpu_state():
    rows = list(csv.reader(subprocess.check_output([
        'nvidia-smi', '--query-gpu=index,uuid,name,utilization.gpu,memory.used',
        '--format=csv,noheader,nounits'], text=True, timeout=60).splitlines()))
    rows = [[cell.strip() for cell in row] for row in rows]
    processes = subprocess.check_output([
        'nvidia-smi', '--query-compute-apps=pid,gpu_uuid,process_name',
        '--format=csv,noheader'], text=True, timeout=60).strip()
    assert len(rows) == 8 and all('B300' in row[2] for row in rows), 'Need eight B300 GPUs'
    assert {row[0] for row in rows} == set(map(str, range(8))), 'Unexpected GPU indices'
    assert not processes, 'GPU compute processes are active; do not launch'
    assert all(row[3] == '0' for row in rows), 'GPU utilization is nonzero'
    return {'gpus': rows, 'compute_processes': processes}

knobs = dict(mma_tiler_mnk=[256,32,256], cluster_shape_mnk=[2,1,1],
    use_2cta_instrs=True, group_hint=512, load_balance_mode='atomic_counter',
    num_sched_stages=2, flag_batch=4, epi_flag_batch=[2,4],
    token_back_mode='epi_warps', in_kernel_fc2_reduce=False)
out = root / 'artifacts/n32-glm5-codegen' / arm
command = ['torchrun', '--master-addr=127.0.0.1', '--master-port=29713',
    '--nproc-per-node=8', str(root / 'runner/dump_compile.py'),
    '--dump-root', str(out / 'exports'), '--label', arm,
    str(source / 'benchmarks/bench_cute_dsl_moe_distributed.py'),
    '--model', 'glm5', '--mode', 'benchmark', '--parallel-modes', 'ep',
    '--num-gpus', '8', '--variants', 'w4a16_megamoe',
    '--num-tokens', '1,2,4,8,16,32,64,128,256,512,4096,8192,16384',
    '--timing', 'cupti', '--cuda-graph', '--precomputed-routing',
    '--no-fused-finalize', '--warmup', '1', '--iters', '1',
    '--log-timing-samples', '--megamoe-knobs', json.dumps(knobs)]
# Reuse the captured arm's controlled environment; do not inherit an unrelated
# diagnostic flag from the shell. No compiler/cache option is added here.
prefixes = ('FLASHINFER_', 'CUTE_DSL_', 'CUDA_', 'TRITON_', 'K3_')
env = {key: value for key, value in os.environ.items()
       if not key.startswith(prefixes) and key not in ('BUILD_NVEP', 'MAX_JOBS')}
env.update(control['environment'])
env.update(PYTHONPATH=str(source), K3_SOURCE_DIR=str(source), PYTHONUNBUFFERED='1')
# Record only the reviewed control keys and explicit source/import settings.
# Keep inherited child environment behavior; never serialize the whole shell.
recorded_env = {key: env[key] for key in control['environment']}
recorded_env.update({key: env[key] for key in
                     ('PYTHONPATH', 'K3_SOURCE_DIR', 'PYTHONUNBUFFERED')})
with (root / '.k3-perf.lock').open('a+') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    before = source_map()
    assert before == expected, 'Source does not match the selected isolated arm'
    out.mkdir(parents=True, exist_ok=False)
    save(out / 'source-before.json', before)
    save(out / 'command.json', command)
    save(out / 'knobs.json', knobs)
    save(out / 'environment.json', recorded_env)
    save(out / 'runtime.json', control['runtime_versions'])
    save(out / 'gpu-before.json', idle_gpu_state())
    with (out / 'native.log').open('w') as log:
        result = subprocess.run(command, cwd=source, env=env,
                                stdout=log, stderr=subprocess.STDOUT)
    after = source_map()
    save(out / 'source-after.json', after)
    save(out / 'exit.json', {'returncode': result.returncode,
                            'source_unchanged': before == after})
    assert before == after, 'Source changed during capture'
    assert result.returncode == 0, 'Inspect native.log'
PY
```

The eight-B300/no-compute-process/zero-utilization preflight runs while the
project lock is held; the advisory lock does not exclude unrelated users.
Only the reviewed control environment and three explicit source/import keys
are serialized, not inherited shell values or credentials. This launches only the
native performance mode: no refcheck, pytest, profiler or AUTO sweep. The
diagnostic timing samples must not enter benchmark tables or aggregates.
The native driver's fixed-tactic mode does not emit `MEGAMOE_TACTIC_JSON`;
attribute these binaries with saved knobs plus each compile receipt's geometry,
source hash, target architecture and compiler options instead.

## Compare original binary artifacts

Require all eight rank export directories, successful PTX/CUBIN export for the
W4A16 MegaMoE target, and unchanged source. If a cache hit bypasses the hook and
there is no binary export, the capture is incomplete; do not silently change
cache/compile flags. Preserve native `.sass` exports where available. The
analyzer also disassembles the **original cubin** without rebuilding PTX:

```bash
python3 -B "$N32_PROJECT/runner/analyze_compile.py" \
  --baseline "$N32_PROJECT/artifacts/n32-glm5-codegen/baseline866c-m256-full13/exports" \
  --candidate "$N32_PROJECT/artifacts/n32-glm5-codegen/fc1-n16-m256-full13/exports" \
  --output "$N32_PROJECT/artifacts/n32-glm5-codegen/fc1-n16-vs866c-m256.json"
```

Repeat only the candidate/output paths for FC2. Keep `.cubin`, `.ptx`, native
`.sass`, disassembly/resource sidecars, per-rank compile JSON, source maps,
command and log. Require all 13 native timing records, eight ranks, and matching
source/configuration before interpreting a delta. The analyzer matches
rank/owner/target/config/options/arch, but its key does not include token
capacity. A full sweep can therefore leave different-capacity MegaMoE binaries
unmatched. Use the receipt's exact `kernel_name` (`_tokens<capacity>`), config,
compiler options and architecture to form per-capacity pairs for all eight
ranks. Preserve originals; separate analysis views may contain copied records
and their referenced artifacts. Do not force different binaries into one
whole-sweep delta. T1/T2/T4/T8 can share capacity 1; identical hashes are one
specialization, not four independent codegen results. Additional unmatched
staging targets are not automatically a kernel mismatch.

## Branch-level questions

Inspect PTX basic blocks and their corresponding SASS control flow. Save exact
label/address ranges beside findings; **whole-binary opcode deltas alone cannot
answer these questions**, especially when N16 adds an alternate runtime branch.

- **FC1 N16:** locate the uniform `valid_tokens <= 16` predicate and both
  successors. In the narrow path, expect two raw `tcgen05.ld...16x64b.x8`
  operations rather than x16, eight alpha/activation elements rather than 16,
  and 12 `shfl.sync.bfly` sites plus selection instructions. Follow that path
  through its join: no scratch TMEM store/load round should remain there, and
  global output stores should lower to 128-bit transactions. The >16 path must
  retain the original raw x16 reads, activation and TMEM transpose. SwiGLU math
  is the original implementation; no native-tanh comparison is involved.
- **FC1 full32, if subsequently captured:** unchanged raw x16 reads and
  activation count; 32 shuffle sites, no scratch transpose, STG256. Confirm
  both routing-score prefetch and output store use the same permuted token
  index. This is a separate candidate, not an overlay on N16.
- **FC2 direct pack:** compare the raw-load-to-first-scratch-store block.
  Both arms must retain 16 packed FP32 alpha multiplications and 32 BF16 scalar
  conversions' worth of work. Look for a real reduction in PRMT/MOV or packing
  around BF16 conversion; a layout-only gather may already disappear. Count
  actual emitted conversion instructions according to their vector width.
  Scratch transpose and final store counts should be unchanged.
- **Release position:** trace the actual accumulator-stage empty-barrier
  arrival/release, not an unrelated scheduler barrier. FC1 N16/full32 should
  place it after both raw-load completions and before activation/shuffles.
  FC2 should place it after the final scratch read completion but before final
  register permutation/deinterleave. Confirm no subsequent TMEM access uses
  the released stage. SASS ordering can establish placement, not measured
  overlap or saved latency; identical placement means the source move bought
  nothing observable in that binary.
- **Registers/spills:** record REG, STACK, LOCAL and all `SETMAXNREG` sites;
  decoder role budgets must remain unchanged. Inspect PTX `ld.local/st.local`
  and SASS LDL/STL, then localize them to the epilogue path. `LOCAL:0` is not
  sufficient: a prior regression had REG96/STACK40/LOCAL0 with real spills.
  Count shuffle/select and packing work together, not shuffles alone.

## Is M128 worth another capture?

Start with the requested matching M256 pair. Add an M128 baseline/candidate
pair only if the relevant GLM5 AUTO result selects M128, the effect differs by
geometry, or M256 exposes a spill/lifetime concern that needs checking under
one-CTA MMA. For that pair change only `mma_tiler_mnk` to `[128,32,256]` and
`use_2cta_instrs` to `false`, retain cluster `[2,1,1]`, G512 and epi return, and
use fresh labels/output paths and the same full 13-token list. M128 changes
MMA/feature work distribution; it
is a distinct specialization, so never compare its resources directly against
M256 as a candidate-minus-baseline delta. No second capture is justified merely
because M128 exists in the catalog.
