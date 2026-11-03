"""Seal metadata plus role/topology raw evidence shards, each below GitHub's limit."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import io
import json
import lzma
import re
import tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HEAD = "2b4732791a3ce48bc3ae6c030a283fab73854e0e"
LIMIT = 100_000_000


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def prepare():
    numeric = read(HERE / "numeric-validation.json")
    assert numeric["passed"] and numeric["head"] == HEAD
    assert numeric["samples"] == 187200 and numeric["candidate_samples"] == 93600
    buckets = {"metadata": {}}
    def add(bucket, name, path, expected=None):
        path = Path(path)
        assert path.is_file() and path.resolve().is_relative_to(ROOT)
        assert not Path(name).is_absolute() and ".." not in Path(name).parts
        assert not name.endswith((".xz", ".gz", ".tar", ".zip", ".pyc"))
        digest = sha(path)
        if expected:
            assert digest == expected, name
        values = buckets.setdefault(bucket, {})
        assert name not in values, name
        values[name] = dict(path=str(path.relative_to(ROOT)), sha256=digest, bytes=path.stat().st_size)
    fixed = ["README.md", "assemble.py", "verify_numeric.py", "plot_external.py", "plot_retained.py",
             "preflight.py", "preflight.json", "build_bundle.py", "patch_body.py", "dependencies.json",
             "render_performance.py", "runtime-context.json", "runtime-notes.md", "scan_publication.py",
             "inputs.json", "manifest.json", "source-equivalence.json", "numeric-validation.json",
             "numerical-tables.md", "benchmark-comparisons.csv", "report/cells.csv", "report/summary.json",
             "report/clock-quartiles.json", "report/runtime-resources.json", "stdout/manifest.json",
             "completed-tables/render_comments.py", "completed-tables/baseline-index.json",
             "completed-tables/formatter-source-proof.json", "completed-tables/manifest.json",
             "retained/manifest.json", "retained/stats.md"]
    for name in fixed:
        add("metadata", name, HERE / name)
    for topology in ("ep", "tp"):
        for name in ("summary-cells.csv", "summary-table.md", "provenance.json"):
            rel = f"external/{topology}/{name}"
            add("metadata", rel, HERE / rel)
        rel = f"plots/plot-manifest-{topology}.json"
        add("metadata", rel, HERE / rel)
        for name, digest in read(HERE / rel)["outputs"].items():
            add("metadata", "plots/" + name, HERE / "plots" / name, digest)
    for plot in read(HERE / "retained/manifest.json")["plots"]:
        for name, digest in plot["outputs"].items():
            add("metadata", "retained/" + name, HERE / "retained" / name, digest)
    for log in read(HERE / "stdout/manifest.json"):
        add("metadata", log["path"], HERE / log["path"], log["sha256"])
    for group in read(HERE / "completed-tables/manifest.json")["groups"]:
        if not group.get("skipped"):
            add("metadata", "completed-tables/" + group["table"], HERE / "completed-tables" / group["table"], group["table_sha256"])
    for ordinal, item in enumerate(read(HERE / "inputs.json")["roots"]):
        data = ROOT / item["data"]
        config = read(data / "perf-config.json")
        receipt_path = data.parent / "fetch-receipt.json"
        receipt = read(receipt_path)
        assert receipt["passed"] and set(receipt["jobs"]) == set(config["jobs"])
        prefix = f"evidence/fresh/{ordinal}-{data.parent.name}"
        add("metadata", prefix + "/fetch-receipt.json", receipt_path)
        for name, digest in receipt["files"].items():
            bucket = "metadata"
            parts = Path(name).parts
            match = re.search(r"(?:^|/)([0-9]+)-(candidate|control)(?:/|\.|$)", name)
            if match:
                assert parts[0] == "results", name
                job = config["jobs"][parts[1]]
                assert config["phases"][int(match[1])] == match[2]
                topology = "tp" if job["tp"] > 1 else "ep"
                bucket = match[2] + "-" + topology
            add(bucket, prefix + "/data/" + name, data / name, digest)
        for name in ("summary.json", "cells.csv", "clock-quartiles.json", "runtime-resources.json", "phase-components.csv", "component-deltas.csv", "table.md"):
            add("metadata", prefix + "/report/" + name, data.parent / "report" / name)
    diagnostic = read(HERE / "diagnostic-inputs.json")
    assert diagnostic["passed"] and diagnostic["head"] == HEAD
    assert diagnostic["control"] == "a620ce7790b32f7f0ae524a811417d2c6cee1152"
    assert diagnostic["main_cells_sha256"] == sha(HERE / "report/cells.csv")
    assert diagnostic["summary"] in diagnostic["files"]
    add("metadata", "diagnostic-inputs.json", HERE / "diagnostic-inputs.json")
    for name, digest in diagnostic["files"].items():
        add("metadata", "evidence/diagnostic/" + name, ROOT / name, digest)
    add("metadata", "diagnostic-summary.json", ROOT / diagnostic["summary"], diagnostic["files"][diagnostic["summary"]])
    assert set(buckets) == {"metadata", "candidate-ep", "candidate-tp", "control-ep", "control-tp"}
    result = dict(passed=True, head=HEAD, buckets=buckets,
        files=sum(map(len, buckets.values())), historical_raw_copied=False, nested_archives=False,
        boundary="Exact fetch-receipt files, named reports and publication outputs only. Original baseline archives are immutable dependencies. URL-dependent drafts are excluded. Raw CAAC evidence is split by role/topology; no samples are omitted.")
    write(HERE / "bundle-allowlist.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    args = parser.parse_args()
    allowlist = prepare()
    if args.prepare:
        print(json.dumps({k: len(v) for k, v in allowlist["buckets"].items()}))
        return
    scan = read(HERE / "credential-scan.json")
    assert scan["passed"] and scan["head"] == HEAD
    assert scan["allowlist_sha256"] == sha(HERE / "bundle-allowlist.json")
    assert scan["scanner_sha256"] == sha(HERE / "scan_publication.py")
    visual = read(HERE / "visual-review.json")
    assert visual["passed"]
    expected_plots = read(HERE / "numeric-validation.json")["plots"]
    assert set(visual["plots"]) == set(expected_plots)
    for name, digest in expected_plots.items():
        assert visual["plots"][name] == sha(HERE / name) == digest
    def seal_archive(item):
        bucket, records = item
        target = HERE / f"publication-{bucket}.tar.xz"
        temporary = target.with_suffix(".xz.building")
        with lzma.open(temporary, "wb", preset=6) as stream, tarfile.open(fileobj=stream, mode="w|") as tar:
            for name, record in sorted(records.items()):
                data = (ROOT / record["path"]).read_bytes()
                assert hashlib.sha256(data).hexdigest() == record["sha256"]
                info = tarfile.TarInfo(name)
                info.size, info.mode, info.mtime = len(data), 0o644, 0
                tar.addfile(info, io.BytesIO(data))
        assert temporary.stat().st_size < LIMIT, (bucket, "Oversized draft retained; split whole jobs, never drop samples")
        temporary.replace(target)
        with tarfile.open(target) as tar:
            assert set(tar.getnames()) == set(records)
            assert len(tar.getnames()) == len(records)
            for name, record in records.items():
                assert hashlib.sha256(tar.extractfile(name).read()).hexdigest() == record["sha256"]
        return dict(name=target.name, sha256=sha(target), bytes=target.stat().st_size,
                    member_count=len(records), files={k: v["sha256"] for k, v in records.items()})

    # Each shard owns its files; map preserves the deterministic manifest order.
    with ThreadPoolExecutor(max_workers=3) as pool:
        archives = list(pool.map(seal_archive, sorted(allowlist["buckets"].items())))
    result = dict(passed=True, head=HEAD, archives=archives, fresh_cells=468,
        candidate_samples=93600, control_samples=93600, raw_samples=187200,
        historical_raw_copied=False, nested_archives=False, per_file_limit_bytes=LIMIT,
        allowlist_sha256=sha(HERE / "bundle-allowlist.json"), numeric_validation_sha256=sha(HERE / "numeric-validation.json"),
        visual_review_sha256=sha(HERE / "visual-review.json"), credential_scan_sha256=sha(HERE / "credential-scan.json"), dependencies_sha256=sha(HERE / "dependencies.json"))
    write(HERE / "bundle-manifest.json", result)
    print(json.dumps([{k: a[k] for k in ("name", "bytes", "sha256")} for a in archives], indent=2))


if __name__ == "__main__":
    main()
