"""Deploy two reviewed helpers exclusively and launch numerical diagnostic d1."""
from datetime import datetime, timezone
import base64
import hashlib
import json
from pathlib import Path
import subprocess

LOCAL = Path(__file__).resolve().parents[1]
RID = "glm52-numerics-20260920-d1"
assets = {name: base64.b64encode((LOCAL / "setup" / name).read_bytes()).decode()
          for name in ("run_numerical_diagnostic_remote.py", "capture_r3_numerical_failure.py")}
hashes = {name: hashlib.sha256(base64.b64decode(data)).hexdigest() for name, data in assets.items()}
remote = '''import base64,hashlib,json,os,subprocess,datetime
from pathlib import Path
root=Path('/data/home/ziangli/flashinfer-sglang-megamoe-benchmark-alignment')
rid=%r
assets=%r
hashes=%r
assert not (root/'diagnostics'/rid).exists()
assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip()
helpers=root/'setup'/('helpers-'+rid);helpers.mkdir(exist_ok=False)
for name,data in assets.items():
 content=base64.b64decode(data);assert hashlib.sha256(content).hexdigest()==hashes[name]
 with (helpers/name).open('xb') as f:f.write(content)
launches=root/'diagnostic-launches';launches.mkdir(exist_ok=True)
log=launches/(rid+'.log');receipt=launches/(rid+'.json');assert not receipt.exists()
argv=['/opt/sglang/bin/python3','-u',str(helpers/'run_numerical_diagnostic_remote.py'),'--task-root',str(root),'--run-id',rid]
with log.open('xb') as out:
 proc=subprocess.Popen(argv,cwd=root,env=dict(os.environ,PYTHONUNBUFFERED='1'),stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
record={'run_id':rid,'pid':proc.pid,'argv':argv,'helpers_sha256':hashes,'log':str(log),'launched_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
with receipt.open('x') as f:json.dump(record,f,indent=2)
print(json.dumps(record))
''' % (RID, assets, hashes)
dest = LOCAL / "artifacts/diagnostic-dispatches" / RID
dest.mkdir(parents=True, exist_ok=False)
for name, data in assets.items():
    (dest / name).write_bytes(base64.b64decode(data))
(dest / "request.json").write_text(json.dumps({"run_id": RID, "hashes": hashes,
    "prepared_at": datetime.now(timezone.utc).isoformat()}, indent=2) + "\n")
result = subprocess.run(["/usr/local/bin/h", "ssh", "fi-sglang-align-0920", "-c", "c2", "-n", "ziangli",
                         "--", "python3", "-c", remote], capture_output=True)
(dest / "stdout.json").write_bytes(result.stdout)
(dest / "stderr").write_bytes(result.stderr)
if result.returncode:
    raise RuntimeError(result.stderr.decode())
record = json.loads(result.stdout)
assert record["helpers_sha256"] == hashes
print(json.dumps(record, indent=2))
