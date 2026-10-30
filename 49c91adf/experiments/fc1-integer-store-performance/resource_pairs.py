"""Pair source-guarded native compilation sequences across all four phases."""
from pathlib import Path
import argparse
import json

p=argparse.ArgumentParser()
p.add_argument('data',type=Path)
a=p.parse_args()
c=json.loads((a.data/'perf-config.json').read_text())
rows=[]
configuration=('index','gather_input','launch_threads','compile_options','route_tile','cta_group_size','tile_k','activation_dtype','weight_dtype')
for job in c['jobs']:
    root=a.data/'results'/job
    receipt=json.loads((root/'receipt.json').read_text())
    assert receipt['complete'] and all(x['verified'] for x in receipt['phases'])
    phases=[]
    for phase in receipt['phases']:
        label=f"{phase['index']}-{phase['role']}"
        guards=list((root/'register-guard'/label).glob('*/receipt.json'))
        assert len(guards)==1
        guard=json.loads(guards[0].read_text())
        assert guard['all_guarded'] and guard['exitstatus']==0 and not guard['compiler_options_changed']
        assert all(x['passed'] and x['analysis']['local_bytes']==0 for x in guard['compilations'])
        phases.append([dict(configuration={k:x[k] for k in configuration},resources=x['analysis'],checks=x['checks'],required_pool=x['required_pool'],available_initial_pool=x['available_initial_pool']) for x in guard['compilations']])
    assert phases[0]==phases[3] and phases[1]==phases[2]
    assert len(phases[0])==len(phases[1])
    for before,after in zip(phases[0],phases[1],strict=True):
        assert before['configuration']==after['configuration']
        rows.append(dict(job=job,configuration=before['configuration'],control=before['resources'],candidate=after['resources'],resources_unchanged=before['resources']==after['resources'],register_delta=after['resources']['initial_regs']-before['resources']['initial_regs']))
out=a.data.parent/'report';out.mkdir(exist_ok=True)
result=dict(passed=True,rows=rows,all_resources_unchanged=all(x['resources_unchanged'] for x in rows),boundary='Deterministic native compilation sequence paired within each source-bound job. Same recorded frozen choices are separately checked by report_evidence; this metadata does not claim an exact token-to-library join beyond the existing swap guard.')
(out/'resource-pairs.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(passed=True,pairs=len(rows),all_resources_unchanged=result['all_resources_unchanged'],changed=[x for x in rows if not x['resources_unchanged']])))
