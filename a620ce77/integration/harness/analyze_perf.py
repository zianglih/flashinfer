"""Audit paired fixed-winner CUPTI phases and their kernel/clock timelines."""
import argparse,collections,hashlib,json,math,statistics
from pathlib import Path

med=statistics.median
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def analyze(root):
 receipt_path=root/'receipt.json';r=json.loads(receipt_path.read_text());assert r['complete']and all(p['verified']for p in r['phases']);phases=[];samples=[]
 for p in r['phases']:
  role=p.get('role',p.get('arm'));label=f"{p['index']}-{role}";f=root/label/'results.json';assert sha(f)==p['results_sha256'];d=json.loads(f.read_text());assert d['profile_calls']==0 and not d['native_diagnostic']['admitted_tactics'];telemetry=[json.loads(x)for x in(root/'telemetry'/label/'samples.jsonl').read_text().splitlines()];measurements=iter(d['native_diagnostic']['measurements'])
  for row in d['rows']:
   for result in row['results']:
    m=next(measurements);assert len(m['milliseconds'])==100 and m['event_fallback_forbidden']and m['timer']=='CUPTI';rr=[]
    for i,(ms,(a,b))in enumerate(zip(m['milliseconds'],m['iter_timestamps'])):
     ids={l[2]for l in m['launches']if a<=l[0]<=b};ks=sorted((k for k in m['activities']if k[3]in ids),key=lambda k:k[1]);assert 4 <= len(ks) <= 9,(root,row['tokens'],len(ks));first=min(k[1]for k in ks);end=max(k[2]for k in ks);assert math.isclose((end-first)/1e6,ms,abs_tol=1e-12);last=first;gc=qc=0;z=dict(phase=label,role=role,tokens=row['tokens'],backend=result['backend'],index=i,e2e_us=ms*1000)
     for k in ks:
      n=k[0]
      if 'Sm100BlockScaledGroupedGemmKernel'in n or 'Sm100W4A16GroupedGemmKernel'in n:gc+=1;name=f'fc{gc}'
      elif 'Quantize'in n:qc+=1;name='input_quant'if qc==1 else'intermediate_quant'
      elif 'routingInitExpertCounts'in n:name='route_init'
      elif 'topk_kernel'in n:name='route_topk'
      elif 'routingIndices'in n:name='route_sort'
      elif 'MoeFinalizeKernel'in n:name='combine'
      else:name='other_'+str(ks.index(k))
      z[name+'_us']=(k[2]-k[1])/1000;z[name+'_start_us']=(k[1]-first)/1000;z[name+'_end_us']=(k[2]-first)/1000;z[name+'_extension_us']=max(0,k[2]-max(last,k[1]))/1000;z[name+'_gap_us']=max(0,k[1]-last)/1000;last=max(last,k[2])
     assert gc==2;assert qc == (2 if result['backend']=='CuteDSL PER-TOKEN' else 1 if result['backend']=='CuteDSL W4A4' else 0),(result['backend'],qc);assert math.isclose(sum(v for k,v in z.items()if k.endswith(('_extension_us','_gap_us'))),z['e2e_us'],abs_tol=1e-8)
     z['fc2_after_fc1_us']=z['fc2_end_us']-z['fc1_end_us'];z['clock_begin_ns']=first;z['clock_end_ns']=end;rr.append(z)
    keys=[k for k in rr[0]if k.endswith('_us')];tactics=list({json.dumps({k:h[k]for k in('key','runner','tactic')},sort_keys=True):{k:h[k]for k in('key','runner','tactic')}for h in m['cache_hits']}.values());o=dict(phase=label,role=role,tokens=row['tokens'],backend=result['backend'],medians={k:med(z[k]for z in rr)for k in keys},tactics=tactics,quartiles=[])
    for q in range(4):
     qr=rr[q*25:(q+1)*25];begin=min(z['clock_begin_ns']for z in qr);end=max(z['clock_end_ns']for z in qr);tt=[t for t in telemetry if begin<=t['start']['cupti_ns']<=end]
     clock={k:dict(min=min(t[k]for t in tt),median=med(t[k]for t in tt),max=max(t[k]for t in tt))for k in('sm_mhz','memory_mhz','power_mw','temperature_c')} if tt else {};clock.update(available=bool(tt),reasons=dict(collections.Counter(str(t['clocks_event_reasons'])for t in tt)),samples=len(tt));o['quartiles'].append(dict(quartile=q,medians={k:med(z[k]for z in qr)for k in keys},clock=clock))
    phases.append(o);samples+=rr
  assert next(measurements,None)is None
 cells=[]
 for tokens,backend in sorted({(p['tokens'],p['backend'])for p in phases}):
  pp=[p for p in phases if(p['tokens'],p['backend'])==(tokens,backend)];roles={p['role']for p in pp}
  if roles=={'control','candidate'}:ordered_roles=('control','candidate')
  elif roles=={'candidate'}:ordered_roles=('candidate',)
  else:raise AssertionError(roles)
  by={role:[p for p in pp if p['role']==role]for role in ordered_roles};assert all(len(x)==2 for x in by.values());times={role:[p['medians']['e2e_us']for p in v]for role,v in by.items()};g={role:math.sqrt(math.prod(v))for role,v in times.items()};cells.append(dict(tokens=tokens,backend=backend,control_us=g.get('control'),candidate_us=g['candidate'],speedup_percent=(g['control']/g['candidate']-1)*100 if 'control' in g else None,repeat_spread_percent={role:(max(v)/min(v)-1)*100 for role,v in times.items()},phase_us=times,component_medians={role:{key:med(p['medians'][key]for p in v)for key in v[0]['medians']}for role,v in by.items()},clock_mhz=sorted({q['clock']['sm_mhz']['median']for p in pp for q in p['quartiles']if q['clock']['available']}),clock_reasons=sorted({k for p in pp for q in p['quartiles']for k in q['clock']['reasons']})))
 out=dict(complete=True,receipt_sha256=sha(receipt_path),job=r.get('job'),sources=r.get('sources'),boundary=r['boundary'],cells=cells,phases=phases);(root/'analysis.json').write_text(json.dumps(out,indent=2)+'\n');(root/'component-samples.json').write_text(json.dumps(samples)+'\n');return out

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('root',type=Path);a=p.parse_args();x=analyze(a.root);print(json.dumps(x['cells'],indent=2))
