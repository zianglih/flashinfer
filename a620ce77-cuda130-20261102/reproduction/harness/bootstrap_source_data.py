"""Materialize source-package native data paths declared in pyproject.toml."""
import argparse
import hashlib
import json
from pathlib import Path
import time


def source_data(repo):
    links = {"csrc": "../../csrc", "include": "../../include",
        "cutlass": "../../3rdparty/cutlass", "cccl": "../../3rdparty/cccl",
        "spdlog": "../../3rdparty/spdlog"}
    data = repo / "flashinfer/data"
    data.mkdir(exist_ok=True)
    record = {}
    for name, target in links.items():
        link = data / name
        if not link.is_symlink():
            assert not link.exists(), link
            link.symlink_to(target, target_is_directory=True)
        assert link.readlink() == Path(target) and link.resolve().is_dir()
        record[str(link.relative_to(repo))] = str(link.resolve())
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    before = args.config.read_bytes()
    config = json.loads(before)
    records = {}
    for role, source in config["sources"].items():
        source["native_data_links"] = source_data(Path(source["repo"]))
        Path(source["source_file"]).write_text(json.dumps(source, indent=2, sort_keys=True) + "\n")
        records[role] = source["native_data_links"]
    h = Path(__file__).parent
    config["observer_hashes"] = {str(p.relative_to(h)): hashlib.sha256(p.read_bytes()).hexdigest() for p in h.rglob("*.py")}
    args.config.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
    proof = dict(created=time.time(), config_before_sha256=hashlib.sha256(before).hexdigest(),
        config_after_sha256=hashlib.sha256(args.config.read_bytes()).hexdigest(), native_data_links=records,
        boundary="Packaging data path bootstrap only; symlinks reference each arm's exact Git source and pinned native dependencies. No source bytes, kernel math, tactics, or compiled artifacts changed.")
    (h / "source-data-bootstrap.json").write_text(json.dumps(proof, indent=2) + "\n")
    print(json.dumps(proof))


if __name__ == "__main__":
    main()
