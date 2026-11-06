# Combined epilogue qualification passed

Frozen combined kernel413c92b951fd426540f07446869b3e055733e126ae254ed7a2295f262d72ccd0 on77391e28: paired six-wait transpose plus ternary absmax. Scope remains unstaged in `flashinfer-swap-absmax-tree-review`.

- Fresh retained-control and combined-candidate arms each passed39 existing exact cases, zero failures/errors/skips, and76 executable CUBIN/resource checks. Tests cover all swap formats, SiTU/GeGLU/ReLU2, per-token output, one/twoCTA, narrow/partial tiles, K tails, stages and persistent reuse.
- All76 matched resource signatures have no growth in REG/STACK/LOCAL or LDL/STL sites. Actual7739 wideM512/K8 W4A8/MXFP8 baseline is160B stack with20LDL/20STL sites; combined is identical. Do not reuse the older b139168B/21-site baseline label. The other74 captures are zero-local.
- All39 reachable FC1 epilogues preserve their FMNMX site counts. Twelve relevant cases shorten max dependency8→3; thirteen SF32 cases9→4. Othercases keep their shorter/no-reduction chains. The paired waits alter generated instructions as expected, so no FC2/PTX/CUBIN identity claim is made against7739.
- All785 fetched artifact hashes passed; archive SHA256 `86dbae73d41969c6ca6ea3f7687f88d08d6454d1193479689614ff78e2691496`,17,117,403 bytes. Source/helper manifests and raw outputs are retained in `exact-evidence/`.
- `local-source.json` binds all514 sources. AST proofs match each changed function to its isolated component; all513 other files match7739. `integration-onto-c1c5402d.json` independently verifies that applying the exact `_absmax` function to committed paired-six-waitc1c5402d produces this measured combined source with no other difference. Scoped precommit passed.

This is numerical/resource/static-code qualification only. No combined performance or sanitizer run. The isolated tree44-cell results remain b139/abd55; standalone six-wait timing remains separate. No production source was modified by this qualification task.
