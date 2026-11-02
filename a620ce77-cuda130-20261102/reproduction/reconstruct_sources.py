"""Reconstruct both pinned source trees, then verify every archived file hash.

Requires Git/network and an empty source checkout destination. No builds or GPU
work are performed. Historical benchmark adapter is the only source overlay.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent


def run(*command):
    subprocess.run(command, check=True)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    data = json.loads((ROOT / "source-revisions.json").read_text())
    for role, record in data["sources"].items():
        source = ROOT / "sources" / role
        assert not source.exists(), f"Refusing to modify existing source tree: {source}"
        manifest_path = ROOT / "sources" / (role + "-manifest.json")
        assert sha(manifest_path) == record["source_manifest_sha256"]
        run("git", "clone", "--filter=blob:none", "--no-checkout", data["repository"], str(source))
        run("git", "-C", str(source), "fetch", "origin", record["head"])
        run("git", "-C", str(source), "checkout", "--detach", record["head"])
        run("git", "-C", str(source), "submodule", "update", "--init", *record["submodules"])
        for path, head in record["submodules"].items():
            actual = subprocess.check_output(["git", "-C", str(source / path), "rev-parse", "HEAD"], text=True).strip()
            assert actual == head, path
        if record["benchmark_adapter_sha256"]:
            adapter = ROOT / "sources/before-benchmark-adapter.py"
            assert sha(adapter) == record["benchmark_adapter_sha256"]
            shutil.copyfile(adapter, source / "benchmarks/bench_moe_deepseek.py")
        manifest = json.loads(manifest_path.read_text())
        for path, expected in manifest["files"].items():
            assert sha(source / path) == expected, (role, path)
        print(json.dumps(dict(role=role, head=record["head"], files_verified=len(manifest["files"]))))


if __name__ == "__main__":
    main()
