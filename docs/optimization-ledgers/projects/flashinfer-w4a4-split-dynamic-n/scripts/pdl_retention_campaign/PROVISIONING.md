# CPU provisioning receipt

Provisioned on 2026-10-25 to `fi-w4a4-narrow-1025`, c1/ziangli, under `/workspace/flashinfer-w4a4-split-dynamic-n/scripts/pdl_retention_campaign`. Only named files were copied through `/usr/local/bin/h`; no recursive mirror/delete, source mutation, commit, CUDA import, GPU command, or benchmark launch occurred.

The current [provision-r3/receipt.json](provision-r3/receipt.json) reports `prerequisites_pass=true`. It pins ten campaign helpers/documents, five unchanged existing observer/helper files, the corrected-aab control's six source hashes, common benchmark/timer/tuner sources, environment, actual native headers/source trees, six native `build.ninja` files, package versions, and an unapproved remote A1 dry-run. `campaign.pending.json` still has no candidate repo, commit, source map or gate receipts and has `launch_approved=false`.

The active launcher SHA256 is `649426e3aebd55e0298938e5311e118ff2df871620c833d5602047973306a3ad`. Its measured observer loops are unchanged. The remote and local helper hashes match. The root-reserved GPU UUID assignments remain NVFP4/TRT2, MXFP8 3 and mixed4; this provisioning neither checks GPU activity nor claims those slots are currently idle. Execution rechecks them after the internal winner gate.

## Preserved setup findings

- `provision-r1` copied the campaign helpers but stopped when the frozen MX observer was absent remotely. `provision-r2` restored the existing local observer and its helpers byte-for-byte, without rewriting measurement code. All original files already present had to match exactly.
- The second prerequisite check incorrectly assumed every source-checkout gitlink directory was populated. `profile-aab93f/3rdparty/*` is intentionally uninitialized; a plain `git rev-parse HEAD` there ascends into its parent and returns aab, not a vendor identity. The failed receipt is preserved and is not evidence of changed vendor content.
- Actual native inputs follow `flashinfer/jit/env.py:398–411`: `flashinfer/data/{cutlass,cccl,spdlog}` resolve to the project-owned read-only baseline header checkouts. The corrected guard requires their own repository root, exact candidate gitlink HEAD, and clean tracked/untracked content. Their HEADs are CUTLASS `b46b16d003484063bca4ed365e44095c4c6ed633`, CCCL `16bd510c9b712e82b0ab6cbb630d8e29ba1f7116`, and spdlog `c3aed4b68373955e1cc94307683d44dca1515d2b`.
- The data `csrc/include` roots resolve to the retained candidate442 source. Their Git trees, respectively `0544fbc4bded1fc21539ed97fc603492ee27c82d` and `ad3dd79f5db10d8806709ddc0001cf15b459d8f6`, match aab's corresponding native trees and are clean. This preserves the established native cache epoch without switching to the original a65 cache.
- NIXL is uninitialized and unused by this single-GPU nondistributed campaign. Its gitlink is recorded; it was not cloned or downloaded. Frozen `profile-aab93f` and all shared header targets were left unchanged.
- Before updating the campaign's guard/README/CPU-check receipt, the provisioner required their previous exact hashes and archived those bytes under `provisioned-v1/` locally and remotely. Earlier attempts, logs and remote programs remain available.

The existing native workspace is `cache/candidate-442`; package metadata is Torch `2.12.0a0+5aff3928d8.nv26.5.50603568`, CuTe `4.7.1`, and CUPTI Python `13.4.0`. Six native build receipts cover FP4 quantization, routing, MXFP8 quantization, TRT utilities, TRT MoE and MoE utilities. `CUTE_DSL_KEEP` and `CUTE_DSL_DUMP_DIR` are unset, and the launcher also removes them from children. No source-specific CuTe cache reuse is assumed for an unknown winner.

## Frozen-clone handoff

[FROZEN_CLONE_PLAN.md](FROZEN_CLONE_PLAN.md) prepares new independent local `flashinfer-pdl-retention-frozen` and remote `pdl-retention-frozen` checkouts. Both proposed destinations were absent during preparation. No clone or commit was created. After root supplies the passing behavior source and gate, copy only its approved file map, let root review/create the freeze commit, transfer a self-contained Git bundle, and verify the identical commit/tree/blob hashes remotely. Restore only the known data/build-metadata setup and actual header inputs. A remote recommit is unnecessary and would risk a different SHA.

Provisioning is complete; winner selection, the clean freeze commit, exact gate binding and internal execution release remain pending. This is not a request for new user permission.


## Final freeze deployment

The final commit8c1a is provisioned in independent remote `pdl-retention-frozen`, with shallow boundaryaab after an unrelated historical missing-object failure. See `freeze-deploy-r1` (failure), `freeze-deploy-r2/receipt.json` (successful same-commit import, fsck, source/blob/header checks), and `campaign-provision/receipt.json` (immutable approved config and five exact gate hashes). No control/source repair, remote recommit, native-cache epoch switch, or historical baseline rerun occurred.
