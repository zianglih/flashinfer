"""Summarize immutable SHA-collected calibration evidence, without GPU access."""

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import statistics
import sys


PROJECT = Path(__file__).resolve().parents[1]
RUNTIME_BASE = "ad0a5e5e78e57070ec7c582efe733cb55cd8839f"
PHASES = ("correctness", "core", "auto", "routing", "prefill")
GROUP_FIELDS = (
    "phase",
    "ep",
    "communication",
    "capacity",
    "tokens",
    "knobs",
    "precomputed_routing",
    "graph",
    "timer",
    "refcheck_policy",
)


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text())


def verified_transfer(transfer):
    receipt = read_json(transfer / "verification.json")
    if receipt.get("verified") is not True:
        raise ValueError("Collector receipt is not verified")
    files = {}
    for record in receipt["files"]:
        relative = record["path"]
        path = transfer / relative
        if (
            relative in files
            or not path.resolve().is_relative_to(transfer.resolve())
            or path.is_symlink()
        ):
            raise ValueError(f"Duplicate/unsafe evidence path: {relative}")
        if path.stat().st_size != record["size"] or sha256(path) != record["sha256"]:
            raise ValueError(f"Collected bytes changed: {relative}")
        files[relative] = {"size": record["size"], "sha256": record["sha256"]}
    return receipt, files


def frozen_driver(dispatch, provenance, run_id):
    receipt = read_json(dispatch / "receipt.json")
    if receipt["run_id"] != run_id:
        raise ValueError("Dispatch/run IDs differ")
    for filename, key in (
        ("run_calibration_remote.py", "driver_sha256"),
        ("run_deferred_cupti.py", "wrapper_sha256"),
    ):
        actual = sha256(dispatch / "helpers" / filename)
        if actual != receipt["helper_sha256"][filename] or actual != provenance[key]:
            raise ValueError(
                f"Frozen {filename} does not match dispatched/run provenance"
            )
    spec = importlib.util.spec_from_file_location(
        "frozen_calibration_validator", dispatch / "helpers/run_calibration_remote.py"
    )
    module = importlib.util.module_from_spec(spec)
    old_bytecode_setting = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = old_bytecode_setting
    if (
        module.SOURCE_COMMIT != provenance["source"]["benchmark_commit"]
        or module.RUNTIME_BASE != provenance["source"]["runtime_base"]
        or module.RUNTIME_BASE != RUNTIME_BASE
    ):
        raise ValueError("Unsupported benchmark/runtime source")
    return module, receipt


def matched_pair(split_samples, mega_samples):
    split_us = statistics.median(split_samples) * 1000
    mega_us = statistics.median(mega_samples) * 1000
    return dict(
        split_us=split_us,
        mega_us=mega_us,
        speedup_split_over_mega=split_us / mega_us,
        mega_latency_change_percent=100 * (mega_us / split_us - 1),
    )


def aggregate(successes):
    groups = {}
    for job, validation, evidence in successes:
        if job["phase"] == "correctness":
            continue
        samples = {
            (row["profile_label"].removeprefix("ep::"), row["global_tokens"]): row[
                "samples_ms"
            ]
            for row in validation["records"]["DISTRIBUTED_TIMING_SAMPLES_JSON"]
        }
        for tokens in job["tokens"]:
            setting = {
                name: tokens
                if name == "tokens"
                else job.get(name, "cross-pair")
                if name == "refcheck_policy"
                else job[name]
                for name in GROUP_FIELDS
            }
            cross_pair = [
                row
                for row in validation["records"]["refcheck"]
                if row["tokens"] == tokens
            ]
            if len(cross_pair) != 1:
                raise ValueError(
                    "Each accepted latency pair must preserve its cross-pair diagnostic"
                )
            oracle = [
                row
                for row in validation["records"].get("ORACLE_REFCHECK_JSON", [])
                if row["global_tokens"] == tokens
            ]
            if setting["refcheck_policy"] == "per-path" and (
                validation.get("accepted_latency") is not True
                or len(oracle) != 2
                or {row["variant"] for row in oracle} != {"w4a16", "w4a16_megamoe"}
                or any(row["status"] != "PASS" for row in oracle)
            ):
                raise ValueError(
                    "Per-path latency lacks both accepted independent oracle results"
                )
            key = tuple(setting[name] for name in GROUP_FIELDS)
            group = groups.setdefault(key, dict(setting=setting, repeats={}))
            repeat = job["repeat"]
            if repeat not in (1, 2) or repeat in group["repeats"]:
                raise ValueError(f"Duplicate/unsupported repeat: {key}, r{repeat}")
            split = samples[("w4a16", tokens)]
            mega = samples[("w4a16_megamoe", tokens)]
            if (
                len(split) != 100
                or len(mega) != 100
                or not all(math.isfinite(x) and x > 0 for x in split + mega)
            ):
                raise ValueError(
                    "Performance repeats must contain 100 positive finite samples per arm"
                )
            group["repeats"][repeat] = dict(
                repeat=repeat,
                sample_count_per_arm=100,
                **matched_pair(split, mega),
                evidence=evidence,
                cross_pair=cross_pair[0],
                per_path_oracle=oracle,
                _split=split,
                _mega=mega,
            )
    rows = []
    for group in groups.values():
        repeats = group["repeats"]
        complete = set(repeats) == {1, 2}
        pooled = None
        if complete:
            pooled = dict(
                sample_count_per_arm=200,
                **matched_pair(
                    repeats[1]["_split"] + repeats[2]["_split"],
                    repeats[1]["_mega"] + repeats[2]["_mega"],
                ),
            )
        rows.append(
            dict(
                **group["setting"],
                complete_repeats=complete,
                pooled=pooled,
                repeats=[
                    {k: v for k, v in repeats[r].items() if not k.startswith("_")}
                    for r in sorted(repeats)
                ],
            )
        )
    return sorted(
        rows,
        key=lambda row: (
            PHASES.index(row["phase"]),
            row["ep"],
            row["communication"],
            row["capacity"] or 0,
            row["tokens"],
            row["knobs"] or "none",
            row["precomputed_routing"],
            row["graph"],
        ),
    )


def load_evidence(transfer, dispatch=None, allow_partial=False):
    receipt, files = verified_transfer(transfer)
    run_id = receipt["run_id"]
    if not run_id or Path(run_id).name != run_id or run_id in (".", ".."):
        raise ValueError("Invalid run ID")
    run = transfer / "runs" / run_id

    def recorded(path):
        relative = path.relative_to(transfer).as_posix()
        if relative not in files:
            raise ValueError(f"Evidence not bound by collector receipt: {relative}")
        return read_json(path)

    provenance = recorded(run / "provenance.json")
    plan = recorded(run / "plan.json")
    if provenance["source"]["runtime_base"] != RUNTIME_BASE:
        raise ValueError("Unexpected source pins")
    dispatch = dispatch or PROJECT / "artifacts/dispatches" / run_id
    driver, launch = frozen_driver(dispatch, provenance, run_id)
    if (
        hasattr(driver, "reference_identity")
        and provenance.get("refcheck_policy") != driver.REFCHECK_POLICY
    ):
        raise ValueError("Run provenance differs from the frozen per-path policy")
    expected_jobs = driver.jobs_for(list(PHASES))
    if (
        plan["run_id"] != run_id
        or plan["jobs"] != expected_jobs
        or set(plan["phases"]) != set(PHASES)
        or plan["required_phases"] != list(PHASES)
        or plan["omitted_required_phases"]
    ):
        raise ValueError("This summarizer requires the complete declared 60-job plan")
    if provenance["image_declared"] != driver.IMAGE:
        raise ValueError("Unexpected image declaration")
    for relative in provenance["environment_sha256"]:
        recorded(run / "environment" / relative)
    if (
        driver.validate_environment(
            run / "environment", provenance["runtime"], provenance["source"]
        )
        != provenance["environment_sha256"]
    ):
        raise ValueError("Environment hashes differ from run provenance")
    final_exit = recorded(run / "exit.json") if (run / "exit.json").exists() else None
    expected_ids = {job["id"] for job in expected_jobs}
    actual_ids = {
        path.name for path in run.iterdir() if path.is_dir() and path.name[:3].isdigit()
    }
    if not actual_ids <= expected_ids:
        raise ValueError("Unexpected case directory")
    successes, failures, missing = [], [], []
    remote_run = Path(launch["run_root"])
    remote_source = driver.TASK_ROOT / "sources/flashinfer-ad0"
    for job in expected_jobs:
        case = run / job["id"]
        if not (case / "exit.json").exists():
            missing.append(job["id"])
            continue
        exit_record = recorded(case / "exit.json")
        invocation = recorded(case / "invocation.json")
        log = case / "benchmark.log"
        relative_log = log.relative_to(transfer).as_posix()
        if (
            relative_log not in files
            or exit_record["log_sha256"] != files[relative_log]["sha256"]
        ):
            raise ValueError("Case exit/log SHA mismatch")
        if (
            invocation["job"] != job
            or invocation["pins"] != provenance["source"]
            or invocation["wrapper_sha256"] != provenance["wrapper_sha256"]
            or invocation["runtime_versions"] != provenance["runtime"]["versions"]
            or invocation["cwd"] != str(remote_source)
            or invocation["argv"]
            != driver.benchmark_argv(
                job,
                provenance["python"],
                Path(launch["helper_dir"]) / "run_deferred_cupti.py",
            )
            or invocation["knob_cache_initially_absent"] is not True
        ):
            raise ValueError(f"Invocation config/pins mismatch: {job['id']}")
        expected_env = {
            "PYTHONPATH": str(remote_source),
            "OMP_NUM_THREADS": "1",
            "CUDA_VISIBLE_DEVICES": ",".join(map(str, range(job["ep"]))),
            "FLASHINFER_CUDA_ARCH_LIST": "10.3a",
            "MAX_JOBS": "16",
            "FLASHINFER_NVCC_THREADS": "2",
            "FLASHINFER_WORKSPACE_BASE": str(remote_run / "compiled-cache"),
            "FLASHINFER_MOE_EP_KNOB_CACHE": str(remote_run / job["id"] / "knobs.json"),
            "CUDA_CACHE_PATH": str(remote_run / "compiled-cache/cuda"),
            "XDG_CACHE_HOME": str(remote_run / "compiled-cache/xdg"),
            "PYTHONUNBUFFERED": "1",
        }
        if hasattr(driver, "TIMING_STAGE"):
            expected_env["TRITON_CACHE_DIR"] = str(remote_run / "compiled-cache/triton")
            if provenance.get("timing_stage") != driver.TIMING_STAGE:
                raise ValueError("Timing stage differs from the frozen driver")
        if any(
            invocation["env"].get(key) != value for key, value in expected_env.items()
        ):
            raise ValueError(f"Invocation environment mismatch: {job['id']}")
        if (
            exit_record.get("passed") is not True
            or exit_record["exit_code"] != 0
            or exit_record["timed_out"]
        ):
            diagnostic = {}
            try:
                parsed = driver.parse_records(log)
                diagnostic = dict(
                    cross_pair=parsed.get("refcheck", []),
                    per_path_oracle=parsed.get("ORACLE_REFCHECK_JSON", []),
                )
            except (ValueError, KeyError, TypeError) as exc:
                diagnostic = dict(diagnostic_parse_error=str(exc))
            failures.append(
                dict(job=job["id"], exit=exit_record, log=relative_log, **diagnostic)
            )
            continue
        if hasattr(driver, "reference_identity"):
            validation = driver.validate_log(
                log,
                job,
                driver.routing_identity(provenance["source"]),
                driver.reference_identity(provenance["source"]),
            )
        elif hasattr(driver, "routing_identity"):
            validation = driver.validate_log(
                log, job, driver.routing_identity(provenance["source"])
            )
        else:
            validation = driver.validate_log(log, job)
        saved = recorded(case / "validation.json")
        if {k: v for k, v in saved.items() if k != "validated_at"} != {
            k: v for k, v in validation.items() if k != "validated_at"
        }:
            raise ValueError(f"Saved/recomputed validation differs: {job['id']}")
        evidence = dict(
            job=job["id"],
            log=relative_log,
            log_sha256=files[relative_log]["sha256"],
            validation=(case / "validation.json").relative_to(transfer).as_posix(),
        )
        successes.append((job, validation, evidence))
    if (run / "gate-receipt.json").exists():
        recorded(run / "gate-receipt.json")
        driver.validate_gate(run, provenance)
    elif len(successes) >= 8:
        raise ValueError("Completed correctness matrix lacks a sealed gate receipt")
    complete = (
        len(successes) == 60
        and not failures
        and not missing
        and final_exit is not None
        and final_exit.get("status") == "completed"
        and final_exit.get("completed_jobs") == 60
        and final_exit.get("omitted_required_phases") == []
    )
    if not complete and not allow_partial:
        raise ValueError(
            f"Not final: {len(successes)}/60 jobs passed, {len(failures)} failed, {len(missing)} missing; use --allow-partial only for internal review"
        )
    if complete:
        archived_launch = recorded(transfer / "launches" / f"{run_id}.json")
        if archived_launch != launch:
            raise ValueError("Collected/frozen launch receipts differ")
        if f"launches/{run_id}.log" not in files:
            raise ValueError("Final collection lacks launch log")
    rows = aggregate(successes)
    if complete and (
        len(rows) != 110 or not all(row["complete_repeats"] for row in rows)
    ):
        raise ValueError("Final paired matrix must have 110 complete groups")
    cross_pair_records = [
        dict(job=job["id"], phase=job["phase"], **row)
        for job, validation, _ in successes
        for row in validation["records"]["refcheck"]
    ]
    policy = getattr(driver, "REFCHECK_POLICY", "cross-pair")
    return dict(
        status="FINAL" if complete else "PARTIAL_INTERNAL_ONLY",
        run_id=run_id,
        collected_at=receipt["collected_at"],
        successful_jobs=len(successes),
        expected_jobs=60,
        successful_jobs_by_phase={
            phase: sum(job["phase"] == phase for job, _, _ in successes)
            for phase in PHASES
        },
        failed_jobs=failures,
        missing_jobs=missing,
        run_exit=final_exit,
        provenance=provenance,
        routing_identity=(
            driver.routing_identity(provenance["source"])
            if hasattr(driver, "routing_identity")
            else None
        ),
        performance_groups=rows,
        refcheck_policy=policy,
        reference_identity=(
            driver.reference_identity(provenance["source"])
            if hasattr(driver, "reference_identity")
            else None
        ),
        cross_pair_diagnostics=dict(
            scope="Validated completed jobs; failed-job raw logs remain separately linked",
            records=cross_pair_records,
            status_counts={
                status: sum(row["status"] == status for row in cross_pair_records)
                for status in ("PASS", "FAIL")
            },
            all_recorded_pairs_passed=bool(cross_pair_records)
            and all(row["status"] == "PASS" for row in cross_pair_records),
            equivalence_claim=False,
            failed_job_records=[
                dict(job=failure["job"], **row)
                for failure in failures
                for row in failure.get("cross_pair", [])
            ],
            failed_job_status_counts={
                status: sum(
                    row["status"] == status
                    for failure in failures
                    for row in failure.get("cross_pair", [])
                )
                for status in ("PASS", "FAIL")
            },
        ),
        correctness=dict(
            excluded_from_performance=True,
            successful_jobs=sum(
                job["phase"] == "correctness" for job, _, _ in successes
            ),
            timed_replays_numerically_checked=False,
            refcheck_policy=policy,
            accepted_latency_criterion=(
                "both independent per-path oracle checks plus requested same-backend graph checks passed at atol=rtol=1e-2; cross-pair FAIL retained"
                if policy == "per-path"
                else "frozen original cross-pair/graph validation policy"
            ),
            oracle_refcheck_count=sum(
                validation.get("oracle_refcheck_count", 0)
                for _, validation, _ in successes
            ),
        ),
        transfer_receipt_sha256=sha256(transfer / "verification.json"),
        dispatch_receipt_sha256=sha256(dispatch / "receipt.json"),
    ), files


def write_outputs(output, transfer, summary, files):
    output.mkdir(parents=True, exist_ok=False)
    transfer_relative = os.path.relpath(transfer, output)
    summary["evidence_root_relative"] = transfer_relative
    manifest = dict(
        transfer_receipt_sha256=summary["transfer_receipt_sha256"],
        evidence_root_relative=transfer_relative,
        files=files,
    )
    manifest["mapping_sha256"] = hashlib.sha256(
        json.dumps(files, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    (output / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    (output / "raw_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )
    headers = [
        *GROUP_FIELDS,
        "complete_repeats",
        "r1_split_us",
        "r1_mega_us",
        "r2_split_us",
        "r2_mega_us",
        "r1_cross_pair_status",
        "r2_cross_pair_status",
        "pooled_samples_per_arm",
        "pooled_split_us",
        "pooled_mega_us",
        "speedup_split_over_mega",
        "mega_latency_change_percent",
    ]
    table = []
    for row in summary["performance_groups"]:
        record = {name: row[name] for name in GROUP_FIELDS}
        record["complete_repeats"] = row["complete_repeats"]
        for repeat in row["repeats"]:
            record[f"r{repeat['repeat']}_cross_pair_status"] = repeat["cross_pair"][
                "status"
            ]
            for arm in ("split", "mega"):
                record[f"r{repeat['repeat']}_{arm}_us"] = repeat[f"{arm}_us"]
        pooled = row["pooled"]
        if pooled:
            record.update(
                pooled_samples_per_arm=200,
                pooled_split_us=pooled["split_us"],
                pooled_mega_us=pooled["mega_us"],
                speedup_split_over_mega=pooled["speedup_split_over_mega"],
                mega_latency_change_percent=pooled["mega_latency_change_percent"],
            )
        table.append(record)
    with (output / "paired_latency.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(table)
    lines = [
        f"# {summary['status']} — GLM-5.2 routed-MoE calibration",
        "",
        f"Run `{summary['run_id']}`; {summary['successful_jobs']}/60 invocations passed. "
        f"Failed: {len(summary['failed_jobs'])}; missing: {len(summary['missing_jobs'])}.",
        "",
        "Metrics are routed-MoE latency in microseconds, not serving throughput or interactivity. "
        "Speedup = Split/Mega; signed Mega latency change = 100 × (Mega/Split − 1), so negative means lower Mega latency. "
        "Per-repeat medians use 100 raw samples per arm; pooled values require both repeats (200 samples/arm). "
        "No trimming; no pooling across communication modes or other settings. Correctness timings are excluded.",
        "",
        (
            "Independent per-path oracle checks and two additional untimed same-backend graph replays use atol=rtol=1e-2. "
            "The original cross-pair PASS/FAIL diagnostics remain recorded; accepted latency does not imply cross-backend numerical equivalence. "
            if summary.get("refcheck_policy") == "per-path"
            else "Native eager cross-backend refchecks and two additional untimed same-backend graph replays use atol=rtol=1e-2. "
        )
        + "The extra graph checks do not validate every timed replay. All performance samples use the declared CUPTI path, "
        "with callback/detach evidence checked per rank.",
        "",
        f"Source `{summary['provenance']['source']['benchmark_commit']}`; runtime/kernel base `{RUNTIME_BASE}`. "
        "Synthetic H6144/I2048/E256/K8/group1; no attention/shared expert/router GEMM/MTP/checkpoint replay. "
        "The gather paths use equal padding, approximating the serving communication boundary.",
        "",
        "[Full settings, repeat values and provenance](summary.json) · [CSV](paired_latency.csv) · [Raw SHA manifest](raw_manifest.json)",
        "",
    ]
    if summary["status"] != "FINAL":
        lines += [
            "**Internal partial evidence only. Missing/failed invocations prevent a final 60-job conclusion; "
            "a group with only one repeat has no pooled value.**",
            "",
        ]
    if summary.get("routing_identity"):
        route = summary["routing_identity"]
        lines += [
            f"Routing provider: `{route['provider']}`, SGLang `{route['sglang_commit']}`. "
            "The upstream source, kernel AST and local adapter hashes are retained in summary.json and checked for every pair.",
            "",
        ]
    diagnostics = summary.get("cross_pair_diagnostics", {})
    if diagnostics:
        counts = diagnostics["status_counts"]
        lines += [
            f"Cross-pair diagnostics in validated jobs: **{counts['PASS']} PASS, {counts['FAIL']} FAIL**. "
            "Every record and each repeat's diagnostic are preserved in summary.json; no failed cross-pair check is relabeled PASS.",
            "",
        ]

    def fmt(value, signed=False):
        return (
            "missing" if value is None else format(value, "+.3f" if signed else ".3f")
        )

    for phase in PHASES[1:]:
        rows = [row for row in summary["performance_groups"] if row["phase"] == phase]
        lines += [
            f"## {phase}",
            "",
            "| EP | Comm | Cap/rank | Global N | Knobs / routes / execution | Split r1/r2 µs | Mega r1/r2 µs | Cross-pair r1/r2 | Pooled Split µs | Pooled Mega µs | Split/Mega | Mega latency Δ% | Raw logs |",
            "|---:|---|---:|---:|---|---:|---:|---|---:|---:|---:|---:|---|",
        ]
        for row in rows:
            repeats = {r["repeat"]: r for r in row["repeats"]}
            pooled = row["pooled"] or {}
            medians = {
                arm: "/".join(fmt(repeats.get(r, {}).get(f"{arm}_us")) for r in (1, 2))
                for arm in ("split", "mega")
            }
            links = " ".join(
                f"[r{r}](<{Path(transfer_relative, record['evidence']['log']).as_posix()}>)"
                for r, record in repeats.items()
            )
            contract = f"{row['knobs'] or 'None'}/{'precomputed' if row['precomputed_routing'] else 'included'}/{'graph' if row['graph'] else 'eager'}"
            pair_status = "/".join(
                repeats.get(r, {}).get("cross_pair", {}).get("status", "missing")
                for r in (1, 2)
            )
            lines.append(
                f"| {row['ep']} | {row['communication']} | {row['capacity'] or 'live'} | {row['tokens']} | {contract} | {medians['split']} | {medians['mega']} | {pair_status} | {fmt(pooled.get('split_us'))} | {fmt(pooled.get('mega_us'))} | {fmt(pooled.get('speedup_split_over_mega'))} | {fmt(pooled.get('mega_latency_change_percent'), True)} | {links} |"
            )
        if not rows:
            lines += ["", "No validated performance points collected for this phase."]
        lines.append("")
    if summary["failed_jobs"]:
        lines += ["## Excluded failures", ""]
        lines += [
            f"- `{failure['job']}`: exit `{failure['exit']['exit_code']}`, validation `{failure['exit'].get('validation_issue')}`."
            for failure in summary["failed_jobs"]
        ]
    (output / "summary.md").write_text("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transfer", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--dispatch",
        type=Path,
        help="Frozen dispatch directory; default resolves by collected run ID",
    )
    parser.add_argument("--allow-partial", action="store_true")
    args = parser.parse_args()
    summary, files = load_evidence(
        args.transfer.resolve(), args.dispatch, args.allow_partial
    )
    write_outputs(args.output.resolve(), args.transfer.resolve(), summary, files)
    print(
        json.dumps(
            dict(
                status=summary["status"],
                successful_jobs=summary["successful_jobs"],
                performance_groups=len(summary["performance_groups"]),
                output=str(args.output),
            )
        )
    )


if __name__ == "__main__":
    main()
