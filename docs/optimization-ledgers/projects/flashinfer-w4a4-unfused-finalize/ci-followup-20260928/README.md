# PR5319 H100 CI follow-up

Observed latest failed run36472070843, Targeted Unittest(H100), job109096727606, at original tested head bde427290b33c55489e39c75d7e2a25365358ca0. Full output is in artifacts/ci-h100.log.

The complete shard finished: 12740 nodes,1703 passed,4 failed,11033 skipped,0 unknown/pending. The failures were three outdated expected error-message regexes after the upstream SiTU enum addition, and an outdated generated Cake activation matrix row. No failure was in this PR's finalizer or PDL kernel changes. Both affected implementations/tests/docs are inherited unchanged from base07e519fc.

Upstream8b7ab98acdc6e125229c0165cdde9d6a1ab007b1(PR5628) already fixes all four: regexes now match `require ActivationType\.Situ or Swiglu`; the generated Cake row includes SiTU. Rebased the original four commits on a31c72523ae37d82fd657de36ce2b35156c3c559, producing9c39a45529c4bbffd866f7ae6255b19eaf835aa7. Range-diff marks all four commits `=`; the PR still changes exactly6files,306+/8−. Backup branch backup/pr5319-before-ci-fix-20260928 preserves bde42729.

The only CuTe production change since the earlier c2 run is upstreamW4A16 tracing hooks and extraction of the existing fence/release/commit sequence. Its new MegaMoE caller uses transform helpers through its own kernel, not the PR's standalone PDL entry. This warrants a focused W4A16 recheck, not an unrelated multi-rank campaign. Earlier155/214/96 results remain pinned to bde42729; no performance rerun is claimed.

Live NGC recheck still identifies26.05-py3 as newest CUDA13.2 PyTorch image (26.06/07 use13.3;26.08 uses13.4). Temporary c2B300 devbox fi5319-ci-0928 was first requested inziangli; quota was unavailable, so that queued request was deleted and retried ininfra. Same matching nightlySep23 wheel set, CuTe4.7.1 and full-source runtime setup as the earlier run. Commands and hashes are preserved here.

All eight regression-selection cases passed on full9c39a455 source, including all four previously failing nodes. Latest GitHub Build Docs, API/documentation, pre-commit, and CodeRabbit checks pass. New PR Test run36480641864 did not execute GPU tests: it reports CI skipped pending authorization for the rewritten head. All 64 W4A16 cases passed: 64 passed, 30 deselected, 1069 warnings in 388.62s. The regression selection passed 8 cases in 0.56s. There were no failures, errors, or skips in either executed selection.

Recovered complete logs, XML, commands, runtime/source identities, and native library hashes in `c2-evidence.tar.gz` (SHA256 `327f2f65d3d1ba19fb187f58cd9caff0a7b11f61746b413879d9d7549a334960`). All eight imported source module hashes match the local final head. `VALIDATION_PR.md` verifies all 72 verbose-log outcomes against JUnit XML and preserves every per-case result. No new performance benchmark was run.

Final update: GitHub authorized replacement run36482176398 at9c39a455; Permission/Setup passed, AOT build starting and GPU jobs queued. The initial authorization-blocked run is historical. PR remains ready for review and mergeable. Temporary infra c2devbox fi5319-ci-0928 deleted successfully after evidence recovery; see artifacts/devbox-cleanup.log.
