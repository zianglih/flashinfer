"""Splice reviewed performance prose into a fresh PR snapshot; never write GitHub."""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
START = "**End-to-end performance.**"
END = "**Historical shared-helper evidence.**"
OLD_BOUNDARY = "- **Boundary:** no new benchmark or sanitizer run; existing performance figures remain attributed to their original measured revisions."
NEW_BOUNDARY = "- **Boundary:** no new sanitizer run. Fresh benchmark results and their comparison boundaries are reported above."


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--performance-section", type=Path, required=True)
    args = parser.parse_args()
    record = json.loads(args.snapshot.read_text())
    body = record["body"]
    assert body.count(START) == body.count(END) == body.count(OLD_BOUNDARY) == 1
    start, end = body.index(START), body.index(END)
    replacement = args.performance_section.read_text().rstrip() + "\n\n"
    assert replacement.startswith(START) and END not in replacement
    assert "{{" not in replacement and "PLACEHOLDER" not in replacement
    revised = (body[:start] + replacement + body[end:]).replace(OLD_BOUNDARY, NEW_BOUNDARY)
    assert len(revised.encode()) < 65536
    suffix = body[end:].replace(OLD_BOUNDARY, NEW_BOUNDARY)
    assert revised[revised.index(END):] == suffix
    assert revised[:start] == body[:start]
    glm_start, glm_end = body.index("### Shared W4A16 dequantizer: GLM5 MegaMoE"), body.index("## 🔍 Related Issues")
    glm = body[glm_start:glm_end]
    assert glm in revised
    target = HERE / "pr-body.md"
    target.write_text(revised)
    (HERE / "body-edit-proof.json").write_text(json.dumps(dict(passed=True,
        source_snapshot=str(args.snapshot.resolve()), source_body_sha256=digest(body),
        result_body_sha256=digest(revised), preserved_glm5_sha256=digest(glm),
        only_performance_section_and_test_boundary_changed=True, bytes=len(revised.encode())), indent=2) + "\n")
    print(target)


if __name__ == "__main__":
    main()
