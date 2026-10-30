"""Overlay 39 audited W4 cells; preserve the published 429 cells and baselines."""
import csv
import hashlib
import importlib.util
import json
import math
import shutil
import statistics
import subprocess
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OLD = ROOT / "publication"
DATA = [ROOT / "evidence/w4-tail-dequant-screen/1793368574438182000/data",
        ROOT / "evidence/w4-tail-dequant-remaining/1793369332076642000/data"]
RETAINED = "bf072d26b163e71458e7e4dfb12e615b19bd2c9a"
LABEL = "bf072d26 · 39 fresh / 429 reused cells"
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
read = lru_cache(maxsize=None)(lambda p: json.loads(p.read_text()))
rows = lambda p: list(csv.DictReader(p.open()))
key = lambda r: (r["model"], r["topology"], r["backend"], int(r["tokens"]))
gm = lambda rr: 100 * (math.exp(statistics.mean(math.log1p(float(r["speedup_percent"]) / 100) for r in rr)) - 1)


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


def writecsv(path, rr):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rr[0]))
        writer.writeheader()
        writer.writerows(rr)


def main():
    old_hashes = {str(p.relative_to(OLD)): sha(p) for p in OLD.rglob("*") if p.is_file() and ".git" not in p.parts and "assets-repository" not in p.parts}
    peer = read(ROOT / "audits/w4-tail-combined-data-peer.json")
    assert peer["passed"] and peer["retention_cells"] == 33
    assert sha(ROOT / "experiments/w4-tail-dequant/combined39/cells.csv") == peer["combined_cells_sha256"]
    changed = subprocess.check_output(["git", "-C", str(ROOT / "flashinfer"), "diff", "--name-only", "02de7785", RETAINED], text=True).splitlines()
    qualified_hashes = read(ROOT / "experiments/w4-tail-dequant/qualification-summary.json")["source_hashes"]
    assert set(changed) == set(qualified_hashes)
    for name, expected in qualified_hashes.items():
        assert hashlib.sha256(subprocess.check_output(["git", "-C", str(ROOT / "flashinfer"), "show", RETAINED + ":" + name])).hexdigest() == expected
    old_manifest = read(OLD / "manifest.json")
    assert sha(OLD / "report/cells.csv") == old_manifest["report_sha256"]
    base_rows = rows(OLD / "report/cells.csv")
    base = {key(r): r for r in base_rows}
    new = {}
    for data in DATA:
        cfg = read(data / "perf-config.json")
        assert cfg["phases"] == ["control", "candidate", "candidate", "control"]
        for r in rows(data.parent / "report/cells.csv"):
            k = key(r)
            assert k not in new and k in base and r["backend"] == "CuteDSL W4A16"
            new[k] = (r, data)
    expected = {(m, "tp", "CuteDSL W4A16", t) for m in ("v41-flash", "kimi-k3", "nemo3-ultra") for t in (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 4096, 8192, 16384)}
    assert set(new) == expected
    final = []
    provenance = []
    final_records = {}
    for original in base_rows:
        k = key(original)
        updated = dict(original)
        if k in new:
            r, data = new[k]
            phase_paths = [data / "results" / r["job"] / label / "results.json" for label in ("1-candidate", "2-candidate")]
            a1, a2 = float(r["a1_us"]), float(r["a2_us"])
            candidate = math.sqrt(a1 * a2)
            assert math.isclose(candidate, float(r["candidate_us"]), abs_tol=1e-9)
            updated.update(a1_us=a1, a2_us=a2, candidate_us=candidate,
                           candidate_spread_percent=r["candidate_spread_percent"],
                           speedup_percent=100 * (float(original["baseline_us"]) / candidate - 1),
                           variance_flag=max(float(original["control_spread_percent"]), float(r["candidate_spread_percent"])) > 1,
                           candidate_evidence=json.dumps([str(p.relative_to(ROOT)) for p in phase_paths]),
                           source_label=r["source_label"])
            status = "fresh W4 tail"
        else:
            assert updated == original
            phase_paths = [ROOT / p for p in json.loads(original["candidate_evidence"])]
            status = "reused from published 02de evidence"
        for field in ("before1_us", "before2_us", "baseline_us", "baseline_measured_head", "baseline_production_equivalent_head", "baseline_evidence", "control_spread_percent"):
            assert updated[field] == original[field]
        final.append(updated)
        raw = read(phase_paths[-1])
        rr = next(x for x in raw["rows"] if int(x["tokens"]) == k[3])
        result = next(x for x in rr["results"] if x["backend"] == k[2])
        assert math.isclose(result["latency_ms"] * 1000, float(updated["a2_us"]), abs_tol=1e-9)
        provenance.append(dict(model=k[0], topology=k[1], backend=k[2], tokens=k[3], status=status,
                               phase_paths=[str(p.relative_to(ROOT)) for p in phase_paths], phase_sha256=[sha(p) for p in phase_paths]))
        final_records[k] = result
    assert len(final) == 468 and sum(key(r) not in new for r in final) == 429
    writecsv(HERE / "report/cells.csv", final)
    write(HERE / "report/row-provenance.json", provenance)
    selected = {key(r): r for r in final}
    external_proof = {}
    for topology in ("ep", "tp"):
        source = OLD / "external" / topology / "summary-cells.csv"
        external = rows(source)
        changed = 0
        for r in external:
            k = (r["model"], topology, "CuteDSL W4A16", int(r["tokens"]))
            if r["column"] == "w4a16" and k in new:
                candidate = selected[k]
                r.update(current_ms=float(candidate["candidate_us"]) / 1000,
                         candidate_spread_percent=candidate["candidate_spread_percent"], current_evidence=candidate["candidate_evidence"])
                if r["status"] == "measured":
                    r["speed_percent"] = 100 * (float(r["baseline_ms"]) / float(r["current_ms"]) - 1)
                changed += 1
        for a, b in zip(rows(source), external, strict=True):
            for field in ("model", "tokens", "column", "baseline", "status", "baseline_ms", "reason", "baseline_evidence"):
                assert a[field] == b[field]
        assert changed == (39 if topology == "tp" else 0)
        writecsv(HERE / "external" / topology / "summary-cells.csv", external)
        external_proof[topology] = dict(changed_current_cells=changed, baseline_fields_unchanged=True, original_sha256=sha(source))
    clocks = [q for q in read(OLD / "report/clock-quartiles.json") if not (q["job"] in {r[0]["job"] for r in new.values()} and q["backend"] == "CuteDSL W4A16")]
    resources = [r for r in read(OLD / "report/runtime-resources.json") if r["job"] not in {r[0]["job"] for r in new.values()}]
    for data in DATA:
        label = data.parent.parent.name
        clocks += [dict(q, measurement_campaign=label) for q in read(data.parent / "report/clock-quartiles.json") if q["phase"] in ("1-candidate", "2-candidate")]
        resources += [dict(r, measurement_campaign=label) for r in read(data.parent / "report/runtime-resources.json") if r["phase"] in ("1-candidate", "2-candidate")]
    assert len(clocks) == 3744 and all(r["local_bytes"] == 0 for r in resources)
    write(HERE / "report/clock-quartiles.json", clocks)
    write(HERE / "report/runtime-resources.json", resources)
    stdout = []
    for entry in read(OLD / "stdout/manifest.json"):
        src = OLD / entry["path"]
        dest = HERE / entry["path"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
        assert sha(dest) == entry["sha256"]
        stdout.append(dict(entry, campaign="published-02de"))
    for data in DATA:
        campaign = data.parent.parent.name
        cfg = read(data / "perf-config.json")
        for job in cfg["jobs"]:
            for i, role in enumerate(cfg["phases"]):
                phase = f"{i}-{role}"
                src = data / "results" / job / (phase + ".log")
                dest = HERE / "stdout" / campaign / f"{job}-{phase}.log"
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dest)
                assert sha(src) == sha(dest)
                stdout.append(dict(job=job, phase=phase, source=str(src.relative_to(ROOT)), path=str(dest.relative_to(HERE)), sha256=sha(dest), campaign=campaign, boundary="Original stdout bytes; no table parsing or reconstruction."))
    assert len(stdout) == 86
    write(HERE / "stdout/manifest.json", stdout)
    display = [r for r in final if int(r["tokens"]) >= 4]
    groups = {}
    for name, predicate in (("all", lambda r: True), ("swap_ab", lambda r: r["backend"] != "CuteDSL W4A16"), ("w4a16", lambda r: r["backend"] == "CuteDSL W4A16"), ("decode", lambda r: int(r["tokens"]) <= 64), ("middle", lambda r: 128 <= int(r["tokens"]) <= 512), ("prefill", lambda r: int(r["tokens"]) >= 4096)):
        rr = [r for r in display if predicate(r)]
        groups[name] = dict(cells=len(rr), speedup_percent=gm(rr), negative=sum(float(r["speedup_percent"]) < 0 for r in rr))
    available = [q for q in clocks if q["clock"]["available"]]
    summary = dict(passed=True, source_label=LABEL, retained_head=RETAINED, fresh_measurement_base="02de7785c10847b3528340840bed40bd405d85b4", reused_measurement_base="82254e206a44b95d9925e4594fac936731f80d21", fresh_cells=39, reused_cells=429, total_cells=468, displayed_cells=396, candidate_samples=93600, fresh_candidate_samples=7800, reused_candidate_samples=85800, fresh_causal_samples=15600, candidate_loaded_functions=len(resources), clock_quartiles=3744, missing_clock_quartiles=3744-len(available), clock_exception_quartiles=sum(q["clock"]["sm_mhz"]["median"] != 2032 or any(k != "0" for k in q["clock"]["reasons"]) for q in available), all_negative_rows_retained=True, groups=groups, causal_39=peer, external=external_proof, boundary="39 fresh W4 cells plus 429 reused source-equivalent specializations/paths. Historical full and external baselines unchanged. Not a fresh paired 468-cell comparison; Qualified measured base02de plus patch is source-equivalent to retained bf072d26.")
    write(HERE / "report/summary.json", summary)
    write(HERE / "source-reuse-proof.json", dict(passed=True, retained_head=RETAINED, source_label=LABEL, source_hashes=read(ROOT / "experiments/w4-tail-dequant/qualification-summary.json")["source_hashes"], coverage_proof_sha256=sha(ROOT / "experiments/w4-tail-dequant/publication-plan/coverage-proof.json"), previous_manifest_sha256=sha(OLD / "manifest.json"), peer_sha256=sha(ROOT / "audits/w4-tail-combined-data-peer.json"), fresh=39, reused=429, exact_existing_fields_preserved_for_all_429=True, existing_baseline_fields_preserved=True))
    write(HERE / "manifest.json", dict(passed=True, assemble_sha256=sha(__file__), report_sha256=sha(HERE / "report/cells.csv"), summary_sha256=sha(HERE / "report/summary.json"), stdout_manifest_sha256=sha(HERE / "stdout/manifest.json"), published_tree_hashes=old_hashes))
    assert old_hashes == {name: sha(OLD / name) for name in old_hashes}
    print(json.dumps({k: summary[k] for k in ("fresh_cells", "reused_cells", "total_cells", "candidate_loaded_functions", "clock_exception_quartiles", "missing_clock_quartiles", "groups")}, indent=2))


if __name__ == "__main__":
    main()
