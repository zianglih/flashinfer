"""Explicit allowlist: prior sealed members, fresh receipts, named outputs; no discovery recursion."""
import hashlib
import json
import tarfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
OLD=ROOT/'publication-w4-paired-situ'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
write=lambda p,x:Path(p).write_text(json.dumps(x,indent=2)+'\n')

def main():
    members={}
    def add(name,path):
        path=Path(path)
        assert path.is_file() and path.resolve().is_relative_to(ROOT),path
        relative=str(path.relative_to(ROOT))
        assert name not in members or members[name]==relative,name
        members[name]=relative
    oldallow=read(OLD/'bundle-allowlist.json');oldmanifest=read(OLD/'bundle-manifest.json');oldverify=read(OLD/'bundle-verification.json')
    assert oldverify['passed'] and oldverify['archive_format']=='tar.xz'
    assert sha(OLD/'bundle-manifest.json')==oldverify['bundle_manifest_sha256']
    assert sha(OLD/'moe-gather-pipeline-results.tar.xz')==oldverify['archive_sha256']
    assert set(oldmanifest['files'])==set(oldallow['members'])
    for name,relative in oldallow['members'].items():
        assert sha(ROOT/relative)==oldmanifest['files'][name],name
        add('previous-paired-situ-publication/'+name,ROOT/relative)
    for name in ['bundle-manifest.json','bundle-verification.json']:
        add('previous-paired-situ-publication/'+name,OLD/name)
    inherited=dict(passed=True,prior_retained_head=oldmanifest['retained_head'],prior_xz_sha256=oldverify['archive_sha256'],prior_manifest_sha256=sha(OLD/'bundle-manifest.json'),inherited_original_members=len(oldmanifest['files']),all_members_byte_identical=True,prefix='previous-paired-situ-publication/',boundary='Prior XZ members preserved verbatim; no nested archive.')
    write(HERE/'inherited-evidence-proof.json',inherited)
    for name in ['README.md','assemble.py','plot_retained.py','plot_external.py','plot_causal.py','prepare_bundle.py','build_bundle.py','manifest.json','source-reuse-proof.json','revision.json','plot-environment.json','glm5-comparison.md','inherited-evidence-proof.json','visual-review.json','verify_visual_numeric.py']:
        add(name,HERE/name)
    for folder in ['report','source','tail-cutoff-causal','tail-cutoff-acca','paired-situ-causal','paired-situ-acca','integer-store-causal','w4-tail-causal','plots','completed-tables']:
        for path in sorted((HERE/folder).iterdir()):
            if path.is_file() and path.suffix in {'.json','.csv','.md','.py','.patch','.txt','.png','.svg'}:add(str(path.relative_to(HERE)),path)
    for topology in ['ep','tp']:add(f'external/{topology}/summary-cells.csv',HERE/f'external/{topology}/summary-cells.csv')
    stdout=read(HERE/'stdout/manifest.json');assert len(stdout)==154
    add('stdout/manifest.json',HERE/'stdout/manifest.json')
    for record in stdout:
        path=HERE/record['path'];assert sha(path)==record['sha256'];add(record['path'],path)
    fresh_files=0
    for base in [ROOT/'evidence/w4-tail-cutoff-screen/1793393742504067000',ROOT/'evidence/w4-tail-cutoff-acca/1793394140932104000']:
        receipt=read(base/'fetch-receipt.json');assert receipt['passed']
        for relative,digest in receipt['files'].items():
            path=base/'data'/relative;assert sha(path)==digest;add(str(path.relative_to(ROOT)),path);fresh_files+=1
        for name in ['fetch-receipt.json','remote-fetch-record.json']:add(str((base/name).relative_to(ROOT)),base/name)
        for path in sorted((base/'report').iterdir()):
            if path.is_file() and path.suffix in {'.json','.csv','.md'}:add(str(path.relative_to(ROOT)),path)
    assert fresh_files==338
    # Complete frozen native inventories include the matched reused2b8 controls.
    for relative in ['experiments/w4-tail-cutoff/qualification/evidence/1793392766283766000','experiments/w4-tail-cutoff/qualification-extra/evidence/1793393145401734000','experiments/w4-raw-peek/qualification/evidence/1793386426136276000']:
        base=ROOT/relative;receipt=read(base/'fetch.json');assert receipt['fetch_passed']
        for name,digest in receipt['files'].items():
            path=base/'data'/name;assert sha(path)==digest;add(str(path.relative_to(ROOT)),path)
        for name in ['fetch.json','remote.json']:add(str((base/name).relative_to(ROOT)),base/name)
    base=ROOT/'experiments/w4-tail-cutoff/mega-qualification';receipt=read(base/'fetch.json')
    assert sha(base/'evidence.tar.gz')==receipt['sha256']
    native_inventory={}
    with tarfile.open(base/'evidence.tar.gz','r:gz') as tar:
        for member in tar.getmembers():
            if not member.isfile():continue
            name=member.name;assert not Path(name).is_absolute() and '..' not in Path(name).parts
            path=base/'evidence'/name;digest=hashlib.sha256(tar.extractfile(member).read()).hexdigest()
            assert sha(path)==digest;add(str(path.relative_to(ROOT)),path);native_inventory[name]=digest
    write(HERE/'source/mega-native-inventory.json',dict(passed=True,archive_sha256=receipt['sha256'],files=native_inventory))
    add('source/mega-native-inventory.json',HERE/'source/mega-native-inventory.json')
    for name in ['fetch.json','qualification-summary.json','native-summary.json','RESULTS.md','analyze.py','capture_exact.py','run.py','helper-adaptation.json']:add(str((base/name).relative_to(ROOT)),base/name)
    for name in ['w4-tail-cutoff-data-peer.json','w4-tail-cutoff-data-peer.md','w4-tail-cutoff-acca-peer.json','audit_w4_tail_cutoff_data.py','audit_w4_tail_cutoff_acca.py','w4-tail-cutoff-publication-peer.json','w4-tail-cutoff-publication-presentation-peer.json']:
        add('audits/'+name,ROOT/'audits'/name)
    for name in ['readiness.json','cache-ready.json','runtime.json','persistence.json']:
        add('runtime/recovery-1030/'+name,ROOT/'runtime/recovery-1030'/name)
    base=ROOT/'experiments/w4-tail-cutoff'
    explicit=['README.md','README.cpu-ready.md','RESULTS.md','RESULTS.primary.md','QUALIFICATION.md','candidate.patch','candidate-kernel.py.txt','source-proof.json','source_proof.py','cpu-ready.json','precommit.log','qualification-summary.json','pilot-summary.json','extra-summary.json','analyze_qualification.py','seal_qualification.py','analyze_resources.py','selected-winners.json','performance-harness-proof.json','integration-receipt.json','publication-reuse-proof.json','publication-reuse-proof.md','publication_reuse_proof.py','primary-result-receipt.json','final-result-receipt.json','write_results.py','analyze_acca.py','prepare_screen.py','prepare_acca.py','launch_acca.py','postflight.py','postflight_acca.py','fetch_screen.py','retirement/receipt.json','retirement/candidate.patch','retirement/candidate-kernel.py.txt','retirement/status.txt','retirement/worktrees-before.txt','reverse-prefill/RESULTS.md','reverse-prefill/result-receipt.json','reverse-prefill/preparation.json','reverse-prefill/perf-config.json','reverse-prefill/launch.json','reverse-prefill/launch-preflight.json','reverse-prefill/gpu-release.json','reverse-prefill/preflight-format-failure/failure.json','reverse-prefill/preflight-format-failure/launch.stderr','reverse-prefill/preflight-format-failure/preparation.json','performance-screen/preparation.json','performance-screen/launch.json','performance-screen/gpu-release.json','performance-screen/transport-r1.json','performance-screen/launch.stderr.argv-failure']
    for name in explicit:add(str((base/name).relative_to(ROOT)),base/name)
    helpers=read(base/'performance-harness-proof.json')['helpers']
    for name,digest in helpers.items():
        path=base/'performance-harness'/name;assert sha(path)==digest;add(str(path.relative_to(ROOT)),path)
    members['bundle-allowlist.json']=str((HERE/'bundle-allowlist.json').relative_to(ROOT))
    manifest=dict(passed=True,retained_head=read(HERE/'revision.json')['retained_head'],inherited_manifest='publication-w4-paired-situ/bundle-manifest.json',inherited_manifest_sha256=sha(OLD/'bundle-manifest.json'),inherited_xz_sha256=oldverify['archive_sha256'],inherited_original_members=len(oldmanifest['files']),fresh_manifest_files=fresh_files,members=dict(sorted(members.items())),boundary='Explicit sealed/fetch manifests and bounded named outputs only. Body drafts, caches, archives, publisher logs and transport previews excluded.')
    write(HERE/'bundle-allowlist.json',manifest)
    print(json.dumps(dict(members=len(members),fresh_manifest_files=fresh_files,total_input_bytes=sum((ROOT/p).stat().st_size for p in members.values()))))

if __name__=='__main__':main()
