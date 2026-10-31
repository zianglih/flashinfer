"""Guard candidate cubins before the unmodified benchmark observer measures them."""
import json
import os
from pathlib import Path
import sys


def run(main, observer_file):
    root = Path(observer_file).resolve().parent
    config = json.loads(Path(os.environ['FI_OWNERSHIP_CONFIG']).read_text())
    repo = Path(sys.argv[sys.argv.index('--repo') + 1]).resolve()
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    arm = next(name for name,s in config['sources'].items() if repo == Path(s['repo']).resolve())
    candidate = config['sources'][arm]
    source_file = Path(candidate['source_file'])
    source = json.loads(source_file.read_text())
    w4 = '--w4a16-only' in sys.argv
    policy = dict(control=80,gather=64,epilogue=144) if w4 else config['register_policies'][arm]
    assert source['source_sha256'] == candidate['source_sha256']
    os.environ.update(
        REG_GUARD_SOURCE=str(source_file),
        REG_GUARD_REPO=str(repo),
        REG_GUARD_KERNEL_SHA=source['source_sha256']['flashinfer/fused_moe/cute_dsl/blackwell/' + ('moe_w4a16_kernel.py' if w4 else 'moe_swap_ab_kernel.py')],
        REG_GUARD_OUTPUT=str(output.parent / 'register-guard' / output.name),
        **{'REG_GUARD_' + key.upper(): str(value) for key, value in policy.items()},
    )
    sys.path.insert(0, str(repo))
    if w4:
        from register_guard_w4 import install
    else:
        from register_guard import install
    finish = install()
    exitstatus = 1
    try:
        result = main()
        exitstatus = 0 if result is None else int(result)
        return result
    finally:
        finish(exitstatus)
