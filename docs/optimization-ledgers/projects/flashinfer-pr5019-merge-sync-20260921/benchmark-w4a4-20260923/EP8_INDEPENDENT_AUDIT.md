# EP8 independent evidence audit

EP8 sweep 1 was initially reconstructed from all eight rank JSONL files on 2026-09-23, without invoking the campaign renderer. The completed two-sweep audit follows below.

- All 3,900 rank-MAX samples exactly match maxima reconstructed from 31,200 raw rank spans, with 100 positive finite samples per arm/token row and the required fixed arm order.
- Input and route hashes match across all three arms. Canonical weight hashes remain constant across all 13 token rows. Source/helper manifests, measured revision, and image exactly match the EP4 campaign; helpers still match their recorded bytes.
- All 312 untimed logical rank/output checks are finite and repeat-bit equal, including empty source ranks. Output shapes/dtypes match the global-token partition and BF16 output contract.
- All ranks agree on every selected Mega tactic (208 rank records). Both Mega variants use FC2 routing placement with IKR disabled; all ranks record 39 deferred CUPTI finalizations and successful completion.
- All 13 archive members match extracted evidence bytes. Archive SHA-256: `b4cd9a4a50abe7925d22a4c7823e3800562361e0185ebbdf8f727cd3f871dd10`.

No correctness or provenance finding. These output checks do not establish numerical equivalence across precision modes.

## Completed pair and final publication audit

After sweep 2 completed, independent reconstruction from all 16 EP8 rank files confirmed all 13 pooled rows in `final-performance.json`: 200-sample medians, both speedup ratios, per-sweep medians, MAD, successive 25-sample medians, and both sweeps' full selected tactic dictionaries match exactly. All 7,800 rank-MAX samples reconstruct from 62,400 raw spans; all 624 untimed logical output checks are finite and repeat-bit equal. All ranks agree on the 416 Mega tactic records. Inputs/routes/weights, environment, source/helper manifests and node/boot identity match across sweeps, and both archives match the final evidence-file hashes. The EP4 result remains identical to its independently validated preview.

EP8 decode 4–512 geometric speedups of Mega W4A16 are **1.226528038651223× over Split W4A16** and **1.1207783291114768× over Mega W4A4**. Prefill precision ratios at 4096/8192/16384 are **0.6448660638041163× / 0.48230632349434066× / 0.4035229451651081×**; W4A4's prefill advantage is retained.

The final publication draft, SHA-256 `bef0ffd51f0da790b5737b0ae5613df1fd7dd3d4c5fd6473a01f9544172d5bc1`, contains the exact 26 final latency/tactic rows and 52 per-sweep latency rows, four matching archive hashes, and all 936 logical output checks. It explicitly scopes each check to two extra eager forwards, preserves measured `44a04fd + patch428b` separately from published `19e8aebb`, and includes the timing-drift/near-parity caveat. Both Bash blocks pass syntax checks. No pending status, private paths or removed runtime-alpha performance section remains. Experimental/reviewer/CodeRabbit content exactly matches the fresh `pr5019-final-prewrite.json` snapshot. No blocking publication finding.
