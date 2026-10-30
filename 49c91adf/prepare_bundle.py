"""Build an explicit allowlist from frozen receipts and named publication outputs."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OLD = ROOT / 'publication-w4-tail'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
read = lambda p: json.loads(Path(p).read_text())
write = lambda p, x: Path(p).write_text(json.dumps(x, indent=2) + '\n')


def main():
    members = {}
    def add(name, path):
        path = Path(path)
        assert path.is_file() and path.resolve().is_relative_to(ROOT), path
        relative = str(path.relative_to(ROOT))
        assert name not in members or members[name] == relative, name
        members[name] = relative
    old_allow = read(OLD / 'bundle-allowlist.json')
    old_manifest = read(OLD / 'bundle-manifest.json')
    old_verify = read(OLD / 'bundle-verification.json')
    assert old_verify['passed'] and old_verify['archive_format'] == 'tar.xz'
    assert sha(OLD / 'bundle-manifest.json') == old_verify['bundle_manifest_sha256']
    assert sha(OLD / 'moe-gather-pipeline-results.tar.xz') == old_verify['archive_sha256']
    assert set(old_manifest['files']) == set(old_allow['members'])
    for name, relative in old_allow['members'].items():
        assert sha(ROOT / relative) == old_manifest['files'][name], name
        add('previous-w4-publication/' + name, ROOT / relative)
    for name in ['bundle-manifest.json', 'bundle-verification.json']:
        add('previous-w4-publication/' + name, OLD / name)
    inherited = dict(passed=True, prior_retained_head=old_manifest['retained_head'],
        prior_xz_sha256=old_verify['archive_sha256'], prior_manifest_sha256=sha(OLD/'bundle-manifest.json'),
        inherited_original_members=len(old_manifest['files']), all_members_byte_identical=True,
        prefix='previous-w4-publication/',
        boundary='Prior XZ members are preserved verbatim under a historical prefix; no nested archive or new gzip transport is used.')
    write(HERE/'inherited-evidence-proof.json', inherited)

    # Fixed lists and one-level output directories exclude body drafts, logs of
    # publishing, build archives and transient matplotlib caches by construction.
    for name in ['README.md','assemble.py','plot_retained.py','plot_external.py','plot_causal.py',
                 'prepare_bundle.py','build_bundle.py','manifest.json','source-reuse-proof.json',
                 'plot-environment.json','glm5-comparison.md','inherited-evidence-proof.json','visual-review.json','verify_visual_numeric.py']:
        add(name, HERE/name)
    for folder in ['report','source','integer-store-causal','w4-tail-causal','plots','completed-tables']:
        for path in sorted((HERE/folder).iterdir()):
            if path.is_file() and path.suffix in {'.json','.csv','.md','.py','.patch','.txt','.png','.svg'}:
                add(str(path.relative_to(HERE)), path)
    for topology in ['ep','tp']:
        add(f'external/{topology}/summary-cells.csv', HERE/f'external/{topology}/summary-cells.csv')
    stdout = read(HERE/'stdout/manifest.json')
    assert isinstance(stdout,list) and len(stdout)==134
    for path in sorted((HERE/'stdout').glob('*.json')):
        add(str(path.relative_to(HERE)),path)
    # Names come from the already assembled original stdout receipt, not from
    # a recursive publication scan.
    for record in stdout:
        path=HERE/record['path']
        assert sha(path)==record['sha256']
        add(record['path'],path)

    fetches = [ROOT/'evidence/fc1-integer-store-screen/1793370953565557000',
               ROOT/'evidence/fc1-integer-store-remaining/1793371744150407000']
    fresh_files = 0
    for base in fetches:
        receipt = read(base/'fetch-receipt.json')
        assert receipt['passed']
        for relative, digest in receipt['files'].items():
            path = base/'data'/relative
            assert sha(path) == digest, path
            add(str(path.relative_to(ROOT)),path)
            fresh_files += 1
        for name in ['fetch-receipt.json','remote-fetch-record.json']:
            path=base/name
            if path.exists(): add(str(path.relative_to(ROOT)),path)
        for path in sorted((base/'report').iterdir()):
            if path.is_file() and path.suffix in {'.json','.csv','.md'}:
                add(str(path.relative_to(ROOT)),path)

    for path in sorted((ROOT/'audits').glob('fc1-integer-store-*.json')):
        add(str(path.relative_to(ROOT)),path)
    for path in sorted((ROOT/'audits').glob('audit_fc1_integer_store*.py')):
        add(str(path.relative_to(ROOT)),path)
    for name in ['integer-store-publication-peer.json','integer-store-publication-presentation-peer.json']:
        add('audits/'+name,ROOT/'audits'/name)
    explicit = [
      'experiments/fc1-integer-store-performance/FULL_RESULTS.md',
      'experiments/fc1-integer-store-performance/combine.py',
      'experiments/fc1-integer-store-performance/resource_pairs.py',
      'experiments/fc1-integer-store-performance/source-final.json',
      'experiments/fc1-integer-store-performance/scope-reuse-final.json',
      'experiments/fc1-integer-store-performance/remaining/AFFECTED_SCOPE.md',
      'experiments/fc1-integer-store-performance/remaining/affected-scope.json',
      'experiments/fc1-integer-store-performance/remaining/local-receipt-path-correction.json',
      'experiments/fc1-integer-store-atomic-fix/qualification-summary.json',
      'experiments/fc1-integer-store-gated/reuse-proof.json',
      'experiments/fc1-integer-store-atomic-fix/attempt-evidence/complete-evidence/receipt.json',
      'experiments/fc1-integer-store-fused-boundary/final-evidence/complete-evidence/receipt.json',
    ]
    for name in explicit: add(name,ROOT/name)
    for leaf in ['experiments/fc1-integer-store-atomic-fix','experiments/fc1-integer-store-fused-boundary','experiments/fc1-integer-store-gated']:
        for pattern in ['*summary.json','*proof.json','source-*.json','guard-*.json','*analysis.json']:
            for path in sorted((ROOT/leaf).glob(pattern)):
                add(str(path.relative_to(ROOT)),path)
    # Every new archive input is pinned here; the packer never discovers inputs.
    members['bundle-allowlist.json']=str((HERE/'bundle-allowlist.json').relative_to(ROOT))
    manifest = dict(passed=True, retained_head='49c91adf47d30fc2049c76cbaf34d0ccf3291434',
        inherited_manifest='publication-w4-tail/bundle-manifest.json', inherited_manifest_sha256=sha(OLD/'bundle-manifest.json'),
        inherited_xz_sha256=old_verify['archive_sha256'], inherited_original_members=len(old_manifest['files']),
        fresh_manifest_files=fresh_files,
        members=dict(sorted(members.items())), boundary='Explicit original manifest, fresh fetch manifests and bounded named output collections only; body drafts, caches, archives and publisher logs excluded.')
    write(HERE/'bundle-allowlist.json',manifest)
    print(json.dumps(dict(members=len(members),fresh_manifest_files=fresh_files,total_input_bytes=sum((ROOT/p).stat().st_size for p in members.values()))))


if __name__=='__main__': main()
