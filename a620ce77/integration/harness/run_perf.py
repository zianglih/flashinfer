"""Source-bound AA or CAAC replay of frozen native choices with strict CUPTI."""

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import signal
import statistics
import subprocess
import time


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def manifest(path):
    return {str(p.relative_to(path)): sha(p) for p in sorted(path.rglob('*')) if p.is_file()}


def gpu_state(gpu):
    return subprocess.check_output(['nvidia-smi', '-i', str(gpu),
        '--query-gpu=uuid,memory.used,utilization.gpu,clocks.sm,temperature.gpu,power.draw',
        '--format=csv,noheader'], text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--job', required=True)
    parser.add_argument('--gpu', type=int, required=True)
    args = parser.parse_args()
    args.config = args.config.resolve()
    config = json.loads(args.config.read_text())
    job = config['jobs'][args.job]
    out = Path(config['output']) / args.job
    out.mkdir(parents=True, exist_ok=False)
    assert not subprocess.check_output(['nvidia-smi', '-i', str(args.gpu),
        '--query-compute-apps=pid', '--format=csv,noheader'], text=True).strip()
    observer = Path(config['observer'])
    for rel, digest in config['observer_hashes'].items():
        assert sha(observer.parent / rel) == digest, rel
    baseline_path = Path(job['winner_results'])
    baseline = json.loads(baseline_path.read_text())
    assert baseline['complete'] and baseline['swap_ab'] and not baseline['use_fused_finalize']
    assert baseline['profile_calls'] == 0
    argv = baseline['benchmark_argv']
    for flag, expected in [('--model', job['model']), ('--tp', str(job['tp'])), ('--ep', str(job['ep']))]:
        assert argv[argv.index(flag) + 1] == expected, (flag, expected)
    winners, routes = {}, {}
    samples = iter(baseline['native_diagnostic']['measurements'])
    for row in baseline['rows']:
        routes[row['tokens']] = row['routing_identity']
        for result in row['results']:
            measure = next(samples)
            identities = [{k: h[k] for k in ('key', 'runner', 'tactic')} for h in measure['cache_hits']]
            winners[(row['tokens'], result['backend'])] = list({json.dumps(v, sort_keys=True): v for v in identities}.values())
    assert next(samples, None) is None
    initial_cache = Path(job['winner_cache'])
    assert initial_cache.is_dir()
    frozen = manifest(initial_cache)
    assert frozen
    for role in dict.fromkeys(config['phases']):
        shutil.copytree(initial_cache, out / ('cache-' + role))
        assert manifest(out / ('cache-' + role)) == frozen

    def verify_source(role):
        source = config['sources'][role]
        repo = Path(source['repo'])
        assert role != 'control' or source['head'] == config['control_head']
        for rel, digest in source['source_sha256'].items():
            assert sha(repo / rel) == digest, (role, rel)
        sealed = json.loads(Path(source['tracked_manifest']).read_text())
        assert sha(source['tracked_manifest']) == source['tracked_manifest_sha256']
        # All tracked bytes are verified at source freeze and once pre/post
        # campaign; each process checks the bounded launch dependency subset.
        assert all(sealed[rel] == digest for rel, digest in source['source_sha256'].items())

    receipt = dict(complete=False, job=job, config_sha256=sha(args.config),
        helper_sha256=sha(__file__), observer_hashes=config['observer_hashes'],
        sources=config['sources'], winner_results_sha256=sha(baseline_path),
        winner_cache_manifest=frozen, gpu=args.gpu, gpu_initial=gpu_state(args.gpu), phases=[],
        boundary=config['boundary'])
    gpu_uuid = receipt['gpu_initial'].split(',')[0].strip()

    def save():
        (out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')

    save()
    try:
        for index, role in enumerate(config['phases']):
            verify_source(role)
            source = config['sources'][role]
            repo = Path(source['repo'])
            cache = out / ('cache-' + role)
            assert manifest(cache) == frozen
            env = {k: v for k, v in os.environ.items() if not k.startswith(('FLASHINFER_', 'TRTLLM_', 'CUTE_DSL_', 'FI_')) and k not in ('CUDA_VISIBLE_DEVICES', 'PYTHONOPTIMIZE')}
            settings = dict(CUDA_VISIBLE_DEVICES=str(args.gpu),
                FI_OWNERSHIP_CONFIG=str(args.config), FI_FROZEN_HEAD=source['head'],
                PYTHONPATH=os.pathsep.join(x for x in (str(repo), config['python_deps']) if x),
                FLASHINFER_WORKSPACE_BASE=source['workspace_base'],
                FLASHINFER_CUBIN_DIR=source['cubin_dir'],
                CUTE_DSL_CACHE_DIR=source['cute_cache'],
                CUDA_CACHE_PATH=config['driver_cache'], FLASHINFER_JIT_BUILD_LOG=str(out / f'{index}-{role}-native-build.jsonl'),
                FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY='1', FLASHINFER_CUDA_ARCH_LIST='10.3a',
                FLASHINFER_DIST_AWARE_AUTOTUNE='0', TRTLLM_ENABLE_PDL='1',
                FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH='0', TRTLLM_DISABLE_FP4_QUANT_FAST_MATH='0',
                MAX_JOBS='4', OMP_NUM_THREADS='1', PYTHONUNBUFFERED='1',
                TRITON_CACHE_DIR=str(out / 'triton' / role))
            env.update(settings)
            dest = out / f'{index}-{role}'
            command = [config['python'], '-u', str(observer), '--repo', str(repo), '--output', str(dest), *(['--w4a4-only'] if job.get('w4a4_only') else []), *(['--w4a16-only'] if job.get('w4a16_only') else []), '--',
                '--functional-api', '--model', job['model'], '--ep', str(job['ep']), '--tp', str(job['tp']),
                '--quant-family', job['family'], '--backends', job['backends'],
                '--num-tokens', ','.join(map(str, job['tokens'])), '--cache', str(cache),
                '--swap-ab', '--no-fused-finalize', '--warmup', '10', '--iters', '100', '--no-autotune', '--output-format', 'both']
            if job['family'] == 'nvfp4':
                command.append('--include-activation-quant')
            phase = dict(index=index, role=role, command=command, environment=settings,
                started=time.time(), gpu_before=gpu_state(args.gpu), results=str(dest / 'results.json'))
            assert phase['gpu_before'].split(',')[0].strip() == gpu_uuid
            receipt['phases'].append(phase)
            save()
            log_path = out / f'{index}-{role}.log'
            compiler_dir=out / f'{index}-{role}-compiler-artifacts'
            compiler_dir.mkdir()
            with log_path.open('w') as log:
                wrapped = [config['python'], '-u', str(observer.parent / 'nvml_clock_wrapper.py'), '--gpu', str(args.gpu), '--interval-ms', '2', '--output', str(out / 'telemetry' / dest.name), '--', *command]
                process = subprocess.Popen(wrapped, cwd=compiler_dir, env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                try:
                    code = process.wait(timeout=config.get('phase_timeout_seconds', 900))
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
                    phase['timeout'] = True
                    save()
                    raise
                result = subprocess.CompletedProcess(wrapped, code)
            phase.update(returncode=result.returncode, seconds=time.time() - phase['started'], gpu_after=gpu_state(args.gpu))
            save()
            result.check_returncode()
            verify_source(role)
            data = json.loads((dest / 'results.json').read_text())
            assert data['complete'] and data['swap_ab'] and not data['use_fused_finalize']
            assert data['profile_calls'] == 0 and not data['native_diagnostic']['admitted_tactics']
            assert data['benchmark_sha256'] == source['source_sha256']['benchmarks/bench_moe_deepseek.py']
            assert data['observer_sha256'] == sha(observer)
            assert [r['tokens'] for r in data['rows']] == job['tokens']
            measurements = iter(data['native_diagnostic']['measurements'])
            medians = []
            native_resolutions = []
            for row in data['rows']:
                assert row['routing_identity'] == routes[row['tokens']]
                for result_row in row['results']:
                    measure = next(measurements)
                    values = measure['milliseconds']
                    assert len(values) == 100 and all(math.isfinite(v) and v > 0 for v in values)
                    assert measure['timer'] == 'CUPTI' and measure['event_fallback_forbidden']
                    assert statistics.median(values) == measure['median_ms'] == result_row['latency_ms']
                    assert all(h['hit'] for h in measure['cache_hits'])
                    identities = [{k: h[k] for k in ('key', 'runner', 'tactic')} for h in measure['cache_hits']]
                    identities = list({json.dumps(v, sort_keys=True): v for v in identities}.values())
                    assert identities == winners[(row['tokens'], result_row['backend'])]
                    assert len(identities)==1
                    selected=identities[0]['tactic']
                    if job.get('w4a16_only'):
                        expected_tactic=config['default_w4a16_moe_tactic'] if selected==-1 else selected
                        resolved=measure['w4_resolved_configs']
                        assert {x['stage'] for x in resolved}=={'fc1','fc2'} and len(resolved)==2
                        assert measure['w4_default_tactic']==config['default_w4a16_moe_tactic']
                        assert measure['w4_resolution_source_sha256']=={
                            'tuner.py':source['source_sha256']['flashinfer/fused_moe/cute_dsl/tuner.py'],
                            'moe_w4a16.py':source['source_sha256']['flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16.py']}
                        for native in resolved:
                            assert native['tokens']==row['tokens']
                            assert native['resolved_moe_tactic']==expected_tactic
                            assert native['supplied_moe_tactic']==(None if selected==-1 else selected)
                            stage_tactic=expected_tactic[0 if native['stage']=='fc1' else 1]
                            assert native['mma_tiler_mnk']==stage_tactic[0]
                            assert native['cluster_shape_mn']==stage_tactic[1]
                            assert native['raster_along_m']==stage_tactic[2]
                        native_resolutions.extend(resolved)
                    else:
                        assert selected != -1, 'Blockscaled replay must use an explicit recorded tactic'
                    medians.append(dict(tokens=row['tokens'], backend=result_row['backend'], ms=measure['median_ms']))
            assert next(measurements, None) is None
            assert len(medians) == job['expected_cells']
            assert phase['gpu_after'].split(',')[0].strip() == gpu_uuid
            guards = sorted((out / 'register-guard' / dest.name).glob('*/receipt.json'))
            assert guards, 'Missing runtime register guard'
            phase['register_guards'] = []
            for guard_path in guards:
                guard = json.loads(guard_path.read_text())
                assert guard['exitstatus'] == 0 and guard['all_guarded']
                assert guard['kernel_sha256'] == source['source_sha256']['flashinfer/fused_moe/cute_dsl/blackwell/' + ('moe_w4a16_kernel.py' if job.get('w4a16_only') else 'moe_swap_ab_kernel.py')]
                assert guard['policy'] == (dict(control=80,gather=64,epilogue=144) if job.get('w4a16_only') else config['register_policies'][role])
                phase['register_guards'].append(dict(path=str(guard_path), sha256=sha(guard_path)))
            native_by_library={}
            for guard_path in guards:
                for compiled in json.loads(guard_path.read_text())['compilations']:
                    native_by_library[compiled['library_handle']]=compiled
            for native in native_resolutions:
                compiled=native_by_library[native['compiled_library']]
                assert compiled['gather_input']==(native['stage']=='fc1')
                for field in ('mma_tiler_mnk','cluster_shape_mn','raster_along_m','use_clc_scheduler','enable_pdl'):
                    assert compiled[field]==native[field],field
            canonical=[{k:v for k,v in x.items() if k!='compiled_library'} for x in native_resolutions]
            if index:
                assert canonical==receipt['phases'][0]['native_resolved_configs']
            phase['native_resolved_configs']=canonical
            assert manifest(cache) == frozen
            clock_path = out / 'telemetry' / dest.name / 'receipt.json'
            clock = json.loads(clock_path.read_text())
            assert clock['complete'] and clock['returncode'] == 0
            phase['telemetry_receipt_sha256'] = sha(clock_path)
            phase.update(verified=True, medians=medians, results_sha256=sha(dest / 'results.json'), stdout_sha256=sha(log_path))
            save()
        for role in dict.fromkeys(config['phases']):
            verify_source(role)
        receipt.update(complete=True, finished=time.time())
        save()
    except BaseException as exc:
        receipt.update(error=repr(exc), finished=time.time())
        save()
        raise


if __name__ == '__main__':
    main()
