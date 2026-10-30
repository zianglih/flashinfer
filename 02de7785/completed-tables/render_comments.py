"""Run the benchmark's unchanged table printer on saved candidate/TRTLLM rows."""

import ast
import contextlib
from dataclasses import dataclass, replace
import hashlib
import io
import json
from pathlib import Path
import re
import struct
import subprocess

HERE = Path(__file__).resolve().parent
PERF = HERE.parent
PROJECT = PERF.parent
OLD_PROJECT = Path("/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n")
DATA = [PROJECT / "evidence/composed-swap-full/1793363709386584000/data",
        PROJECT / "evidence/r2-w4-full/1793362889737047000/data"]
REPO = PROJECT / "flashinfer"
HEAD = "02de7785c10847b3528340840bed40bd405d85b4"
BENCH = "benchmarks/bench_moe_deepseek.py"
TOKENS = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 4096, 8192, 16384]
MODELS = [("v3", "V3", 8), ("v41-flash", "V41F", 4),
          ("kimi-k3", "K3", 8), ("nemo3-ultra", "N3U", 8)]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(path.read_text())


def printer():
    source = subprocess.check_output(["git", "-C", str(REPO), "show", f"{HEAD}:{BENCH}"])
    assert sha(source) == "84855eed2a84d4147488144db3b08830fa696e3ce4306ec4fa8b3cbd0724585e"
    names = {"DeepSeekConfig", "BenchResult", "_backend_skip_reason", "_table_layout",
             "_print_header", "_print_row", "_print_footer"}
    nodes = []
    for node in ast.parse(source).body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names:
            nodes.append(node)
        elif isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "MODEL_CONFIGS" for t in node.targets):
            nodes.append(node)
    namespace = dict(dataclass=dataclass, DEFAULT_SWIGLU_LIMIT=struct.unpack(">f", bytes.fromhex("7f7fffff"))[0])
    exec(compile(ast.Module(body=nodes, type_ignores=[]), BENCH, "exec"), namespace)
    return namespace


def render(ns, model, ep, tp, family, rows):
    ns["CFG"] = replace(ns["MODEL_CONFIGS"][model])
    ns["CFG"].intermediate_size //= tp
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        ns["_print_header"](ep, tp, ns["CFG"].num_experts // ep, True, True, 0.01,
                             include_activation_quant=family == "nvfp4",
                             use_fused_finalize=False, quant_family=family, swap_ab=True)
        for row in rows:
            ns["_print_row"]([ns["BenchResult"](**c) for c in row["results"]],
                             row["histogram"], row["tokens"], quant_family=family)
        ns["_print_footer"](family)
    return output.getvalue()


def main():
    ns = printer()
    config = {"jobs": {}}
    job_roots = {}
    for data_root in DATA:
        source_config = read(data_root / "perf-config.json")
        for job_name, job in source_config["jobs"].items():
            assert job_name not in config["jobs"]
            config["jobs"][job_name] = job
            job_roots[job_name] = data_root
    equivalence = read(PERF / "retained-source-equivalence.json")
    assert equivalence["passed"] and equivalence["retained_head"] == HEAD
    assert read(HERE / "formatter-source-proof.json")["printer_AST_identical_to326"]
    baselines = read(HERE / "baseline-index.json")
    assert baselines["passed"] and baselines["candidate_measured_head"] == "326c4a793085e79b64b9c7fd79e77320c220ccba"
    baseline_index = {(g["topology"], g["model"], g["family"]): g for g in baselines["groups"]}
    candidates, sources, original_proof = {}, {}, []
    for name, job in config["jobs"].items():
        path = job_roots[name] / "results" / name / "1-candidate/results.json"
        data = read(path)
        assert data["complete"] and data["exit_code"] == 0
        relative = str(path.relative_to(PROJECT))
        sources[relative] = sha(path.read_bytes())
        text = render(ns, job["model"], job["ep"], job["tp"], job["family"], data["rows"])
        original = (PERF / "stdout" / f"{name}-1-candidate.log").read_bytes()
        match = re.search(rb"(?m)^=+\n(?=[^\n]*MoE Benchmark:)", original)
        assert match and text.encode() == b"\n" + original[match.start():], name
        original_proof.append(dict(job=name, table_sha256=sha(text.encode())))
        topology = "tp" if job["tp"] > 1 else "ep"
        for row in data["rows"]:
            assert all(c["tokens"] == row["tokens"] for c in row["results"])
            key = topology, job["model"], job["family"], row["tokens"]
            output = candidates.setdefault(key, dict(tokens=row["tokens"], histogram=row["histogram"],
                                                       routing_identity=row["routing_identity"], results=[], origins=[]))
            assert output["histogram"] == row["histogram"]
            assert output["routing_identity"] == row["routing_identity"]
            output["results"].extend(row["results"])
            output["origins"].extend(dict(backend=c["backend"], source=relative) for c in row["results"])
    assert len(original_proof) == 31
    tables, groups, counts = {}, [], {"fresh": 0, "reused": 0}
    for topology in ("ep", "tp"):
        for model, label, parallel in MODELS:
            ep, tp = (parallel, 1) if topology == "ep" else (1, parallel)
            for family in ("nvfp4", "mxfp"):
                key = topology, model, family
                baseline = baseline_index[key]
                rows = [candidates[*key, token] for token in TOKENS if (*key, token) in candidates]
                if not rows:
                    assert key == ("tp", "v41-flash", "mxfp")
                    groups.append(dict(topology=topology, model=model, family=family, skipped=True))
                    continue
                assert len(rows) == 13
                inputs = []
                if baseline["source"]:
                    inputs.append((baseline["source"], baseline["backends"]))
                if baseline.get("bf16_source"):
                    inputs.append((baseline["bf16_source"], ["TRTLLM BF16"]))
                for relative, labels in inputs:
                    path = OLD_PROJECT / relative
                    data = read(path)
                    assert data["complete"] and data.get("exit_code", 0) == 0
                    expected_sha = baseline["bf16_source_sha256"] if labels == ["TRTLLM BF16"] else baseline["source_sha256"]
                    assert sha(path.read_bytes()) == expected_sha
                    argv = data["benchmark_argv"]
                    option = lambda flag, default: argv[argv.index(flag) + 1] if flag in argv else default
                    assert option("--model", "v3") == model
                    assert int(option("--ep", ns["MODEL_CONFIGS"][model].default_ep)) == ep
                    assert int(option("--tp", 1)) == tp
                    assert "--num-experts" not in argv
                    sources["historical:" + relative] = sha(path.read_bytes())
                    old_rows = {r["tokens"]: r for r in data["rows"]}
                    for row in rows:
                        old = old_rows[row["tokens"]]
                        if "routing_identity" in old:
                            assert old["routing_identity"] == row["routing_identity"], (key, row["tokens"], relative)
                        assert old["histogram"] == row["histogram"], (key, row["tokens"], relative)
                        selected = [c for c in old["results"] if c["backend"] in labels]
                        assert {c["backend"] for c in selected} == set(labels)
                        assert all(c["tokens"] == row["tokens"] for c in selected)
                        if labels != ["TRTLLM BF16"]:
                            assert old["include_activation_quant"] == (family == "nvfp4")
                        row["results"].extend(selected)
                        row["origins"].extend(dict(backend=c["backend"], source="historical:" + relative) for c in selected)
                for row in rows:
                    assert len({c["backend"] for c in row["results"]}) == len(row["results"])
                    counts["fresh"] += sum(c["backend"].startswith("CuteDSL") for c in row["results"])
                    counts["reused"] += sum(c["backend"].startswith("TRTLLM") for c in row["results"])
                text = render(ns, model, ep, tp, family, rows)
                filename = f"{topology}-{model}-{family}.txt"
                (HERE / filename).write_text(text)
                tables[key] = text
                groups.append(dict(topology=topology, model=model, family=family, table=filename,
                                   table_sha256=sha(text.encode()), rows=rows))
    assert counts == {"fresh": 468, "reused": 390}
    archive = "https://github.com/zianglih/flashinfer/raw/refs/heads/codex/moe-gather-pipeline-assets/02de7785/moe-gather-pipeline-results.tar.gz"
    comments = []
    for part, (topology, model_slice) in enumerate((("ep", MODELS[:2]), ("ep", MODELS[2:]),
                                                   ("tp", MODELS[:2]), ("tp", MODELS[2:])), 1):
        label = " / ".join(f"{label} {topology.upper()}{parallel}" for _, label, parallel in model_slice)
        body = (f"<!-- moe-gather-pipeline-completed-tables-{HEAD[:8]}-part-{part} -->\n"
                f"### Benchmark table output — {label} ({part}/4)\n\n"
                "Printed by the unchanged benchmark table functions from saved records: "
                f"fresh CuTe DSL final-pass results source-equivalent to `{HEAD[:8]}` plus the original TRTLLM final-pass results. "
                "TRTLLM is reused, not rerun; these are separate-run comparisons. "
                "The original measurement records retain their actual base `82254e20` plus frozen patch identifiers. "
                "The heatmaps use two-pass aggregates. Missing or unsupported records remain N/A. "
                f"[Original fresh-run logs]({archive}).\n\n")
        if part == 1:
            body += ("BF16 reuses the original `f7182d5c` measurements: the logs report CUPTI and CUDA Graphs, "
                     "but these older records predate the per-record strict timing guards.\n\n")
        for model, model_label, parallel in model_slice:
            for family in ("nvfp4", "mxfp"):
                key = topology, model, family
                body += f"**{model_label} {topology.upper()}{parallel} · {family.upper()}**\n\n"
                if key not in tables:
                    body += "Not run: no supported baseline comparison.\n\n"
                    continue
                body += "```text\n" + tables[key] + "```\n\n"
        assert len(body.encode()) < 65536
        path = HERE / f"part-{part}.md"
        path.write_text(body)
        comments.append(dict(part=part, label=label, path=path.name, bytes=len(body.encode()), sha256=sha(body.encode())))
    output = dict(passed=True, retained_head=HEAD, actual_measurement_base=equivalence["actual_measurement_base"],
        source_equivalence_sha256=sha((PERF/"retained-source-equivalence.json").read_bytes()),
        historical_project=str(OLD_PROJECT), historical_index_sha256=sha((HERE/"baseline-index.json").read_bytes()), formatter_source_sha256=sha(subprocess.check_output(
        ["git", "-C", str(REPO), "show", f"{HEAD}:{BENCH}"])), original_outputs_reproduced=original_proof,
        sources=sources, groups=groups, counts=counts, comments=comments)
    (HERE / "manifest.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(dict(original_outputs_reproduced=31, tables=len(tables), counts=counts,
                         comment_bytes=[c["bytes"] for c in comments])))


if __name__ == "__main__":
    main()
