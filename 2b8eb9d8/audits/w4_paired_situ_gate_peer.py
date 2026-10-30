"""Independent read-only raw/native and RN-chain replay for paired SiTU."""
import ast
from collections import Counter
import contextlib
import hashlib
import io
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "experiments/w4-paired-situ"
E = FOLDER / "qualification/evidence/1793379350474754000/data"
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
read = lambda p: json.loads(Path(p).read_text())
fetch = read(E.parent / "fetch.json")
assert fetch['fetch_passed'] and fetch['passed'] and fetch['complete']
assert sha(E.parent/'evidence.tar.gz') == fetch['sha256']
for name,digest in fetch['files'].items():assert sha(E/name)==digest,name
receipt=read(E/'receipt.json');summary=read(FOLDER/'qualification-summary.json')
assert receipt['passed'] and receipt['complete'] and receipt['full_source_preflight'] and receipt['full_source_postflight']
assert len(receipt['runs'])==12 and summary['evidence_receipt_sha256']==sha(E/'receipt.json')
sources={r:read(E/f'source-{r}.json') for r in ('control','candidate')}
rel='flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py'
for role,s in sources.items():
    assert sha(E/f'source-{role}.json')==receipt['source_hashes'][role]
    assert len(s['source_sha256'])==13245 and sha(E/f'{role}-tracked.json')==s['tracked_manifest_sha256']
    assert read(E/f'{role}-tracked.json')==s['source_sha256']
changed=[p for p in sources['control']['source_sha256'] if sources['control']['source_sha256'][p]!=sources['candidate']['source_sha256'][p]]
assert changed==[rel]
assert sources['candidate']['source_sha256'][rel]=='5e61d04544524410b273b8e49ee2b8f6d9e20266c22346aba06ab3743c2c4e1d'
assert sha(ROOT/'flashinfer-w4-paired-situ-review'/rel)==sources['candidate']['source_sha256'][rel]
for name,digest in receipt['helpers'].items():assert sha(E/'helpers'/name)==digest
for name,digest in receipt['recovery'].items():assert sha(E/'recovery-records'/name)==digest
assert sha(E/'recovery-readiness.json')==receipt['recovery_readiness_sha256']
cases=read(E/'cases.json');rows=[];chains=0
def count(text):
    return Counter(re.findall(r'/\*[0-9a-fA-F]+\*/\s+(?:@!?P\w+\s+)?([A-Za-z][A-Za-z0-9_.]*)(?=[\s;])',text))
def rn_chains(ptx):
    constants=dict(re.findall(r'mov\.b32\s+(%r\d+),\s*0f([0-9A-Fa-f]{8});',ptx))
    packs={a:(b,c) for a,b,c in re.findall(r'mov\.b64\s+(%rd\d+),\s*\{(%r\d+),\s*(%r\d+)\};',ptx)}
    muls={a:(b,c) for a,b,c in re.findall(r'mul\.rn\.f32x2\s+(%rd\d+),\s*(%rd\d+),\s*(%rd\d+);',ptx)}
    rcp=set(re.findall(r'rcp\.approx\.ftz\.f32\s+(%r\d+),',ptx))
    pairs=re.findall(r'sub\.rn\.f32x2\s+(%rd\d+),\s*(%rd\d+),\s*(%rd\d+);',ptx)
    assert pairs
    def packed_bits(reg):return tuple(constants.get(x,'').upper() for x in packs.get(reg,()))
    for _,scaled,one in pairs:
        assert packed_bits(one)==('3F800000','3F800000')
        x,y=muls[scaled]
        if packed_bits(x)==('40000000','40000000'):x,y=y,x
        assert packed_bits(y)==('40000000','40000000')
        assert len(packs[x])==2 and all(v in rcp for v in packs[x])
    return len(pairs)
for case,spec in enumerate(cases):
    caps={}
    for role in ('control','candidate'):
        name=f'{role}-w4a16-{case}';run=next(x for x in receipt['runs'] if x['name']==name)
        assert run['returncode']==0 and sha(E/f'{name}.log')==run['stdout_sha256']
        result=read(E/name/'result.json');assert result['passed'] and result['case']==spec
        cap=read(E/name/'codegen/receipt.json');assert cap['exitstatus']==0 and not cap['compiler_options_changed'] and len(cap['kernels'])==3
        guards=list((E/name/'register-guard').glob('*/receipt.json'));assert len(guards)==1
        g=read(guards[0]);assert g['all_guarded'] and g['exitstatus']==0 and not g['compiler_options_changed']
        assert all(x['passed'] and x['analysis']['local_bytes']==0 for x in g['compilations'])
        for k in cap['kernels']:
            for ext in ('ptx','cubin','sass'):assert sha(E/name/'codegen'/(k['stem']+'.'+ext))==k[ext+'_sha256']
            assert k['native_resources']['local_bytes']==0
        caps[role]=cap['kernels']
    for stage,(control,candidate) in enumerate(zip(caps['control'],caps['candidate'],strict=True)):
        assert control['configuration']==candidate['configuration'] and control['compile_options']==candidate['compile_options'] and control['native_resources']==candidate['native_resources']
        paths={r:E/f'{r}-w4a16-{case}'/'codegen'/k['stem'] for r,k in [('control',control),('candidate',candidate)]}
        ptx={r:p.with_suffix('.ptx').read_text() for r,p in paths.items()};sass={r:p.with_suffix('.sass').read_text() for r,p in paths.items()}
        counts={r:count(x) for r,x in sass.items()};affected=stage==0 and spec['beta'] is not None
        equal=all(control[x+'_sha256']==candidate[x+'_sha256'] for x in ('ptx','cubin','sass'))
        if not affected:assert equal
        else:
            assert control['native_resources']['registers']==candidate['native_resources']['registers']==96
            assert control['compile_options']=="--ptxas-options='-maxrregcount=96'"
            assert all(counts[r]['FFMA']==counts[r]['FFMA2']==0 for r in counts)
            for op in ('MUFU.EX2','MUFU.RCP'):assert counts['control'][op]==counts['candidate'][op]
            assert Counter(re.findall(r'\b((?:ex2|rcp)\.[A-Za-z0-9_.]+)\s',ptx['control']))==Counter(re.findall(r'\b((?:ex2|rcp)\.[A-Za-z0-9_.]+)\s',ptx['candidate']))
            assert not re.search(r'\b(?:mul|add|sub)\.[^\s;]*ftz[^\s;]*\.f32x2',ptx['candidate'])
            assert not re.search(r'\bfma\.',ptx['candidate'])
            chains+=rn_chains(ptx['candidate'])
            delta={k:counts['candidate'][k]-counts['control'][k] for k in set(counts['candidate'])|set(counts['control']) if counts['candidate'][k]!=counts['control'][k]}
            assert set(delta)<= {'FADD','FADD2','FMUL','FMUL2'}
        rows.append(dict(case=case,stage=stage,affected=affected,raw_equal=equal,registers=control['native_resources']['registers'],local_bytes=0,non_nop_delta=sum(counts['candidate'].values())-counts['candidate']['NOP']-sum(counts['control'].values())+counts['control']['NOP']))
# Replay the author's actual-source symbolic graph without its two artifact writes.
path=FOLDER/'source_audit.py';tree=ast.parse(path.read_text());removed=0;body=[]
for n in tree.body:
    if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Attribute) and n.value.func.attr=='write_text':removed+=1
    else:body.append(n)
assert removed==2;tree.body=body;scope={'__file__':str(path),'__name__':'peer_readonly'}
with contextlib.redirect_stdout(io.StringIO()):exec(compile(tree,str(path),'exec'),scope)
assert scope['result']==read(FOLDER/'source-audit.json')
result=dict(passed=True,candidate_sha256=sources['candidate']['source_sha256'][rel],fetch_sha256=sha(E.parent/'fetch.json'),summary_sha256=sha(FOLDER/'qualification-summary.json'),files=len(fetch['files']),source_files_per_arm=13245,exact_calls=12,native_pairs=18,affected_fc1=4,unaffected_identical_pairs=14,all_resources_unchanged=True,all_local_zero=True,independent_native_rn_2rcp_minus1_chains=chains,symbolic_lane_graphs=scope['result']['symbolic_scalar_lane_graph_comparisons'],rows=rows,peer_script_sha256=sha(__file__),boundary='Existing finite-output exact oracle plus actual native/source rounding audit. No direct exceptional-input helper execution is present in this evidence; no NaN payload or exhaustive device-input claim. Source/codegen qualification does not establish performance.')
(ROOT/'audits/w4-paired-situ-gate-peer.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))
