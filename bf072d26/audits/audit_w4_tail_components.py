"""Independent source, loaded-resource and timeline joins; no GPU execution."""
import csv
import hashlib
import json
import math
import statistics
from pathlib import Path

P = Path(__file__).resolve().parents[1]
R = P / "evidence/w4-tail-dequant-screen/1793368574438182000"
D = R / "data"
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
same = lambda a, b: math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-8)
cfg = read(D / "perf-config.json")
qual_path = P / "experiments/w4-tail-dequant/qualification-summary.json"
qual = read(qual_path)
assert qual["passed"]
assert qual["source_manifests"] == {
    role: source["freeze_receipt_sha256"] for role, source in cfg["sources"].items()
}
for path, digest in qual["source_hashes"].items():
    assert cfg["sources"]["candidate"]["source_sha256"][path] == digest
    assert sha(P / "flashinfer-w4-tail-dequant-review" / path) == digest
for path, digest in qual["receipts"].items():
    assert sha(P / path) == digest
inventories = {
    role: read(D / Path(s["tracked_manifest"]).name)
    for role, s in cfg["sources"].items()
}
assert inventories["control"].keys() == inventories["candidate"].keys()
changed = sorted(k for k in inventories["control"] if inventories["control"][k] != inventories["candidate"][k])
assert changed == sorted(qual["source_hashes"])
phases = {}
resources = {}
for job in cfg["jobs"]:
    folder = D / "results" / job
    receipt = read(folder / "receipt.json")
    analysis = read(folder / "analysis.json")
    for phase in receipt["phases"]:
        label = f"{phase['index']}-{phase['role']}"
        libraries = {}
        for entry in phase["register_guards"]:
            path = folder / Path(entry["path"]).relative_to(Path(cfg["output"]) / job)
            assert sha(path) == entry["sha256"]
            for compiled in read(path)["compilations"]:
                libraries[compiled["library_handle"]] = compiled
        raw = read(folder / label / "results.json")
        measurements = iter(raw["native_diagnostic"]["measurements"])
        for row in raw["rows"]:
            for result in row["results"]:
                measurement = next(measurements)
                for resolved in measurement["w4_resolved_configs"]:
                    fn = libraries[resolved["compiled_library"]]
                    record = dict(fn["analysis"])
                    for name in ("gather_input", "mma_tiler_mnk", "cluster_shape_mn", "raster_along_m", "use_clc_scheduler", "enable_pdl", "compile_options"):
                        record[name] = fn[name]
                    resources.setdefault((job, row["tokens"], resolved["stage"]), {})[label] = record
                samples = []
                for begin, end in measurement["iter_timestamps"]:
                    ids = {entry[2] for entry in measurement["launches"] if begin <= entry[0] <= end}
                    kernels = sorted((entry for entry in measurement["activities"] if entry[3] in ids), key=lambda entry: entry[1])
                    frontier = kernels[0][1]
                    values = {}
                    fc = 0
                    for kernel in kernels:
                        if "Sm100W4A16GroupedGemmKernel" in kernel[0]:
                            fc += 1
                            name = f"fc{fc}"
                        elif "MoeFinalizeKernel" in kernel[0]:
                            name = "combine"
                        else:
                            name = None
                        if name:
                            values[name + "_us"] = (kernel[2] - kernel[1]) / 1000
                            values[name + "_extension_us"] = max(0, kernel[2] - max(frontier, kernel[1])) / 1000
                        frontier = max(frontier, kernel[2])
                    assert fc == 2
                    samples.append(values)
                measured = {key: statistics.median(s[key] for s in samples) for key in samples[0]}
                expected = next(x for x in analysis["phases"] if x["phase"] == label and x["tokens"] == row["tokens"] and x["backend"] == result["backend"])
                assert all(same(value, expected["medians"][key]) for key, value in measured.items())
                phases[(job, row["tokens"], label)] = measured
        assert next(measurements, None) is None
assert len(resources) == 24 and len(phases) == 48
for key, values in resources.items():
    assert len(values) == 4 and all(x == values["0-control"] for x in values.values()), key
assert all(row["resources_unchanged"] for row in read(R / "report/resource-deltas.json")["rows"])
components = list(csv.DictReader((R / "report/component-deltas.csv").open()))
for row in components:
    key = (row["job"], int(row["tokens"]))
    for metric in phases[(*key, "0-control")]:
        control = statistics.mean(phases[(*key, label)][metric] for label in ("0-control", "3-control"))
        candidate = statistics.mean(phases[(*key, label)][metric] for label in ("1-candidate", "2-candidate"))
        assert same(float(row["control_" + metric]), control)
        assert same(float(row["candidate_" + metric]), candidate)
        assert same(float(row["delta_" + metric]), candidate - control)
result = {
    "passed": True,
    "source_files_changed": changed,
    "qualification_sha256": sha(qual_path),
    "config_sha256": sha(D / "perf-config.json"),
    "raw_audit_sha256": sha(P / "audits/w4-tail-data-peer.json"),
    "resource_report_sha256": sha(R / "report/resource-deltas.json"),
    "component_report_sha256": sha(R / "report/component-deltas.csv"),
    "all_24_cell_stage_resources_and_compile_configs_equal_in_four_phases": True,
    "component_medians_replayed": len(phases) * 6,
    "component_deltas_replayed": len(components) * 6,
    "boundary": "Resources are actual driver attributes plus source-bound native compile configuration, not exact timed native cubin identity. Timeline extensions account for overlapping kernels; separate component medians need not sum to the E2E median. No samples removed or new timings run.",
}
(P / "audits/w4-tail-components-peer.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
