# Independent d788 native admission

PASS for the three actual compile-only captures; admission was sent before this
note. Source d78808f4a7573a0f6e36be6e369c14c4f925299ae22201ef7d9621a5be94668a,
manifest b85f584ce13e2e2616ec684de966a2977f113f93fea9f3bfb74a04bd2e92513c,
transport b848151a / formatted patch a5563156. Controls are the actual0910b64a8
captures with recorded matching compiler/DSL, not new0911a control captures.
Support-library85d7 versus older native-cache bytes are a separate boundary;
this review is device codegen/source admission, not a timing equivalence claim.
No compilation, launch, validator/oracle replay or original comparator rerun.

Candidate roots are profiles/cu132-recovery0911a-dispatch-total-bound-no-exhaustion-checks-default-candidate-{case}/codegen;
controls use cu132-recovery0910b-dispatch-total-bound-default-candidate-{case}.

| Case | Candidate result SHA256 | SASS instructions before→after |
|---|---|---|
| n64-f4-direct | 85d1d71dc75cdab97893b4a0a3b747802246d261f04d720f98c7cfbeffbdd838 | 5496→5480 |
| n128-f8-reuse | a6c01833abc47ef4ecb00b7300a5778b99598fd46801205651a3184581ddef2c | 6192→6184 |
| n64-f1-direct | 69fc9a4c838cdad593e373fc1988517fb920e3a519c3c647d4c2469070adb4ba | 5448→5432 |

All three have compile1/launch0/alloc0/collective-init0; config/options exact to
controls. REG96/640 threads/STACK0/LOCAL0/staticSMEM1024/grid[2,1,74] stay fixed.
Dynamic SMEM200064/230784/200064 and raw/B/D5/3/3,4/3/2,5/3/3 stay fixed for
both FC1/FC2; scheduler2 and register redistribution remain unchanged.

**Mapping/empty exit.** One total REDUX remains at d290/ef10/d270. Initial total
checks d2b0/ef30/d290 skip to the existing tail when no token is admitted.
Prefix loops now test only token versus expert_end: N64 d390/d500, N128
f010/f1c0, F1 d350/d4c0. The per-lane expert-count selection and SHFL remain
(d480/f190/d440), followed by the existing expert-change/rank-lane checks and
unrolled rank peeling. The three obsolete expert<num_experts exhaustion guards
and their merges are removed. Under the unchanged nonnegative Int32 prefix
contract, outer token<total guarantees the prefix search finds a valid expert,
including zero prefixes; no unchecked out-of-range exhaustion path is newly
reachable. Stride592 and one phase XOR remain. Backedge total checks
11c70/13920/11b10 branch to d390/f010/d350 respectively.

**Protected protocol.** With only PTX virtual-register numbers normalized, the
ordered election, bulk-copy/wait/commit, mbarrier, CTA/warp barrier, release
atomic and tcgen05 instruction sequences equal their respective controls.
Their counts are elect51/52/51, bulk19/23/16, mbarrier118/113/118,
bar30/31/29, release13/14/12 and tcgen0586/128/86. Full-mask election operands,
READ/full wait distinction, F1 specialization, full-batch/tail syncs, phases,
publication and inherited reuse return remain present. This is protected
sequence equality, not whole-native or scheduling-control identity.

Actual routing sequence (LDG→input→payload→provenance→commit→weight STG):
N64/F4 115f0→11710→11930→11940→11950→11960;
N128/F8 13290→133c0→135e0→135f0→13600→13610;
N64/F1 115b0→116d0→118b0→118c0→118d0→118e0.
For each LDG the encoded write dependency is5. The mainline's first explicit
result use and first waitmask0x20 are the final weight STG, after payload issue;
intervening bulk DEPBAR does not consume that result dependency. The separate
election-recovery WARPSYNC still can wait earlier: N64/F4 153b0 mask0x24,
N128/F8 17be0 mask0x2a and N64/F1 15120 mask0x24. All include wb5; preserve the
conditional mainline/recovery qualification and infer neither recovery frequency
nor end-to-end overlap benefit from these static sites.

SASS SHA256: N64/F4 8a9dc3f41fc51c206f585224d74450d3466b67c26a2241ef572c7135d3b14402;
N128/F8 f57c5d29da7d25a012f908cbba722c15419edd7c6b3b1ab1cabc08d64305dc28;
N64/F1 b998ac6a3e6edb3d9e0aa10d043fa5d954198e65a30ef27cdebea3fde5f0396a.
