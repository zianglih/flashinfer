"""Seal local result assets plus full fresh CAAC raw evidence, without publishing."""
import gzip
import hashlib
import io
import json
import shutil
import subprocess
import tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
HEAD = "bf072d26b163e71458e7e4dfb12e615b19bd2c9a"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
write = lambda p, v: p.write_text(json.dumps(v, indent=2) + "\n")


def main():
    audit_names = ["w4-tail-data-peer.json", "w4-tail-components-peer.json", "w4-tail-remaining-data-peer.json", "w4-tail-remaining-components-peer.json", "w4-tail-combined-data-peer.json", "w4-tail-performance-peer.md", "w4-tail-combined-performance-peer.md", "w4-tail-publication-peer.json", "w4-tail-publication-finalization.json"]
    (HERE / "audits").mkdir(exist_ok=True)
    for name in audit_names:
        shutil.copyfile(ROOT / "audits" / name, HERE / "audits" / name)
    (HERE / "w4-tail-causal").mkdir(exist_ok=True)
    for name in ("cells.csv", "summary.json", "table.md", "matrix.md"):
        shutil.copyfile(ROOT / "experiments/w4-tail-dequant/combined39" / name, HERE / "w4-tail-causal" / name)
    shutil.copyfile(ROOT / "publication/assets-repository/02de7785/glm5-comparison.md", HERE / "glm5-comparison.md")
    (HERE / "source").mkdir(exist_ok=True)
    qualification = json.loads((ROOT / "experiments/w4-tail-dequant/qualification-summary.json").read_text())
    for name, digest in qualification["source_hashes"].items():
        raw = subprocess.check_output(["git", "-C", str(ROOT / "flashinfer"), "show", HEAD + ":" + name])
        assert hashlib.sha256(raw).hexdigest() == digest
        (HERE / "source" / Path(name).name).write_bytes(raw)
    (HERE / "source/candidate.patch").write_bytes(subprocess.check_output(["git", "-C", str(ROOT / "flashinfer"), "diff", "02de7785", HEAD, "--", *qualification["source_hashes"]]))
    shutil.copyfile(ROOT / "experiments/w4-tail-dequant/qualification-summary.json", HERE / "source/qualification-summary.json")
    shutil.copyfile(ROOT / "experiments/w4-tail-dequant/publication-plan/coverage-proof.json", HERE / "source/coverage-proof.json")
    shutil.copyfile(ROOT / "publication/retained-source-equivalence.json", HERE / "source/previous-source-equivalence.json")
    write(HERE / "source/commit.json", dict(retained_head=HEAD, measured_base="02de7785c10847b3528340840bed40bd405d85b4", source_sha256=qualification["source_hashes"], boundary="Only the two qualified files differ from02de; immutable raw measurements retain02de plus patch. Reused records retain their earlier actual measured source."))
    excluded = {"PR_BODY.md", "write_pr_body.py", "freeze-manifest.json", "bundle-manifest.json", "bundle-verification.json", "moe-gather-pipeline-results.tar.gz"}
    members = {str(p.relative_to(HERE)): p for p in HERE.rglob("*") if p.is_file() and p.name not in excluded and not any(n in p.parts for n in (".mpl-cache", "__pycache__"))}
    for relative in ("evidence/w4-tail-dequant-screen/1793368574438182000", "evidence/w4-tail-dequant-remaining/1793369332076642000"):
        base = ROOT / relative
        for p in base.rglob("*"):
            if p.is_file() and p.suffix not in (".gz", ".tar"):
                members[str(p.relative_to(ROOT))] = p
    for name in ("audit_w4_tail_data.py", "audit_w4_tail_components.py", "audit_w4_tail_remaining.py", "audit_w4_tail_remaining_components.py", "audit_w4_tail_combined.py"):
        members["audits/" + name] = ROOT / "audits" / name
    assert "w4-tail-causal/table.md" in members and "glm5-comparison.md" in members
    assert all(name not in members for name in ("PR_BODY.md", "write_pr_body.py"))
    manifest = dict(passed=True, retained_head=HEAD, files={name: sha(p) for name, p in sorted(members.items())}, fresh_raw_samples=15600, fresh_cells=39, reused_cells=429, original_stdout_logs=86, all_fresh_raw_data_included=True, body_draft_excluded=True, boundary="Standalone result assets and full raw fresh C/A/A/C evidence; original published429 cells and historical baseline provenance retained. No remote writes.")
    write(HERE / "bundle-manifest.json", manifest)
    members["bundle-manifest.json"] = HERE / "bundle-manifest.json"
    archive = HERE / "moe-gather-pipeline-results.tar.gz"
    with archive.open("wb") as f, gzip.GzipFile(filename="", mode="wb", fileobj=f, mtime=0) as gz, tarfile.open(fileobj=gz, mode="w") as tar:
        for name, path in sorted(members.items()):
            raw = path.read_bytes()
            info = tarfile.TarInfo(name)
            info.size = len(raw)
            info.mode = 0o644
            info.mtime = 0
            tar.addfile(info, io.BytesIO(raw))
    with tarfile.open(archive, "r:gz") as tar:
        assert set(tar.getnames()) == set(members)
        for name, path in members.items():
            assert hashlib.sha256(tar.extractfile(name).read()).hexdigest() == sha(path), name
    result = dict(passed=True, archive_sha256=sha(archive), archive_bytes=archive.stat().st_size, member_count=len(members), bundle_manifest_sha256=sha(HERE / "bundle-manifest.json"), peer_sha256=sha(HERE / "audits/w4-tail-publication-finalization.json"), root_visual_sha256=sha(HERE / "visual-review.json"), body_draft_excluded=True, w4_tail_causal_table_included=True, glm5_table_included=True)
    write(HERE / "bundle-verification.json", result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
