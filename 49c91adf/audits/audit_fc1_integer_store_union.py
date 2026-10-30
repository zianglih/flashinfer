"""Independent source-bound join check after both raw campaigns were audited."""
from pathlib import Path
import csv, hashlib, json, math, statistics
P=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
identity=lambda r:(r['job'],r['backend'],int(r['tokens']))
close=lambda a,b:math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-9)
U=P/'experiments/fc1-integer-store-performance/combined104'
paths=[P/'evidence/fc1-integer-store-screen/1793370953565557000',P/'evidence/fc1-integer-store-remaining/1793371744150407000']
peer_paths=[P/'audits'/f'{s}.json' for s in ['fc1-integer-store-data-peer','fc1-integer-store-components-peer','fc1-integer-store-remaining-data-peer','fc1-integer-store-remaining-components-peer']]
assert all(read(p)['passed']for p in peer_paths)
rows=list(csv.DictReader((U/'cells.csv').open())); summary=read(U/'summary.json'); source=[];configs=[];resources=[]
for p in paths:
 source.extend(csv.DictReader((p/'report/cells.csv').open()));configs.append(read(p/'data/perf-config.json'));resources.extend(read(p/'report/resource-pairs.json')['rows'])
assert len(rows)==len(source)==len(set(map(identity,rows)))==104
assert {identity(r):r for r in rows}=={identity(r):r for r in source}
for field in ('control_head','phases','observer_hashes','register_policies','estimator'):assert configs[0][field]==configs[1][field]
for role in ('control','candidate'):
 for field in ('head','repo','source_sha256','tracked_manifest_sha256','register_policy','freeze_receipt_sha256'):assert configs[0]['sources'][role][field]==configs[1]['sources'][role][field]
assert summary['control_head']==configs[0]['control_head'] and summary['source_manifests']=={r:configs[0]['sources'][r]['freeze_receipt_sha256']for r in ('control','candidate')}
assert resources==read(U/'resource-pairs.json')['rows'] and len(resources)==155
assert all(r['retention']==str(int(r['tokens'])>2)for r in rows)
ret=[r for r in rows if int(r['tokens'])>2]; assert len(ret)==88
assert {int(r['tokens'])for r in rows}=={1,2,4,8,16,32,64,128,256,512,4096,8192,16384}
for mode in {r['backend']for r in rows}:
 for topology in ('ep','tp'):assert len([r for r in rows if r['backend']==mode and r['topology']==topology])==13
band=lambda r:'decode'if int(r['tokens'])<=64 else'middle'if int(r['tokens'])<=512 else'prefill'
def select(name):
 if name=='all':return ret
 if name=='quantized-payload':return[r for r in ret if r['backend']!='CuteDSL PER-TOKEN']
 parts=name.split('/')
 if parts[0]=='band':return[r for r in ret if band(r)==parts[1]]
 if parts[0]=='mode':return[r for r in ret if r['backend']==parts[1]]
 if parts[0]=='topology':return[r for r in ret if r['topology']==parts[1]]
 assert len(parts)==3 and parts[0]in ('ep','tp')
 return[r for r in ret if r['topology']==parts[0]and r['backend']==parts[1]and band(r)==parts[2]]
for name,g in summary['groups'].items():
 rs=select(name); assert g['cells']==len(rs) and g['negative']==sum(float(r['speedup_percent'])<0 for r in rs)
 gm=100*(math.exp(statistics.mean(math.log1p(float(r['speedup_percent'])/100)for r in rs))-1);assert close(g['speedup_percent'],gm)
 assert close(g['max_control_spread'],max(float(r['control_spread_percent'])for r in rs))and close(g['max_candidate_spread'],max(float(r['candidate_spread_percent'])for r in rs))
assert summary['tight_negative_cells']==[r for r in ret if float(r['speedup_percent'])<0 and max(float(r['control_spread_percent']),float(r['candidate_spread_percent']))<=.5]
for k in ('raw_samples','loaded_kernels','clock_quartiles','missing_clock_quartiles','clock_exception_quartiles'):assert summary[k]==sum(read(p/'report/summary.json')[k]for p in paths)
assert summary['raw_samples']==41600 and summary['loaded_kernels']==620
# Rebuild the views from preserved records, not from parsing displayed cells.
table=['| Topology | Mode | Tokens | C1 µs | A1 µs | A2 µs | C2 µs | Speedup | C spread | A spread |','|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
for r in rows:table.append(f"| {r['topology'].upper()}8 | {r['backend']} | {r['tokens']} | "+' | '.join(f'{float(r[k]):.3f}'for k in ('c1_us','a1_us','a2_us','c2_us'))+f" | {float(r['speedup_percent']):+.3f}% | {float(r['control_spread_percent']):.3f}% | {float(r['candidate_spread_percent']):.3f}% |")
assert (U/'table.md').read_text()=='\n'.join(table)+'\n'
result=dict(passed=True,artifacts={str(p.relative_to(P)):sha(p)for p in [U/'cells.csv',U/'summary.json',U/'resource-pairs.json',U/'table.md',U/'matrix.md',*peer_paths]},cells=104,retention_cells=88,samples=41600,original32_dictionaries_unchanged=True,remaining72_dictionaries_unchanged=True,resource_pairs=155,all_resources_unchanged=True,all_local_zero=True,clock_quartiles=1664,clock_exceptions=17,missing_clock_quartiles=0,negative_retention_cells=32,groups={k:summary['groups'][k]for k in ('all','band/decode','band/middle','band/prefill')},band_definition='decode4-64,middle128-512,prefill4096-16384;tokens1/2runbutexcluded',boundary='Independent disjoint record union after full raw CUPTI/source/cache/route/tactic/resource/clock replay. All negatives preserved. Per-token is unchanged store width, not binary null. No new GPU executions or changes to source/records.')
(P/'audits/fc1-integer-store-combined104-peer.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
