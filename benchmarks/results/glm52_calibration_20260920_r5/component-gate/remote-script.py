import datetime,hashlib,json,os,pathlib,re,subprocess,sys
root=pathlib.Path('/data/home/ziangli/flashinfer-sglang-megamoe-benchmark-alignment'); source=root/'sources/flashinfer-ad0'; commit='bd8391858db504c8997e704c7952f4d48ccab591'; stage='timing-r5'; hashes={'benchmarks/w4a16_contract_reference.py': 'b25576fb75b550554deb453b051793c56495f80d866fd53694c5b27fa801914d', 'benchmarks/moe_distributed_layout.py': 'a66953bc8db2c38cb6fa23f5fa84c89721a0a09a9aad5b83eeba0c44d1a83d76', 'tests/test_w4a16_contract_reference.py': 'ca493f923b2205574b29cc8bdf14ce1a367287b949c89fa4d6156aaded4ac8a4'}
assert subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()==commit
assert not subprocess.check_output(['git','-C',str(source),'status','--porcelain'],text=True).strip()
assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip()
for parent in ('runs','diagnostics'):
 for existing in (root/parent).glob('*'): assert (existing/'exit.json').exists(),str(existing)
for name,sha in hashes.items(): assert hashlib.sha256((source/name).read_bytes()).hexdigest()==sha,name
seal=json.loads((root/'environment'/stage/'setup-completed.json').read_text());assert seal['source_head']==commit
expected=json.loads((root/'environment'/stage/'runtime-after.json').read_text())
probe=[sys.executable,str(root/'setup/probe_runtime.py')]
assert json.loads(subprocess.check_output(probe))==expected
dest=root/'validation'/('contract-reference-'+stage);dest.mkdir(parents=True,exist_ok=False)
env=dict(os.environ);env.update(CUDA_VISIBLE_DEVICES='0',TRITON_CACHE_DIR=str(dest/'triton-cache'),PYTHONUNBUFFERED='1')
argv=[sys.executable,'-B','tests/test_w4a16_contract_reference.py','-v']
invocation={'argv':argv,'commit':commit,'source_sha256':hashes,'timing_stage':stage,'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'unit/reference GPU validation only; no measured performance'}
(dest/'invocation.json').write_text(json.dumps(invocation,indent=2)+'\n')
errors=[];returncode=None;source_unchanged=False;runtime_unchanged=False;gpu_after=None
def failed(stage_name,error):
 errors.append({'stage':stage_name,'type':type(error).__name__,'message':str(error)})
try:
 with (dest/'stdout.log').open('x') as out,(dest/'stderr.log').open('x') as err:
  result=subprocess.run(argv,cwd=source,env=env,stdout=out,stderr=err,timeout=600)
  returncode=result.returncode
except Exception as error:
 failed('test_execution',error)
finally:
 try:
  assert json.loads(subprocess.check_output(probe))==expected,'runtime drift'
  runtime_unchanged=True
 except Exception as error:failed('runtime_postcheck',error)
 try:
  assert subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()==commit,'source HEAD drift'
  assert not subprocess.check_output(['git','-C',str(source),'status','--porcelain'],text=True).strip(),'source checkout changed'
  for name,sha in hashes.items():assert hashlib.sha256((source/name).read_bytes()).hexdigest()==sha,name
  source_unchanged=True
 except Exception as error:failed('source_postcheck',error)
 try:
  gpu_after=subprocess.check_output(['nvidia-smi','--query-gpu=index,utilization.gpu,memory.used','--format=csv,noheader'],text=True)
 except Exception as error:failed('gpu_postcheck',error)
logs=''
for name in ('stdout.log','stderr.log'):
 path=dest/name
 if not path.exists():path.write_text('')
 logs+=path.read_text()
passed=not errors and returncode==0 and re.search(r'Ran 12 tests',logs) is not None and re.search(r'^OK$',logs,re.M) is not None and 'skipped=' not in logs
record={'completed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':returncode,'passed':passed,'skips_permitted':False,'expected_tests':12,'source_unchanged':source_unchanged,'runtime_unchanged':runtime_unchanged,'gpu_after':gpu_after,'errors':errors}
(dest/'exit.json').write_text(json.dumps(record,indent=2)+'\n')
files=[]
for name in ('invocation.json','stdout.log','stderr.log','exit.json'):
 data=(dest/name).read_bytes();files.append({'name':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'data':__import__('base64').b64encode(data).decode()})
print(json.dumps({'record':record,'remote':str(dest),'files':files}))
