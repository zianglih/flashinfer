"""Independent all-cell replay of the frozen integer-store482b CUPTI evidence."""
from pathlib import Path
import collections, csv, hashlib, json, math, statistics, sys

P=Path(__file__).resolve().parents[1]
R=Path(sys.argv[1]).resolve()
D=R/'data'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
close=lambda a,b:math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-9)
fetch=read(R/'fetch-receipt.json')
assert fetch['passed']
for n,h in fetch['files'].items():assert sha(D/n)==h,n
c=read(D/'perf-config.json');campaign=read(D/'campaign.json')
assert campaign['complete'] and campaign['passed']
assert campaign['config_sha256']==sha(D/'perf-config.json')
assert c['phases']==['control','candidate','candidate','control']
assert c['control_head']=='bf072d26b163e71458e7e4dfb12e615b19bd2c9a'
q=read(D/'qualification.json');assert q['passed']and q['candidate_kernel_sha256']=='482b636a1714486e2ffb34c8ae005da3cef26f25f0ce034ba1eb59c6198d6276'
assert q['qualification_summary_sha256']==sha(P/q['qualification_summary'])
control=read(D/'control-tracked.json');candidate=read(D/'candidate-tracked.json');delta=[n for n in control if control[n]!=candidate[n]];assert delta==['flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py']
assert candidate[delta[0]]==q['candidate_kernel_sha256']
cache_import=read(P/'harness/cache-import.json');assert cache_import['passed']and cache_import['no_retuning']
for role,s in c['sources'].items():
    m=D/Path(s['tracked_manifest']).name
    assert sha(m)==s['tracked_manifest_sha256']
    full=read(m)
    assert len(full)==13245 and all(full[n]==v for n,v in s['source_sha256'].items())
    for side in ('full_source_before','full_source_after'):
        assert campaign[side][role]['manifest_sha256']==sha(m)
        assert campaign[side][role]['files']==len(full)
rows=[];sample_count=phase_count=guards=quartiles=clock_gaps=clock_exceptions=0
for name,j in c['jobs'].items():
    folder=D/'results'/name;r=read(folder/'receipt.json');a=read(folder/'analysis.json')
    assert r['complete'] and r['job']==j and r['sources']==c['sources']
    assert r['config_sha256']==sha(D/'perf-config.json') and r['observer_hashes']==c['observer_hashes']
    assert a['complete'] and a['receipt_sha256']==sha(folder/'receipt.json')
    assert [x['role'] for x in r['phases']]==c['phases']
    expected=read(P/'harness/frozen-inputs'/name/'expected.json')
    assert sha(P/'harness/frozen-inputs'/name/'expected.json')==r['winner_results_sha256']
    route={x['tokens']:x['routing_identity'] for x in expected['rows']}
    es=iter(expected['native_diagnostic']['measurements']);tactics={}
    for er in expected['rows']:
        for result in er['results']:
            em=next(es)
            tactics[(er['tokens'],result['backend'])]={json.dumps({k:h[k] for k in ('key','runner','tactic')},sort_keys=True) for h in em['cache_hits']}
    assert next(es,None) is None
    imported=cache_import['jobs'][name];namespace='v2/'+imported['env_hash']
    cache={namespace+'/entries/'+p.name:sha(p)for p in(P/'harness/frozen-inputs'/name/'cache').glob('v2/*/entries/*.json')}
    cache[namespace+'/manifest.json']=hashlib.sha256((json.dumps(imported['manifest'],indent=2,sort_keys=True)+'\n').encode()).hexdigest()
    assert cache==r['winner_cache_manifest']
    medians={};contracts={}
    for phase in r['phases']:
        role=phase['role'];label=f"{phase['index']}-{role}";path=folder/label/'results.json';data=read(path)
        assert phase['verified'] and phase['returncode']==0 and sha(path)==phase['results_sha256']
        assert phase['gpu_before'].split(',')[0]==phase['gpu_after'].split(',')[0]==r['gpu_initial'].split(',')[0]
        assert sha(folder/f'{label}.log')==phase['stdout_sha256']
        assert data['complete'] and data['swap_ab'] and not data['use_fused_finalize'] and data['exit_code']==0
        assert data['profile_calls']==0 and not data['native_diagnostic']['admitted_tactics']
        assert data['benchmark_sha256']==c['sources'][role]['source_sha256']['benchmarks/bench_moe_deepseek.py']
        assert data['managed_cache_before']==data['managed_cache_after']==r['winner_cache_manifest']
        assert data['observer_sha256']==c['observer_hashes']['observe_benchmark.py']
        telemetry=[json.loads(z) for z in (folder/'telemetry'/label/'samples.jsonl').read_text().splitlines()]
        assert sha(folder/'telemetry'/label/'receipt.json')==phase['telemetry_receipt_sha256']
        measures=iter(data['native_diagnostic']['measurements'])
        for row in data['rows']:
            assert row['routing_identity']==route[row['tokens']]
            assert row['include_activation_quant']==(j['family']=='nvfp4')
            assert sorted(row['backend_labels'])==sorted(j['expected_backends'])
            assert row['quantization_environment_before']==row['quantization_environment_after']
            ident=row['tokens'];contract=(row['arm_contracts'],row['histogram'])
            if ident in contracts:assert contracts[ident]==contract
            else:contracts[ident]=contract
            for result in row['results']:
                m=next(measures);key=(row['tokens'],result['backend'])
                assert m['timer']=='CUPTI' and m['event_fallback_forbidden']
                assert len(m['milliseconds'])==len(m['iter_timestamps'])==100
                assert all(x['hit'] and x['tactic']!=-1 for x in m['cache_hits'])
                assert all(x['profiling_policy'][-1]=='cold'for x in m['cache_hits'])
                assert m['profile_calls_before']==m['profile_calls_after']==0 and not m['tuning_mode']
                selected={json.dumps({k:h[k] for k in ('key','runner','tactic')},sort_keys=True) for h in m['cache_hits']}
                assert selected==tactics[key] and len(selected)==1
                bounds=[];raw=[]
                for ms,(begin,end) in zip(m['milliseconds'],m['iter_timestamps']):
                    ids={x[2] for x in m['launches'] if begin<=x[0]<=end}
                    kernels=[x for x in m['activities'] if x[3] in ids]
                    assert 4<=len(kernels)<=9
                    assert sum('Sm100BlockScaledGroupedGemmKernel' in x[0] for x in kernels)==2
                    assert sum('Quantize' in x[0] for x in kernels)==(2 if key[1]=='CuteDSL PER-TOKEN' else 1 if key[1]=='CuteDSL W4A4' else 0)
                    lo=min(x[1] for x in kernels);hi=max(x[2] for x in kernels)
                    assert close((hi-lo)/1e6,ms) and math.isfinite(ms) and ms>0
                    bounds.append((lo,hi));raw.append(ms*1000)
                median=statistics.median(raw)
                assert close(median,m['median_ms']*1000) and close(median,result['latency_ms']*1000)
                medians[(label,*key)]=median
                ap=next(x for x in a['phases'] if (x['phase'],x['tokens'],x['backend'])==(label,*key))
                assert close(ap['medians']['e2e_us'],median)
                for q in range(4):
                    lo=min(x[0] for x in bounds[q*25:(q+1)*25]);hi=max(x[1] for x in bounds[q*25:(q+1)*25])
                    ts=[x for x in telemetry if lo<=x['start']['cupti_ns']<=hi]
                    actual=ap['quartiles'][q];clock=actual['clock']
                    assert close(actual['medians']['e2e_us'],statistics.median(raw[q*25:(q+1)*25]))
                    assert clock['available']==bool(ts) and clock['samples']==len(ts)
                    assert clock['reasons']==dict(collections.Counter(str(x['clocks_event_reasons']) for x in ts))
                    for f in ('sm_mhz','memory_mhz','power_mw','temperature_c'):
                        if ts:assert clock[f]==dict(min=min(x[f] for x in ts),median=statistics.median(x[f] for x in ts),max=max(x[f] for x in ts))
                    clock_gaps+=not ts
                    clock_exceptions+=bool(ts) and (clock['sm_mhz']['median']!=2032 or any(x!='0' for x in clock['reasons']))
                    quartiles+=1
                sample_count+=100;phase_count+=1
        assert next(measures,None) is None
        for g in phase['register_guards']:
            rel=Path(g['path']).relative_to(Path(c['output'])/name);path=folder/rel;guard=read(path)
            assert sha(path)==g['sha256'] and guard['exitstatus']==0 and guard['all_guarded'] and not guard['compiler_options_changed']
            assert guard['kernel_sha256']==c['sources'][role]['source_sha256']['flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py']
            assert guard['policy']==c['register_policies'][role]
            for compiled in guard['compilations']:
                assert compiled['passed']and compiled['analysis']['local_bytes']==0 and compiled['compile_options']=='';guards+=1
    assert len(a['cells'])==j['expected_cells']
    for cell in a['cells']:
        key=(cell['tokens'],cell['backend'])
        v={role:[medians[(f"{p['index']}-{role}",*key)] for p in r['phases'] if p['role']==role] for role in ('control','candidate')}
        assert all(all(close(x,y) for x,y in zip(v[role],cell['phase_us'][role])) for role in v)
        control=math.sqrt(math.prod(v['control']));candidate=math.sqrt(math.prod(v['candidate']));speed=(control/candidate-1)*100
        assert close(control,cell['control_us']) and close(candidate,cell['candidate_us']) and close(speed,cell['speedup_percent'])
        rows.append(dict(job=name,tokens=key[0],backend=key[1],speedup_percent=speed))
assert len(rows)==72 and sample_count==28800 and phase_count==288 and quartiles==1152
report=list(csv.DictReader((R/'report/cells.csv').open()));assert len(report)==len(rows)
for row in rows:
    other=next(x for x in report if (x['job'],int(x['tokens']),x['backend'])==(row['job'],row['tokens'],row['backend']))
    assert close(float(other['speedup_percent']),row['speedup_percent'])
result=dict(passed=True,config_sha256=sha(D/'perf-config.json'),archive_sha256=fetch.get('archive_sha256'),source_manifests={r:s['freeze_receipt_sha256'] for r,s in c['sources'].items()},jobs=6,cells=len(rows),phase_medians=phase_count,samples=sample_count,loaded_resource_records=guards,clock_quartiles=quartiles,missing_clock_quartiles=clock_gaps,clock_exception_quartiles=clock_exceptions,negative_cells=sum(x['speedup_percent']<0 for x in rows),geomean_percent=100*(math.exp(statistics.mean(math.log1p(x['speedup_percent']/100) for x in rows))-1),all_report_cells_preserved=True,boundary='Independent raw CUPTI correlation/span, median/CAAC, route/tactic/cache/source/resource and raw NVML quartile replay. No new GPU execution; all negative and clock-exception cells preserved. No source or timing-helper changes.')
(P/'audits/fc1-integer-store-remaining-data-peer.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
