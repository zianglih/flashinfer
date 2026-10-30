"""Seal explicitly allowlisted result/evidence files as a deterministic XZ tar."""
import hashlib
import io
import json
import lzma
import tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
HEAD = "bf072d26b163e71458e7e4dfb12e615b19bd2c9a"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def main():
    # Never recurse over the publication directory: it also contains preview
    # archives, publishing logs, and provisional body files owned by the parent.
    allowlist = json.loads((HERE / "bundle-allowlist.json").read_text())
    members = {name: ROOT / source for name, source in allowlist["members"].items()}
    assert len(members) == len(allowlist["members"])
    assert all(not Path(name).is_absolute() and ".." not in Path(name).parts for name in members)
    assert all(path.resolve().is_relative_to(ROOT) and path.is_file() for path in members.values())
    assert all(not name.endswith((".tar", ".gz", ".xz", ".zip")) for name in members)
    assert all(Path(name).name not in {"PR_BODY.md", "write_pr_body.py", "assets-publish.log", "assets-small-commit.log", "assets-receipt.json", "archive-recompression.json"} for name in members)
    assert "w4-tail-causal/table.md" in members and "glm5-comparison.md" in members

    old_path = ROOT / allowlist["original_bundle_manifest"]
    assert sha(old_path) == allowlist["original_bundle_manifest_sha256"]
    old = json.loads(old_path.read_text())
    assert set(old["files"]) <= set(members)
    changed = {name: {"old": digest, "new": sha(members[name])}
               for name, digest in old["files"].items() if sha(members[name]) != digest}
    assert set(changed) == set(allowlist["permitted_transport_changes"]), changed
    transport = json.loads((HERE / "archive-transport-proof.json").read_text())
    assert transport["passed"] and transport["changed_original_members"] == changed
    assert transport["native_tables_unchanged"] and transport["original_raw_and_stdout_unchanged"]

    manifest = dict(
        passed=True, retained_head=HEAD, archive_format="tar.xz",
        files={name: sha(path) for name, path in sorted(members.items())},
        allowlist_sha256=sha(HERE / "bundle-allowlist.json"),
        transport_proof_sha256=sha(HERE / "archive-transport-proof.json"),
        original_gzip_sha256=allowlist["original_gzip_sha256"],
        original_gzip_manifest_sha256=allowlist["original_bundle_manifest_sha256"],
        fresh_raw_samples=15600, fresh_cells=39, reused_cells=429,
        original_stdout_logs=86, all_fresh_raw_data_included=True,
        body_draft_excluded=True,
        boundary="Lossless XZ delivery of the original sealed evidence; only archive links, renderer/comment hashes and packaging metadata changed. Native tables, measurements, source/reuse proofs, images and raw logs are unchanged. No remote writes.",
    )
    write(HERE / "bundle-manifest.json", manifest)
    members["bundle-manifest.json"] = HERE / "bundle-manifest.json"
    archive = HERE / "moe-gather-pipeline-results.tar.xz"
    temporary = HERE / "moe-gather-pipeline-results.tar.xz.building"
    with lzma.open(temporary, "wb", format=lzma.FORMAT_XZ, check=lzma.CHECK_CRC64, preset=6) as xz, tarfile.open(fileobj=xz, mode="w|") as tar:
        for name, path in sorted(members.items()):
            raw = path.read_bytes()
            info = tarfile.TarInfo(name)
            info.size = len(raw)
            info.mode = 0o644
            info.mtime = 0
            tar.addfile(info, io.BytesIO(raw))
    temporary.replace(archive)
    with tarfile.open(archive, "r:xz") as tar:
        names = tar.getnames()
        assert len(names) == len(set(names)) == len(members)
        assert set(names) == set(members)
        for name, path in members.items():
            assert hashlib.sha256(tar.extractfile(name).read()).hexdigest() == sha(path), name
    result = dict(
        passed=True, archive_format="tar.xz", archive_sha256=sha(archive),
        archive_bytes=archive.stat().st_size, member_count=len(members),
        bundle_manifest_sha256=sha(HERE / "bundle-manifest.json"),
        allowlist_sha256=sha(HERE / "bundle-allowlist.json"),
        transport_proof_sha256=sha(HERE / "archive-transport-proof.json"),
        original_gzip_sha256=allowlist["original_gzip_sha256"],
        peer_sha256=sha(HERE / "audits/w4-tail-publication-finalization.json"),
        root_visual_sha256=sha(HERE / "visual-review.json"),
        body_draft_excluded=True, recursive_archives_excluded=True,
        w4_tail_causal_table_included=True, glm5_table_included=True,
    )
    write(HERE / "bundle-verification.json", result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
