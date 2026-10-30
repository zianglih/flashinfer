"""Join fresh two-pass candidate evidence to explicitly historical baselines."""
import argparse,csv,hashlib,json,math,shutil,statistics,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];HERE=Path(__file__).resolve().parent
OLD=Path('/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n')
MEASURED_OLD='326c4a793085e79b64b9c7fd79e77320c220ccba';BASE='82254e206a44b95d9925e4594fac936731f80d21'
MODELS=[('v3','V3',8),('v41-flash','V41F',4),('kimi-k3','K3',8),('nemo3-ultra','N3U',8)]
MODES=['CuteDSL W4A4','CuteDSL PER-TOKEN','CuteDSL W4A16','CuteDSL MXFP4x8','CuteDSL MXFP8']
TOKENS=[1,2,4,8,16,32,64,128,256,512,4096,8192,16384]
COLUMNS=[('trtllm_w4a4','TRTLLM W4A4',MODES[0]),('trtllm_per_token','TRTLLM PER-TOKEN',MODES[1]),('trtllm_mxfp4x8','TRTLLM MXFP4x8',MODES[3]),('trtllm_mxfp8','TRTLLM MXFP8',MODES[4]),('legacy_w4a4','Non-swap W4A4',MODES[0]),('legacy_per_token','Non-swap PER-TOKEN',MODES[1]),('legacy_mxfp4x8','Non-swap MXFP4x8†',MODES[3]),('legacy_mxfp8','Non-swap MXFP8†',MODES[4]),('w4a16','W4A16 before PR',MODES[2])]
BASELINE_FIELDS=['model','tokens','column','baseline','status','baseline_ms','reason','baseline_evidence']
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def readcsv(p):return list(csv.DictReader(Path(p).open()))
def writecsv(p,rows):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('w') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def writejson(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')
def gm(rows):return 100*(math.exp(statistics.mean(math.log1p(float(r['speedup_percent'])/100) for r in rows))-1)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--swap',type=Path,required=True);p.add_argument('--w4',type=Path,required=True);p.add_argument('--retained-head',required=True);a=p.parse_args()
 roots=[a.swap.resolve(),a.w4.resolve()];fresh={};sources={};full_sources={};clocks=[];native=[];stdout=[];all_files={};stats=[]
 for data in roots:
  report=data.parent/'report';summary=json.loads((report/'summary.json').read_text());assert summary['passed'] and summary['complete_campaign']
  config=json.loads((data/'perf-config.json').read_text());assert config['phases']==['candidate','candidate']
  source=config['sources']['candidate'];scope='w4a16' if all(j.get('w4a16_only') for j in config['jobs'].values()) else 'swap_ab';sources[scope]=source
  tracked=data/Path(source['tracked_manifest']).name;assert sha(tracked)==source['tracked_manifest_sha256'];full_sources[scope]=json.loads(tracked.read_text())
  stats.append(summary)
  rows=readcsv(report/'cells.csv');assert len(rows)==summary['cells']
  for r in rows:
   key=(r['model'],r['topology'],r['backend'],int(r['tokens']));assert key not in fresh
   r={**r,'tokens':int(r['tokens']),'a1_us':float(r['a1_us']),'a2_us':float(r['a2_us']),'candidate_us':float(r['candidate_us']),'candidate_spread_percent':float(r['candidate_spread_percent'])}
   assert math.isclose(r['candidate_us'],math.sqrt(r['a1_us']*r['a2_us']),abs_tol=1e-9)
   r['candidate_evidence']=[str((data/'results'/r['job']/label/'results.json').relative_to(ROOT)) for label in ('0-candidate','1-candidate')]
   fresh[key]=r
  clocks+=json.loads((report/'clock-quartiles.json').read_text());native+=json.loads((report/'runtime-resources.json').read_text())
  for job in config['jobs']:
   folder=data/'results'/job
   for phase in ('0-candidate','1-candidate'):
    original=folder/(phase+'.log');dest=HERE/'stdout'/(job+'-'+phase+'.log');dest.parent.mkdir(exist_ok=True)
    shutil.copyfile(original,dest);assert sha(dest)==sha(original)
    stdout.append(dict(job=job,phase=phase,source=str(original.relative_to(ROOT)),path=str(dest.relative_to(HERE)),sha256=sha(dest),boundary='Original native stdout, including original CSV and table columns/N/A. No parsing, row merging or reconstruction.'))
  for file in (data/'perf-config.json',data.parent/'fetch-receipt.json',report/'summary.json',report/'cells.csv'):all_files[str(file.relative_to(ROOT))]=sha(file)
 assert len(fresh)==468 and len(stdout)==62 and len(clocks)==3744
 assert sum(x['samples'] for x in stats)==93600
 assert set(full_sources['w4a16'])==set(full_sources['swap_ab']) and len(full_sources['swap_ab'])==13245
 source_diff={k:[full_sources['w4a16'][k],v] for k,v in full_sources['swap_ab'].items() if full_sources['w4a16'][k]!=v}
 assert set(source_diff)=={'flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py'}
 repo=ROOT/'flashinfer'
 retained_changed=subprocess.check_output(['git','-C',str(repo),'diff','--name-only',BASE,a.retained_head],text=True).splitlines()
 assert set(retained_changed)=={'flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py','flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_utils.py'}
 retained_hashes={name:hashlib.sha256(subprocess.check_output(['git','-C',str(repo),'show',a.retained_head+':'+name])).hexdigest() for name in retained_changed}
 assert all(full_sources['swap_ab'][name]==digest for name,digest in retained_hashes.items())
 writejson(HERE/'retained-source-equivalence.json',dict(passed=True,retained_head=a.retained_head,actual_measurement_base=BASE,changed_from_base=retained_hashes,full_manifest_sha256=sources['swap_ab']['tracked_manifest_sha256'],w4_only_difference=source_diff,boundary='Immutable measurements retain their actual base822 and experiment labels. The retained commit has exactly the two qualified changed files, whose bytes match the frozen composed snapshot; all other tracked bytes were verified against822 before and after timing. W4R2 differs only in unused swap source.'))
 historical_path=ROOT/'harness/historical/report/cells.csv';historical=readcsv(historical_path)
 old={(r['model'],r['topology'],r['backend'],int(r['tokens'])):r for r in historical};assert set(old)==set(fresh)
 changes=subprocess.check_output(['git','-C',str(ROOT/'flashinfer'),'diff','--name-only',MEASURED_OLD,BASE],text=True).splitlines()
 assert set(changes)=={'benchmarks/bench_cute_dsl_moe_distributed.py','benchmarks/bench_moe_deepseek.py','scripts/sanitize_cute_dsl_moe_swap_ab.py'}
 report_rows=[]
 for key,r in fresh.items():
  before=old[key];assert before['candidate_measurement_head']==MEASURED_OLD
  b1,b2=float(before['a1_us']),float(before['a2_us']);baseline=math.sqrt(b1*b2);speed=100*(baseline/r['candidate_us']-1)
  report_rows.append(dict(model=r['model'],topology=r['topology'],backend=r['backend'],tokens=r['tokens'],before1_us=b1,before2_us=b2,a1_us=r['a1_us'],a2_us=r['a2_us'],baseline_us=baseline,candidate_us=r['candidate_us'],speedup_percent=speed,control_spread_percent=float(before['candidate_spread_percent']),candidate_spread_percent=r['candidate_spread_percent'],variance_flag=max(float(before['candidate_spread_percent']),r['candidate_spread_percent'])>1,baseline_measured_head=MEASURED_OLD,baseline_production_equivalent_head=BASE,baseline_evidence=before['candidate_evidence'],candidate_evidence=json.dumps(r['candidate_evidence']),source_label=r['source_label']))
 report_rows.sort(key=lambda r:(next(i for i,x in enumerate(MODELS) if x[0]==r['model']),r['topology'],MODES.index(r['backend']),r['tokens']))
 writecsv(HERE/'report/cells.csv',report_rows)
 displayed=[r for r in report_rows if r['tokens']>=4];assert len(displayed)==396
 groups={}
 for name,predicate in [('all',lambda r:True),('decode',lambda r:r['tokens']<=64),('middle',lambda r:128<=r['tokens']<=512),('prefill',lambda r:r['tokens']>=4096),('swap_ab',lambda r:r['backend']!='CuteDSL W4A16'),('w4a16',lambda r:r['backend']=='CuteDSL W4A16')]:
  rr=[r for r in displayed if predicate(r)];groups[name]=dict(cells=len(rr),speedup_percent=gm(rr),negative=sum(r['speedup_percent']<0 for r in rr))
 for mode in MODES:
  rr=[r for r in displayed if r['backend']==mode];groups[mode]=dict(cells=len(rr),speedup_percent=gm(rr),negative=sum(r['speedup_percent']<0 for r in rr))
 for topology in ('ep','tp'):
  selected={(r['model'],r['tokens'],r['backend']):r for r in report_rows if r['topology']==topology}
  lines=['| Model | Tokens | '+' | '.join(x.removeprefix('CuteDSL ') for x in MODES)+' |','|---|---:|'+'---:|'*len(MODES)]
  for model,label,parallel in MODELS:
   for token in TOKENS[2:]:
    values=[selected.get((model,token,mode)) for mode in MODES]
    lines.append(f'| {label} {topology.upper()}{parallel} | {token} | '+' | '.join(f"{r['speedup_percent']:+.2f}%"+('*' if r['variance_flag'] else '') if r else 'N/A' for r in values)+' |')
  (HERE/'report'/f'retained-table-{topology}.md').write_text('\n'.join(lines)+'\n')
 external_files={}
 for topology in ('ep','tp'):
  oldpath=ROOT/'harness/historical/external'/topology/'summary-cells.csv';external=readcsv(oldpath);revised=[]
  for r in external:
   dtype=next(x[2] for x in COLUMNS if x[0]==r['column']);key=(r['model'],topology,dtype,int(r['tokens']));value=fresh.get(key)
   updated=dict(r);updated['candidate_spread_percent']=value['candidate_spread_percent'] if value else '';updated['current_ms']=value['candidate_us']/1000 if value else '';updated['current_evidence']=json.dumps(value['candidate_evidence']) if value else '[]'
   updated['speed_percent']=100*(float(r['baseline_ms'])/float(updated['current_ms'])-1) if r['status']=='measured' else ''
   assert all(updated[k]==r[k] for k in BASELINE_FIELDS);revised.append(updated)
  folder=HERE/'external'/topology;writecsv(folder/'summary-cells.csv',revised)
  lines=['| Model | Tokens | '+' | '.join(x[1] for x in COLUMNS)+' |','|---|---:|'+'---:|'*len(COLUMNS)]
  lookup={(r['model'],int(r['tokens']),r['column']):r for r in revised}
  for model,label,parallel in MODELS:
   for token in TOKENS[2:]:
    entries=[lookup[(model,token,c[0])] for c in COLUMNS]
    lines.append(f'| {label} {topology.upper()}{parallel} | {token} | '+' | '.join(f"{float(r['speed_percent']):+.2f}%" if r['status']=='measured' else 'N/A' for r in entries)+' |')
  (folder/'summary-table.md').write_text('\n'.join(lines)+'\n')
  external_files[topology]=dict(original_csv=str(oldpath.relative_to(ROOT)),original_sha256=sha(oldpath),new_csv_sha256=sha(folder/'summary-cells.csv'),baseline_fields_unchanged=True,rows=len(revised),displayed_negative=sum(float(r['speed_percent'])<0 for r in revised if r['status']=='measured' and int(r['tokens'])>=4),unsupported=sum(r['status']=='unsupported' for r in revised))
 writejson(HERE/'report/clock-quartiles.json',clocks);writejson(HERE/'report/runtime-resources.json',native);writejson(HERE/'stdout/manifest.json',stdout)
 available=[q for q in clocks if q['clock']['available']]
 summary=dict(passed=True,retained_head=a.retained_head,actual_measurement_base=BASE,cells=468,displayed=396,samples=93600,loaded_kernels=len(native),recorded_default_joins=sum(x['default_stage_resource_joins'] for x in stats),clock_quartiles=3744,missing_clock_quartiles=3744-len(available),clock_exception_quartiles=sum(q['clock']['sm_mhz']['median']!=2032 or set(q['clock']['reasons'])!={'0'} for q in available),max_candidate_spread_percent=max(r['candidate_spread_percent'] for r in report_rows),displayed_variance_flags=sum(r['variance_flag'] for r in displayed),groups=groups,all_negative_rows_retained=True,historical_baseline=dict(measured_head=MEASURED_OLD,production_equivalent_head=BASE,changed_files=changes,fields_used='Previous a1/a2 and candidate_evidence, not the older d35 c1/c2 columns.',csv_sha256=sha(historical_path)),sources=sources,w4_source_reuse=dict(differences=source_diff,boundary='All W4 production dependencies unchanged between measured R2 and measured composed snapshots; only swap kernel differs.'),external=external_files,inputs=all_files,boundary='Full heatmaps reuse historical baselines; they are not fresh same-GPU causal comparisons. Fresh compact822 CAAC evidence remains separate. Tokens1/2 preserved in rawdata but omitted from plots; all original stdout retained verbatim.')
 writejson(HERE/'report/summary.json',summary)
 writejson(HERE/'manifest.json',dict(passed=True,assemble_sha256=sha(__file__),report_sha256=sha(HERE/'report/cells.csv'),summary_sha256=sha(HERE/'report/summary.json'),stdout_manifest_sha256=sha(HERE/'stdout/manifest.json'),inputs=all_files))
 print(json.dumps({k:summary[k] for k in ('cells','samples','displayed','loaded_kernels','recorded_default_joins','missing_clock_quartiles','clock_exception_quartiles','max_candidate_spread_percent','groups')}))
if __name__=='__main__':main()
