"""Inspect diagnostic d1 without package or cache mutation."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess

root=Path(__file__).resolve().parents[1]
remote='''import json,subprocess,datetime
from pathlib import Path
root=Path('/data/home/ziangli/flashinfer-sglang-megamoe-benchmark-alignment');rid='glm52-numerics-20260920-d1'
launch=json.loads((root/'diagnostic-launches'/(rid+'.json')).read_text());run=root/'diagnostics'/rid
def read(p):return json.loads(p.read_text()) if p.exists() else None
def tail(p):
 if not p.exists():return None
 with p.open('rb') as f:f.seek(0,2);f.seek(max(0,f.tell()-4500));return f.read().decode(errors='replace')
print(json.dumps({'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'launch':launch,'pid_alive':(Path('/proc')/str(launch['pid'])).exists(),'exit':read(run/'exit.json'),'worker':read(run/'worker.json'),'log_tail':tail(run/'diagnostic.log'),'launcher_tail':tail(Path(launch['log'])),'gpu':subprocess.check_output(['nvidia-smi','--query-gpu=index,utilization.gpu,memory.used','--format=csv,noheader,nounits'],text=True)}))
'''
r=subprocess.run(['/usr/local/bin/h','ssh','fi-sglang-align-0920','-c','c2','-n','ziangli','--','python3','-c',remote],capture_output=True)
d=root/'artifacts/diagnostic-status';d.mkdir(exist_ok=True);stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
(d/(stamp+'.stdout.json')).write_bytes(r.stdout);(d/(stamp+'.stderr')).write_bytes(r.stderr)
if r.returncode:raise RuntimeError(r.stderr.decode())
print(json.dumps(json.loads(r.stdout),indent=2))
