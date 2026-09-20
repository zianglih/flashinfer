"""Plot only the complete, strictly summarized routed-MoE core latency matrix."""

import argparse
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import statistics


TOKENS = (16, 32, 64, 128, 256, 512, 1024)
COMMS = ("alltoall", "allgather", "allreduce")
PHASE_COUNTS = {"correctness": 8, "core": 24, "auto": 12, "routing": 8, "prefill": 8}
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
    with Path(path).open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def close(actual, expected):
    return math.isfinite(actual) and math.isclose(
        actual, expected, rel_tol=1e-12, abs_tol=1e-10
    )


def select_core(summary, synthetic=False):
    """Check the final report contract; do not upgrade a partial summary."""
    require(
        summary["status"] == ("SYNTHETIC_NOT_MEASURED" if synthetic else "FINAL"),
        "A complete FINAL summary is required",
    )
    require(
        bool(summary.get("synthetic", False)) == synthetic,
        "Synthetic/production identity mismatch",
    )
    if synthetic:
        require(
            summary["run_id"].startswith("SYNTHETIC-"),
            "Synthetic run ID must be explicit",
        )
    require(
        summary["successful_jobs"] == summary["expected_jobs"] == 60,
        "Require all 60 jobs",
    )
    require(
        summary["successful_jobs_by_phase"] == PHASE_COUNTS,
        "Incomplete required phases",
    )
    require(
        not summary["failed_jobs"] and not summary["missing_jobs"],
        "Failed/missing jobs cannot be plotted",
    )
    exit_record = summary["run_exit"]
    require(
        exit_record is not None
        and exit_record["status"] == "completed"
        and exit_record["completed_jobs"] == 60
        and exit_record["omitted_required_phases"] == [],
        "Missing successful full-run exit",
    )
    require(
        summary["refcheck_policy"] == "per-path", "Require per-path-contract validation"
    )
    require(
        summary["correctness"]["successful_jobs"] == 8
        and summary["correctness"]["excluded_from_performance"] is True,
        "Correctness gate must be complete and excluded",
    )
    require(
        summary["cross_pair_diagnostics"]["equivalence_claim"] is False,
        "No native-equivalence claim is permitted",
    )
    groups = summary["performance_groups"]
    require(len(groups) == 110, "Require all 110 performance groups")
    keys = [tuple(row[key] for key in GROUP_FIELDS) for row in groups]
    require(len(set(keys)) == 110, "Duplicate performance groups")
    for row in groups:
        require(
            row["complete_repeats"] is True
            and row["pooled"]["sample_count_per_arm"] == 200,
            "Every group must pool 200 samples per arm",
        )
        require(
            sorted(r["repeat"] for r in row["repeats"]) == [1, 2],
            "Require repeats 1 and 2",
        )
        require(
            all(r["sample_count_per_arm"] == 100 for r in row["repeats"]),
            "Require 100 samples per repeat",
        )
        require(
            all(
                math.isfinite(row["pooled"][f"{arm}_us"])
                and row["pooled"][f"{arm}_us"] > 0
                for arm in ("split", "mega")
            ),
            "Invalid pooled latency",
        )
    core = [row for row in groups if row["phase"] == "core"]
    expected = set(itertools.product((4, 8), (None, 32768), COMMS, TOKENS))
    coordinates = {
        (r["ep"], r["capacity"], r["communication"], r["tokens"]) for r in core
    }
    require(
        len(core) == 84 and coordinates == expected,
        "Core must contain exactly 84 coordinates",
    )
    for row in core:
        require(
            row["knobs"] is None
            and row["precomputed_routing"] is False
            and row["graph"] is True
            and row["timer"] == "cupti"
            and row["refcheck_policy"] == "per-path",
            "Core settings changed",
        )
    return core


def verify_selected(summary_path, summary, core, dispatch=None):
    """Bind selected medians to the strict summary's immutable raw evidence."""
    from summarize_calibration import load_evidence

    manifest_path = summary_path.with_name("raw_manifest.json")
    manifest = read_json(manifest_path)
    files = manifest["files"]
    require(
        hashlib.sha256(
            json.dumps(files, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        == manifest["mapping_sha256"],
        "Raw manifest mapping changed",
    )
    require(
        manifest["evidence_root_relative"] == summary["evidence_root_relative"],
        "Evidence roots differ",
    )
    evidence_root = (summary_path.parent / summary["evidence_root_relative"]).resolve()
    recomputed, raw_files = load_evidence(
        evidence_root, dispatch=dispatch, allow_partial=False
    )
    require(
        recomputed
        == {k: v for k, v in summary.items() if k != "evidence_root_relative"},
        "Input summary differs from strict final recomputation",
    )
    require(raw_files == files, "Strict final raw manifest differs")
    receipt_path = evidence_root / "verification.json"
    require(
        sha256(receipt_path)
        == summary["transfer_receipt_sha256"]
        == manifest["transfer_receipt_sha256"],
        "Collector receipt changed",
    )
    receipt = read_json(receipt_path)
    require(
        receipt["verified"] is True and receipt["run_id"] == summary["run_id"],
        "Collector identity differs",
    )
    require(
        {
            r["path"]: {"size": r["size"], "sha256": r["sha256"]}
            for r in receipt["files"]
        }
        == files,
        "Collector/summary manifests differ",
    )
    checked, validations, ownership = {}, {}, {}

    def bound_file(relative):
        path = evidence_root / relative
        require(
            path.resolve().is_relative_to(evidence_root)
            and not path.is_symlink()
            and path.is_file(),
            "Unsafe evidence path",
        )
        if relative not in checked:
            record = files[relative]
            require(
                path.stat().st_size == record["size"]
                and sha256(path) == record["sha256"],
                f"Evidence changed: {relative}",
            )
            checked[relative] = record
        return path

    provenance = read_json(bound_file(f"runs/{summary['run_id']}/provenance.json"))
    require(provenance == summary["provenance"], "Source/runtime provenance differs")
    for row in core:
        pooled = {"split": [], "mega": []}
        for repeat in row["repeats"]:
            evidence = repeat["evidence"]
            log = bound_file(evidence["log"])
            require(
                checked[evidence["log"]]["sha256"] == evidence["log_sha256"],
                "Selected log SHA differs",
            )
            validation_path = bound_file(evidence["validation"])
            require(
                validation_path.parent == log.parent
                and log.parent.name == evidence["job"],
                "Log/job/validation mismatch",
            )
            group = (row["ep"], row["communication"], row["capacity"], repeat["repeat"])
            require(
                ownership.setdefault(evidence["job"], group) == group,
                "One invocation reused across paired groups",
            )
            if evidence["job"] not in validations:
                validation = read_json(validation_path)
                require(
                    validation["accepted_latency"] is True
                    and validation["refcheck_policy"] == "per-path",
                    "Raw validation did not accept per-path latency",
                )
                validations[evidence["job"]] = validation
            validation = validations[evidence["job"]]
            for arm, variant in (("split", "w4a16"), ("mega", "w4a16_megamoe")):
                matches = [
                    r
                    for r in validation["records"]["DISTRIBUTED_TIMING_SAMPLES_JSON"]
                    if r["profile_label"] == f"ep::{variant}"
                    and r["global_tokens"] == row["tokens"]
                ]
                require(len(matches) == 1, "Missing/duplicate selected sample record")
                record = matches[0]
                expected = dict(
                    world_size=row["ep"],
                    ep_communication=row["communication"],
                    megamoe_capacity_override=row["capacity"],
                    timer="cupti",
                    cuda_graph=True,
                    precomputed_routing=False,
                    cold_l2_cache=True,
                    sample_aggregation="per_iteration_rank_max",
                    sample_count=100,
                    repeat_iters=100,
                    model_shape="glm-5.2",
                )
                require(
                    all(record[k] == v for k, v in expected.items()),
                    "Selected sample identity differs",
                )
                values = record["samples_ms"]
                require(
                    len(values) == 100
                    and all(math.isfinite(x) and x > 0 for x in values),
                    "Invalid selected samples",
                )
                require(
                    close(repeat[f"{arm}_us"], statistics.median(values) * 1000),
                    "Repeat median differs from samples",
                )
                pooled[arm].extend(values)
            require(
                repeat["cross_pair"]["status"] in ("PASS", "FAIL"),
                "Native diagnostic missing",
            )
        for arm in ("split", "mega"):
            require(
                close(
                    row["pooled"][f"{arm}_us"], statistics.median(pooled[arm]) * 1000
                ),
                "Pooled median differs from 200 original samples",
            )
    require(len(validations) == 24, "Core must reference 24 distinct invocations")
    return dict(
        raw_manifest_sha256=sha256(manifest_path),
        evidence_root=str(evidence_root),
        verified_selected_files=checked,
    )


def render(output, summary, core, synthetic=False):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import ScalarFormatter

    plt.rcParams.update(
        {
            "font.size": 10,
            "svg.fonttype": "none",
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )
    outputs = []
    comm_names = {
        "alltoall": "Split: all-to-all",
        "allgather": "Split: all-gather + reduce-scatter",
        "allreduce": "Split: all-reduce gather + reduce-scatter",
    }
    lookup = {
        (r["ep"], r["capacity"], r["communication"], r["tokens"]): r for r in core
    }
    for ep in (4, 8):
        upper = 1.08 * max(
            row["pooled"][f"{arm}_us"]
            for row in core
            if row["ep"] == ep
            for arm in ("split", "mega")
        )
        fig, axes = plt.subplots(2, 3, figsize=(15.2, 8.7), sharex=True, sharey=True)
        fig.subplots_adjust(
            left=0.073, right=0.982, bottom=0.18, top=0.78, hspace=0.31, wspace=0.17
        )
        marker = "SYNTHETIC — NOT MEASURED | " if synthetic else ""
        fig.suptitle(
            f"{marker}GLM-5.2 routed-MoE latency · EP{ep}",
            y=0.976,
            fontsize=18,
            fontweight="bold",
        )
        fig.text(
            0.5,
            0.933,
            "H6144 / I2048 / E256 / K8 · routing included · default knobs · CUDA graph · cold L2 · CUPTI rank-MAX",
            ha="center",
            fontsize=11,
        )
        native = [
            repeat["cross_pair"]["status"]
            for row in core
            if row["ep"] == ep
            for repeat in row["repeats"]
        ]
        fig.text(
            0.5,
            0.902,
            f"Per-path-contract validated · native cross-pair: {native.count('PASS')} PASS / {native.count('FAIL')} FAIL · no serving or equivalence claim",
            ha="center",
            fontsize=10,
        )
        for ri, cap in enumerate((None, 32768)):
            for ci, comm in enumerate(COMMS):
                ax = axes[ri, ci]
                rows = [lookup[(ep, cap, comm, n)] for n in TOKENS]
                ax.plot(
                    TOKENS,
                    [r["pooled"]["split_us"] for r in rows],
                    "o-",
                    color="#2364aa",
                    label="W4A16 Split",
                    linewidth=2,
                    markersize=5,
                )
                ax.plot(
                    TOKENS,
                    [r["pooled"]["mega_us"] for r in rows],
                    "s-",
                    color="#cf5c16",
                    label="W4A16 Mega",
                    linewidth=2,
                    markersize=5,
                )
                ax.set_xscale("log", base=2)
                ax.set_xticks(TOKENS)
                ax.xaxis.set_major_formatter(ScalarFormatter())
                ax.grid(True, alpha=0.22)
                ax.set_ylim(0, upper)
                cap_label = f"live = ceil(N/{ep})" if cap is None else "32768"
                ax.set_title(
                    f"{comm_names[comm]}\nMega capacity/rank: {cap_label}",
                    fontsize=10,
                    pad=9,
                )
                if ci == 0:
                    ax.set_ylabel("Pooled median latency (µs)")
                if ri == 1:
                    ax.set_xlabel("Global token rows N (log₂)")
                if synthetic:
                    ax.text(
                        0.5,
                        0.08,
                        "SYNTHETIC / NOT MEASURED",
                        transform=ax.transAxes,
                        ha="center",
                        color="#8f2635",
                        alpha=0.65,
                        fontsize=9,
                    )
        handles, labels = axes[0, 0].get_legend_handles_labels()
        fig.legend(
            handles,
            labels,
            loc="upper center",
            bbox_to_anchor=(0.5, 0.881),
            ncol=2,
            frameon=False,
            fontsize=11,
        )
        fig.text(
            0.073,
            0.103,
            "Each point: median of 100 + 100 original samples/arm; no trimming. Mega is measured separately for each paired comm/capacity.",
            fontsize=10,
        )
        fig.text(
            0.073,
            0.077,
            "Two untimed graph replays checked per variant/N; not every timed replay. Other control phases remain in the complete summary.",
            fontsize=10,
        )
        source = summary["provenance"]["source"]
        fig.text(
            0.073,
            0.045,
            f"Run: {summary['run_id']}   |   benchmark {source['benchmark_commit'][:12]}   |   runtime {source['runtime_base'][:12]}",
            fontsize=9,
            color="#444444",
        )
        for extension in ("png", "svg"):
            path = (
                output
                / f"{'SYNTHETIC-' if synthetic else ''}core-latency-ep{ep}.{extension}"
            )
            fig.savefig(path, dpi=180, facecolor="white")
            outputs.append(path)
        plt.close(fig)
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--dispatch",
        type=Path,
        help="Optional original frozen dispatch directory, passed to the strict final validator",
    )
    parser.add_argument(
        "--synthetic",
        action="store_true",
        help="Layout-only fixture: requires explicit SYNTHETIC identity; never accepts partial measured data",
    )
    args = parser.parse_args()
    summary_path = args.summary.resolve()
    summary = read_json(summary_path)
    core = select_core(summary, args.synthetic)
    if args.synthetic:
        require(
            "SYNTHETIC" in str(args.output),
            "Synthetic output path must contain SYNTHETIC",
        )
        verification = {"synthetic": True, "verified_selected_files": {}}
    else:
        verification = verify_selected(summary_path, summary, core, args.dispatch)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    figures = render(output, summary, core, args.synthetic)
    if "evidence_root" in verification:
        verification["evidence_root_relative"] = os.path.relpath(
            verification.pop("evidence_root"), output
        )
    manifest = dict(
        status="SYNTHETIC_NOT_MEASURED" if args.synthetic else "FINAL",
        run_id=summary["run_id"],
        selected_group_count=len(core),
        summary_relative=os.path.relpath(summary_path, output),
        summary_sha256=sha256(summary_path),
        plotting_helper_sha256=sha256(__file__),
        provenance=summary["provenance"],
        metric_definition="1000 * median(concatenated r1+r2 samples_ms), 200 samples/arm; each sample is per-iteration rank MAX; core/routing included/graph/CUPTI/cold L2 only",
        grouping_fields=list(GROUP_FIELDS),
        equivalence_claim=False,
        source_functions={
            "benchmarks/bench_cute_dsl_moe_distributed.py": "_run_distributed_iterations",
            "setup/summarize_calibration.py": ["aggregate", "matched_pair"],
        },
        summary_helper_sha256=sha256(
            Path(__file__).with_name("summarize_calibration.py")
        ),
        routing_identity=summary.get("routing_identity"),
        reference_identity=summary.get("reference_identity"),
        selected_metrics=[
            {
                **{key: row[key] for key in GROUP_FIELDS},
                "pooled": row["pooled"],
                "repeats": [
                    {
                        key: value
                        for key, value in repeat.items()
                        if key != "per_path_oracle"
                    }
                    for repeat in row["repeats"]
                ],
            }
            for row in core
        ],
        verification=verification,
        figures={
            p.name: {"sha256": sha256(p), "size": p.stat().st_size} for p in figures
        },
    )
    (output / "figure_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )
    print(
        json.dumps(
            {
                "status": manifest["status"],
                "figures": len(figures),
                "selected_groups": len(core),
                "output": str(output),
            }
        )
    )


if __name__ == "__main__":
    main()
