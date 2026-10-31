"""Seal an incremental fresh-data XZ allowlist; never copy historical raw archives."""
import argparse
import fcntl
import hashlib
import io
import json
import lzma
import tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
HEAD = "a620ce7790b32f7f0ae524a811417d2c6cee1152"
LIMIT = 100_000_000


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def make_allowlist():
    numeric = read(HERE / "numeric-validation.json")
    assert numeric["passed"] and numeric["head"] == HEAD and numeric["samples"] == 93600
    inputs = read(HERE / "inputs.json")
    members = {}
    def add(name, path, expected=None):
        path = Path(path)
        assert not Path(name).is_absolute() and ".." not in Path(name).parts
        assert path.is_file() and path.resolve().is_relative_to(ROOT)
        assert name not in members and not name.endswith((".gz", ".xz", ".tar", ".zip", ".pyc"))
        if expected:
            assert sha(path) == expected, name
        members[name] = str(path.relative_to(ROOT))

    fixed = ["README.md", "assemble.py", "verify_numeric.py", "plot_external.py", "build_bundle.py",
             "dependencies.json", "inputs.json", "manifest.json", "source-equivalence.json",
             "numeric-validation.json", "numerical-tables.md", "benchmark-comparisons.csv",
             "source/publication-plan.md", "source/publication-source-diff.json", "source/pr7290-before.json",
             "report/cells.csv", "report/summary.json", "report/clock-quartiles.json", "report/runtime-resources.json",
             "stdout/manifest.json", "completed-tables/render_comments.py", "completed-tables/baseline-index.json",
             "completed-tables/formatter-source-proof.json", "completed-tables/manifest.json"]
    for name in fixed:
        add(name, HERE / name)
    for topology in ("ep", "tp"):
        for name in ("summary-cells.csv", "summary-table.md", "provenance.json"):
            relative = f"external/{topology}/{name}"
            add(relative, HERE / relative)
        relative = f"plots/plot-manifest-{topology}.json"
        add(relative, HERE / relative)
        for name, digest in read(HERE / relative)["outputs"].items():
            add("plots/" + name, HERE / "plots" / name, digest)
    for log in read(HERE / "stdout/manifest.json"):
        add(log["path"], HERE / log["path"], log["sha256"])
    for group in read(HERE / "completed-tables/manifest.json")["groups"]:
        if not group.get("skipped"):
            add("completed-tables/" + group["table"], HERE / "completed-tables" / group["table"], group["table_sha256"])
    for item in inputs["roots"]:
        data = ROOT / item["data"]
        receipt_path = data.parent / "fetch-receipt.json"
        receipt = read(receipt_path)
        assert receipt["passed"] and len(receipt["jobs"]) == 31
        prefix = "evidence/fresh/" + data.parent.name
        add(prefix + "/fetch-receipt.json", receipt_path)
        for name, digest in receipt["files"].items():
            add(prefix + "/data/" + name, data / name, digest)
        # Reports are derived from precisely this sealed raw leaf; do not traverse parent publications.
        for name in ("summary.json", "cells.csv", "clock-quartiles.json", "runtime-resources.json", "phase-components.csv", "table.md"):
            add(prefix + "/report/" + name, data.parent / "report" / name)
    smoke = ROOT / "integration/pr7290-refresh-20261030/smoke-evidence"
    archive_manifest = read(smoke / "data/archive-manifest.json")
    assert archive_manifest["passed"] and read(smoke / "fetch.json")["passed"]
    add("evidence/smoke/fetch.json", smoke / "fetch.json")
    add("evidence/smoke/data/archive-manifest.json", smoke / "data/archive-manifest.json")
    for name, digest in archive_manifest["files"].items():
        add("evidence/smoke/data/" + name, smoke / "data" / name, digest)
    for name in ("smoke-summary.json", "plan.json", "harness-proof.json", "source-full.json",
                 "prepare.py", "preflight.py", "postflight.py", "launch.py", "fetch.py",
                 "performance-closure.json", "RESULTS.md", "README.md"):
        add("integration/" + name, ROOT / "integration/pr7290-refresh-20261030" / name)
    helper_proof = read(ROOT / "integration/pr7290-refresh-20261030/harness-proof.json")
    assert helper_proof["passed"] and helper_proof["all_twelve_byte_identical"]
    for name, digest in helper_proof["helpers"].items():
        add("integration/harness/" + name, ROOT / "integration/pr7290-refresh-20261030/harness" / name, digest)
    for name in ("runtime/recovery-paired-error/runtime.json",
                 "experiments/sf-coordinate-cache/cache-recovery/cache-ready-current.json",
                 "experiments/sf-coordinate-cache/cache-recovery/readiness-current.json"):
        add("runtime/" + Path(name).name, ROOT / name)
    result = dict(passed=True, head=HEAD, members=dict(sorted(members.items())),
        file_sha256={name: sha(ROOT / path) for name, path in sorted(members.items())},
        dependencies_sha256=sha(HERE / "dependencies.json"),
        boundary="Explicit fresh performance/smoke manifests and named derived outputs only. Historical raw evidence is an immutable dependency. Body, comment URL drafts, publishers and nested archives are excluded.")
    write(HERE / "bundle-allowlist.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true", help="Write the evidence allowlist; sealing additionally requires visual and independent peer receipts.")
    args = parser.parse_args()
    allowlist = make_allowlist()
    if args.prepare:
        print(json.dumps(dict(prepared=True, members=len(allowlist["members"]), allowlist_sha256=sha(HERE / "bundle-allowlist.json"))))
        return
    members = {name: ROOT / path for name, path in allowlist["members"].items()}
    for relative in ("audits/pr7290-a620-data-peer.json", "audits/pr7290-a620-publication-peer.json",
                     "audits/pr7290-a620-smoke-peer.json"):
        assert read(ROOT / relative)["passed"]
        members[relative] = ROOT / relative
    visual = read(HERE / "visual-review.json")
    assert visual["passed"]
    for name, digest in visual["plots"].items():
        assert sha(HERE / name) == digest
    assert set(read(HERE / "numeric-validation.json")["plots"]) == set(visual["plots"])
    members["visual-review.json"] = HERE / "visual-review.json"
    members["bundle-allowlist.json"] = HERE / "bundle-allowlist.json"
    manifest = dict(passed=True, head=HEAD, files={name: sha(path) for name, path in sorted(members.items())},
        fresh_cells=468, raw_samples=93600, smoke_exact_calls=7, smoke_native_kernels=21,
        dependencies_sha256=sha(HERE / "dependencies.json"), body_and_comment_drafts_excluded=True,
        archive_format="tar.xz", per_file_limit_bytes=LIMIT)
    write(HERE / "bundle-manifest.json", manifest)
    members["bundle-manifest.json"] = HERE / "bundle-manifest.json"
    temporary = HERE / "publication-evidence.tar.xz.building"
    archive = HERE / "publication-evidence.tar.xz"
    with lzma.open(temporary, "wb", format=lzma.FORMAT_XZ, check=lzma.CHECK_CRC64, preset=6) as stream, tarfile.open(fileobj=stream, mode="w|") as tar:
        for name, path in sorted(members.items()):
            data = path.read_bytes()
            info = tarfile.TarInfo(name)
            info.size, info.mode, info.mtime = len(data), 0o644, 0
            tar.addfile(info, io.BytesIO(data))
    assert temporary.stat().st_size < LIMIT, "Preserve this oversized draft and split whole evidence leaves; never omit samples."
    temporary.replace(archive)
    with tarfile.open(archive, "r:xz") as tar:
        assert len(tar.getnames()) == len(set(tar.getnames())) == len(members)
        assert set(tar.getnames()) == set(members)
        for name, path in members.items():
            assert hashlib.sha256(tar.extractfile(name).read()).hexdigest() == sha(path)
    result = dict(passed=True, head=HEAD, archive_sha256=sha(archive), archive_bytes=archive.stat().st_size,
        archive_name=archive.name, member_count=len(members), bundle_manifest_sha256=sha(HERE / "bundle-manifest.json"),
        allowlist_sha256=sha(HERE / "bundle-allowlist.json"), dependencies_sha256=sha(HERE / "dependencies.json"),
        original_stdout_logs=62, fresh_cells=468, raw_samples=93600, reused_candidate_cells=0,
        incremental=True, nested_archives=False, historical_raw_copied=False)
    write(HERE / "bundle-verification.json", result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    with (HERE / ".bundle.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        main()
