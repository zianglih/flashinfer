"""Read-only peer gate for completed fresh CUDA13.0 evidence/publication files."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import tarfile

from analyze_cuda130 import HEADS, TOKENS, analyze_job, geo, load, sha
from check_public_text import inspect_bytes

MODELS = [("v3", "V3", 8), ("v41-flash", "V41F", 4),
          ("kimi-k3", "K3", 8), ("nemo3-ultra", "N3U", 8)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--publication", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    data = args.data / "results" if (args.data / "results").is_dir() else args.data
    audit, pub = load(args.audit), args.publication
    assert audit["summary"]["complete"]
    assert (audit["summary"]["jobs"], audit["summary"]["cells"], audit["summary"]["retention_cells"], audit["summary"]["raw_samples"]) == (8, 104, 88, 41600)
    # Recompute every raw span, phase median, fixed choice and fresh route,
    # without editing the final audit file that presentation artifacts bind.
    replayed = [analyze_job(data / job["job"]) for job in audit["jobs"]]
    assert replayed == audit["jobs"]
    lookup = {(job["job"], cell["token"]): cell for job in replayed for cell in job["cells"]}
    retained = [c for c in lookup.values() if c["retention"]]
    assert len(lookup) == 104 and len(retained) == 88
    for topology in ("all", "ep", "tp"):
        for group in ("all", "decode", "prefill"):
            selected = [c for c in retained if (topology == "all" or c[topology] > 1)
                        and (group == "all" or (c["token"] <= 512 if group == "decode" else c["token"] >= 4096))]
            expected = (geo(c["before_us"] / c["after_us"] for c in selected) - 1) * 100
            assert math.isclose(audit["summary"]["stats"][topology + "_" + group]["speedup_percent"], expected, abs_tol=1e-12)
    report = load(pub / "report-inputs.json")
    assert report["complete"] and report["audit_sha256"] == sha(args.audit)
    assert report["sources"] == HEADS and not report["raw_tables_parsed"]
    labels = {f"{label} {top.upper()}{degree}": f"{top}-{model}-w4a16"
              for top in ("ep", "tp") for model, label, degree in MODELS}
    table = list(csv.DictReader((pub / "tables.csv").open()))
    assert len(table) == 104
    seen = set()
    for row in table:
        key = labels[row["model"]], int(row["tokens"])
        assert key not in seen
        seen.add(key)
        expected = lookup[key]
        for name in ("before_us", "after_us", "speedup_percent", "conservative_speedup_percent"):
            assert math.isclose(float(row[name]), expected[name], abs_tol=1e-12)
        for name, role, index in (("c1_us", "before", 0), ("c2_us", "before", 1), ("a1_us", "after", 0), ("a2_us", "after", 1)):
            assert math.isclose(float(row[name]), expected["phase_us"][role][index], abs_tol=1e-12)
    assert seen == set(lookup)
    image_manifest = load(pub / "cuda130-w4a16-before-after-manifest.json")
    assert image_manifest["preview"] is False and (image_manifest["rows"], image_manifest["columns"]) == (11, 8)
    assert image_manifest["source_sha256"] == sha(args.audit)
    assert len(image_manifest["cells"]) == 88
    for item in image_manifest["cells"]:
        cell = lookup[labels[item["label"]], item["token"]]
        assert item["token"] in TOKENS[2:]
        assert item["value"] == cell["speedup_percent"]
        assert item["star"] == (max(cell["repeat_spread_percent"].values()) > 1)
    for filename, digest in image_manifest["outputs"].items():
        assert sha(pub / filename) == digest
    native = load(pub / "native-output-manifest.json")
    assert native["original_output_unchanged"] and len(native["logs"]) == 32
    for item in native["logs"]:
        assert sha(pub / item["path"]) == sha(data / item["job"] / (item["phase"] + ".log")) == item["sha256"]
    bundle = load(pub / "bundle-manifest.json")
    assert bundle["complete"] and bundle["audit_sha256"] == sha(args.audit)
    assert (bundle["fresh_cases"], bundle["retention_cases"], bundle["fresh_samples"]) == (104, 88, 41600)
    assert len(bundle["artifacts"]) == 3
    members, raw_results, sensitive_findings = {}, 0, []
    for artifact in bundle["artifacts"]:
        path = pub / artifact["name"]
        assert path.stat().st_size == artifact["bytes"] < 100_000_000
        assert sha(path) == artifact["sha256"]
        with tarfile.open(path, "r:xz") as archive:
            member_manifest = artifact["member_manifest"]
            assert set(archive.getnames()) == set(artifact["files"]) | {member_manifest}
            embedded = json.loads(archive.extractfile(member_manifest).read())
            assert embedded["files"] == artifact["files"]
            for name, identity in artifact["files"].items():
                content = archive.extractfile(name).read()
                assert len(content) == identity["bytes"]
                assert hashlib.sha256(content).hexdigest() == identity["sha256"]
                sensitive_findings.extend(inspect_bytes(name, content))
                if name.startswith("results/"):
                    assert sha(data / Path(name).relative_to("results")) == identity["sha256"]
                    raw_results += name.endswith("/results.json")
                members[name] = identity["sha256"]
    assert raw_results == 32
    sensitive_receipt = dict(passed=not sensitive_findings, archive_files_inspected=len(members),
        findings=sensitive_findings, boundary="Pattern inspection of exact selected archive text; reports file/category/count only, never matched values.")
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    (args.receipt.parent / "public-text-review.json").write_text(json.dumps(sensitive_receipt, indent=2) + "\n")
    assert not sensitive_findings, sensitive_findings
    # A benchmark replay recipe is distinct from the actual measured config.
    # Preserve the latter so all 8 receipt.config_sha256 bindings are checkable.
    config_hashes = {load(data / job["job"] / "receipt.json")["config_sha256"] for job in replayed}
    assert len(config_hashes) == 1
    assert next(iter(config_hashes)) in set(members.values()), "Measured execution config missing from archive"
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    result = dict(passed=True, audit_sha256=sha(args.audit), source_heads=HEADS,
        fresh_cases=104, retention_cases=88, fresh_samples=41600,
        report_manifest_sha256=sha(pub / "report-inputs.json"), bundle_manifest_sha256=sha(pub / "bundle-manifest.json"),
        checks=dict(fresh_raw_cupti_replayed=True, fixed_choices_and_routes=True,
                    resolved_after_configs=True, independent_summary_ratios=True,
                    all_104_table_values=True, all_88_plot_values=True,
                    native_stdout_32_files_unchanged=True, archives_rehashed=True,
                    measured_config_archived=True, public_text_credential_scan=True),
        boundary="Independent CPU-only evidence and publication audit. Root separately owns visual inspection and all public writes.")
    args.receipt.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
