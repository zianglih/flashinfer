"""Preserve the original32 rows and join the disjoint72-cell extension."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import math
import statistics

p=argparse.ArgumentParser();p.add_argument('remaining',type=Path);a=p.parse_args()
HERE=Path(__file__).resolve().parent;PROJECT=HERE.parents[1]
initial=PROJECT/'evidence/fc1-integer-store-screen/1793370953565557000/data'
sources=[initial,a.remaining.resolve()];out=HERE/'combined104';out.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
identity=lambda r:(r['job'],r['backend'],int(r['tokens']))
gm=lambda rs:100*(math.exp(statistics.mean(math.log1p(float(r['speedup_percent'])/100)for r in rs))-1)
configs=[json.loads((s/'perf-config.json').read_text())for s in sources]
for role in ('control','candidate'):
    for field in ('head','repo','source_sha256','tracked_manifest_sha256','register_policy','freeze_receipt_sha256'):
        assert configs[0]['sources'][role][field]==configs[1]['sources'][role][field]
for field in ('control_head','phases','observer_hashes','register_policies','estimator'):
    assert configs[0][field]==configs[1][field]
rows=[];summaries=[];resources=[];inputs=[]
for source,count in zip(sources,(32,72),strict=True):
    report=source.parent/'report';s=json.loads((report/'summary.json').read_text());assert s['passed']and s['complete_campaign']and s['measured_cells']==count
    native=json.loads((report/'resource-pairs.json').read_text());assert native['passed'];resources.extend(native['rows'])
    cells=list(csv.DictReader((report/'cells.csv').open()));assert len(cells)==count
    assert not set(map(identity,rows))&set(map(identity,cells));rows.extend(cells);summaries.append(s)
    inputs.append(dict(data=str(source),config_sha256=sha(source/'perf-config.json'),cells_sha256=sha(report/'cells.csv'),summary_sha256=sha(report/'summary.json'),resources_sha256=sha(report/'resource-pairs.json'),cells=count))
original=list(csv.DictReader((initial.parent/'report/cells.csv').open()))
assert all(next(r for r in rows if identity(r)==identity(old))==old for old in original)
rows.sort(key=identity);assert len(rows)==len(set(map(identity,rows)))==104
assert {int(r['tokens'])for r in rows}=={1,2,4,8,16,32,64,128,256,512,4096,8192,16384}
assert all((r['retention']=='True')==(int(r['tokens'])>=4)for r in rows)
kept=[r for r in rows if r['retention']=='True'];assert len(kept)==88
with(out/'cells.csv').open('w')as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
band=lambda r:'decode'if int(r['tokens'])<=64 else'middle'if int(r['tokens'])<=512 else'prefill'
groups={};selectors=[('all',lambda r:True),('quantized-payload',lambda r:r['backend']!='CuteDSL PER-TOKEN')]
selectors += [('band/'+b,lambda r,b=b:band(r)==b)for b in ('decode','middle','prefill')]
selectors += [('mode/'+b,lambda r,b=b:r['backend']==b)for b in sorted({r['backend']for r in rows})]
selectors += [('topology/'+t,lambda r,t=t:r['topology']==t)for t in ('ep','tp')]
selectors += [(t+'/'+m+'/'+b,lambda r,t=t,m=m,b=b:r['topology']==t and r['backend']==m and band(r)==b)for t in ('ep','tp')for m in sorted({r['backend']for r in rows})for b in ('decode','middle','prefill')]
for name,select in selectors:
    selected=[r for r in kept if select(r)];groups[name]=dict(cells=len(selected),speedup_percent=gm(selected),negative=sum(float(r['speedup_percent'])<0 for r in selected),max_control_spread=max(float(r['control_spread_percent'])for r in selected),max_candidate_spread=max(float(r['candidate_spread_percent'])for r in selected))
tight=[r for r in kept if float(r['speedup_percent'])<0 and max(float(r['control_spread_percent']),float(r['candidate_spread_percent']))<=.5]
summary=dict(passed=True,cells=104,retention_cells=88,raw_samples=sum(s['raw_samples']for s in summaries),original32_unchanged=True,inputs=inputs,control_head=configs[0]['control_head'],source_manifests={r:configs[0]['sources'][r]['freeze_receipt_sha256']for r in ('control','candidate')},estimator=configs[0]['estimator'],groups=groups,tight_negative_cells=tight,resource_pairs=len(resources),resources_unchanged=all(r['resources_unchanged']for r in resources),**{k:sum(s[k]for s in summaries)for k in ('loaded_kernels','clock_quartiles','missing_clock_quartiles','clock_exception_quartiles')},boundary='Exact disjoint32+72CAAC union; no row/sample/negative removed. Tokens1/2excluded only from retention. Per-token is an unchanged-store-width comparator, not a binary-null control. Source/timing/helper identities agree across both campaigns. No unrelated364cell timing rerun.')
assert summary['raw_samples']==41600
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
(out/'resource-pairs.json').write_text(json.dumps(dict(passed=True,rows=resources),indent=2)+'\n')
lines=['| Topology | Mode | Tokens | C1 µs | A1 µs | A2 µs | C2 µs | Speedup | C spread | A spread |','|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
for r in rows:lines.append(f"| {r['topology'].upper()}8 | {r['backend']} | {r['tokens']} | "+' | '.join(f'{float(r[k]):.3f}'for k in ('c1_us','a1_us','a2_us','c2_us'))+f" | {float(r['speedup_percent']):+.3f}% | {float(r['control_spread_percent']):.3f}% | {float(r['candidate_spread_percent']):.3f}% |")
(out/'table.md').write_text('\n'.join(lines)+'\n')
tokens=sorted({int(r['tokens'])for r in rows});lines=['| Topology | Mode | '+' | '.join(map(str,tokens))+' |','|---|---|'+'---:|'*len(tokens)]
for t,m in sorted({(r['topology'],r['backend'])for r in rows}):
    selected={int(r['tokens']):r for r in rows if(r['topology'],r['backend'])==(t,m)}
    lines.append(f'| {t.upper()}8 | {m} | '+' | '.join(f'{float(selected[n]["speedup_percent"]):+.3f}%'for n in tokens)+' |')
(out/'matrix.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(summary))
