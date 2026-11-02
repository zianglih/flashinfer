"""Bind source snapshots and replay published W4 tactics on the installed runtime.

Only cache environment metadata is rebound. Neither source, entry keys, tactics,
profiling policies, nor historical data are rewritten. No profiling is performed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

H = Path(__file__).resolve().parent
ROOT = H.parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def import_choices(role):
    repo = ROOT / "sources" / role
    sys.path.insert(0, str(repo))
    from flashinfer.autotuner.autotuner import _collect_metadata

    metadata = _collect_metadata()
    output = H / "rebound" / role
    output.mkdir(parents=True, exist_ok=False)
    records = {}
    for name in json.loads((H / "jobs.json").read_text()):
        frozen = H / "frozen" / name
        if role == "before":
            original = json.loads((frozen / "before-cache.json").read_text())
            entries = {k: v for k, v in original.items() if k != "_metadata"}
            target = output / (name + ".json")
            write(target, dict(entries, _metadata=metadata))
            saved = json.loads(target.read_text())
            assert {k: v for k, v in saved.items() if k != "_metadata"} == entries
            records[name] = dict(path=str(target), kind="native", before_metadata=original["_metadata"],
                after_metadata=metadata, entries_sha256=hashlib.sha256(json.dumps(entries, sort_keys=True).encode()).hexdigest())
        elif role == "after":
            from flashinfer.autotune_cache import ManagedAutotuneCache

            manifests = list((frozen / "after-cache/v2").glob("*/manifest.json"))
            assert len(manifests) == 1
            old = json.loads(manifests[0].read_text())
            extra = {k: v for k, v in old.items() if k not in metadata and k != "cache_schema"}
            assert set(extra) <= {"measure_execution_mode"}, extra
            cache = ManagedAutotuneCache(dict(metadata, **extra), root=output / name)
            cache.entries_dir.mkdir(parents=True)
            write(cache.env_dir / "manifest.json", cache.manifest)
            for src in (manifests[0].parent / "entries").glob("*.json"):
                dst = cache.entries_dir / src.name
                shutil.copy2(src, dst)
                assert sha(src) == sha(dst)
            records[name] = dict(path=str(output / name), kind="managed", before_metadata=old,
                after_metadata=cache.manifest, original_entry_bytes_preserved=True)
        else:
            raise ValueError(role)
    write(output / "receipt.json", dict(role=role, jobs=records, metadata=metadata, no_retuning=True,
        boundary="Explicit fixed-choice replay across runtimes. Metadata is refreshed to permit recompilation of published tile choices; this does not establish optimal tactics on CUDA13.0."))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--import-role", choices=("before", "after"))
    parser.add_argument("--cache-root", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.import_role:
        import_choices(args.import_role)
        return
    assert args.cache_root and args.output
    args.cache_root = args.cache_root.resolve()
    args.output = args.output.resolve()
    proof = json.loads((H / "frozen-provenance.json").read_text())
    for rel, digest in proof["files"].items():
        assert sha(ROOT / rel) == digest, rel
    sources = {}
    from bootstrap_source_data import source_data
    for role in ("before", "after"):
        snapshot = json.loads((ROOT / "sources" / (role + "-manifest.json")).read_text())
        repo = ROOT / "sources" / role
        for rel, digest in snapshot["files"].items():
            assert sha(repo / rel) == digest, (role, rel)
        # Per-process verification binds the Python dispatch, JIT and kernels;
        # the full native header/source tree was verified immediately above.
        owned = {p: d for p, d in snapshot["files"].items()
                 if p.startswith(("flashinfer/", "benchmarks/")) and p.endswith(".py")}
        source = dict(head=snapshot["head"], repo=str(repo), source_sha256=owned,
            tracked_manifest=str(ROOT / "sources" / (role + "-manifest.json")),
            tracked_manifest_sha256=sha(ROOT / "sources" / (role + "-manifest.json")),
            source_file=str(H / (role + "-source.json")),
            workspace_base=str(args.cache_root / "cpp" / role),
            cute_cache=str(args.cache_root / "cute" / role),
            cubin_dir=str(args.cache_root / "cubin" / role),
            swap_ab=role == "after")
        source["native_data_links"] = source_data(repo)
        write(Path(source["source_file"]), source)
        sources[role] = source
        subprocess.run([sys.executable, str(Path(__file__).resolve()), "--import-role", role], check=True)
    jobs = json.loads((H / "jobs.json").read_text())
    for name, job in jobs.items():
        job["arms"] = {}
        for role in ("before", "after"):
            imported = json.loads((H / "rebound" / role / "receipt.json").read_text())["jobs"][name]
            job["arms"][role] = dict(winner_results=str(H / "frozen" / name / (role + "-expected.json")),
                winner_cache=imported["path"], cache_kind=imported["kind"], observer=str(H / role / "observe_benchmark.py"))
    config = dict(python=sys.executable, jobs=jobs, sources=sources, output=str(args.output.resolve()),
        driver_cache=str(args.cache_root / "driver"), phases=["before", "after", "after", "before"],
        observer_hashes={str(p.relative_to(H)): sha(p) for p in H.rglob("*.py")},
        phase_timeout_seconds=7200, default_w4a16_moe_tactic=[[[256, 128, 256], [2, 1], True], [[256, 128, 256], [2, 1], True]],
        boundary="Fresh CUDA13.0 C-A-A-C strict CUPTI cold-L2 CUDA-graph replay; 10 warmups and100 samples per cell per phase. Published per-arm tile choices are frozen, no tuning. Before002 old64 layout versus aftera620 new16 layout. Full pipeline W4A16 BF16 input, unfused finalize. Tokens1/2 raw only; aggregates exclude them. Fresh routing must match across arms; historical route identity differences are recorded.")
    write(H / "config.json", config)
    print(json.dumps(dict(config=str(H / "config.json"), jobs=len(jobs), cells_per_phase=104)))


if __name__ == "__main__":
    main()
