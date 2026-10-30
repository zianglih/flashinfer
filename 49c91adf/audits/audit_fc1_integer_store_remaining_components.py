"""Independent native resource sequence and overlapping component audit."""
from pathlib import Path
import hashlib,json,math,statistics
R=Path(__file__).resolve().parents[1];E=R/'evidence/fc1-integer-store-remaining/1793371744150407000';D=E/'data';read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();same=lambda a,b:math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-8)
cfg=read(D/'perf-config.json');saved=read(E/'report/resource-pairs.json');resources=[];components=[];phase_count=0
fields=('index','gather_input','launch_threads','compile_options','route_tile','cta_group_size','tile_k','activation_dtype','weight_dtype')
for job in cfg['jobs']:
 folder=D/'results'/job;receipt=read(folder/'receipt.json');analysis=read(folder/'analysis.json');compiled=[];phases={}
 for phase in receipt['phases']:
  label=f"{phase['index']}-{phase['role']}";guards=phase['register_guards'];assert len(guards)==1;gpath=folder/Path(guards[0]['path']).relative_to(Path(cfg['output'])/job);assert sha(gpath)==guards[0]['sha256'];g=read(gpath);assert g['all_guarded']and g['exitstatus']==0
  compiled.append([dict(configuration={f:x[f]for f in fields},resources=x['analysis'])for x in g['compilations']])
  raw=read(folder/label/'results.json');ms=iter(raw['native_diagnostic']['measurements'])
  for row in raw['rows']:
   for result in row['results']:
    m=next(ms);values=[]
    for begin,end in m['iter_timestamps']:
     ids={x[2]for x in m['launches']if begin<=x[0]<=end};ks=sorted([x for x in m['activities']if x[3]in ids],key=lambda x:x[1]);frontier=ks[0][1];count=0;v={}
     for k in ks:
      if'Sm100BlockScaledGroupedGemmKernel'in k[0]:count+=1;name=f'fc{count}'
      elif'MoeFinalizeKernel'in k[0]:name='combine'
      else:name=None
      if name:v[name+'_us']=(k[2]-k[1])/1000;v[name+'_extension_us']=max(0,k[2]-max(frontier,k[1]))/1000
      frontier=max(frontier,k[2])
     assert count==2;values.append(v)
    medians={k:statistics.median(v[k]for v in values)for k in values[0]};a=next(x for x in analysis['phases']if(x['phase'],x['tokens'],x['backend'])==(label,row['tokens'],result['backend']));assert all(same(v,a['medians'][k])for k,v in medians.items());phases[(row['tokens'],result['backend'],label)]=medians;phase_count+=1
  assert next(ms,None)is None
 assert compiled[0]==compiled[3]and compiled[1]==compiled[2]and len(compiled[0])==len(compiled[1])
 for x,y in zip(compiled[0],compiled[1],strict=True):
  assert x==y and x['resources']['local_bytes']==0
  match=next(z for z in saved['rows']if z['job']==job and z['configuration']==x['configuration']);assert match['control']==x['resources']and match['candidate']==y['resources']and match['resources_unchanged'];resources.append(match)
 for cell in analysis['cells']:
  t,b=cell['tokens'],cell['backend'];a={k:statistics.mean(phases[t,b,p][k]for p in ['0-control','3-control'])for k in phases[t,b,'0-control']};c={k:statistics.mean(phases[t,b,p][k]for p in ['1-candidate','2-candidate'])for k in a};components.append(dict(job=job,tokens=t,backend=b,e2e_speedup_percent=cell['speedup_percent'],both_candidates_below_both_controls=max(cell['phase_us']['candidate'])<min(cell['phase_us']['control']),control=a,candidate=c,delta={k:c[k]-a[k]for k in a},phase_us=cell['phase_us']))
assert len(resources)==len(saved['rows'])==99 and phase_count==288 and len(components)==72
out=dict(passed=True,resource_pairs=99,all_resources_equal=True,all_local_zero=True,component_phase_medians_recomputed=phase_count*6,source_and_raw_audit_sha256=sha(R/'audits/fc1-integer-store-remaining-data-peer.json'),native_resource_report_sha256=sha(E/'report/resource-pairs.json'),components=components,boundary='Native resources paired by guarded compilation sequence and frozen choice identity; no exact timed token-to-library/native-cubin claim. FC1/FC2 are successive GEMM activities on the dependent chain; component extensions account for overlap. Medians of separate components need not sum to E2E median. No new GPU measurements.')
(R/'audits/fc1-integer-store-remaining-components-peer.json').write_text(json.dumps(out,indent=2)+'\n')
for row in components:
 if row['tokens']>=4096:print(row['job'],row['tokens'],row['backend'],round(row['e2e_speedup_percent'],3),row['both_candidates_below_both_controls'],{k:round(v,3)for k,v in row['delta'].items()if k.endswith('extension_us')})
