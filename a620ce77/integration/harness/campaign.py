"""Serialize jobs within each explicitly assigned GPU; no resource allocation."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import threading
import time

H = Path(__file__).resolve().parent


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--gpus", nargs="+", type=int, required=True)
    a = p.parse_args()
    a.config = a.config.resolve()
    assert len(a.gpus) == len(set(a.gpus))
    c = json.loads(a.config.read_text())
    assert json.loads((H / "cache-import.json").read_text())["passed"]
    out = Path(c["output"]).parent
    lanes = {gpu: [] for gpu in a.gpus}
    for i, (name, job) in enumerate(c["jobs"].items()):
        lanes[a.gpus[i % len(a.gpus)]].append(name)
    record = dict(complete=False, started=time.time(), control_head=c["control_head"], label=c["label"], config_sha256=hashlib.sha256(a.config.read_bytes()).hexdigest(), lanes={})
    lock = threading.Lock()

    def verify_full_sources(boundary):
        proof = {}
        for role, source in c["sources"].items():
            path = Path(source["tracked_manifest"])
            assert hashlib.sha256(path.read_bytes()).hexdigest() == source["tracked_manifest_sha256"]
            files = json.loads(path.read_text())
            for name, digest in files.items():
                assert hashlib.sha256((Path(source["repo"]) / name).read_bytes()).hexdigest() == digest, (role, name)
            proof[role] = dict(files=len(files), manifest_sha256=source["tracked_manifest_sha256"], verified=time.time())
        record["full_source_" + boundary] = proof
        save()

    def save():
        (out / "campaign.json").write_text(json.dumps(record, indent=2) + "\n")

    def run(gpu, jobs):
        rows = []
        for name in jobs:
            command = [sys.executable, str(H / "run_perf.py"), "--config", str(a.config), "--job", name, "--gpu", str(gpu)]
            row = dict(job=name, gpu=gpu, command=command, started=time.time())
            with (out / f"gpu{gpu}-{name}.log").open("w") as log:
                result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
            row.update(returncode=result.returncode, finished=time.time())
            rows.append(row)
            with lock:
                record["lanes"][str(gpu)] = rows
                save()
            result.check_returncode()
            subprocess.run([sys.executable, str(H / "analyze_perf.py"), str(Path(c["output"]) / name)], check=True, stdout=subprocess.DEVNULL)

    try:
        save()
        verify_full_sources("before")
        with ThreadPoolExecutor(max_workers=len(a.gpus)) as pool:
            list(pool.map(lambda item: run(*item), lanes.items()))
        verify_full_sources("after")
        record.update(complete=True, passed=True, finished=time.time())
        save()
    except BaseException as exc:
        record.update(complete=True, passed=False, error=repr(exc), finished=time.time())
        save()
        raise


if __name__ == "__main__":
    main()
