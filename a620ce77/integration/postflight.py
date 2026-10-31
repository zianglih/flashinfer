"""Verify terminal campaign source/native cache and release GPUs 1–4."""
from pathlib import Path
import json,subprocess
O=Path(__file__).resolve().parent
code=r'''
from pathlib import Path
import hashlib,json,subprocess,time
R=Path('/data/ziangli/flashinfer-moe-gather-pipeline');O=R/'runs/pr7290-retained-refresh';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
c=json.loads((O/'campaign.json').read_text());assert c['complete'] and c['passed'] and c['full_source_after']
p=json.loads((O/'launch-preflight.json').read_text());assert p['passed'];rows=[]
for x in p['native_modules']:
 lib=Path(x['library']);ninja=lib.parent/'build.ninja'
 assert sha(lib)==x['library_sha256'] and sha(ninja)==x['ninja_sha256']
 dry=subprocess.check_output(['ninja','-n','-C',str(lib.parent)],text=True);assert 'no work to do' in dry
 rows.append(dict(x,ninja_noop=dry))
gpus=[]
for gpu in range(8):
 line=subprocess.check_output(['nvidia-smi','-i',str(gpu),'--query-gpu=uuid,memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip();u,m,v=[s.strip()for s in line.split(',')]
 apps=subprocess.check_output(['nvidia-smi','-i',str(gpu),'--query-compute-apps=pid','--format=csv,noheader'],text=True).strip()
 assert int(m)<=16 and int(v)==0 and not apps,(gpu,line,apps)
 assert u==next(v['uuid'] for v in p['idle'] if v['gpu']==gpu);gpus.append(dict(gpu=gpu,uuid=u,memory_mib=int(m),utilization_percent=int(v),compute_pids=apps))
r=dict(passed=True,time=time.time(),campaign_sha256=sha(O/'campaign.json'),config_sha256=sha(O/'perf-config.json'),preflight_sha256=sha(O/'launch-preflight.json'),native_modules=rows,all_native_release_bytes_unchanged=True,full_sources_after=c['full_source_after'],gpus_idle=gpus)
(O/'release-postflight.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
'''
p=subprocess.run(['/usr/local/bin/h','ssh','fi-gather-pipeline-resume-1030','-c','c2','-n','ziangli','--','python3','-c',code],cwd='/Users/ziangli/playground/repos/hai',text=True,capture_output=True,check=True)
r=json.loads(p.stdout);assert r['passed'];(O/'screen/gpu-release.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(passed=True,campaign_sha256=r['campaign_sha256'],all_native_release_bytes_unchanged=True,gpus_idle=8)))
