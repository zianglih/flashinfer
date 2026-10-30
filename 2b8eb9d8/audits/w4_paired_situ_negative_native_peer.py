"""Independent local replay of the frozen negative-tactic native capture."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "experiments/w4-paired-situ/negative-native-r2"
DATA = BASE / "evidence"
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
load = lambda p: json.loads(Path(p).read_text())
manifest = load(DATA / "fetch-manifest.json")
for name, digest in manifest.items():
    assert sha(DATA / name) == digest, name
fetch = load(BASE / "fetch-receipt.json")
assert fetch["passed"] and sha(BASE / "evidence.tar.gz") == fetch["archive_sha256"]
receipt = load(DATA / "receipt.json")
assert receipt["passed"] and receipt["complete"] and len(receipt["runs"]) == 4
assert receipt["full_source_preflight"] and receipt["full_source_postflight"]
config_path = ROOT / "evidence/w4-paired-situ-screen/1793379864881706000/data/perf-config.json"
config = load(config_path)
assert sha(config_path) == receipt["config_sha256"]
for name, digest in receipt["helpers"].items():
    assert sha(DATA / name) == digest
summary = load(BASE / "native-summary.json")
rows = []
for tokens in (16, 32):
    expected = load(DATA / f"expected-{tokens}.json")
    arms = {}
    for role in ("control", "candidate"):
        directory = DATA / f"{role}-{tokens}"
        run = load(directory / "receipt.json")
        assert run["returncode"] == 0 and run["source"] == config["sources"][role]
        selection = load(directory / "selection.json")
        assert selection["complete"]
        assert selection["selections"] == expected["selections"]
        assert selection["routes"] == [expected["routing_identity"]]
        actual = [{k: v for k, v in x.items() if k != "compiled_library"} for x in selection["w4_resolution"]["w4_resolved_configs"]]
        assert actual == expected["resolved_configs"]
        guards = load(next((directory / "register-guard").glob("*/receipt.json")))
        assert guards["all_guarded"] and guards["exitstatus"] == 0 and not guards["compiler_options_changed"]
        path = next((directory / "loaded-codegen").glob("*/receipt.json"))
        captures = load(path)
        assert [x["stage"] for x in captures] == ["fc1", "fc2", "combine"]
        for index, capture in enumerate(captures):
            assert capture["loaded_resources"]["local_bytes"] == 0
            for ext in ("ptx", "cubin", "sass"):
                assert sha(path.parent / (capture["stage"] + "." + ext)) == capture[ext + "_sha256"]
            if index < 2:
                guard = guards["compilations"][index]
                assert guard["passed"] and all(guard["checks"].values())
                assert guard["analysis"] == capture["loaded_resources"]
                assert guard["compile_options"] == capture["compile_options"]
                assert {k: guard[k] for k in capture["configuration"]} == capture["configuration"]
        arms[role] = (path.parent, captures)
    for index, stage in enumerate(("fc1", "fc2", "combine")):
        c, a = (arms[role][1][index] for role in ("control", "candidate"))
        assert c["loaded_resources"] == a["loaded_resources"]
        assert c["configuration"] == a["configuration"] and c["compile_options"] == a["compile_options"]
        counts = {}
        for role in arms:
            sass = (arms[role][0] / (stage + ".sass")).read_text()
            counts[role] = Counter(re.findall(r"/\*[0-9a-fA-F]+\*/\s+(?:@!?P\w+\s+)?([A-Za-z][\w.]*)(?=[\s;])", sass))
            assert counts[role]["LDL"] == counts[role]["STL"] == 0
        delta = {op: counts["candidate"][op] - counts["control"][op] for op in counts["candidate"].keys() | counts["control"].keys() if counts["candidate"][op] != counts["control"][op]}
        if stage == "fc1":
            assert set(delta) <= {"FADD", "FADD2", "FMUL", "FMUL2", "NOP"}
            assert not counts["candidate"]["FFMA"] and not counts["candidate"]["FFMA2"]
            ptx = {role: (arms[role][0] / "fc1.ptx").read_text() for role in arms}
            sfus = {role: Counter(re.findall(r"\b((?:ex2|rcp)\.[\w.]+)\s", text)) for role, text in ptx.items()}
            assert sfus["control"] == sfus["candidate"]
            assert "mul.rn.f32x2" in ptx["candidate"] and "sub.rn.f32x2" in ptx["candidate"]
        else:
            assert all(c[x + "_sha256"] == a[x + "_sha256"] for x in ("ptx", "cubin", "sass"))
        non_nop_delta = sum(delta.values()) - delta.get("NOP", 0)
        reported = next(x for x in summary["rows"] if x["tokens"] == tokens and x["stage"] == stage)
        assert delta == reported["opcode_delta"]
        assert non_nop_delta == reported["non_nop"]["candidate"] - reported["non_nop"]["control"]
        rows.append({"tokens": tokens, "stage": stage, "resources": c["loaded_resources"], "non_nop_delta": non_nop_delta, "raw_cubin_equal": c["cubin_sha256"] == a["cubin_sha256"]})

repeat_path = ROOT / "experiments/w4-paired-situ/acca-screen/perf-config.json"
repeat = load(repeat_path)
allowed = {"boundary", "label", "output", "phases", "jobs", "sources"}
assert {k:v for k,v in repeat.items() if k not in allowed} == {k:v for k,v in config.items() if k not in allowed}
for role in repeat["sources"]:
    source = repeat["sources"][role]
    old_source = config["sources"][role]
    assert {k:v for k,v in source.items() if k not in ("source_file", "tracked_manifest")} == {k:v for k,v in old_source.items() if k not in ("source_file", "tracked_manifest")}
    for key in ("source_file", "tracked_manifest"):
        assert source[key] == old_source[key].replace("/runs/w4-paired-situ-screen/", "/runs/w4-paired-situ-acca/")
assert repeat["phases"] == ["candidate", "control", "control", "candidate"]
for name, job in repeat["jobs"].items():
    assert {k:v for k,v in job.items() if k not in ("tokens", "expected_cells")} == {k:v for k,v in config["jobs"][name].items() if k not in ("tokens", "expected_cells")}
    assert set(job["tokens"]) <= set(config["jobs"][name]["tokens"])
assert sum(x["expected_cells"] for x in repeat["jobs"].values()) == 6
result = {"passed": True, "candidate_sha256": "5e61d04544524410b273b8e49ee2b8f6d9e20266c22346aba06ab3743c2c4e1d", "native_summary_sha256": sha(BASE / "native-summary.json"), "receipt_sha256": sha(DATA / "receipt.json"), "archive_sha256": fetch["archive_sha256"], "files_verified": len(manifest), "native_pairs": 6, "rows": rows, "acca_config_sha256": sha(repeat_path), "same_sources_cache_helpers_tactics_routes": True, "boundary": "Source/resource/codegen proof only. FC1 scalar-to-packed arithmetic changes local epilogue scheduling; four FC2/finalizer pairs are raw-identical. No claim that unchanged counts imply identical instruction order, or that routing-span variation explains kernel performance. ACCA data remains separate from original CAAC.", "peer_script_sha256": sha(__file__)}
(ROOT / "audits/w4-paired-situ-negative-native-peer.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({k:v for k,v in result.items() if k != "rows"}, indent=2))
