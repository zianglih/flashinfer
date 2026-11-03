"""Check publication inputs already available; no GPU or network work."""
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HEAD = "2b4732791a3ce48bc3ae6c030a283fab73854e0e"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    name = HERE / "completed-tables/render_comments.py"
    spec = importlib.util.spec_from_file_location("table_printer", name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    ns = module.printer()
    index = HERE / "completed-tables/baseline-index.json"
    assert sha(index) == "51ce4db4f9beac023ba3eb6c0755c585a294cddded3948875dcd8745d6db6284"
    sources = {}
    for group in json.loads(index.read_text())["groups"]:
        for key in ("source", "bf16_source"):
            if group.get(key):
                p = module.OLD_PROJECT / group[key]
                assert sha(p) == group[key + "_sha256"]
                sources[str(p)] = sha(p)
    external = {}
    for topology, expected in [("ep", "01bed08308cb6da4c66648535eb9699a39523c1ed8f67333b4945e002d5270fe"),
                               ("tp", "f5be713170238a13a3f0f4c89dc16ac099ed3d75a08bd45aac6a0443e7d5d6ad")]:
        p = ROOT / f"harness/historical/external/{topology}/summary-cells.csv"
        assert sha(p) == expected
        external[topology] = expected
    current = subprocess.check_output(["git", "-C", str(ROOT / "flashinfer"), "show", f"{HEAD}:{module.BENCH}"])
    previous = subprocess.check_output(["git", "-C", str(ROOT / "flashinfer"), "show", f"a620ce779:{module.BENCH}"])
    assert current == previous
    # Exercise every table layout with verified old structured rows; no ASCII parsing.
    manifest = json.loads((ROOT / "publication-pr7290-a620/completed-tables/manifest.json").read_text())
    reproduced = []
    for group in manifest["groups"]:
        if group.get("skipped"):
            continue
        cfg = ns["MODEL_CONFIGS"][group["model"]]
        ep, tp = (cfg.default_ep, 1) if group["topology"] == "ep" else (1, cfg.default_ep)
        text = module.render(ns, group["model"], ep, tp, group["family"], group["rows"])
        assert hashlib.sha256(text.encode()).hexdigest() == group["table_sha256"]
        reproduced.append(group["table"])
    result = dict(passed=True, head=HEAD, benchmark_unchanged_from_retained=True,
        benchmark_sha256=hashlib.sha256(current).hexdigest(), baseline_index_sha256=sha(index),
        historical_source_files=sources, external_baseline_sha256=external,
        prior_completed_tables_reproduced=reproduced, fresh_campaign_verified=False,
        boundary="Preparation only: historical baseline files and unchanged native table printer verified. Fresh source, timing, caches, routes, clocks and plots require completed CAAC evidence.")
    (HERE / "preflight.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("passed", "head", "benchmark_unchanged_from_retained", "fresh_campaign_verified")}))


if __name__ == "__main__":
    main()
