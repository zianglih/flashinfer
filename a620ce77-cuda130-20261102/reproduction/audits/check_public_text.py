"""Inspect selected public evidence text without ever printing matched values."""
import re


PATTERNS = {
    "credential_url": re.compile(r"https?://[^\s/:]+:[^\s/@]+@", re.IGNORECASE),
    "signed_or_authenticated_url": re.compile(r"https?://[^\s<>\"']*[?&](?:X-Amz-(?:Signature|Credential|Security-Token)|X-Goog-(?:Signature|Credential)|access_token|api_key|token|sig)=[^\s&<>\"']+", re.IGNORECASE),
    "github_token": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,})\b"),
    "aws_access_key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "slack_token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
    "huggingface_token": re.compile(r"\bhf_[A-Za-z0-9]{25,}\b"),
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"),
    "assigned_secret": re.compile(r"\b(?:GITHUB_TOKEN|GH_TOKEN|AWS_SECRET_ACCESS_KEY|AWS_SESSION_TOKEN|HF_TOKEN|OPENAI_API_KEY|ANTHROPIC_API_KEY)\b[\"']?\s*[:=]\s*[\"']?([^\s\"',}]+)", re.IGNORECASE),
    "bearer_authorization": re.compile(r"\bAuthorization[\"']?\s*[:=]\s*[\"']?Bearer\s+[A-Za-z0-9_./+=-]{15,}", re.IGNORECASE),
}


def inspect_bytes(name, content):
    if b"\x00" in content[:4096]:
        return []
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return []
    findings = []
    for category, pattern in PATTERNS.items():
        matches = list(pattern.finditer(text))
        if category == "assigned_secret":
            matches = [m for m in matches
                       if m.group(1).lower() not in ("none", "null", "false", "true", "unset")
                       and not m.group(1).startswith("re.compile(")]
        if matches:
            findings.append(dict(file=name, category=category, count=len(matches)))
    return findings
