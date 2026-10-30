"""Read-only independent source-specialization and exact existing-row reuse check."""
from pathlib import Path
import ast,csv,hashlib,json,subprocess
R=Path(__file__).resolve().parents[1];O=R/'experiments/w4-paired-situ';repo=R/'flashinfer'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
p=read(O/'source-reuse-proof.json');old=R/'publication-integer-store/report/cells.csv';fresh=R/'evidence/w4-paired-situ-screen/1793379864881706000/report/cells.csv'
assert p['passed'] and p['previous_report_sha256']==sha(old) and p['fresh_report_sha256']==sha(fresh)
rows=list(csv.DictReader(old.open()));new=list(csv.DictReader(fresh.open()));key=lambda x:(x['model'],x['topology'],x['backend'],int(x['tokens']))
assert len(rows)==len({key(x)for x in rows})==468 and len(new)==len({key(x)for x in new})==26
want={('kimi-k3',top,'CuteDSL W4A16',t)for top in ['ep','tp']for t in [1,2,4,8,16,32,64,128,256,512,4096,8192,16384]}
assert set(map(tuple,p['affected_cells']))=={key(x)for x in new}==want
reuse={key(x):x for x in rows if key(x)not in want};assert len(reuse)==442
assert sum(x[2]!='CuteDSL W4A16'for x in reuse)==364
assert sum(x[2]=='CuteDSL W4A16'for x in reuse)==78
actual={tuple(x['identity']):x['full_existing_row_sha256']for x in p['reusable_rows']};assert len(actual)==442 and actual.keys()==reuse.keys()
for k,x in reuse.items():assert actual[k]==hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
base='49c91adf47d30fc2049c76cbaf34d0ccf3291434';head='2b8eb9d8f72ceda3952fbb05054fee97173fc9c7';rel='flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py'
git=lambda *x:subprocess.check_output(['git',*x],cwd=repo)
assert git('diff','--name-only',base,head).decode().splitlines()==[rel]
assert hashlib.sha256(git('show',head+':'+rel)).hexdigest()==p['candidate_kernel_sha256']=='5e61d04544524410b273b8e49ee2b8f6d9e20266c22346aba06ab3743c2c4e1d'
source=read(O/'source-audit.json');assert source['passed'] and source['outside_helper_and_paired_call_rewrite_ast_identical'] and sha(O/'source-audit.json')==p['source_audit_sha256']
tree=ast.parse(git('show',head+':'+rel));parent={c:n for n in ast.walk(tree)for c in ast.iter_child_nodes(n)};calls=[]
for n in ast.walk(tree):
 if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='_w4a16_scaled_tanh_pair':
  tests=[];c=n
  while c in parent:
   c=parent[c]
   if isinstance(c,ast.If):tests.append(ast.unparse(c.test))
  assert 'cutlass.const_expr(self.activation_type == ActivationType.Swiglu.value and self.situ_beta is not None)'in tests
  calls.append(n.lineno)
assert len(calls)==2
bench=ast.parse(git('show',head+':benchmarks/bench_moe_deepseek.py'));defaults={};models={}
for n in bench.body:
 if isinstance(n,ast.ClassDef)and n.name=='DeepSeekConfig':
  for x in n.body:
   if isinstance(x,ast.AnnAssign)and x.value is not None and x.target.id in ['activation','situ_beta','situ_linear_beta']:defaults[x.target.id]=ast.literal_eval(x.value)
 for target in getattr(n,'targets',[]):
  if isinstance(target,ast.Name)and target.id=='MODEL_CONFIGS':
   for k,v in zip(n.value.keys,n.value.values):models[ast.literal_eval(k)]={**defaults,**{a.arg:ast.literal_eval(a.value)for a in v.keywords}}
assert {m:{k:v[k]for k in defaults}for m,v in models.items()}==p['model_activation_configs']
assert sha(O/'qualification-summary.json')==p['qualified_unaffected_native_images']['qualification_summary_sha256']
assert sha(O/'negative-native-r2/native-summary.json')==p['qualified_unaffected_native_images']['negative_native_summary_sha256']
for f in ['w4-paired-situ-data-root.json','w4-paired-situ-acca-data-root.json']:assert read(R/'audits'/f)['passed']
receipt={'passed':True,'reuse_proof_sha256':sha(O/'source-reuse-proof.json'),'retained_head':head,'measured_base':base,'candidate_kernel_sha256':p['candidate_kernel_sha256'],'fresh_original_caac_cells':26,'reuse_exact_full_row_hashes':442,'reuse_swap_source_identical':364,'reuse_non_situ_w4_constexpr_graphs':78,'existing_situ_callsite_count':len(calls),'old_report_sha256':sha(old),'fresh_report_sha256':sha(fresh),'boundary':'Independent scope and row-hash audit. ACCA remains a separate diagnostic and does not replace primary CAAC values. Native identities are representative; not all442 cases recompiled. Raw replay was independently completed by root and remains separately bound.'}
(R/'audits/w4-paired-situ-reuse-peer.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
