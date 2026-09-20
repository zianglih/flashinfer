"""Local, CPU-only guard checks using a real temporary Git repository."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("capture", ROOT / "setup/capture_r3_numerical_failure.py")
capture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture)
checks = []
with tempfile.TemporaryDirectory(prefix="numerics-contract-", dir=ROOT / "artifacts") as tmp:
    root = Path(tmp)
    source = root / "source"
    source.mkdir()
    def git(*args):
        return subprocess.check_output(["git", "-C", str(source), *args], text=True).strip()
    git("init", "-q")
    git("config", "user.name", "Local Fixture")
    git("config", "user.email", "fixture@example.invalid")
    for name in capture.SOURCE_SHA:
        file = source / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text("# fixture: " + name + "\n")
    (source / "flashinfer").mkdir()
    (source / "flashinfer/runtime.py").write_text("# runtime fixture\n")
    git("add", ".")
    git("commit", "-qm", "fixture")
    capture.SOURCE_COMMIT = capture.RUNTIME_BASE = git("rev-parse", "HEAD")
    capture.SOURCE_SHA = {name: capture.sha(source / name) for name in capture.SOURCE_SHA}
    real = ROOT / "artifacts/run-transfers/glm52-calibration-20260920-r3-20260920T165707Z/runs/glm52-calibration-20260920-r3/001-correctness-ep4-allgather-caplive-r1/invocation.json"
    original = json.loads(real.read_text())
    original["pins"] = dict(benchmark_commit=capture.SOURCE_COMMIT, benchmark_sha256=capture.SOURCE_SHA, runtime_base=capture.RUNTIME_BASE)
    baseline = root / "r3/job/invocation.json"
    baseline.parent.mkdir(parents=True)
    cache = root / "r3/compiled-cache"
    cache.mkdir()
    for name, suffix in (("FLASHINFER_WORKSPACE_BASE", ""), ("TRITON_CACHE_DIR", "triton"), ("XDG_CACHE_HOME", "xdg"), ("CUDA_CACHE_PATH", "cuda")):
        original["env"][name] = str(cache / suffix)
    def run(name, value=None, out=None, expected=None):
        baseline.write_text(json.dumps(original if value is None else value))
        try:
            capture.prepare_contract(source, root / "new" if out is None else out, baseline)
        except ValueError as exc:
            assert expected and expected in str(exc), (name, exc)
        else:
            assert expected is None, name
        checks.append(name)
    run("valid real Git and file hashes")
    run("reject output under source", out=source / "new", expected="outside")
    run("reject output under preserved r3", out=root / "r3/new", expected="original run")
    (root / "existing").mkdir()
    run("reject existing output", out=root / "existing", expected="new and outside")
    altered = copy.deepcopy(original)
    altered["job"]["precomputed_routing"] = True
    run("reject changed routing job", altered, expected="case settings")
    altered = copy.deepcopy(original)
    altered["argv"].append("--no-pdl")
    run("reject changed PDL", altered, expected="PDL flags")
    altered = copy.deepcopy(original)
    altered["env"]["TRITON_CACHE_DIR"] = str(root / "elsewhere")
    run("reject escaped cache", altered, expected="escapes")
    altered = copy.deepcopy(original)
    altered["pins"]["runtime_base"] = "wrong"
    run("reject source identity drift", altered, expected="pins differ")
    (source / "untracked").write_text("dirty")
    run("reject dirty source", expected="not clean")
    (source / "untracked").unlink()
    file = next(iter(capture.SOURCE_SHA))
    old_sha = capture.SOURCE_SHA[file]
    capture.SOURCE_SHA[file] = "wrong"
    run("reject source content digest", expected="source hash differs")
    capture.SOURCE_SHA[file] = old_sha
    (source / "flashinfer/runtime.py").write_text("# changed runtime\n")
    git("add", ".")
    git("commit", "-qm", "runtime change")
    capture.SOURCE_COMMIT = git("rev-parse", "HEAD")
    original["pins"]["benchmark_commit"] = capture.SOURCE_COMMIT
    run("reject production kernel delta", expected="kernels differ")
result = {"scope": "CPU fixture only; no CUDA/NCCL or numerical execution", "helper_sha256": capture.sha(ROOT / "setup/capture_r3_numerical_failure.py"), "checks": checks, "passed": len(checks), "failed": 0}
(ROOT / "artifacts/numerical-capture-contract-validation.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
