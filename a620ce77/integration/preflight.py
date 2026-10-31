"""Deploy merged source and run existing source/cache/normal-load/idle preflight; no timing."""
from pathlib import Path
import argparse,base64,gzip,hashlib,json,subprocess

HERE=Path(__file__).resolve().parent
PROJECT=HERE.parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--gpus',nargs='+',type=int,required=True)
a=p.parse_args()
assert a.gpus and len(a.gpus)==len(set(a.gpus)) and set(a.gpus)<=set(range(8))
cpath=HERE/'screen/perf-config.json';c=read(cpath)
assert sha(cpath)==read(HERE/'deployment-plan.json')['config_sha256']
assert read(HERE/'plan.json')['passed']
proof=read(HERE/'harness-proof.json')
for name,digest in proof['helpers'].items():assert sha(HERE/'harness'/name)==digest
ready_path=PROJECT/'experiments/sf-coordinate-cache/cache-recovery/readiness-current.json';ready=read(ready_path)
warm_path=ready_path.parent/'cache-ready-current.json';warm=read(warm_path)
runtime_path=PROJECT/'runtime/recovery-paired-error/runtime.json'
assert ready['passed'] and warm['passed']
assert sha(ready_path)=='e466ac7cea8bbdf4e4c9d60f21ae63c26569cd19cbff7805acceda4984dc2ea0'
assert sha(warm_path)==ready['cache_sha256']=='ad6b3a6d3158eef0907ed535e199737ac7b96ed0b14de5b4b7b6df0351e37702'
assert sha(runtime_path)==ready['runtime_sha256']
files={name:(HERE/'screen'/name).read_text() for name in ('perf-config.json','source-candidate.json')}
assert set(files)=={'perf-config.json','source-candidate.json'}
files['source-full.json']=(HERE/'source-full.json').read_text()
files['restored-utils.py']=(PROJECT/'flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_utils.py').read_text()
files['plan.json']=(HERE/'plan.json').read_text()
files['deployment-plan.json']=(HERE/'deployment-plan.json').read_text()
files['selected-winners.json']=(HERE/'selected-winners.json').read_text()
for role in c['sources']:
    files[f'{role}-tracked.json']=(HERE/'screen'/f'{role}-tracked.json').read_text()
files['recovery-readiness.json']=ready_path.read_text()
files['recovery-cache-ready.json']=warm_path.read_text()
files['recovery-runtime.json']=runtime_path.read_text()
payload=dict(config_sha256=sha(cpath),plan_sha256=sha(HERE/'plan.json'),gpus=a.gpus,files=files,
             helpers={n:(HERE/'harness'/n).read_text() for n in proof['helpers']},helper_hashes=proof['helpers'],
             ready_sha256=sha(ready_path),warm_sha256=sha(warm_path),
             native_helper=(PROJECT/'harness/native_preflight.py').read_text())
packed=base64.b64encode(gzip.compress(json.dumps(payload).encode())).decode()
script='PACKED='+repr(packed)+'\n'+r'''
from pathlib import Path
import base64,csv,gzip,hashlib,io,json,os,subprocess,time
p=json.loads(gzip.decompress(base64.b64decode(PACKED)))
root=Path('/data/ziangli/flashinfer-moe-gather-pipeline');out=root/'runs/pr7290-retained-refresh';owned=root/'integration/pr7290-refresh-20261030';h=owned/'harness'
sha=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
write=lambda path,value:path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
assert not out.exists() and not h.exists()
c=json.loads(p['files']['perf-config.json']);assert hashlib.sha256(p['files']['perf-config.json'].encode()).hexdigest()==p['config_sha256']
plan=json.loads(p['files']['plan.json']);assert hashlib.sha256(p['files']['plan.json'].encode()).hexdigest()==p['plan_sha256']
assert plan['passed'] and plan['cells']==468 and plan['samples']==93600
warm_path=root/'experiments/sf-coordinate-cache/cache-recovery/cache-ready-current.json';assert sha(warm_path)==p['warm_sha256'];warm=json.loads(warm_path.read_text())
ready=json.loads(p['files']['recovery-readiness.json'])
assert hashlib.sha256(p['files']['recovery-readiness.json'].encode()).hexdigest()==p['ready_sha256']
runtime=json.loads(p['files']['recovery-runtime.json'])
assert hashlib.sha256(p['files']['recovery-runtime.json'].encode()).hexdigest()==ready['runtime_sha256']
assert sha(ready['runtime_path'])==ready['runtime_sha256']
expected_uuids={int(row['index']):row['uuid'].strip() for row in csv.DictReader(io.StringIO(runtime['gpu']),skipinitialspace=True)}
# Materialize one immutable merged snapshot from the verified c1ac inventory.
owned.mkdir(parents=True,exist_ok=False);(owned/'screen').mkdir()
full=json.loads(p['files']['source-full.json']);assert full['head']==plan['head']=='a620ce7790b32f7f0ae524a811417d2c6cee1152'
assert hashlib.sha256(p['files']['source-full.json'].encode()).hexdigest()==plan['source_full_sha256']
parent=Path(full['parent_source_file']);assert sha(parent)==plan['base_source_sha256']
old=json.loads(parent.read_text());repo=Path(full['repo']);assert not repo.exists()
subprocess.run(['cp','-al',old['repo'],str(repo)],check=True)
name='flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_utils.py';(repo/name).unlink();(repo/name).write_text(p['files']['restored-utils.py'])
assert sha(repo/name)==full['source_sha256'][name]
assert {n:dict(before=old['source_sha256'][n],after=d)for n,d in full['source_sha256'].items()if d!=old['source_sha256'][n]}==plan['exact_delta_from_c1ac']
(owned/'source-full.json').write_text(p['files']['source-full.json'])
(owned/'screen/candidate-tracked.json').write_text(p['files']['candidate-tracked.json'])
(owned/'screen/source-candidate.json').write_text(p['files']['source-candidate.json'])
# Verify the original full immutable inventories with the existing two-arm boundary.
from concurrent.futures import ThreadPoolExecutor
def verify_source(item):
    role,s=item
    assert sha(s['freeze_receipt'])==s['freeze_receipt_sha256']
    frozen=json.loads(Path(s['freeze_receipt']).read_text())
    tracked=json.loads(p['files'][f'{role}-tracked.json'])
    assert hashlib.sha256(p['files'][f'{role}-tracked.json'].encode()).hexdigest()==s['tracked_manifest_sha256']
    assert tracked==frozen['source_sha256'] and len(tracked)==13245
    for name,digest in tracked.items():assert sha(Path(s['repo'])/name)==digest,(role,name)
    for name,digest in s['source_sha256'].items():assert tracked[name]==digest
    return role,dict(files=len(tracked),source_record_sha256=s['freeze_receipt_sha256'],tracked_manifest_sha256=s['tracked_manifest_sha256'])
with ThreadPoolExecutor(max_workers=2) as pool:full_sources=dict(pool.map(verify_source,c['sources'].items()))
workspace=Path(warm['modules'][0]['library']).parent.parent.parent
for role,s in c['sources'].items():
    folder=Path(s['workspace_base'])/'.cache/flashinfer/0.0.0+unknown/103a/cached_ops'
    folder.mkdir(parents=True,exist_ok=True);assert not folder.is_symlink()
    Path(s['cute_cache']).mkdir(parents=True,exist_ok=True)
    gen=folder.parent/'generated'
    if not gen.exists():gen.symlink_to(workspace/'generated',target_is_directory=True)
    assert gen.is_symlink() and gen.resolve()==(workspace/'generated').resolve()
    for row in warm['modules']:
        link=folder/row['name'];target=Path(row['library']).parent
        if not link.exists():link.symlink_to(target,target_is_directory=True)
        assert link.is_symlink() and link.resolve()==target.resolve()
native={};arm_env={}
for role,s in c['sources'].items():
    env={k:v for k,v in os.environ.items() if not k.startswith(('FLASHINFER_','TRTLLM_','CUTE_DSL_','FI_')) and k not in ('CUDA_VISIBLE_DEVICES','PYTHONOPTIMIZE')}
    env.update(PYTHONPATH=os.pathsep.join(x for x in (s['repo'],c['python_deps']) if x),FLASHINFER_WORKSPACE_BASE=s['workspace_base'],FLASHINFER_CUBIN_DIR=s['cubin_dir'],CUTE_DSL_CACHE_DIR=s['cute_cache'],CUDA_CACHE_PATH=c['driver_cache'],FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY='1',FLASHINFER_CUDA_ARCH_LIST='10.3a',FLASHINFER_DIST_AWARE_AUTOTUNE='0',TRTLLM_ENABLE_PDL='1',FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH='0',TRTLLM_DISABLE_FP4_QUANT_FAST_MATH='0',FLASHINFER_JIT_VERBOSE='0',FLASHINFER_JIT_DEBUG='0',MAX_JOBS='4',OMP_NUM_THREADS='1')
    arm_env[role]=env
    r=subprocess.run([c['python'],'-c',p['native_helper']],cwd=s['repo'],env=env,text=True,capture_output=True,check=True);native[role]=json.loads(r.stdout)
assert len(native)==1 and 'candidate' in native
workspace=Path(warm['modules'][0]['library']).parent.parent.parent;modules=[];private={}
for role,s in c['sources'].items():
    folder=Path(s['workspace_base'])/'.cache/flashinfer/0.0.0+unknown/103a/cached_ops'
    assert folder.is_dir() and not folder.is_symlink() and Path(s['cute_cache']).is_dir()
    assert Path(native[role]['native_paths']['workspace'])==folder.parent
    assert (folder.parent/'generated').is_symlink() and (folder.parent/'generated').resolve()==workspace/'generated'
    assert Path(s['cubin_dir'])==workspace.parent.parent/'cubins'
    links={x.name for x in folder.iterdir() if x.is_symlink()}
    assert links==set(native[role])-{'native_paths'}
    for name in links:assert (folder/name).resolve()==(workspace/'cached_ops'/name).resolve()
    private[role]=dict(cached_ops=str(folder),cute_cache=s['cute_cache'],cubin_dir=s['cubin_dir'],generated_root=str((folder.parent/'generated').resolve()),shared_modules=sorted(links))
assert private['candidate']['cached_ops']!=str(workspace/'cached_ops')
for row in warm['modules']:
    library=Path(row['library']);build=library.parent/'build.ninja'
    assert sha(library)==row['after']['library_sha256'] and sha(build)==row['after']['ninja_sha256']
    assert build.read_text()==native['candidate'][row['name']] and '-G ' not in build.read_text() and '-g ' not in build.read_text()
    check=subprocess.run(['ninja','-n','-C',str(library.parent)],text=True,capture_output=True,check=True);assert 'no work to do' in check.stdout
    modules.append(dict(name=row['name'],library=str(library),library_sha256=sha(library),ninja_sha256=sha(build),noop=check.stdout))
# Exact normal-load block reused from qualification-extra-r1; no forced rebuild.
load_code="from flashinfer.jit.dsv3_optimizations import gen_dsv3_fused_routing_module as a; from flashinfer.jit.moe_utils import gen_moe_utils_module as b; from flashinfer.jit.fp4_quantization import gen_fp4_quantization_sm103_module as c; from flashinfer.jit.fp8_quantization import gen_mxfp8_quantization_sm100_module as d; [f().build_and_load() for f in (a,b,c,d)]"
normal_loads={};load_logs={}
for role,s in c['sources'].items():
    loaded=subprocess.run([c['python'],'-c',load_code],cwd=s['repo'],env=arm_env[role],text=True,capture_output=True)
    assert loaded.returncode==0,(role,loaded.stdout,loaded.stderr)
    for module in modules:
        library=Path(module['library']);assert sha(library)==module['library_sha256'] and sha(library.parent/'build.ninja')==module['ninja_sha256'],(role,module)
        dry=subprocess.run(['ninja','-n','-C',str(library.parent)],text=True,capture_output=True,check=True);assert 'no work to do' in dry.stdout,(role,dry.stdout)
    load_logs[f'native-load-{role}.stdout']=loaded.stdout;load_logs[f'native-load-{role}.stderr']=loaded.stderr
    normal_loads[role]=dict(passed=True,workspace_base=s['workspace_base'],cubin_dir=s['cubin_dir'],stdout_sha256=hashlib.sha256(loaded.stdout.encode()).hexdigest(),stderr_sha256=hashlib.sha256(loaded.stderr.encode()).hexdigest(),adopted_current_ninja_elf_preserved=True)
winner_inputs={}
for name,job in c['jobs'].items():
    expected=Path(job['winner_results']);cache=Path(job['winner_cache'])
    assert expected.is_file() and cache.is_dir()
    baseline=json.loads(expected.read_text());assert baseline['complete'] and baseline['profile_calls']==0
    winner_inputs[name]=dict(expected_sha256=sha(expected),cache_manifest={str(f.relative_to(cache)):sha(f)for f in sorted(cache.rglob('*'))if f.is_file()})
    assert winner_inputs[name]['cache_manifest']
idle=[]
for gpu in p['gpus']:
    line=subprocess.check_output(['nvidia-smi','-i',str(gpu),'--query-gpu=uuid,memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip();uuid,mem,util=[x.strip() for x in line.split(',')]
    apps=subprocess.check_output(['nvidia-smi','-i',str(gpu),'--query-compute-apps=pid','--format=csv,noheader'],text=True).strip();assert int(mem)<=16 and int(util)==0 and not apps,(gpu,line,apps)
    assert uuid==expected_uuids[gpu]
    time.sleep(0.15)
    second=subprocess.check_output(['nvidia-smi','-i',str(gpu),'--query-gpu=uuid,memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip()
    uuid2,mem2,util2=[x.strip() for x in second.split(',')]
    apps2=subprocess.check_output(['nvidia-smi','-i',str(gpu),'--query-compute-apps=pid','--format=csv,noheader'],text=True).strip()
    assert uuid2==uuid and int(mem2)<=16 and int(util2)==0 and not apps2,(gpu,second,apps2)
    idle.append(dict(gpu=gpu,uuid=uuid,memory_mib=int(mem2),utilization_percent=int(util2),compute_pids=apps2,first_memory_mib=int(mem),first_utilization_percent=int(util),idle_policy='two fresh no-PID, zero-util samples, <=16MiB driver residue'))
out.mkdir();h.mkdir(parents=True)
for name,value in p['files'].items():(out/name).write_text(value)
for role,s in c['sources'].items():
    (out/f'{role}-tracked.json').write_bytes(Path(s['tracked_manifest']).read_bytes())
    (out/f'qualification-{role}-source.json').write_bytes(Path(s['freeze_receipt']).read_bytes())
for name,value in load_logs.items():(out/name).write_text(value)
for name,value in p['helpers'].items():
    (h/name).write_text(value);assert sha(h/name)==p['helper_hashes'][name]
assert sha(out/'perf-config.json')==p['config_sha256']
write(out/'native-generated-preflight.json',native)
preflight=dict(passed=True,time=time.time(),config_sha256=p['config_sha256'],native_modules=modules,private_caches=private,actual_private_arm_normal_loads=normal_loads,idle=idle,node='fi-gather-pipeline-resume-1030',cluster='c2',namespace='ziangli',readiness_sha256=p['ready_sha256'],cache_ready_sha256=p['warm_sha256'],source_plan_sha256=p['plan_sha256'],full_sources_before=full_sources,winner_inputs=winner_inputs,boundary='Fresh merged-head AA refresh in explicitly adopted current release cohort: moe_utils046552b8 plus three original ELFs. Actual candidate normal loader preserve current Ninja/ELF hashes and canonical generated/cubin inputs. Failed original restoration is preserved separately. No prior rows or phases reused.')
write(out/'launch-preflight.json',preflight)
print(json.dumps(dict(preflight=preflight)))
'''
compile(script,'preflight.remote.py','exec')
(HERE/'preflight.remote.py').write_text(script)
transport=HERE/'transport';transport.mkdir(exist_ok=True);(transport/'preflight.py').write_text(script)
remote_transport='/data/ziangli/flashinfer-moe-gather-pipeline/integration/pr7290-refresh-transport'
sync=subprocess.run(['/usr/local/bin/h','sync','fi-gather-pipeline-resume-1030','-c','c2','-n','ziangli','--source-dir',str(transport),'--remote-path',remote_transport],cwd='/Users/ziangli/playground/repos/hai',text=True,capture_output=True)
(HERE/'transport.stdout').write_text(sync.stdout);(HERE/'transport.stderr').write_text(sync.stderr);sync.check_returncode()
r=subprocess.run(['/usr/local/bin/h','ssh','fi-gather-pipeline-resume-1030','-c','c2','-n','ziangli','--','python3',remote_transport+'/preflight.py'],cwd='/Users/ziangli/playground/repos/hai',text=True,capture_output=True)
(HERE/'screen/preflight.stdout').write_text(r.stdout);(HERE/'screen/preflight.stderr').write_text(r.stderr)
if r.returncode:raise RuntimeError(f'Launch preflight exited {r.returncode}; see screen/launch.stderr')
data=json.loads(r.stdout)
for key,name in [('preflight','launch-preflight.json')]:write_path=HERE/'screen'/name;write_path.write_text(json.dumps(data[key],indent=2,sort_keys=True)+'\n')
print(json.dumps(dict(passed=data['preflight']['passed'],full_sources=data['preflight']['full_sources_before'],gpus=len(data['preflight']['idle']))))
