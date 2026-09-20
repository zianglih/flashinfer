"""Run an exclusive, sealed-environment numerical capture; no timing claim."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import traceback


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    with path.open("x") as handle:
        json.dump(value, handle, indent=2)
        handle.write("\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-root", required=True, type=Path)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    if args.run_id != "glm52-numerics-20260920-d1":
        raise ValueError("This frozen launcher is specific to diagnostic d1")
    root = args.task_root
    frozen = root / "setup/helpers-glm52-calibration-20260920-r3"
    driver = frozen / "run_calibration_remote.py"
    if digest(driver) != "b664ff95778b2598c30618e02867f687a3a8bca75cd559b4a58a66daa20ad224":
        raise ValueError("Frozen r3 driver changed")
    spec = importlib.util.spec_from_file_location("frozen_r3", driver)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    run = root / "diagnostics" / args.run_id
    run.mkdir(parents=True, exist_ok=False)
    result = {"started_at": datetime.now(timezone.utc).isoformat(),
              "run_id": args.run_id, "kind": "numerical_capture_only",
              "timing_enabled": False, "strict_gate_relaxed": False}
    process = None
    try:
        previous = root / "runs/glm52-calibration-20260920-r3"
        previous_exit = json.loads((previous / "exit.json").read_text())
        if previous_exit.get("status") != "failed":
            raise ValueError("Expected preserved r3 failure")
        if subprocess.check_output(["nvidia-smi", "--query-compute-apps=pid",
                                    "--format=csv,noheader"], text=True).strip():
            raise ValueError("GPU processes are active")
        source = root / "sources/flashinfer-ad0"
        source_record = module.source_proof(source)
        python = "/opt/sglang/bin/python3"
        runtime = json.loads(subprocess.check_output([python, str(frozen / "probe_runtime.py")], text=True))
        seals = module.validate_environment(root / "environment", runtime, source_record)
        baseline = previous / "001-correctness-ep4-allgather-caplive-r1/invocation.json"
        invocation = json.loads(baseline.read_text())
        env = os.environ.copy()
        env.update(invocation["env"])
        env["FLASHINFER_MOE_EP_KNOB_CACHE"] = str(run / "capture/knobs.json")
        helper = Path(__file__).with_name("capture_r3_numerical_failure.py")
        argv = [python, "-m", "torch.distributed.run", "--master-addr=127.0.0.1",
                "--master-port=30328", "--nnodes=1", "--nproc-per-node=4",
                "--max-restarts=0", str(helper), "--source-root", str(source),
                "--output-root", str(run / "capture"), "--baseline-invocation", str(baseline)]
        save(run / "provenance.json", {"source": source_record, "runtime": runtime,
             "environment_sha256": seals, "baseline_sha256": digest(baseline),
             "capture_helper_sha256": digest(helper), "driver_sha256": digest(__file__),
             "argv": argv, "env": {k: env[k] for k in invocation["env"]},
             "reused_compilation_cache": invocation["env"]["FLASHINFER_WORKSPACE_BASE"],
             "new_knob_path": env["FLASHINFER_MOE_EP_KNOB_CACHE"]})
        with (run / "diagnostic.log").open("xb") as log:
            process = subprocess.Popen(argv, cwd=source, env=env, stdout=log,
                                       stderr=subprocess.STDOUT, start_new_session=True)
            result["worker_pid"] = process.pid
            save(run / "worker.json", {"pid": process.pid, "argv": argv})
            try:
                result["worker_exit"] = process.wait(timeout=1800)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
                raise
        capture_files = []
        for n in (1, 3):
            for rank in range(4):
                record = run / "capture" / f"n{n}" / f"rank{rank}.json"
                tensor = record.with_suffix(".pt")
                if record.is_file() and tensor.is_file():
                    data = json.loads(record.read_text())
                    if data["payload_sha256"] != digest(tensor):
                        raise ValueError("Captured tensor hash differs")
                    capture_files.append({"record": str(record.relative_to(run)),
                                          "sha256": digest(record), "data": data})
        result["captures"] = capture_files
        result["all_eight_rank_case_payloads_saved"] = len(capture_files) == 8
        result["strict_numerical_gate_passed"] = (result["worker_exit"] == 0 and
            len(capture_files) == 8 and all(c["data"]["strict_refcheck_status"] == "PASS"
                                           for c in capture_files))
    except Exception:
        result["launcher_error"] = traceback.format_exc()
    finally:
        result["finished_at"] = datetime.now(timezone.utc).isoformat()
        result["gpu_after"] = subprocess.check_output(["nvidia-smi", "--query-gpu=index,utilization.gpu,memory.used",
                                                        "--format=csv,noheader,nounits"], text=True)
        save(run / "exit.json", result)
    # Expected strict comparison failure remains a failure, even if capture succeeds.
    return 0 if result.get("strict_numerical_gate_passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
