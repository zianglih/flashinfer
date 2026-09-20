"""Assemble a local, portable r5 publication candidate from FINAL evidence only."""

import argparse
import itertools
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import unquote

from summarize_calibration import load_evidence, sha256


PROJECT = Path(__file__).resolve().parents[1]
RUN_ID = "glm52-calibration-20260920-r5"
BENCHMARK = "bd8391858db504c8997e704c7952f4d48ccab591"
PLOT_SHA = "1d1d5537ff2141d5703553de2d99f892b9926fe9677019482b48b300c3c2ac97"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    return json.loads(Path(path).read_text())


def file_record(path):
    return {"size": path.stat().st_size, "sha256": sha256(path)}


def safe_file(root, relative):
    relative = Path(relative)
    require(
        not relative.is_absolute() and ".." not in relative.parts,
        "Unsafe relative path",
    )
    path = root / relative
    require(
        path.is_file() and not any(p.is_symlink() for p in [path, *path.parents]),
        f"Missing or linked file: {path}",
    )
    return path


def verify_receipt(root, count=None):
    receipt = read_json(root / "verification.json")
    require(receipt.get("verified") is True, "Unverified transfer")
    paths = [r["path"] for r in receipt["files"]]
    require(len(paths) == len(set(paths)), "Duplicate receipt member")
    if count is not None:
        require(len(paths) == count, "Wrong receipt payload count")
    for record in receipt["files"]:
        require(
            file_record(safe_file(root, record["path"]))
            == {k: record[k] for k in ("size", "sha256")},
            "Receipt payload changed",
        )
    return receipt


def preflight(args):
    """Reject partial runs before creating a destination or importing plotting."""
    require(not args.output.exists(), "Output already exists")
    for source in (
        args.transfer,
        args.dispatch,
        args.environment,
        args.component_gate,
        args.source,
    ):
        require(
            not args.output.is_relative_to(source),
            "Output cannot be nested in an input tree",
        )
    summary, files = load_evidence(args.transfer, args.dispatch, allow_partial=False)
    require(
        summary["status"] == "FINAL" and summary["run_id"] == RUN_ID,
        "Only the complete r5 run is supported",
    )
    require(
        summary["provenance"]["source"]["benchmark_commit"] == BENCHMARK
        and summary["refcheck_policy"] == "per-path",
        "Wrong source or acceptance policy",
    )
    require(len(summary["performance_groups"]) == 110, "Incomplete paired matrix")
    require(
        sha256(PROJECT / "setup/plot_calibration_core.py") == PLOT_SHA,
        "Plot helper is not the independently accepted version",
    )
    source_hashes, proof_names = verify_supporting_evidence(args, summary, files)
    return summary, source_hashes, proof_names


def verify_supporting_evidence(args, summary, files):
    """Verify existing supporting receipts without creating or promoting a run."""
    env = verify_receipt(args.environment, 12)
    require(
        env["devbox"] == "fi-sglang-align-0920"
        and env["cluster"] == "c2"
        and env["namespace"] == "ziangli",
        "Wrong environment node",
    )
    for relative, digest in summary["provenance"]["environment_sha256"].items():
        require(
            sha256(safe_file(args.environment, "environment/" + relative)) == digest,
            "Environment differs from run seal",
        )
    gate = read_json(args.component_gate / "verification.json")
    exit_record = read_json(args.component_gate / "exit.json")
    require(
        gate["record"] == exit_record
        and exit_record["passed"] is True
        and exit_record["exit_code"] == 0
        and exit_record["expected_tests"] == 12
        and exit_record["skips_permitted"] is False
        and exit_record["source_unchanged"] is True
        and exit_record["runtime_unchanged"] is True
        and not exit_record["errors"],
        "Actual 12-test component gate did not pass",
    )
    for record in gate["files"]:
        require(
            file_record(safe_file(args.component_gate, record["name"]))
            == {"sha256": record["sha256"], "size": record["bytes"]},
            "Component gate payload changed",
        )
    stderr = (args.component_gate / "stderr.log").read_text()
    require(
        "Ran 12 tests" in stderr
        and stderr.rstrip().endswith("OK")
        and "skipped" not in stderr.lower(),
        "Component test count/skip mismatch",
    )
    invocation = read_json(args.component_gate / "invocation.json")
    require(
        invocation["commit"] == BENCHMARK and invocation["timing_stage"] == "timing-r5",
        "Component source differs",
    )
    source_hashes = {
        **summary["provenance"]["source"]["benchmark_sha256"],
        **invocation["source_sha256"],
    }
    for relative, digest in source_hashes.items():
        require(
            sha256(safe_file(args.source, relative)) == digest,
            "Local source differs from tested bytes",
        )

    proof_names = set()
    for name in ("r5-prelaunch", "r5-full-correctness", "r5-full-core"):
        review_path = args.proofs / f"{name}-independent-review.json"
        review = read_json(review_path)
        acceptance = read_json(args.proofs / f"{name}-parent-acceptance.json")
        require(
            review["status"] == "passed" and review["issue_count"] == 0,
            f"Unaccepted proof: {name}",
        )
        if name == "r5-full-core":
            require(
                acceptance["accepted"] is True
                and acceptance["issue_count"] == 0
                and acceptance["review_sha256"] == sha256(review_path),
                "Parent/core review SHA differs",
            )
        elif name == "r5-full-correctness":
            require(
                acceptance["status"] == "accepted"
                and acceptance["independent_review_sha256"] == sha256(review_path),
                "Parent/correctness review SHA differs",
            )
        else:
            require(
                acceptance["gpu_test_count"] == 12
                and acceptance["gpu_test_skips"] == 0
                and not acceptance["issues"]
                and acceptance["runtime_identity_validated_by_driver"] is True,
                "Prelaunch acceptance differs",
            )
            require(
                review["source_commit"] == BENCHMARK and review["run_id"] == RUN_ID,
                "Prelaunch review identity differs",
            )
        proof_names.update(
            (f"{name}-independent-review.json", f"{name}-parent-acceptance.json")
        )
    core = read_json(args.proofs / "r5-full-core-independent-review.json")
    require(
        core["source"] == summary["provenance"]["source"] and core["group_count"] == 84,
        "Core review does not bind this run/source",
    )
    for relative, record in core["bound_raw_files"].items():
        require(
            files[relative] == record, "Reviewed core bytes differ from final evidence"
        )
    correctness = read_json(args.proofs / "r5-full-correctness-independent-review.json")
    for relative, digest in correctness["raw_file_sha256"].items():
        require(
            files[relative]["sha256"] == digest,
            "Reviewed correctness bytes differ from final evidence",
        )
    for name, digest in core["reused_review_sha256"].items():
        require(
            sha256(safe_file(args.proofs, name)) == digest, "Reused core review changed"
        )
        proof_names.add(name)
    coverage = read_json(args.proofs / "serving-autotune-coverage-review.json")
    coverage_acceptance = read_json(
        args.proofs / "serving-autotune-coverage-parent-acceptance.json"
    )
    require(
        coverage["review_status"] == "passed"
        and coverage["issue_count"] == 0
        and coverage_acceptance["status"]
        == "source_and_actual_log_coverage_review_accepted"
        and coverage_acceptance["review_sha256"]
        == sha256(args.proofs / "serving-autotune-coverage-review.json"),
        "Autotune coverage review is unaccepted",
    )
    proof_names.update(
        (
            "serving-autotune-coverage-review.json",
            "serving-autotune-coverage-review.md",
            "serving-autotune-coverage-parent-acceptance.json",
        )
    )
    return source_hashes, sorted(proof_names)


def copy_file(source, target, output, copies):
    require(
        source.is_file() and not any(p.is_symlink() for p in [source, *source.parents]),
        "Linked or special source",
    )
    before = file_record(source)
    target.parent.mkdir(parents=True, exist_ok=True)
    with source.open("rb") as src, target.open("xb") as dst:
        shutil.copyfileobj(src, dst)
    require(
        file_record(target) == before == file_record(source),
        f"Copy/source bytes changed: {source}",
    )
    copies[target.relative_to(output).as_posix()] = {
        **before,
        "original_source": str(source),
    }


def copy_tree(source, target, output, copies):
    require(source.is_dir() and not source.is_symlink(), "Invalid source tree")
    for path in sorted(source.rglob("*")):
        require(not path.is_symlink(), f"Linked tree member: {path}")
        if path.is_dir():
            continue
        require(path.is_file(), "Special tree member")
        copy_file(path, target / path.relative_to(source), output, copies)


def run_tool(output, name, argv):
    result = subprocess.run(
        [sys.executable, "-B", *map(str, argv)], cwd=output, capture_output=True
    )
    (output / "assembly" / f"{name}.stdout").write_bytes(result.stdout)
    (output / "assembly" / f"{name}.stderr").write_bytes(result.stderr)
    require(
        result.returncode == 0,
        f"Copied {name} failed; preserve output and inspect assembly logs",
    )


def distributions(rows):
    result = []
    for phase, ep, comm in itertools.product(
        ("core", "auto", "routing", "prefill"),
        (4, 8),
        ("alltoall", "allgather", "allreduce"),
    ):
        group = [
            r
            for r in rows
            if (r["phase"], r["ep"], r["communication"]) == (phase, ep, comm)
        ]
        if not group:
            continue
        changes = [r["pooled"]["mega_latency_change_percent"] for r in group]
        reversals = sum(
            r["repeats"][0]["mega_latency_change_percent"]
            * r["repeats"][1]["mega_latency_change_percent"]
            < 0
            for r in group
        )
        result.append(
            dict(
                phase=phase,
                ep=ep,
                communication=comm,
                groups=len(group),
                lower=sum(v < 0 for v in changes),
                higher=sum(v > 0 for v in changes),
                equal=sum(v == 0 for v in changes),
                minimum_percent=min(changes),
                maximum_percent=max(changes),
                repeat_sign_reversals=reversals,
            )
        )
    return result


def write_reports(output, summary, proof_names):
    rows = summary["performance_groups"]
    dist = distributions(rows)
    defaults = {
        (r["ep"], r["communication"], r["capacity"], r["tokens"]): r
        for r in rows
        if r["phase"] == "core"
    }
    controls = []
    for row in rows:
        if row["phase"] not in ("auto", "routing"):
            continue
        baseline = defaults[
            (row["ep"], row["communication"], row["capacity"], row["tokens"])
        ]
        controls.append(
            {
                **{
                    k: row[k]
                    for k in ("phase", "ep", "communication", "capacity", "tokens")
                },
                "mega_change_from_default_percent": 100
                * (row["pooled"]["mega_us"] / baseline["pooled"]["mega_us"] - 1),
                "split_control_change_from_default_percent": 100
                * (row["pooled"]["split_us"] / baseline["pooled"]["split_us"] - 1),
            }
        )
    (output / "analysis-values.json").write_text(
        json.dumps(
            dict(
                run_id=summary["run_id"],
                status="SYNTHETIC_NOT_MEASURED"
                if summary.get("synthetic")
                else "FINAL",
                group_distributions=dist,
                matching_default_controls=controls,
                equivalence_claim=False,
            ),
            indent=2,
        )
        + "\n"
    )
    provenance = summary["provenance"]
    versions = provenance["runtime"]["versions"]
    native = summary["cross_pair_diagnostics"]["status_counts"]
    run_relative = f"evidence/runs/{RUN_ID}"
    for zh in (False, True):
        filename = "README_zh.md" if zh else "README.md"
        switch = "[English](README.md)" if zh else "[中文](README_zh.md)"
        lines = [
            "# GLM-5.2 routed-MoE 校准结果"
            if zh
            else "# GLM-5.2 routed-MoE calibration results",
            "",
            switch,
            "",
        ]
        lines += [
            (
                "**FINAL：60/60 jobs，110/110 完整配对组；每组每 arm 合并 200 个样本，共 44,000 个性能样本。** 原始8-job正确性阶段的192个CUDA-event样本仅作诊断，未计入性能。"
                if zh
                else "**FINAL: 60/60 jobs, 110/110 complete paired groups; 200 samples per arm/group, 44,000 performance samples.** The eight-job correctness phase's 192 CUDA-event samples are diagnostic and excluded from performance."
            ),
            "",
            (
                f"独立 per-path 数学/归约契约和请求的图重放检查通过，`atol=rtol=0.01` 不变。原 native cross-pair 结果仍为 {native['PASS']} PASS / {native['FAIL']} FAIL；不得把 per-path 通过解释为跨后端等价。"
                if zh
                else f"Independent per-path expert-math/reduction-contract and requested graph checks pass at unchanged `atol=rtol=0.01`. Native cross-pair outcomes remain {native['PASS']} PASS / {native['FAIL']} FAIL; per-path acceptance does not establish cross-backend equivalence."
            ),
            "",
            ("## 结果与完整原始数据" if zh else "## Results and complete raw evidence"),
            "",
            (
                "[完整110组配对表](PAIRED_TABLES_zh.md) · [严格原始汇总](summary/summary.md) · [未舍入JSON](summary/summary.json) · [CSV](summary/paired_latency.csv) · [全部60份原始日志与tactics](RAW_LOGS.md) · [图与指标SHA](figures/figure_manifest.json)"
                if zh
                else "[All 110 paired groups](PAIRED_TABLES.md) · [Strict original summary](summary/summary.md) · [Unrounded JSON](summary/summary.json) · [CSV](summary/paired_latency.csv) · [All 60 raw logs and tactics](RAW_LOGS.md) · [Figure/metric SHAs](figures/figure_manifest.json)"
            ),
            "",
            (
                "下表统计每个phase/EP/通信组合的观测点；范围不是置信区间，不跨组或样本池计算合并速度比。负Δ表示Mega延迟较低。"
                if zh
                else "The table describes observed coordinates within each phase/EP/communication setting; ranges are not confidence intervals, and no cross-group speedup is pooled. Negative Δ means lower Mega latency."
            ),
            "",
            (
                "| 阶段 | EP | Split通信 | 组数 | Mega较低/较高/相同 | Mega延迟Δ范围 % | 两repeat方向反转 |"
                if zh
                else "| Phase | EP | Split comm | Groups | Mega lower/higher/equal | Mega latency Δ range % | Repeat sign reversals |"
            ),
            "|---|---:|---|---:|---:|---:|---:|",
        ]
        lower_all = sum(
            row["pooled"]["mega_latency_change_percent"] < 0 for row in rows
        )
        higher_all = sum(
            row["pooled"]["mega_latency_change_percent"] > 0 for row in rows
        )
        reversals_all = sum(
            row["repeats"][0]["mega_latency_change_percent"]
            * row["repeats"][1]["mega_latency_change_percent"]
            < 0
            for row in rows
        )
        # Insert before the table, so the same explicit counts appear in both languages.
        lines[-2:-2] = [
            (
                f"全部{len(rows)}组：Mega延迟较低{lower_all}组、较高{higher_all}组；{reversals_all}组在两次repeat之间变号。仅统计观测方向，不是跨工作负载合并收益。"
                if zh
                else f"Across all {len(rows)} coordinates: Mega latency is lower at {lower_all}, higher at {higher_all}; {reversals_all} reverse direction between repeats. These are observed direction counts, not a pooled gain across workloads."
            ),
            "",
        ]
        for d in dist:
            lines.append(
                f"| {d['phase']} | {d['ep']} | {d['communication']} | {d['groups']} | {d['lower']}/{d['higher']}/{d['equal']} | {d['minimum_percent']:+.4f} to {d['maximum_percent']:+.4f} | {d['repeat_sign_reversals']} |"
            )
        prefill = [row for row in rows if row["phase"] == "prefill"]
        lower_prefill = sum(
            row["pooled"]["mega_latency_change_percent"] < 0 for row in prefill
        )
        higher_prefill = [
            row for row in prefill if row["pooled"]["mega_latency_change_percent"] > 0
        ]
        exceptions = "; ".join(
            f"EP{row['ep']}/{row['communication']} N{row['tokens']}: {row['pooled']['mega_latency_change_percent']:+.4f}%"
            for row in higher_prefill
        ) or ("无" if zh else "none")
        lines += [
            "",
            (
                f"**Eager prefill：Mega在{len(prefill)}点中{lower_prefill}点延迟较低、{len(higher_prefill)}点较高。较高点：{exceptions}。** 这些大N点使用default Mega knobs，不是AUTO结果。"
                if zh
                else f"**Eager prefill: Mega latency is lower at {lower_prefill}/{len(prefill)} points and higher at {len(higher_prefill)}/{len(prefill)}. Higher-latency points: {exceptions}.** These large-N points use default Mega knobs, not AUTO."
            ),
            "",
        ]
        lines += [
            "",
            (
                "## AUTO / routing 控制与跨invocation漂移"
                if zh
                else "## AUTO / routing controls and cross-invocation drift"
            ),
            "",
            (
                "与同EP/通信/容量/N的default core比较，两列都保留。AUTO行的Split控制没有更换算法；其跨invocation漂移限制了纯调优收益的归因。routing行两arm都改成precomputed routing。以下不是同一进程内因果消融，也没有计算跨行平均收益。"
                if zh
                else "Compare to default core at the same EP/communication/capacity/N, retaining both arms. AUTO's Split control uses the same algorithm; its cross-invocation drift limits attribution to tuning alone. Routing rows change both arms to precomputed routing. These are not within-process causal ablations; gains are not averaged across rows."
            ),
            "",
            (
                "| 控制 | EP | Comm | N | Mega相对default Δ% | Split控制相对default Δ% |"
                if zh
                else "| Control | EP | Comm | N | Mega vs default Δ% | Split control vs default Δ% |"
            ),
            "|---|---:|---|---:|---:|---:|",
        ]
        for control in controls:
            lines.append(
                f"| {control['phase']} | {control['ep']} | {control['communication']} | {control['tokens']} | {control['mega_change_from_default_percent']:+.4f} | {control['split_control_change_from_default_percent']:+.4f} |"
            )
        lines += [
            "",
            "![EP4](figures/core-latency-ep4.png)",
            "",
            "![EP8](figures/core-latency-ep8.png)",
            "",
            ("## 口径与限制" if zh else "## Metric and limitations"),
            "",
        ]
        lines += [
            (
                "- 每个arm的`latency_us = 1000 × median(r1.samples_ms + r2.samples_ms)`，100+100样本不裁剪；每个样本为rank-MAX。速度比为Split/Mega，带符号变化为`100×(Mega/Split−1)`。每种EP/通信/容量/N/knobs/routing/graph设置独立配对，Mega不跨通信复用。"
                if zh
                else "- For each arm, `latency_us = 1000 × median(r1.samples_ms + r2.samples_ms)`: 100+100 untrimmed rank-MAX samples. Speedup is Split/Mega; signed change is `100×(Mega/Split−1)`. EP/communication/capacity/N/knobs/routing/graph settings remain separate; Mega observations are never reused across communications."
            ),
            (
                "- 图仅展示84个core组：default knobs、routing included、CUDA graph、CUPTI、cold L2。auto为6组独立tuning，routing为12组precomputed控制，prefill为8组eager N4096/16384；完整表保留全部110组。"
                if zh
                else "- Figures select 84 core groups: default knobs, routing included, CUDA graph, CUPTI, cold L2. Six auto groups use independent tuning, 12 routing groups are precomputed controls, and eight prefill groups are eager N4096/16384. All 110 groups remain in the full tables."
            ),
            (
                "- 这是合成H6144/I2048/E256/K8/group1 routed-MoE，随机输入，不是checkpoint replay；没有attention/shared expert/router GEMM/MTP。横轴是全局token行数，不是请求数；延迟不是serving吞吐、TPOT或交互性，不能证明原serving性能差异的因果。"
                if zh
                else "- Synthetic H6144/I2048/E256/K8/group1 routed-MoE with random inputs, not checkpoint replay; attention/shared expert/router GEMM/MTP are excluded. N counts global token rows, not requests. Latencies are not serving throughput, TPOT or interactivity and do not prove the cause of the serving gap."
            ),
            (
                "- 两次额外的untimed poisoned-output图重放被检查，而不是所有timed replay；cuBLASLt和规定的NCCL原语仍是可信边界。r5原始input tensors未保存。两repeat不能建立统计显著性，跨repeat反转明确保留。"
                if zh
                else "- Two additional untimed poisoned-output graph replays are checked, not every timed replay; cuBLASLt and the documented NCCL primitives remain trusted boundaries. Raw r5 input tensors were not captured. Two repeats do not establish statistical significance; sign reversals remain visible."
            ),
            (
                "- 调优范围：[固定版本源码与16份serving日志审查](proofs/serving-autotune-coverage-review.md)确认Split全部启动了调优，但普通EAGLE明确跳过额外EXTEND pass，无法证明大prefill专门调优。Serving Mega使用独立None路径，不是auto。r5 Split各invocation显式按最大N调优；Mega AUTO仅覆盖graph N16/128/1024，eager大N仍default。不得声称prefill Mega已autotuned或据此归因serving。"
                if zh
                else "- Tuning coverage: the [fixed-source / 16-serving-log review](proofs/serving-autotune-coverage-review.md) confirms Split startup tuning, but ordinary EAGLE explicitly skips the extra EXTEND pass; dedicated large-prefill tuning is unproven. Serving Mega uses its separate None path, not auto. r5 tunes Split at each invocation's maximum N; Mega AUTO covers graph N16/128/1024 only, while eager large-N remains default. Do not call prefill Mega autotuned or attribute serving behavior to this control."
            ),
            (
                "- r3/d1原始strict FAIL未被改判；其完整tensor诊断已单独发布，本包不重复复制。缓存归档和节点清理属于独立流程；本包不声称已归档或已清理。"
                if zh
                else "- Original r3/d1 strict FAIL outcomes are unchanged. Their full tensor diagnosis is published separately and is not duplicated here. Cache archival and node cleanup are separate workflows; this bundle makes no archival or cleanup claim."
            ),
            "",
            (
                "## 环境、源码与复算"
                if zh
                else "## Environment, source and reproduction"
            ),
            "",
            f"- Benchmark `{BENCHMARK}`; runtime/kernel `{provenance['source']['runtime_base']}`; {provenance['image_declared']}.",
            f"- NVIDIA B300, EP4/EP8; Torch `{versions['torch']}`, CUDA `{provenance['runtime']['torch_cuda']}`, CuTe `{versions['nvidia-cutlass-dsl']}`, CUPTI `{versions['cupti-python']}` / `{versions['nvidia-cuda-cupti']}`, loaded NCCL `{'.'.join(map(str, provenance['runtime']['nccl']))}`.",
            f"- [Exact argv/env/source/runtime]({run_relative}/provenance.json) · [60-job plan]({run_relative}/plan.json) · [Correctness seal]({run_relative}/gate-receipt.json) · [Completion]({run_relative}/exit.json).",
            "- [12 setup receipts](environment/verification.json) · [Actual 12-test component gate](component-gate/verification.json) · [Unmodified proof index](PROOFS.md) · [Copy manifest](copy-manifest.json) · [Complete bundle hashes](bundle-manifest.json).",
            "",
            (
                "在此目录使用已安装Matplotlib的Python，仅CPU复算；输出路径必须是新的。"
                if zh
                else "From this directory, use an existing Python environment with Matplotlib for CPU-only reproduction; output paths must be new."
            ),
            "",
            "```bash",
            "python3 -B tools/summarize_calibration.py --transfer evidence --dispatch dispatch --output recomputed-summary",
            "python3 -B tools/plot_calibration_core.py --summary recomputed-summary/summary.json --dispatch dispatch --output recomputed-figures",
            "python3 -B tools/check_calibration_raw_arithmetic.py --summary recomputed-summary/summary.json --output recomputed-raw-arithmetic.json",
            "```",
            "",
            (
                "原始JSON中绝对路径与历史review中的旧snapshot名称按原文保留作为provenance；可点击导航均来自本包相对路径。所有raw、源码、helper、回执逐字复制并重新SHA校验。组装完成不是最终独立审查或GitHub发布批准。"
                if zh
                else "Original absolute JSON paths and historical review snapshot names remain unchanged as provenance; clickable navigation uses bundle-relative paths. Raw files, sources, helpers and receipts are byte-copied and rehashed. Assembly completion is not independent final-review or GitHub-publication approval."
            ),
        ]
        (output / filename).write_text("\n".join(lines) + "\n")
        table = [
            "# 完整配对延迟表" if zh else "# Complete paired latency table",
            "",
            "[English](PAIRED_TABLES.md)" if zh else "[中文](PAIRED_TABLES_zh.md)",
            "",
            (
                "110组；单位µs；pooled = median(每arm 100+100原始样本)。原native PASS/FAIL保留。"
                if zh
                else "110 groups; µs; pooled = median(100 + 100 raw samples/arm). Native PASS/FAIL is preserved."
            ),
            "",
            (
                "| 阶段 | EP | 通信 | 每rank容量 | 全局N | Knobs/路由/图 | Split r1/r2 µs | Mega r1/r2 µs | 合并Split µs | 合并Mega µs | Split/Mega | Mega Δ% | Native r1/r2 | 原始日志 |"
                if zh
                else "| Phase | EP | Comm | Capacity/rank | Global N | Knobs/routes/graph | Split r1/r2 µs | Mega r1/r2 µs | Pooled Split µs | Pooled Mega µs | Split/Mega | Mega Δ% | Native r1/r2 | Raw logs |"
            ),
            "|---|---:|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---|---|",
        ]
        for row in rows:
            r1, r2 = sorted(row["repeats"], key=lambda r: r["repeat"])
            pooled = row["pooled"]
            links = " ".join(
                f"[r{r['repeat']}](evidence/{r['evidence']['log']})" for r in (r1, r2)
            )
            config = f"{row['knobs'] or 'None'}/{'precomputed' if row['precomputed_routing'] else 'included'}/{'graph' if row['graph'] else 'eager'}"
            table.append(
                f"| {row['phase']} | {row['ep']} | {row['communication']} | {row['capacity'] or 'live'} | {row['tokens']} | {config} | {r1['split_us']:.4f}/{r2['split_us']:.4f} | {r1['mega_us']:.4f}/{r2['mega_us']:.4f} | {pooled['split_us']:.4f} | {pooled['mega_us']:.4f} | {pooled['speedup_split_over_mega']:.6f} | {pooled['mega_latency_change_percent']:+.4f} | {r1['cross_pair']['status']}/{r2['cross_pair']['status']} | {links} |"
            )
        (output / ("PAIRED_TABLES_zh.md" if zh else "PAIRED_TABLES.md")).write_text(
            "\n".join(table) + "\n"
        )
    proofs = [
        "# Unmodified independent evidence / 原始独立审查",
        "",
        "These JSON files retain their original scopes and historical snapshot paths. Core/earlier reviews are not an independent final60 review. 原始scope与路径保留；不把早期审查改称最终审查。",
        "",
    ]
    proofs += [f"- [{name}](proofs/{name})" for name in proof_names]
    (output / "PROOFS.md").write_text("\n".join(proofs) + "\n")
    logs = [
        "# All raw invocation logs / 全部原始日志",
        "",
        "All sample arrays, timing records, routing/capacity metadata, AUTO tactics, graph/oracle checks and native failures remain in these unmodified logs and validation JSON. 正确性阶段仅诊断；性能数据逐sample保留。",
        "",
        "| Invocation | Raw log | Raw validation | Exact command/env | Exit |",
        "|---|---|---|---|---|",
    ]
    for job in read_json(output / run_relative / "plan.json")["jobs"]:
        base = f"{run_relative}/{job['id']}"
        logs.append(
            f"| {job['id']} | [log]({base}/benchmark.log) | [JSON]({base}/validation.json) | [argv/env]({base}/invocation.json) | [exit]({base}/exit.json) |"
        )
    (output / "RAW_LOGS.md").write_text("\n".join(logs) + "\n")
    if summary.get("synthetic"):
        # Direct renderer fixtures only; the production CLI has no synthetic bypass.
        for name in (
            "README.md",
            "README_zh.md",
            "PAIRED_TABLES.md",
            "PAIRED_TABLES_zh.md",
            "RAW_LOGS.md",
            "PROOFS.md",
        ):
            path = output / name
            path.write_text(
                "**SYNTHETIC — NOT MEASURED; report-layout test only.**\n\n"
                + path.read_text()
            )


def verify_links(output, pending_manifest=False):
    count = 0
    for path in output.rglob("*.md"):
        for target in re.findall(r"\]\((?:<([^>]+)>|([^\s)]+))\)", path.read_text()):
            link = unquote(target[0] or target[1]).split("#")[0]
            if not link or "://" in link:
                continue
            destination = (path.parent / link).resolve()
            require(
                destination.is_relative_to(output)
                and (
                    destination.exists()
                    or (
                        pending_manifest
                        and destination == output / "bundle-manifest.json"
                    )
                ),
                f"Nonportable link: {path.name}: {link}",
            )
            count += 1
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transfer", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--dispatch", type=Path, default=PROJECT / f"artifacts/dispatches/{RUN_ID}"
    )
    parser.add_argument(
        "--environment",
        type=Path,
        default=PROJECT / "artifacts/environment-transfers/20260920T174910Z",
    )
    parser.add_argument(
        "--component-gate",
        type=Path,
        default=PROJECT / "artifacts/contract-reference-timing-r5",
    )
    parser.add_argument("--proofs", type=Path, default=PROJECT / "artifacts")
    parser.add_argument("--source", type=Path, default=PROJECT / "flashinfer")
    parser.add_argument(
        "--additional-proof",
        type=Path,
        action="append",
        default=[],
        help="Explicit later review/acceptance files; copied verbatim, not relabeled as final acceptance",
    )
    args = parser.parse_args()
    for key, value in vars(args).items():
        setattr(
            args,
            key,
            [p.resolve() for p in value]
            if isinstance(value, list)
            else value.resolve(),
        )
    summary, source_hashes, proof_names = preflight(args)
    output = args.output
    output.mkdir(parents=True, exist_ok=False)
    (output / "assembly").mkdir()
    copies = {}
    for source, relative in (
        (args.transfer, "evidence"),
        (args.dispatch, "dispatch"),
        (args.environment, "environment"),
        (args.component_gate, "component-gate"),
    ):
        copy_tree(source, output / relative, output, copies)
    for name in proof_names:
        copy_file(
            safe_file(args.proofs, name), output / "proofs" / name, output, copies
        )
    for path in args.additional_proof:
        require(path.name not in proof_names, "Additional proof name collision")
        copy_file(path, output / "proofs" / path.name, output, copies)
        proof_names.append(path.name)
    for relative in source_hashes:
        copy_file(
            safe_file(args.source, relative),
            output / "tested-source" / relative,
            output,
            copies,
        )
    for name in (
        "summarize_calibration.py",
        "plot_calibration_core.py",
        "check_calibration_raw_arithmetic.py",
        Path(__file__).name,
    ):
        copy_file(PROJECT / "setup" / name, output / "tools" / name, output, copies)
    (output / "copy-manifest.json").write_text(
        json.dumps(
            dict(copies=copies, duplicate_cache_or_d1_payload=False),
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    run_tool(
        output,
        "summarize",
        [
            "tools/summarize_calibration.py",
            "--transfer",
            "evidence",
            "--dispatch",
            "dispatch",
            "--output",
            "summary",
        ],
    )
    copied_summary = read_json(output / "summary/summary.json")
    require(
        {k: v for k, v in copied_summary.items() if k != "evidence_root_relative"}
        == summary,
        "Copied evidence summary changed",
    )
    run_tool(
        output,
        "plot",
        [
            "tools/plot_calibration_core.py",
            "--summary",
            "summary/summary.json",
            "--dispatch",
            "dispatch",
            "--output",
            "figures",
        ],
    )
    run_tool(
        output,
        "raw-arithmetic",
        [
            "tools/check_calibration_raw_arithmetic.py",
            "--summary",
            "summary/summary.json",
            "--output",
            "assembly/raw-arithmetic.json",
        ],
    )
    write_reports(output, copied_summary, proof_names)
    link_count = verify_links(output, pending_manifest=True)
    for relative, record in copies.items():
        require(
            file_record(output / relative)
            == {k: record[k] for k in ("size", "sha256")},
            "Copied payload changed during assembly",
        )
    files = {
        p.relative_to(output).as_posix(): file_record(p)
        for p in sorted(output.rglob("*"))
        if p.is_file()
    }
    (output / "bundle-manifest.json").write_text(
        json.dumps(
            dict(
                run_id=RUN_ID,
                status="FINAL_PUBLICATION_CANDIDATE",
                files=files,
                relative_links_checked=link_count,
                independent_final_review_required=True,
                historical_failures_unchanged=True,
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    require(verify_links(output) == link_count, "Final link verification differs")
    (output / "assembly-completed.json").write_text(
        json.dumps(
            dict(
                status="completed",
                run_id=RUN_ID,
                successful_jobs=60,
                paired_groups=110,
                bundle_manifest_sha256=sha256(output / "bundle-manifest.json"),
                copied_files=len(copies),
                payload_files=len(files),
                relative_links_checked=link_count,
                publication_performed=False,
            ),
            indent=2,
        )
        + "\n"
    )
    print(
        json.dumps(
            dict(
                output=str(output),
                status="FINAL_PUBLICATION_CANDIDATE",
                copied_files=len(copies),
                paired_groups=110,
            )
        )
    )


if __name__ == "__main__":
    main()
