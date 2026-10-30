"""Independently audit the26/442 publication overlay without writing inputs."""
from pathlib import Path
from functools import lru_cache
import csv,hashlib,json,math,statistics,subprocess
R=Path(__file__).resolve().parents[1];P=R/'publication-w4-paired-situ';O=R/'publication-integer-store';F=R/'evidence/w4-paired-situ-screen/1793379864881706000';HEAD='2b8eb9d8f72ceda3952fbb05054fee97173fc9c7'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
@lru_cache(None)
def read(p):return json.loads(Path(p).read_text())
def rows(p):return list(csv.DictReader(Path(p).open()))
def key(r):return(r['model'],r['topology'],r['backend'],int(r['tokens']))
def close(a,b):assert math.isclose(float(a),float(b),rel_tol=0,abs_tol=1e-9),(a,b)
old={key(r):r for r in rows(O/'report/cells.csv')};new={key(r):r for r in rows(P/'report/cells.csv')};fresh={key(r):r for r in rows(F/'report/cells.csv')};expected={('kimi-k3',topo,'CuteDSL W4A16',t)for topo in('ep','tp')for t in(1,2,4,8,16,32,64,128,256,512,4096,8192,16384)}
assert len(new)==468 and new.keys()==old.keys() and set(fresh)==expected
provenance={key(x):x for x in read(P/'report/row-provenance.json')};assert provenance.keys()==new.keys()
reused=0
for k,r in new.items():
 if k not in fresh:assert r==old[k];reused+=1
 else:
  f=fresh[k]
  for field in('a1_us','a2_us','candidate_us','candidate_spread_percent'):close(r[field],f[field])
  for field in('before1_us','before2_us','baseline_us','baseline_measured_head','baseline_production_equivalent_head','baseline_evidence','control_spread_percent'):assert r[field]==old[k][field]
  close(r['candidate_us'],math.sqrt(float(f['a1_us'])*float(f['a2_us'])))
  close(r['speedup_percent'],100*(float(old[k]['baseline_us'])/float(r['candidate_us'])-1))
  assert(r['variance_flag']=='True')==(max(float(old[k]['control_spread_percent']),float(f['candidate_spread_percent']))>1)
  assert r['source_label']==f['source_label']
  assert all('w4-paired-situ-screen' in p and 'acca' not in p for p in json.loads(r['candidate_evidence']))
 pr=provenance[k];assert pr['phase_paths']==json.loads(r['candidate_evidence'])
 for phase,field,digest in zip(pr['phase_paths'],('a1_us','a2_us'),pr['phase_sha256'],strict=True):
  assert sha(R/phase)==digest;raw=read(R/phase);row=next(x for x in raw['rows']if x['tokens']==k[3]);result=next(x for x in row['results']if x['backend']==k[2]);close(result['latency_ms']*1000,r[field])
assert reused==442
summary=read(P/'report/summary.json');assert summary['fresh_cells']==26 and summary['reused_cells']==442 and summary['retained_head']==HEAD
shown=[r for r in new.values()if int(r['tokens'])>=4];assert len(shown)==summary['displayed_cells']==396
neg=sum(float(r['speedup_percent'])<0 for r in shown);assert neg==summary['groups']['all']['negative']
close(summary['groups']['all']['speedup_percent'],100*math.expm1(statistics.mean(math.log1p(float(r['speedup_percent'])/100)for r in shown)))
external_changed={}
for topo in('ep','tp'):
 a,b=rows(O/f'external/{topo}/summary-cells.csv'),rows(P/f'external/{topo}/summary-cells.csv');assert len(a)==len(b)==468;changed=0
 for x,y in zip(a,b,strict=True):
  if y['model']=='kimi-k3' and y['column']=='w4a16':
   changed+=1;k=('kimi-k3',topo,'CuteDSL W4A16',int(y['tokens']));close(y['current_ms'],float(new[k]['candidate_us'])/1000)
   for field in('model','tokens','column','baseline','status','baseline_ms','reason','baseline_evidence'):assert x[field]==y[field]
   if y['status']=='measured':close(y['speed_percent'],100*(float(y['baseline_ms'])/float(y['current_ms'])-1))
  else:assert x==y
 assert changed==13;external_changed[topo]=changed
jobs={r['job']for r in fresh.values()}
for name in('clock-quartiles.json','runtime-resources.json'):
 expected_rows=[r for r in read(O/'report'/name)if r['job']not in jobs]+[dict(r,measurement_campaign='w4-paired-situ-screen')for r in read(F/'report'/name)if r['phase']in('1-candidate','2-candidate')]
 assert read(P/'report'/name)==expected_rows
clocks=read(P/'report/clock-quartiles.json');assert len(clocks)==3744
available=[r for r in clocks if r['clock']['available']];assert summary['missing_clock_quartiles']==3744-len(available)==1
exceptions=sum(q['clock']['sm_mhz']['median']!=2032 or set(q['clock']['reasons'])!={'0'}for q in available);assert exceptions==summary['clock_exception_quartiles']==89
assert summary['causal_26']==read(R/'audits/w4-paired-situ-data-root.json') and summary['separate_acca_diagnostic']==read(R/'audits/w4-paired-situ-acca-data-root.json')
stdout=read(P/'stdout/manifest.json');assert len(stdout)==142
for entry in stdout:assert sha(P/entry['path'])==sha(R/entry['source'])==entry['sha256']
assert stdout[:134]==read(O/'stdout/manifest.json')
source=read(P/'source-reuse-proof.json');assert source['retained_head']==HEAD and source['fresh']==26 and source['reused']==442
assert read(R/'audits/w4-paired-situ-retained-source-peer.json')['passed']
for name,digest in source['source_hashes'].items():assert hashlib.sha256(subprocess.check_output(['git','-C',str(R/'flashinfer'),'show',HEAD+':'+name])).hexdigest()==digest
manifest=read(P/'manifest.json');assert manifest['report_sha256']==sha(P/'report/cells.csv') and manifest['summary_sha256']==sha(P/'report/summary.json')
for name,digest in manifest['published_tree_hashes'].items():assert sha(O/name)==digest
out={'passed':True,'retained_head':HEAD,'fresh_cells':26,'reused_full_dictionaries':442,'shown_cells':396,'all_negative_displayed_cells_preserved':neg,'external_changed':external_changed,'historical_baseline_fields_unchanged':True,'both_candidate_phase_raw_values_verified_for_all468':True,'primary_only_no_acca_substitution':True,'stdout_files_preserved':142,'clock_quartiles':3744,'missing_clock_quartiles':1,'clock_exception_quartiles':89,'previous_publication_unchanged':True,'manifest_sha256':sha(P/'manifest.json'),'report_sha256':sha(P/'report/cells.csv'),'summary_sha256':sha(P/'report/summary.json'),'row_provenance_sha256':sha(P/'report/row-provenance.json'),'source_reuse_sha256':sha(P/'source-reuse-proof.json'),'retained_source_peer_sha256':sha(R/'audits/w4-paired-situ-retained-source-peer.json'),'boundary':'Independent structured overlay/raw median/provenance/source/resource-clock selection audit. Root full26 and separateACCA raw audits are reused, not replaced. Native printed tables, plot appearance and archive membership have separate forthcoming gates. No new GPU execution or claim of fresh paired468 evidence.'}
(R/'audits/w4-paired-situ-publication-overlay-peer.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
