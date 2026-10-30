"""Replay all original table suffixes and check new native tables/plot bindings."""
import ast,contextlib,csv,hashlib,io,json,math,struct,subprocess
from dataclasses import dataclass,replace
from functools import lru_cache
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R/'publication-w4-paired-situ';O=R/'publication-integer-store';T=P/'completed-tables';OLD=Path('/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n');HEAD='2b8eb9d8f72ceda3952fbb05054fee97173fc9c7'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
@lru_cache(None)
def read(p):return json.loads(Path(p).read_text())
def rows(p):return list(csv.DictReader(Path(p).open()))
def key(r):return(r['model'],r['topology'],r['backend'],int(r['tokens']))
def close(a,b):assert math.isclose(float(a),float(b),rel_tol=0,abs_tol=1e-9),(a,b)
causal={key(r):r for r in rows(R/'evidence/w4-paired-situ-screen/1793379864881706000/report/cells.csv')}
m=read(T/'manifest.json');assert m['retained_head']==HEAD
names={'DeepSeekConfig','BenchResult','MODEL_CONFIGS','_backend_skip_reason','_table_layout','_print_header','_print_row','_print_footer'}
def nodes(source):return[x for x in ast.parse(source).body if (isinstance(x,(ast.ClassDef,ast.FunctionDef))and x.name in names)or(isinstance(x,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='MODEL_CONFIGS'for t in x.targets))]
source=subprocess.check_output(['git','-C',str(R/'flashinfer'),'show',HEAD+':benchmarks/bench_moe_deepseek.py']);assert hashlib.sha256(source).hexdigest()==m['formatter_source_sha256'];ns={'dataclass':dataclass,'DEFAULT_SWIGLU_LIMIT':struct.unpack('>f',bytes.fromhex('7f7fffff'))[0]};exec(compile(ast.Module(body=nodes(source),type_ignores=[]),'native-benchmark','exec'),ns)
def render(model,ep,tp,family,records):
 ns['CFG']=replace(ns['MODEL_CONFIGS'][model]);ns['CFG'].intermediate_size//=tp;s=io.StringIO()
 with contextlib.redirect_stdout(s):
  ns['_print_header'](ep,tp,ns['CFG'].num_experts//ep,True,True,0.01,include_activation_quant=family=='nvfp4',use_fused_finalize=False,quant_family=family,swap_ab=True)
  for r in records:ns['_print_row']([ns['BenchResult'](**x)for x in r['results']],r['histogram'],r['tokens'],quant_family=family)
  ns['_print_footer'](family)
 return s.getvalue()
cache={}
for rel,h in m['sources'].items():
 path=OLD/rel.removeprefix('historical:')if rel.startswith('historical:')else R/rel;assert sha(path)==h;cache[rel]=read(path)
stdout=read(P/'stdout/manifest.json');assert len(stdout)==142
for r in stdout:assert sha(P/r['path'])==sha(R/r['source'])==r['sha256']
assert len(m['original_outputs_reproduced'])==51
for entry in m['original_outputs_reproduced']:
 raw=cache[entry['source']];argv=raw['benchmark_argv'];opt=lambda f,d:argv[argv.index(f)+1]if f in argv else d
 text=render(opt('--model','v3'),int(opt('--ep',8)),int(opt('--tp',1)),opt('--quant-family','nvfp4'),raw['rows']);assert hashlib.sha256(text.encode()).hexdigest()==entry['table_sha256']
 logfile=str(Path(entry['source']).parent)+'.log';matches=[r for r in stdout if r['source']==logfile];assert len(matches)==1;assert(P/matches[0]['path']).read_text().endswith(text[1:])
counts=dict(fresh=0,reused_cute=0,reused_trt=0,bf16=0);table_count=0
for group in m['groups']:
 if group.get('skipped'):continue
 table_count+=1;parallel=ns['MODEL_CONFIGS'][group['model']].default_ep;ep,tp=(parallel,1)if group['topology']=='ep'else(1,parallel)
 assert len(group['rows'])==13
 for row in group['rows']:
  assert len(row['results'])==len(row['origins'])
  for value,origin in zip(row['results'],row['origins'],strict=True):
   raw=cache[origin['source']];r=next(x for x in raw['rows']if x['tokens']==row['tokens']);assert[value]==[x for x in r['results']if x['backend']==value['backend']];assert r['histogram']==row['histogram'] and r['routing_identity']==row['routing_identity']
   argv=raw['benchmark_argv'];opt=lambda f,d:argv[argv.index(f)+1]if f in argv else d
   assert opt('--model','v3')==group['model'] and int(opt('--ep',parallel))==ep and int(opt('--tp',1))==tp and '--num-experts'not in argv
   if origin['source'].startswith('historical:'):counts['reused_trt']+=1;counts['bf16']+=value['backend']=='TRTLLM BF16'
   elif origin['fresh']:counts['fresh']+=1;assert (group['model'],group['topology'],value['backend'],row['tokens'])in causal
   else:counts['reused_cute']+=1
 text=render(group['model'],ep,tp,group['family'],group['rows']);assert text==(T/group['table']).read_text();assert hashlib.sha256(text.encode()).hexdigest()==group['table_sha256']
assert table_count==15 and counts==dict(fresh=26,reused_cute=442,reused_trt=390,bf16=52)
for comment in m['comments']:assert sha(T/comment['path'])==comment['sha256']and(T/comment['path']).stat().st_size==comment['bytes']

# Plot data are checked cell-for-cell, not merely by filenames.
for topo in('ep','tp'):
 pm=read(P/f'plots/plot-manifest-{topo}.json');assert pm['source_sha256']==sha(P/f'external/{topo}/summary-cells.csv')
 assert pm['rows']==44 and pm['columns']==9 and pm['tokens']==[4,8,16,32,64,128,256,512,4096,8192,16384]
 ext={(r['model'],int(r['tokens']),r['column']):r for r in rows(P/f'external/{topo}/summary-cells.csv')if int(r['tokens'])>=4};assert len(ext)==len(pm['cells'])==396
 for c in pm['cells']:
  r=ext[c['model'],c['tokens'],c['column']];assert c['status']==r['status']
  if c['status']=='measured':close(c['percent'],r['speed_percent']);close(c['ratio'],float(r['baseline_ms'])/float(r['current_ms']))
 for name,digest in pm['outputs'].items():assert sha(P/'plots'/name)==digest
ret=read(P/'plots/retained-plot-manifest.json');full=rows(P/'report/cells.csv')
for pm in ret['plots']:
 assert pm['source_sha256']==sha(P/'report/cells.csv');rr=[r for r in full if r['topology']==pm['topology']and int(r['tokens'])>=4]
 assert pm['measured']==len(rr) and pm['negative']==sum(float(r['speedup_percent'])<0 for r in rr)
 for name,digest in pm['outputs'].items():assert sha(P/'plots'/name)==digest
causal_plot=read(P/'plots/paired-situ-causal-manifest.json');assert causal_plot['source_sha256']==sha(R/'evidence/w4-paired-situ-screen/1793379864881706000/report/cells.csv')
assert causal_plot['cells']==[r for r in causal.values()if int(r['tokens'])>=4]
assert causal_plot['raw_cells']==26 and causal_plot['displayed_cells']==22 and causal_plot['negative_cells']==9
for name,digest in causal_plot['outputs'].items():assert sha(P/'plots'/name)==digest
out={'passed':True,'retained_head':HEAD,'native_original_suffixes_reproduced':51,'native_tables':table_count,'native_groups':len(m['groups']),'records':counts,'original_stdout_files':142,'comments':4,'all_original_structured_records_preserved':True,'all_route_histogram_model_topology_joins_verified':True,'same_unchanged_native_formatter_replays_ratios_and_winners':True,'external_plotted_cells':792,'retained_plot_negative_cells':sum(p['negative']for p in ret['plots']),'causal_plot_rows':22,'causal_plot_negative_cells':9,'manifest_sha256':sha(T/'manifest.json'),'formatter_source_sha256':m['formatter_source_sha256'],'boundary':'CPU replay from original structured records, not parsing/reformatting printed cells. All51 existing stdout suffixes are byte-identical. Final table rows use final candidate pass; plots retain two-pass aggregates and separate primary causal26. Plot values/hash bindings verified; visual inspection and archive transport remain separate gates.'}
(R/'audits/w4-paired-situ-publication-presentation-peer.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
