"""Fresh source-bound W4A16 C-A-A-C replay with per-arm published tactics."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import signal
import statistics
import subprocess
import time


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def manifest(path):
    if path.is_file():
        return {"native.json": sha(path)}
    return {str(p.relative_to(path)): sha(p) for p in sorted(path.rglob("*")) if p.is_file()}


def gpu_state(gpu):
    return subprocess.check_output(["nvidia-smi", "-i", str(gpu),
        "--query-gpu=uuid,memory.used,utilization.gpu,clocks.sm,temperature.gpu,power.draw",
        "--format=csv,noheader"], text=True).strip()


def identities(measure):
    facts = [{k: h[k] for k in ("key", "runner", "tactic")} for h in measure["cache_hits"]]
    return list({json.dumps(v, sort_keys=True): v for v in facts}.values())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--job", required=True)
    parser.add_argument("--gpu", type=int, required=True)
    parser.add_argument("--tokens", help="Qualification subset only; omitted for full campaign")
    parser.add_argument("--output", type=Path, help="Separate qualification output root")
    parser.add_argument("--dump-compiler", action="store_true", help="Keep PTX/cubin in qualification only; no compiler optimization change")
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    job = config["jobs"][args.job]
    tokens = list(map(int, args.tokens.split(","))) if args.tokens else job["tokens"]
    assert all(t in job["tokens"] for t in tokens)
    out = (args.output or Path(config["output"])) / args.job
    out.mkdir(parents=True, exist_ok=False)
    assert not subprocess.check_output(["nvidia-smi", "-i", str(args.gpu),
        "--query-compute-apps=pid", "--format=csv,noheader"], text=True).strip()
    h = Path(__file__).resolve().parent
    for rel, digest in config["observer_hashes"].items():
        assert sha(h / rel) == digest, rel
    expected, frozen, caches = {}, {}, {}
    for role, arm in job["arms"].items():
        data = json.loads(Path(arm["winner_results"]).read_text())
        assert data["complete"] and data["swap_ab"] == (role == "after") and not data["use_fused_finalize"]
        measurements = iter(data["native_diagnostic"]["measurements"])
        expected[role] = {}
        for row in data["rows"]:
            assert row["backend_labels"] == ["CuteDSL W4A16"]
            expected[role][row["tokens"]] = dict(route=row["routing_identity"], winner=identities(next(measurements)))
        assert next(measurements, None) is None
        original = Path(arm["winner_cache"])
        caches[role] = out / ("cache-" + role + (".json" if arm["cache_kind"] == "native" else ""))
        if original.is_file():
            shutil.copy2(original, caches[role])
        else:
            shutil.copytree(original, caches[role])
        frozen[role] = manifest(original)
        assert manifest(caches[role]) == frozen[role]

    def verify_source(role):
        source = config["sources"][role]
        assert sha(source["tracked_manifest"]) == source["tracked_manifest_sha256"]
        for rel, target in source["native_data_links"].items():
            link = Path(source["repo"]) / rel
            assert link.is_symlink() and str(link.resolve()) == target, (role, rel)
        for rel, digest in source["source_sha256"].items():
            assert sha(Path(source["repo"]) / rel) == digest, (role, rel)

    receipt = dict(complete=False, job=job, tokens=tokens, config_sha256=sha(args.config),
        sources=config["sources"], gpu=args.gpu, gpu_initial=gpu_state(args.gpu), phases=[],
        frozen_caches=frozen, boundary=config["boundary"])
    gpu_uuid = receipt["gpu_initial"].split(",")[0].strip()
    fresh_routes = {}

    def save():
        (out / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")

    save()
    try:
        for index, role in enumerate(config["phases"]):
            verify_source(role)
            source, arm = config["sources"][role], job["arms"][role]
            cache = caches[role]
            assert manifest(cache) == frozen[role]
            env = {k: v for k, v in os.environ.items() if not k.startswith(("FLASHINFER_", "TRTLLM_", "CUTE_DSL_", "FI_")) and k not in ("CUDA_VISIBLE_DEVICES", "PYTHONOPTIMIZE")}
            settings = dict(CUDA_VISIBLE_DEVICES=str(args.gpu), FI_OWNERSHIP_CONFIG=str(args.config.resolve()),
                FI_FROZEN_HEAD=source["head"], PYTHONPATH=source["repo"],
                FLASHINFER_WORKSPACE_BASE=source["workspace_base"], FLASHINFER_CUBIN_DIR=source["cubin_dir"],
                CUTE_DSL_CACHE_DIR=source["cute_cache"], CUDA_CACHE_PATH=config["driver_cache"],
                FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY="1", FLASHINFER_CUDA_ARCH_LIST="10.3a",
                FLASHINFER_DIST_AWARE_AUTOTUNE="0", TRTLLM_ENABLE_PDL="1",
                FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH="0", TRTLLM_DISABLE_FP4_QUANT_FAST_MATH="0",
                MAX_JOBS="4", OMP_NUM_THREADS="1", PYTHONUNBUFFERED="1",
                TRITON_CACHE_DIR=str(out / "triton" / role),
                FLASHINFER_JIT_BUILD_LOG=str(out / f"{index}-{role}-native-build.jsonl"))
            env.update(settings)
            dest = out / f"{index}-{role}"
            if args.dump_compiler:
                settings.update(CUTE_DSL_KEEP="ptx,cubin", CUTE_DSL_DUMP_DIR=str(out / "compiler-dumps" / dest.name))
                env.update(settings)
            command = [config["python"], "-u", arm["observer"], "--repo", source["repo"], "--output", str(dest), "--w4a16-only", "--",
                "--functional-api", "--model", job["model"], "--ep", str(job["ep"]), "--tp", str(job["tp"]),
                "--quant-family", "nvfp4", "--backends", "cutedsl", "--num-tokens", ",".join(map(str, tokens)),
                "--cache", str(cache), "--no-fused-finalize", "--warmup", "10", "--iters", "100", "--no-autotune", "--include-activation-quant"]
            if role == "after":
                command.extend(["--swap-ab", "--output-format", "both"])
            phase = dict(index=index, role=role, command=command, environment=settings, started=time.time(),
                gpu_before=gpu_state(args.gpu), results=str(dest / "results.json"))
            assert phase["gpu_before"].split(",")[0].strip() == gpu_uuid
            receipt["phases"].append(phase)
            save()
            log_path = out / f"{index}-{role}.log"
            compiler = out / f"{index}-{role}-compiler-artifacts"
            compiler.mkdir()
            wrapped = [config["python"], "-u", str(h / "nvml_clock_wrapper.py"), "--gpu", str(args.gpu),
                "--interval-ms", "2", "--output", str(out / "telemetry" / dest.name), "--", *command]
            with log_path.open("w") as log:
                process = subprocess.Popen(wrapped, cwd=compiler, env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                try:
                    code = process.wait(timeout=config["phase_timeout_seconds"])
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
                    phase["timeout"] = True
                    raise
            phase.update(returncode=code, seconds=time.time() - phase["started"], gpu_after=gpu_state(args.gpu))
            save()
            assert code == 0, (args.job, index, role, log_path)
            verify_source(role)
            data = json.loads((dest / "results.json").read_text())
            assert data["complete"] and data["swap_ab"] == (role == "after") and not data["use_fused_finalize"]
            assert not data["native_diagnostic"]["admitted_tactics"]
            assert data.get("profile_calls", 0) == 0
            assert data["benchmark_sha256"] == source["source_sha256"]["benchmarks/bench_moe_deepseek.py"]
            assert data["observer_sha256"] == sha(arm["observer"])
            assert [r["tokens"] for r in data["rows"]] == tokens
            measurements = iter(data["native_diagnostic"]["measurements"])
            medians, historical_routes = [], {}
            for row in data["rows"]:
                token = row["tokens"]
                fresh_routes.setdefault(token, row["routing_identity"])
                assert row["routing_identity"] == fresh_routes[token], ("Fresh arms/repeats routed differently", token)
                historical_routes[token] = row["routing_identity"] == expected[role][token]["route"]
                assert row["backend_labels"] == ["CuteDSL W4A16"]
                result = row["results"][0]
                measure = next(measurements)
                values = measure["milliseconds"]
                assert len(values) == 100 and all(math.isfinite(v) and v > 0 for v in values)
                assert measure["timer"] == "CUPTI" and measure["event_fallback_forbidden"]
                assert statistics.median(values) == measure["median_ms"] == result["latency_ms"]
                assert all(v["hit"] for v in measure["cache_hits"])
                assert identities(measure) == expected[role][token]["winner"], (role, token)
                medians.append(dict(tokens=token, backend=result["backend"], ms=measure["median_ms"]))
            assert next(measurements, None) is None
            assert len(medians) == len(tokens)
            assert phase["gpu_after"].split(",")[0].strip() == gpu_uuid
            assert manifest(cache) == frozen[role], (role, "Frozen cache changed")
            clock = json.loads((out / "telemetry" / dest.name / "receipt.json").read_text())
            assert clock["complete"] and clock["returncode"] == 0
            phase.update(verified=True, medians=medians, historical_routing_matches=historical_routes,
                results_sha256=sha(dest / "results.json"), stdout_sha256=sha(log_path))
            save()
        receipt.update(complete=True, finished=time.time(), common_fresh_routes=fresh_routes)
        save()
    except BaseException as exc:
        receipt.update(error=repr(exc), finished=time.time())
        save()
        raise


if __name__ == "__main__":
    main()
