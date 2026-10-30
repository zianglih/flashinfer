"""Build an explicit allowlist from frozen receipts and named publication outputs."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OLD = ROOT / 'publication-integer-store'
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
        add('previous-integer-publication/' + name, ROOT / relative)
    for name in ['bundle-manifest.json', 'bundle-verification.json']:
        add('previous-integer-publication/' + name, OLD / name)
    inherited = dict(passed=True, prior_retained_head=old_manifest['retained_head'],
        prior_xz_sha256=old_verify['archive_sha256'], prior_manifest_sha256=sha(OLD/'bundle-manifest.json'),
        inherited_original_members=len(old_manifest['files']), all_members_byte_identical=True,
        prefix='previous-integer-publication/',
        boundary='Prior integer-store XZ members are preserved verbatim under a historical prefix; no nested archive or new gzip transport is used.')
    write(HERE/'inherited-evidence-proof.json', inherited)

    # Fixed lists and one-level output directories exclude body drafts, logs of
    # publishing, build archives and transient matplotlib caches by construction.
    for name in ['README.md','assemble.py','plot_retained.py','plot_external.py','plot_causal.py',
                 'prepare_bundle.py','build_bundle.py','manifest.json','source-reuse-proof.json',
                 'plot-environment.json','glm5-comparison.md','inherited-evidence-proof.json','visual-review.json','verify_visual_numeric.py']:
        add(name, HERE/name)
    for folder in ['report','source','paired-situ-causal','paired-situ-acca','integer-store-causal','w4-tail-causal','plots','completed-tables']:
        for path in sorted((HERE/folder).iterdir()):
            if path.is_file() and path.suffix in {'.json','.csv','.md','.py','.patch','.txt','.png','.svg'}:
                add(str(path.relative_to(HERE)), path)
    for topology in ['ep','tp']:
        add(f'external/{topology}/summary-cells.csv', HERE/f'external/{topology}/summary-cells.csv')
    stdout = read(HERE/'stdout/manifest.json')
    assert isinstance(stdout,list) and len(stdout)==142
    for path in sorted((HERE/'stdout').glob('*.json')):
        add(str(path.relative_to(HERE)),path)
    # Names come from the already assembled original stdout receipt, not from
    # a recursive publication scan.
    for record in stdout:
        path=HERE/record['path']
        assert sha(path)==record['sha256']
        add(record['path'],path)

    fetches = [ROOT/'evidence/w4-paired-situ-screen/1793379864881706000',
               ROOT/'evidence/w4-paired-situ-acca/1793380968593160000']
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
    assert fresh_files == 267
    # Both native captures have explicit frozen inventories. They remain raw
    # evidence in XZ, not additional runtime or exceptional-value test claims.
    native_base=ROOT/'experiments/w4-paired-situ/qualification/evidence/1793379350474754000'
    native_receipt=read(native_base/'fetch.json')
    assert native_receipt['passed']
    for relative,digest in native_receipt['files'].items():
        path=native_base/'data'/relative
        assert sha(path)==digest
        add(str(path.relative_to(ROOT)),path)
    for name in ['fetch.json','remote.json']:
        add(str((native_base/name).relative_to(ROOT)),native_base/name)
    native_base=ROOT/'experiments/w4-paired-situ/negative-native-r2/evidence'
    native_receipt=read(native_base/'fetch-manifest.json')
    for relative,digest in native_receipt.items():
        path=native_base/relative
        assert sha(path)==digest
        add(str(path.relative_to(ROOT)),path)
    add(str((native_base/'fetch-manifest.json').relative_to(ROOT)),native_base/'fetch-manifest.json')
    for pattern in ['w4-paired-situ-*.json','*w4_paired_situ*.py']:
        for path in sorted((ROOT/'audits').glob(pattern)):
            add(str(path.relative_to(ROOT)),path)
    for name in ['readiness.json','cache-ready.json','runtime.json','persistence.json']:
        path=ROOT/'runtime/recovery-1030'/name
        add(str(path.relative_to(ROOT)),path)
    explicit = [
      'experiments/w4-paired-situ/retention.json',
      'experiments/w4-paired-situ/integration.json',
      'experiments/w4-paired-situ/review-retirement.json',
      'experiments/w4-paired-situ/source-reuse-proof.json',
      'experiments/w4-paired-situ/RETENTION.md',
      'experiments/w4-paired-situ/PERFORMANCE.md',
      'experiments/w4-paired-situ/ACCA.md',
      'experiments/w4-paired-situ/compare_campaigns.py',
      'experiments/w4-paired-situ/campaign-comparison.json',
      'experiments/w4-paired-situ/source-audit.json',
      'experiments/w4-paired-situ/qualification-summary.json',
      'experiments/w4-paired-situ/negative-native/analyze_components.py',
      'experiments/w4-paired-situ/negative-native/component-phases.csv',
      'experiments/w4-paired-situ/negative-native/component-summary.json',
      'experiments/w4-paired-situ/negative-native/COMPONENTS.md',
      'experiments/w4-paired-situ/negative-native/deploy.stderr',
      'experiments/w4-paired-situ/negative-native-r1/deploy.stderr',
      'experiments/w4-paired-situ/negative-native-r2/analyze.py',
      'experiments/w4-paired-situ/negative-native-r2/native-summary.json',
      'experiments/w4-paired-situ/negative-native-r2/schedule-boundary.json',
      'experiments/w4-paired-situ/negative-native-r2/token-16-fc1-instructions.diff',
      'experiments/w4-paired-situ/negative-native-r2/token-32-fc1-instructions.diff',
      'experiments/w4-paired-situ/negative-native-r2/RESULTS.md',
      'experiments/w4-paired-situ/acca-screen/gpu-release.json',
    ]
    for name in explicit: add(name,ROOT/name)
    # Every new archive input is pinned here; the packer never discovers inputs.
    members['bundle-allowlist.json']=str((HERE/'bundle-allowlist.json').relative_to(ROOT))
    manifest = dict(passed=True, retained_head='2b8eb9d8f72ceda3952fbb05054fee97173fc9c7',
        inherited_manifest='publication-integer-store/bundle-manifest.json', inherited_manifest_sha256=sha(OLD/'bundle-manifest.json'),
        inherited_xz_sha256=old_verify['archive_sha256'], inherited_original_members=len(old_manifest['files']),
        fresh_manifest_files=fresh_files,
        members=dict(sorted(members.items())), boundary='Explicit original manifest, fresh fetch manifests and bounded named output collections only; body drafts, caches, archives and publisher logs excluded.')
    write(HERE/'bundle-allowlist.json',manifest)
    print(json.dumps(dict(members=len(members),fresh_manifest_files=fresh_files,total_input_bytes=sum((ROOT/p).stat().st_size for p in members.values()))))


if __name__=='__main__': main()
