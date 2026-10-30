"""Bounded source/tactic scope and exact previous-row reuse, CPU-only."""
from pathlib import Path
import ast,csv,hashlib,json,subprocess
P=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent;repo=P/'flashinfer'
base='2b8eb9d8f72ceda3952fbb05054fee97173fc9c7';head='c1ac8ce7341039db65195b99445fcdeb193cf226'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
git=lambda *args:subprocess.check_output(['git','-C',str(repo),*args],text=True)
module='flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py'
assert git('rev-parse',head+'^').strip()==base
assert git('diff','--name-only',base,head).splitlines()==[module]
assert hashlib.sha256(git('show',head+':'+module).encode()).hexdigest()=='cbef9186731e78806884f7fa2ba5aad18f5ece379664cf8d3181d5cd54548c10'
bench_rel='benchmarks/bench_moe_deepseek.py';bench=git('show',base+':'+bench_rel);assert bench==git('show',head+':'+bench_rel)
t=ast.parse(bench);cls=next(x for x in t.body if isinstance(x,ast.ClassDef)and x.name=='DeepSeekConfig')
default={x.target.id:ast.literal_eval(x.value)for x in cls.body if isinstance(x,ast.AnnAssign)and x.target.id in ('hidden_size','intermediate_size')}
configs=next(x.value for x in t.body if isinstance(x,ast.Assign)and any(isinstance(y,ast.Name)and y.id=='MODEL_CONFIGS'for y in x.targets));models={}
for name,call in zip(configs.keys,configs.values):
 models[ast.literal_eval(name)]={**default,**{x.arg:ast.literal_eval(x.value)for x in call.keywords if x.arg in default}}
launcher=git('show',base+':flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16.py')
lt=ast.parse(launcher);fallback=ast.literal_eval(next(x.value for x in lt.body if isinstance(x,ast.AnnAssign)and isinstance(x.target,ast.Name)and x.target.id=='DEFAULT_W4A16_MOE_TACTIC'))
kt=ast.parse(git('show',base+':'+module));groups=[ast.literal_eval(n.value)for n in ast.walk(kt)if isinstance(n,ast.Assign)and any(isinstance(y,ast.Attribute)and y.attr=='num_transform_warpgroups'for y in n.targets)];assert groups==[2]
G=groups[0];jobs=read(P/'harness/jobs-full.json');rows=list(csv.DictReader((P/'publication-w4-paired-situ/report/cells.csv').open()));assert len(rows)==468
idof=lambda x:(x['model'],x['topology'],x['backend'],int(x['tokens']))
byid={idof(x):x for x in rows};assert len(byid)==468
inventory=[]
for name,job in jobs.items():
 if not name.endswith('-w4a16'):continue
 ep,tp=job['ep'],job['tp'];model=job['model'];topology='tp'if tp>1 else 'ep'
 dims=models[model];ks=[dims['hidden_size'],dims['intermediate_size']//tp];assert dims['intermediate_size']%tp==0
 f=P/'harness/frozen-inputs'/name/'expected.json';v=read(f);it=iter(v['native_diagnostic']['measurements'])
 for row in v['rows']:
  for result in row['results']:
   m=next(it);assert result['backend']=='CuteDSL W4A16'
   identities={json.dumps({k:h[k]for k in ('key','runner','tactic')},sort_keys=True)for h in m['cache_hits']};assert len(identities)==1 and all(h['hit']for h in m['cache_hits'])
   identity=json.loads(next(iter(identities)));tactic=identity['tactic'];resolved=json.loads(json.dumps(fallback if tactic==-1 else tactic));stages=[]
   for role,k,tac in zip(('fc1','fc2'),ks,resolved):
    S=tac[0][2];assert S%G==0;H=S//G;tail=k%S;guard=0<tail<=S-H
    stages.append(dict(stage=role,consumed_k=k,mma_tiler=tac[0],cluster_shape=tac[1],raster_along_m=tac[2],stage_k=S,transform_groups=G,group_k=H,tail_k=tail,existing_constexpr_guard=guard))
   cell=[model,topology,result['backend'],row['tokens']];assert tuple(cell)in byid
   inventory.append(dict(identity=cell,job=name,recorded_choice=identity,resolved_choice=resolved,expected_sha256=sha(f),stages=stages,affected=any(x['existing_constexpr_guard']for x in stages)))
 assert next(it,None)is None
assert len(inventory)==104
assert all(s["stage_k"]==256 and s["group_k"]==128 for x in inventory for s in x["stages"])
assert sum(x["recorded_choice"]["tactic"]==-1 for x in inventory)==10
changed={tuple(x['identity'])for x in inventory if x['affected']};assert len(changed)==39
assert all(not x['stages'][0]['existing_constexpr_guard'] for x in inventory)
fresh=list(csv.DictReader((P/'evidence/w4-tail-cutoff-screen/1793393742504067000/report/cells.csv').open()));freshkeys={(jobs[x['job']]['model'],'tp',x['backend'],int(x['tokens']))for x in fresh};assert freshkeys==changed
reused=[]
for row in rows:
 if idof(row)in changed:continue
 reused.append(dict(identity=list(idof(row)),full_existing_row_sha256=hashlib.sha256(json.dumps(row,sort_keys=True,separators=(',',':')).encode()).hexdigest()))
assert len(reused)==429 and sum(x['identity'][2]=='CuteDSL W4A16'for x in reused)==65
q=read(O/'qualification-summary.json');assert q['passed']and q['raw_identical_split_pairs']==13 and q['raw_identical_mega_pairs']==2
v=dict(passed=True,cpu_only=True,base_head=base,retained_head=head,source_diff_only=module,candidate_kernel_sha256='cbef9186731e78806884f7fa2ba5aad18f5ece379664cf8d3181d5cd54548c10',previous_report_sha256=sha(P/'publication-w4-paired-situ/report/cells.csv'),fresh_primary_report_sha256=sha(P/'evidence/w4-tail-cutoff-screen/1793393742504067000/report/cells.csv'),qualification_summary_sha256=sha(O/'qualification-summary.json'),source_algebra_proof_sha256=sha(O/'source-proof.json'),model_dimensions=models,default_w4a16_moe_tactic=json.loads(json.dumps(fallback)),inventory=inventory,affected_count=39,reusable_count=429,reusable_w4_count=65,reusable_swap_count=364,affected_cells=sorted(map(list,changed)),reusable_rows=reused,source_qualified_native_boundary='All swap source is unchanged by the sole W4 diff. Every frozen W4 tactic is enumerated above; the existing constexpr guard is false for65 cells, so old/new active graphs are identical. Qualification contains representative aligned/all-live-tail split and padded Mega byte identities; not all429 table signatures were separately recompiled. Fresh39 uses the primaryCAAC only; separateACCA is not pooled or substituted.')
(O/'publication-reuse-proof.json').write_text(json.dumps(v,indent=2)+'\n')
(O/'publication-reuse-proof.md').write_text('''# W4 cutoff publication reuse boundary

Retainedc1ac8ce7 is a direct child of2b8eb9d8 and changes only the qualifiedcbef W4 kernel. The benchmark, W4 launcher, swap kernels and shared external interfaces are unchanged.

The104 existing W4 rows are enumerated from their recorded cache hits, including10 recorded deterministic defaults. Model dimensions come from the unchanged benchmark AST; each resolved FC1/FC2 K stage and two-transform-group geometry is inspected. All frozen stages are K256/group128. The existing constexpr tail predicate is false for65 W4 cells and true only forFC2 in the39 V41F TP4/K3 TP8/N3U TP8 cells. FC1 is unaffected for every model-table row.

Therefore publication replaces exactly39 primary rows and reuses429 prior full-row dictionaries:65 W4 plus364 unchanged swap. JSON contains the complete104-cell tactic/extent inventory and canonical sorted compact-JSON SHA256 for every reused row. Fresh keys exactly equal the source-derived affected set. Tokens1/2 remain in raw tables; retention excludes them. SeparateACCA does not replace or pool with primary timing.

The representative native qualification has13 byte-identical split pairs and2 padded-Mega pairs. The source/constexpr proof supports graph reuse for the remaining signatures; this is not a claim that all429 were separately recompiled. Historical measured revisions, external baseline fields and prior row values must remain unchanged in the new publication.
''')
print(json.dumps(dict(passed=True,affected=39,reusable=429,sha256=sha(O/'publication-reuse-proof.json'))))
