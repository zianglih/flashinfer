"""Independent all-cell replay of the W4 tail cutoff CUPTI evidence."""
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
assert c['control_head']=='2b8eb9d8f72ceda3952fbb05054fee97173fc9c7'
q=read(D/'qualification-summary.json')
assert q==read(P/'experiments/w4-tail-cutoff/qualification-summary.json')
assert q['passed'] and q['split_native_pairs']==24 and q['mega_native_pairs']==2 and q['all_local_zero'] and q['all_resources_equal']
assert q['sources']['candidate']=='cbef9186731e78806884f7fa2ba5aad18f5ece379664cf8d3181d5cd54548c10'
assert q['sources']['control']=='5e61d04544524410b273b8e49ee2b8f6d9e20266c22346aba06ab3743c2c4e1d'
assert c['recovery_readiness_sha256']==sha(P/'runtime/recovery-1030/readiness.json')
qualification_receipts={
'pilot':P/'experiments/w4-tail-cutoff/qualification/evidence/1793392766283766000/data/receipt.json',
'extra':P/'experiments/w4-tail-cutoff/qualification-extra/evidence/1793393145401734000/data/receipt.json',
'reused_control':P/'experiments/w4-raw-peek/qualification/evidence/1793386426136276000/data/receipt.json',
'mega':P/'experiments/w4-tail-cutoff/mega-qualification/evidence/receipt.json'}
for name,h in q['receipts'].items():
    original=qualification_receipts[name];receipt=D/(name+'-exact-receipt.json')
    assert sha(original)==h and read(receipt)==read(original)
    assert read(receipt)['passed'] and read(receipt)['complete']
pre=read(D/'launch-preflight.json');post=read(D/'release-postflight.json')
cache=read(P/'runtime/recovery-1030/cache-ready.json')
assert pre['passed'] and post['passed'] and post['all_native_release_bytes_unchanged']
assert pre['config_sha256']==post['config_sha256']==sha(D/'perf-config.json')
assert post['campaign_sha256']==sha(D/'campaign.json') and post['preflight_sha256']==sha(D/'launch-preflight.json')
assert pre['qualification_summary_sha256']==sha(D/'qualification-summary.json')
assert pre['recovery_readiness_sha256']==c['recovery_readiness_sha256']
assert pre['cache_ready_sha256']==sha(P/'runtime/recovery-1030/cache-ready.json')
assert pre['native_modules']==post['native_modules'] and len(pre['native_modules'])==4
for n in pre['native_modules']:
    m=next(x for x in cache['modules'] if x['name']==n['name'])
    assert n['library_sha256']==m['after']['library_sha256'] and n['ninja_sha256']==m['after']['ninja_sha256'] and n['ninja_noop']
assert all(x['memory_mib']==0 and x['utilization_percent']==0 and not x['compute_pids'] for x in post['gpus_idle'])
control=read(D/'control-tracked.json');candidate=read(D/'candidate-tracked.json')
delta=[n for n in control if control[n]!=candidate[n]]
assert delta==['flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py']
assert candidate[delta[0]]=='cbef9186731e78806884f7fa2ba5aad18f5ece379664cf8d3181d5cd54548c10'
for role,s in c['sources'].items():
    m=D/Path(s['tracked_manifest']).name
    assert sha(m)==s['tracked_manifest_sha256']
    full=read(m)
    assert len(full)==13245 and all(full[n]==v for n,v in s['source_sha256'].items())
    for side in ('full_source_before','full_source_after'):
        assert campaign[side][role]['manifest_sha256']==sha(m)
        assert campaign[side][role]['files']==len(full)
rows=[];sample_count=phase_count=guards=quartiles=clock_gaps=clock_exceptions=default_joins=0
default_cells=set()
clock_details=[];resource_configs={};resource_stage_joins=0
cache_import=read(P/'harness/cache-import.json')
assert cache_import['passed'] and cache_import['no_retuning']
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
    imported=cache_import['jobs'][name];ns='v2/'+imported['env_hash']
    expected_cache={ns+'/entries/'+p.name:sha(p)for p in(P/'harness/frozen-inputs'/name/'cache').glob('v2/*/entries/*.json')}
    expected_cache[ns+'/manifest.json']=hashlib.sha256((json.dumps(imported['manifest'],indent=2,sort_keys=True)+'\n').encode()).hexdigest()
    assert r['winner_cache_manifest']==expected_cache
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
        compiled_by_library={}
        for guard_row in phase['register_guards']:
            gp=folder/Path(guard_row['path']).relative_to(Path(c['output'])/name)
            gd=read(gp);assert sha(gp)==guard_row['sha256']
            for fn in gd['compilations']:
                assert fn['compile_options']==("--ptxas-options='-maxrregcount=96'" if fn['gather_input'] else "")
                compiled_by_library[fn['library_handle']]=fn
        command=phase['command']
        assert command[command.index('--warmup')+1]=='10' and command[command.index('--iters')+1]=='100'
        assert '--no-autotune' in command and '--w4a16-only' in command
        measures=iter(data['native_diagnostic']['measurements'])
        for row in data['rows']:
            assert row['routing_identity']==route[row['tokens']]
            assert row['include_activation_quant']==(j['family']=='nvfp4')
            assert sorted(row['backend_labels'])==sorted(j['expected_backends'])
            assert row['quantization_environment_before']==row['quantization_environment_after']
            assert row['arm_contracts']['CuteDSL W4A16']['initial_activation_quantization_timed'] is False
            ident=row['tokens'];contract=(row['arm_contracts'],row['histogram'])
            if ident in contracts:assert contracts[ident]==contract
            else:contracts[ident]=contract
            for result in row['results']:
                m=next(measures);key=(row['tokens'],result['backend'])
                assert m['timer']=='CUPTI' and m['event_fallback_forbidden']
                assert len(m['milliseconds'])==len(m['iter_timestamps'])==100
                assert all(x['hit'] and x['profiling_policy'][-1]=='cold' for x in m['cache_hits'])
                assert m['profile_calls_before']==m['profile_calls_after']==0 and not m['tuning_mode']
                selected={json.dumps({k:h[k] for k in ('key','runner','tactic')},sort_keys=True) for h in m['cache_hits']}
                assert selected==tactics[key] and len(selected)==1
                tactic=json.loads(next(iter(selected)))['tactic']
                resolved=c['default_w4a16_moe_tactic'] if tactic==-1 else tactic
                if tactic==-1:default_cells.add((name,*key))
                native=m['w4_resolved_configs'];assert len(native)==2 and {n['stage']for n in native}=={'fc1','fc2'}
                for n in native:
                    assert n['supplied_moe_tactic']==(None if tactic==-1 else tactic) and n['resolved_moe_tactic']==resolved
                    fc=resolved[0 if n['stage']=='fc1'else 1]
                    assert n['mma_tiler_mnk']==fc[0] and n['cluster_shape_mn']==fc[1] and n['raster_along_m']==fc[2]
                    fn=compiled_by_library[n['compiled_library']]
                    assert fn['gather_input']==(n['stage']=='fc1')
                    for attr in ('mma_tiler_mnk','cluster_shape_mn','raster_along_m','use_clc_scheduler','enable_pdl'):assert fn[attr]==n[attr]
                    resource_key=(name,row['tokens'],n['stage'])
                    actual_resource={field:fn[field] for field in ('analysis','launch_threads','required_pool','available_initial_pool','compile_options','route_tile','cta_group_size','tile_k','activation_dtype','weight_dtype','mma_tiler_mnk','cluster_shape_mn','raster_along_m','use_clc_scheduler','enable_pdl')}
                    if resource_key in resource_configs:assert resource_configs[resource_key]==actual_resource,resource_key
                    else:resource_configs[resource_key]=actual_resource
                    resource_stage_joins+=1
                    default_joins+=int(tactic==-1)
                bounds=[];raw=[]
                for ms,(begin,end) in zip(m['milliseconds'],m['iter_timestamps']):
                    ids={x[2] for x in m['launches'] if begin<=x[0]<=end}
                    kernels=[x for x in m['activities'] if x[3] in ids]
                    assert 4<=len(kernels)<=9
                    assert sum('Sm100W4A16GroupedGemmKernel' in x[0] for x in kernels)==2
                    assert sum('Quantize' in x[0] for x in kernels)==0
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
                    if not ts or clock['sm_mhz']['median']!=2032 or any(x!='0' for x in clock['reasons']):
                        clock_details.append(dict(job=name,tokens=row['tokens'],phase=label,quartile=q,clock=clock))
                    clock_gaps+=not ts
                    clock_exceptions+=bool(ts) and (clock['sm_mhz']['median']!=2032 or any(x!='0' for x in clock['reasons']))
                    quartiles+=1
                sample_count+=100;phase_count+=1
        assert next(measures,None) is None
        for g in phase['register_guards']:
            rel=Path(g['path']).relative_to(Path(c['output'])/name);path=folder/rel;guard=read(path)
            assert sha(path)==g['sha256'] and guard['exitstatus']==0 and guard['all_guarded'] and not guard['compiler_options_changed']
            assert guard['kernel_sha256']==c['sources'][role]['source_sha256']['flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py']
            assert guard['policy']==c['register_policies'][role]
            for compiled in guard['compilations']:
                assert compiled['passed'] and compiled['analysis']['local_bytes']==0;guards+=1
    assert len(a['cells'])==j['expected_cells']
    for cell in a['cells']:
        key=(cell['tokens'],cell['backend'])
        v={role:[medians[(f"{p['index']}-{role}",*key)] for p in r['phases'] if p['role']==role] for role in ('control','candidate')}
        assert all(all(close(x,y) for x,y in zip(v[role],cell['phase_us'][role])) for role in v)
        control=math.sqrt(math.prod(v['control']));candidate=math.sqrt(math.prod(v['candidate']));speed=(control/candidate-1)*100
        assert close(control,cell['control_us']) and close(candidate,cell['candidate_us']) and close(speed,cell['speedup_percent'])
        spreads={role:(max(values)/min(values)-1)*100 for role,values in v.items()}
        assert all(close(spreads[role],cell['repeat_spread_percent'][role]) for role in spreads)
        rows.append(dict(job=name,tokens=key[0],backend=key[1],control_us=control,candidate_us=candidate,phase_us=v,speedup_percent=speed,repeat_spread_percent=spreads,gpu=r['gpu_initial'],clock_flags=[x for x in clock_details if x['job']==name and x['tokens']==key[0]]))
assert len(rows)==39 and sample_count==15600 and phase_count==156 and quartiles==624
assert len(default_cells)==5 and default_joins==40
report=list(csv.DictReader((R/'report/cells.csv').open()));assert len(report)==len(rows)
for row in rows:
    other=next(x for x in report if (x['job'],int(x['tokens']),x['backend'])==(row['job'],row['tokens'],row['backend']))
    assert close(float(other['speedup_percent']),row['speedup_percent'])
retained=[x for x in rows if x['tokens']>=4]
result=dict(retention_cells=len(retained), retention_geomean_percent=100*(math.exp(statistics.mean(math.log1p(x['speedup_percent']/100) for x in retained))-1), passed=True,config_sha256=sha(D/'perf-config.json'),archive_sha256=fetch.get('archive_sha256'),source_manifests={r:s['freeze_receipt_sha256'] for r,s in c['sources'].items()},jobs=len(c['jobs']),cells=len(rows),phase_medians=phase_count,samples=sample_count,loaded_resource_records=guards,clock_quartiles=quartiles,missing_clock_quartiles=clock_gaps,clock_exception_quartiles=clock_exceptions,negative_cells=sum(x['speedup_percent']<0 for x in rows),geomean_percent=100*(math.exp(statistics.mean(math.log1p(x['speedup_percent']/100) for x in rows))-1),default_cells=sorted(default_cells),default_stage_joins=default_joins,all_report_cells_preserved=True,boundary='Independent raw CUPTI correlation/span, median/CAAC, route/tactic/cache/source/resource and raw NVML quartile replay. Includes recorded-default to actual native geometry/library/resource joins. No new GPU execution; all negative and clock-exception cells preserved. No source or timing-helper changes.')
result.update(resource_stage_joins=resource_stage_joins,distinct_cell_stage_resources=len(resource_configs),resource_configs_identical_across_phases=True,native_release_cohort_equal=True,clock_details=clock_details,negative_rows=[x for x in rows if x['speedup_percent']<0],all_rows=rows)
def gm(v):return 100*(math.exp(statistics.mean(math.log1p(x['speedup_percent']/100) for x in v))-1)
result['retention_by_job']={j:gm([x for x in retained if x['job']==j]) for j in c['jobs']}
result['retention_by_range']={name:gm([x for x in retained if lo<=x['tokens']<=hi]) for name,lo,hi in [('decode',4,64),('middle',128,512),('prefill',4096,16384)]}
result['negative_retention_cells']=sum(x['speedup_percent']<0 for x in retained)
(P/'audits/w4-tail-cutoff-data-peer.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('clock_details','negative_rows','all_rows')},indent=2))
