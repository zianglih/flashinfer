"""Scan only the explicit publication allowlist; never print matching values."""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HEAD = "2b4732791a3ce48bc3ae6c030a283fab73854e0e"
CHUNK = 4 * 1024 * 1024
OVERLAP = 8192

# Prefix filters avoid repeatedly searching multi-gigabyte timing arrays.
PATTERNS = [
    ("private_key", (b"-----BEGIN",), rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA |ENCRYPTED )?PRIVATE KEY-----"),
    ("github_token", (b"gh", b"github_pat_"), rb"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
    ("slack_token", (b"xox",), rb"\bxox[baprs]-[A-Za-z0-9-]{10,}"),
    ("aws_access_key", (b"AKIA", b"ASIA"), rb"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    ("provider_api_key", (b"sk-", b"nvapi-"), rb"\b(?:sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{20,}|nvapi-[A-Za-z0-9_-]{20,})\b"),
    ("google_oauth", (b"ya29.",), rb"\bya29\.[A-Za-z0-9_-]{20,}"),
    ("jwt", (b"eyJ",), rb"\beyJ[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{12,}\b"),
    ("credential_url", (b"://",), rb"https?://[^\s/:@]+:[^\s/@]{6,}@"),
    ("signed_url_token", (b"X-Amz-", b"X-Goog-"), rb"[?&](?:X-Amz-Security-Token|X-Amz-Signature|X-Goog-Signature)=[A-Za-z0-9%+/=_-]{16,}"),
]
PATTERNS = [(name, prefixes, re.compile(pattern)) for name, prefixes, pattern in PATTERNS]
ASSIGNMENT = re.compile(rb'''(?ix)
    (?:["']|\b)(?:AWS_SECRET_ACCESS_KEY|AWS_SESSION_TOKEN|GITHUB_TOKEN|GH_TOKEN|HF_TOKEN|
    HUGGING_FACE_HUB_TOKEN|OPENAI_API_KEY|ANTHROPIC_API_KEY|NVIDIA_API_KEY|NGC_API_KEY|
    WANDB_API_KEY|H_TOKEN|HAI_API_KEY|ACCESS_TOKEN|AUTH_TOKEN|CLIENT_SECRET|PASSWORD|PRIVATE_KEY)
    (?:["']|\b)\s*[:=]\s*["']?([^\s"',}\\]{8,})
''')
AUTH = re.compile(rb"(?i)authorization[\"'\s:=]+(?:bearer|basic)[ \t]+([A-Za-z0-9+/._=-]{12,})")
PLACEHOLDERS = {b"redacted", b"<redacted>", b"[redacted]", b"placeholder", b"your_token_here", b"your_api_key"}
FORBIDDEN_SUFFIXES = (".tar", ".tar.gz", ".tgz", ".xz", ".zip", ".so", ".a", ".o", ".cubin", ".pyc")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    allow_path = HERE / "bundle-allowlist.json"
    allow = json.loads(allow_path.read_text())
    assert allow["passed"] and allow["head"] == HEAD
    categories = Counter()
    affected = set()
    seen_files = set()
    total = 0
    for records in allow["buckets"].values():
        for archive_name, record in records.items():
            assert not archive_name.endswith(FORBIDDEN_SUFFIXES), "Archive/cache artifact in allowlist"
            path = ROOT / record["path"]
            assert path.is_file() and path.resolve().is_relative_to(ROOT)
            if record["path"] in seen_files:
                continue
            seen_files.add(record["path"])
            digest = hashlib.sha256()
            tail = b""
            offset = 0
            hits = set()
            with path.open("rb") as stream:
                while block := stream.read(CHUNK):
                    digest.update(block)
                    total += len(block)
                    data = tail + block
                    origin = offset - len(tail)
                    for category, prefixes, pattern in PATTERNS:
                        if any(prefix in data for prefix in prefixes):
                            hits.update((category, origin + match.start()) for match in pattern.finditer(data))
                    lower = data.lower()
                    if any(word in lower for word in (b"token", b"secret", b"password", b"api_key", b"private_key")):
                        for match in ASSIGNMENT.finditer(data):
                            value = match[1].lower()
                            if value not in PLACEHOLDERS and not value.startswith((b"${", b"os.environ", b"os.getenv", b"getenv(")):
                                hits.add(("credential_assignment", origin + match.start()))
                    if b"authorization" in lower:
                        hits.update(("authorization_header", origin + match.start()) for match in AUTH.finditer(data))
                    offset += len(block)
                    tail = data[-OVERLAP:]
            assert digest.hexdigest() == record["sha256"], "Allowlisted file changed during scan"
            if hits:
                affected.add(record["path"])
                categories.update(category for category, _ in hits)
    result = dict(passed=not categories, head=HEAD, allowlist_sha256=sha(allow_path),
        scanned_files=len(seen_files), scanned_bytes=total, affected_files=len(affected),
        category_counts=dict(categories), scanner_sha256=sha(Path(__file__)),
        full_source_archives_or_compilation_cache_files=0,
        boundary="Bounded pattern scan of the explicit publication allowlist only. Matching values and paths are not emitted. This is a credential screen, not a proof that arbitrary private information is absent.")
    (HERE / "credential-scan.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("passed", "scanned_files", "affected_files", "category_counts", "full_source_archives_or_compilation_cache_files")}))
    assert result["passed"], "Credential-pattern findings require private review before publication"


if __name__ == "__main__":
    main()
