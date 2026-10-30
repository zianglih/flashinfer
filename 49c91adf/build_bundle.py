"""Seal the explicit integer-store publication allowlist as a deterministic XZ tar."""
import fcntl
import hashlib
import io
import json
import lzma
import tarfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sha=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
read=lambda path:json.loads(Path(path).read_text())
write=lambda path,value:Path(path).write_text(json.dumps(value,indent=2)+'\n')


def main():
    allowlist=read(HERE/'bundle-allowlist.json')
    assert allowlist['passed'] and allowlist['retained_head']=='49c91adf47d30fc2049c76cbaf34d0ccf3291434'
    members={name:ROOT/path for name,path in allowlist['members'].items()}
    assert all(not Path(name).is_absolute() and '..' not in Path(name).parts for name in members)
    assert all(path.is_file() and path.resolve().is_relative_to(ROOT) for path in members.values())
    assert all(not name.endswith(('.gz','.xz','.tar','.zip')) for name in members)
    forbidden={'PR_BODY.md','write_pr_body.py','assets-receipt.json','assets-publish.log','archive-recompression.json'}
    assert all(Path(name).name not in forbidden for name in members)
    assert all(name in members for name in ['integer-store-causal/table.md','w4-tail-causal/table.md','glm5-comparison.md','visual-review.json'])
    previous=read(ROOT/allowlist['inherited_manifest'])
    assert sha(ROOT/allowlist['inherited_manifest'])==allowlist['inherited_manifest_sha256']
    for name,digest in previous['files'].items():
        assert sha(members['previous-w4-publication/'+name])==digest,name
    assert len(previous['files'])==allowlist['inherited_original_members']
    for name in ['audits/integer-store-publication-peer.json','audits/integer-store-publication-presentation-peer.json']:
        assert read(members[name])['passed']
    assert read(HERE/'visual-review.json')['passed']
    fresh=read(HERE/'integer-store-causal/summary.json')
    assert fresh['cells']==104 and fresh['raw_samples']==41600
    manifest=dict(passed=True,retained_head=allowlist['retained_head'],archive_format='tar.xz',
        files={name:sha(path) for name,path in sorted(members.items())},allowlist_sha256=sha(HERE/'bundle-allowlist.json'),
        inherited_manifest_sha256=allowlist['inherited_manifest_sha256'],inherited_xz_sha256=allowlist['inherited_xz_sha256'],
        fresh_raw_samples=41600,fresh_cells=104,reused_cells=364,original_stdout_logs=134,
        all_fresh_raw_data_included=True,body_draft_excluded=True,
        boundary='New direct XZ publication. Prior sealed W4 evidence preserved under previous-w4-publication; fresh104 CAAC and full468 derived outputs are distinct. No recursive/nested archive or publisher artifacts.')
    write(HERE/'bundle-manifest.json',manifest)
    members['bundle-manifest.json']=HERE/'bundle-manifest.json'
    archive=HERE/'moe-gather-pipeline-results.tar.xz'
    temporary=HERE/'moe-gather-pipeline-results.tar.xz.building'
    with lzma.open(temporary,'wb',format=lzma.FORMAT_XZ,check=lzma.CHECK_CRC64,preset=6) as stream,tarfile.open(fileobj=stream,mode='w|') as tar:
        for name,path in sorted(members.items()):
            raw=path.read_bytes();info=tarfile.TarInfo(name);info.size=len(raw);info.mode=0o644;info.mtime=0
            tar.addfile(info,io.BytesIO(raw))
    temporary.replace(archive)
    with tarfile.open(archive,'r:xz') as tar:
        names=tar.getnames();assert len(names)==len(set(names))==len(members) and set(names)==set(members)
        for name,path in members.items():
            assert hashlib.sha256(tar.extractfile(name).read()).hexdigest()==sha(path),name
    result=dict(passed=True,archive_format='tar.xz',archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,
        member_count=len(members),bundle_manifest_sha256=sha(HERE/'bundle-manifest.json'),
        allowlist_sha256=sha(HERE/'bundle-allowlist.json'),inherited_xz_sha256=allowlist['inherited_xz_sha256'],
        publication_peer_sha256=sha(members['audits/integer-store-publication-peer.json']),
        presentation_peer_sha256=sha(members['audits/integer-store-publication-presentation-peer.json']),
        root_visual_sha256=sha(HERE/'visual-review.json'),body_draft_excluded=True,recursive_archives_excluded=True,
        integer_store_causal_table_included=True,w4_tail_causal_table_included=True,glm5_table_included=True)
    write(HERE/'bundle-verification.json',result)
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    with (HERE/'.bundle.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        main()
