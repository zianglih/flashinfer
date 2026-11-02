"""Run the eight fixed W4 jobs on separate GPUs and verify full source postflight."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--smoke", type=Path, required=True)
    args = p.parse_args()
    config = json.loads(args.config.read_text())
    smoke = json.loads(args.smoke.read_text())
    assert smoke["complete"] and smoke["tokens"] == [4, 4096]
    assert smoke["config_sha256"] == hashlib.sha256(args.config.read_bytes()).hexdigest()
    root = Path(config["output"]).parent
    dest = root / "campaign.json"
    assert not dest.exists()
    running = []
    receipt = dict(complete=False, started=time.time(), config=str(args.config.resolve()),
        config_sha256=smoke["config_sha256"], smoke=str(args.smoke.resolve()), jobs=[])

    def save():
        dest.write_text(json.dumps(receipt, indent=2) + "\n")

    save()
    for gpu, name in enumerate(mode + "-" + model + "-w4a16" for mode in ("ep", "tp")
                              for model in ("v3", "v41-flash", "kimi-k3", "nemo3-ultra")):
        assert name in config["jobs"]
        command = [sys.executable, str(Path(__file__).with_name("run_pair.py")),
            "--config", str(args.config.resolve()), "--job", name, "--gpu", str(gpu)]
        log_path = root / (name + ".launcher.log")
        with log_path.open("w") as log:
            process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
        record = dict(job=name, gpu=gpu, pid=process.pid, command=command, log=str(log_path), started=time.time())
        receipt["jobs"].append(record)
        running.append((process, record))
        save()
    print(json.dumps(receipt), flush=True)
    for process, record in running:
        record.update(returncode=process.wait(), finished=time.time())
        save()
    receipt["all_jobs_passed"] = all(r["returncode"] == 0 for r in receipt["jobs"])
    # Bind native C++ headers and all tracked bytes again after the last GPU run.
    receipt["source_postflight"] = {}
    for role, source in config["sources"].items():
        manifest = json.loads(Path(source["tracked_manifest"]).read_text())
        mismatches = []
        for rel, digest in manifest["files"].items():
            path = Path(source["repo"]) / rel
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                mismatches.append(rel)
        receipt["source_postflight"][role] = dict(head=source["head"], files=len(manifest["files"]), mismatches=mismatches)
        save()
    receipt.update(complete=receipt["all_jobs_passed"] and all(not d["mismatches"] for d in receipt["source_postflight"].values()), finished=time.time())
    save()
    assert receipt["complete"], dest


if __name__ == "__main__":
    main()
