"""Launch the approved merged-head full AA after existing preflight and exact smoke."""
from pathlib import Path
import base64,hashlib,json,subprocess
H=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
plan=json.loads((H/'plan.json').read_text());assert plan['passed']and plan['cells']==468 and plan['samples']==93600
config_sha=sha(H/'screen/perf-config.json');assert config_sha==plan['config_sha256']
code=r'''
from pathlib import Path
import hashlib,json,subprocess,time
R=Path('/data/ziangli/flashinfer-moe-gather-pipeline');H=R/'integration/pr7290-refresh-20261030';O=R/'runs/pr7290-retained-refresh';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
c=json.loads((O/'perf-config.json').read_text());p=json.loads((O/'launch-preflight.json').read_text());smoke=json.loads((H/'smoke/receipt.json').read_text())
assert sha(O/'perf-config.json')==CONFIG_SHA and p['passed']and p['config_sha256']==CONFIG_SHA
assert smoke['passed']and smoke['complete']and len(smoke['runs'])==7 and smoke['full_source_postflight']and smoke['native_cache_unchanged']
assert not(O/'campaign.json').exists() and not(O/'launch.json').exists()
for row in p['native_modules']:
 lib=Path(row['library']);assert sha(lib)==row['library_sha256']and sha(lib.parent/'build.ninja')==row['ninja_sha256'];assert 'no work to do'in subprocess.check_output(['ninja','-n','-C',str(lib.parent)],text=True)
idle=[]
for gpu in range(8):
 samples=[]
 for _ in range(2):
  line=subprocess.check_output(['nvidia-smi','-i',str(gpu),'--query-gpu=uuid,memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip();u,m,v=[x.strip()for x in line.split(',')];apps=subprocess.check_output(['nvidia-smi','-i',str(gpu),'--query-compute-apps=pid','--format=csv,noheader'],text=True).strip()
  assert not apps and int(m)<=16 and int(v)==0 and u==next(x['uuid']for x in p['idle']if x['gpu']==gpu),(gpu,line,apps)
  samples.append(dict(uuid=u,memory_mib=int(m),utilization=int(v),compute_pids=apps));time.sleep(.15)
 idle.append(dict(gpu=gpu,samples=samples))
(O/'smoke-receipt.json').write_bytes((H/'smoke/receipt.json').read_bytes());(O/'smoke-plan.json').write_bytes((H/'smoke/plan.json').read_bytes())
command=[c['python'],'-u',str(H/'harness/campaign.py'),'--config',str(O/'perf-config.json'),'--gpus',*map(str,range(8))]
with(O/'controller.log').open('x')as log:proc=subprocess.Popen(command,cwd=O,stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True)
r=dict(passed=True,pid=proc.pid,launched=time.time(),command=command,head=c['control_head'],jobs=31,cells=468,samples=93600,config_sha256=CONFIG_SHA,preflight_sha256=sha(O/'launch-preflight.json'),smoke_receipt_sha256=sha(H/'smoke/receipt.json'),idle=idle)
(O/'launch.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
'''
code='CONFIG_SHA='+repr(config_sha)+'\n'+code
p=subprocess.run(['/usr/local/bin/h','ssh','fi-gather-pipeline-resume-1030','-c','c2','-n','ziangli','--','python3','-c',code],cwd='/Users/ziangli/playground/repos/hai',text=True,capture_output=True)
(H/'screen/launch.stdout').write_text(p.stdout);(H/'screen/launch.stderr').write_text(p.stderr);p.check_returncode();r=json.loads(p.stdout);assert r['passed'];(H/'screen/launch.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
