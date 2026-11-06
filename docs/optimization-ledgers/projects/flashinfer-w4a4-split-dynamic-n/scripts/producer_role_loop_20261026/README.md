# Producer role loop factoring

Independent unstaged source: `../../flashinfer-producer-role-loop-20261026`,
HEAD `dd266b91fdf61dae2de45ee9192d36c81c56be23`. Candidate patch: `27071f1958af501736e4922ac77aa8edb18120f65b0eb1f406d8f930a289c2c5`.
Only the Blackwell split blockscaled GEMM core changes.

The existing K loop is moved into one CuTe JIT helper whose `issue_tma` role
is compile-time constant. A warp-zero selection happens once per work tile;
warp zero retains all weight, weight-scale and activation TMA issues, while
all four producer warps retain the existing narrow-SF copies and arrivals.
There is no new public argument, dtype/shape policy, ring or ownership change.
The helper returns the advanced producer state explicitly. Persistent tile
scheduling, epilogue, scale publication, empty release/tail and startup PDL
prefetch are unchanged. Static reduction counts retain constexpr annotations.

`static-checks.json` proves the extracted loop is AST-equivalent except for
constexpr warp-role decisions and the reduction-size argument name. All other
class methods are unchanged. Ruff lint/format and `git diff --check` pass.

The control is frozen `retained-policy-r2/flashinfer`: its 0def+8828ab24 tree
is byte-identical to dd266b91, as recorded by the parent commit receipt.
Both source manifests and native shared-cache receipts are checked. GPU7 is
reserved only for the bounded public codegen capture and exact gate. Timing
is conditional on real SASS branch removal without spills/resource regression.
Rejected after the bounded four-case screen; no production change or push.

## Installed SDK persistence audit

Read-only live c3 source matches the earlier recorded CuTe DSL 4.7.1 SDK.
`compiler.py:1514-1515` forces `compile_only=True` and `no_cache=True` in
`cute.compile`; `dsl.py:2862-2863` separately disables caching for compile-only.
`CUTE_DSL_DISABLE_FILE_CACHING` defaults false, but cannot override these.
Both SDK disk loading and dumping are guarded by `not no_cache`, so there is
no environment-only persistent-cache switch for the current compile path.
`CUTE_DSL_CACHE_DIR` is recognized, but does not imply persisted objects.
Exact installed sources/hashes are in `sdk-cache-source.json`. No SDK changes
or environment changes were made to any running campaign. Native C++ modules,
generated sources, locks and cubins remain persistently shared through the
existing source-verified workspace preparation helper.

## Bounded validation so far

- Public V41 MXFP8 T128 captures both compile and execute successfully. FC1
  remains 80 registers; FC2 remains 90. Both keep 215,936 bytes dynamic shared
  memory, five operand stages, two accumulator stages, 128 TMEM columns,
  one resident CTA and zero spills.
- FC2 producer-role branches inside the old K loop (0x14c0 and 0x1a80) become
  one role selection outside the loop (0x13c0). The smaller SF-only loop is
  automatically fully unrolled by ptxas. Static instruction sites grow
  1,232 to 1,496 and cubin bytes 49,656 to 56,600. This is a code-size tradeoff,
  not an executed-instruction count. Original reduction bounds were already
  constexpr; neither source uses an explicit unroll directive here.
- 32 control plus 32 candidate changing-data/routes graph replays pass exact
  source-paired byte comparison, including empty then reactivated routes.
  Four configs cover standard/per-token NVFP4, MXFP8, MXFP4x8, narrow/wide SF,
  one/two CTA, inline/overlapped epilogues, static/CLC, and PDL off/on. Sixteen
  cores compile per source; all have zero spills and unchanged MMA commit
  counts. See `gate-summary.json`, `gate-registers.json`, and raw `gate/`.
- Broader forced-geometry gate register use does rise in seven cores, including
  inline N16/one-CTA FC2 from 106 to 124 (PDL) and 132 (no PDL). Storage and
  stage counts stay unchanged. The public V41 target's unchanged resource
  result should not be generalized to every geometry.
- Initial V41 MXFP8 T128 CAAC full-chain ratio is 0.99884x: neutral/slightly
  negative, insufficient to justify the code-size increase by itself.

## Final decision: reject

The source-paired gate passed, and SASS confirmed branch removal, but the
four authorized public saved-tactic comparisons show no useful gain. Each
process uses the existing benchmark methodology: cold L2, CUDA graphs, CUPTI,
10 warmups and 100 samples. CAAC repeats use identical saved tactics and
routing hashes; initial activation quantization is included for NVFP4.
No source, timing-cache or policy mutation occurs between arms.

| Model / dtype / tokens | Control C0 / C1 (us) | Candidate A0 / A1 (us) | Ratio |
|---|---:|---:|---:|
| kimi-k3 / MXFP4x8 / 64 | 233.2325 / 233.2320 | 234.6085 / 234.3050 | 0.994777x |
| kimi-k3 / W4A4 / 64 | 242.0975 / 241.6010 | 241.6965 / 241.9850 | 1.000035x |
| v3 / W4A4 / 64 | 132.8320 / 132.9290 | 133.2010 / 133.1530 | 0.997774x |
| v41-flash / MXFP8 / 128 | 469.0730 / 468.9615 | 469.6330 / 469.4890 | 0.998842x |

The existing `cutedsl` NV-family selector also runs unchanged W4A16. Its raw
results are retained as unchanged-path observations, not optimization wins.
The decision remains reject: extra code, some additional registers, and no
meaningful improvement. No unroll-policy follow-up or broader timing run.
GPU7 is idle and explicitly released to the pipeline agent for final tests.

Raw receipts, native cache pins, logs and all 100-sample arrays are in
`screens/`; exact/codegen outputs are in `gate/` and `codegen/`. Source and
helper files remain in the project folder. The canonical repository is untouched.
